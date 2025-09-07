from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncpg
import httpx
import logging
from sentence_transformers import SentenceTransformer
import fitz  # PyMuPDF
import nltk
from nltk.tokenize import sent_tokenize
from io import BytesIO
from typing import List
import os
from docx import Document

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="RAG Buchassistent API", version="1.0.0")

# CORS für Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global objects
embedder = None
db_pool = None

# material für die tokenizer
nltk.download('punkt')
nltk.download('punkt_tab')

class QuestionRequest(BaseModel):
    question: str
    book_id: str
    max_results: int = 3

@app.on_event("startup")
async def startup():
    global embedder, db_pool
    
    logger.info("Initializing services...")
    
    # Sentence Transformer laden
    embedder = SentenceTransformer('all-MiniLM-L6-v2')
    logger.info("Embedding model loaded")
    
    # PostgreSQL Connection Pool
    database_url = os.getenv("DATABASE_URL", 
        "postgresql://rag_user:rag_password@postgres:5432/buchplattform")
    
    try:
        db_pool = await asyncpg.create_pool(database_url, min_size=2, max_size=10)
        logger.info("PostgreSQL connection pool created")
        
        # Test connection
        async with db_pool.acquire() as conn:
            version = await conn.fetchval("SELECT version()")
            logger.info(f"Connected to PostgreSQL: {version[:50]}...")
            
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise

@app.get("/health")
async def health_check():
    try:
        async with db_pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        return {"status": "healthy", "services": {"postgresql": True, "embedder": True}}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

@app.post("/ask")
async def ask_question(request: QuestionRequest):
    """Frage an ein spezifisches Buch stellen"""
    
    try:
        async with db_pool.acquire() as conn:
            # Prüfen ob Buch existiert
            book_exists = await conn.fetchval(
                "SELECT book_id FROM books WHERE book_id = $1", request.book_id
            )
            if not book_exists:
                raise HTTPException(status_code=404, detail=f"Buch '{request.book_id}' nicht gefunden")
            
            # Frage-Embedding erstellen
            query_embedding = embedder.encode([request.question])[0]
            
            # Vector Similarity Search
            results = await conn.fetch("""
                SELECT content, page_number, chunk_id,
                       1 - (embedding <=> $1::vector) as similarity
                FROM book_chunks 
                WHERE book_id = $2 
                ORDER BY embedding <=> $1::vector 
                LIMIT $3
            """, str(query_embedding.tolist()), request.book_id, request.max_results)
            
            if not results:
                raise HTTPException(status_code=404, detail=f"Keine Inhalte für Buch '{request.book_id}' gefunden")
            
            # Kontext zusammenstellen
            context_chunks = [result['content'] for result in results]
            context = "\n\n".join(context_chunks)
            
            # Prompt für Ollama
            prompt = f"""Du bist ein hilfsreicher Buchassistent. Beantworte die Frage basierend auf dem Kontext aus dem Buch. 
Wenn die Antwort nicht im Kontext steht, sage das ehrlich.

Kontext aus dem Buch "{request.book_id}":
{context}

Frage: {request.question}

Antwort:"""

            # Ollama API Call (mit längerem Timeout für Modell-Loading)
            ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
            async with httpx.AsyncClient(timeout=180.0) as client:  # 3 Minuten Timeout
                response = await client.post(
                    f"{ollama_url}/api/generate",
                    json={
                        "model": "llama3.1:8b",
                        "prompt": prompt,
                        "stream": False
                    }
                )
            
            if response.status_code != 200:
                logger.error(f"Ollama error: {response.text}")
                raise HTTPException(status_code=500, detail="Fehler bei LLM-Anfrage")
            
            answer = response.json().get("response", "Keine Antwort erhalten")
            
            return {
                "question": request.question,
                "answer": answer,
                "book_id": request.book_id,
                "context_chunks_used": len(context_chunks),
                "sources": [
                    {
                        "page": result['page_number'],
                        "similarity": float(result['similarity'])
                    } for result in results
                ]
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler bei Fragenbeantwortung: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/books/{book_id}")
async def delete_book(book_id: str):
    """Buch und alle seine Chunks löschen"""
    
    try:
        async with db_pool.acquire() as conn:
            # Prüfen ob Buch existiert
            existing = await conn.fetchval(
                "SELECT book_id FROM books WHERE book_id = $1", book_id
            )
            if not existing:
                raise HTTPException(status_code=404, detail=f"Buch '{book_id}' nicht gefunden")
            
            # Löschen in Transaktion
            async with conn.transaction():
                # Erst zählen wie viele Chunks existieren
                chunks_count = await conn.fetchval(
                    "SELECT COUNT(*) FROM book_chunks WHERE book_id = $1", book_id
                )
                
                # Chunks löschen
                await conn.execute("DELETE FROM book_chunks WHERE book_id = $1", book_id)
                
                # Buch löschen
                await conn.execute("DELETE FROM books WHERE book_id = $1", book_id)
            
            logger.info(f"Buch '{book_id}' gelöscht: {chunks_count} Chunks entfernt")
            
            return {
                "message": f"Buch '{book_id}' erfolgreich gelöscht",
                "chunks_deleted": chunks_count or 0
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler beim Löschen des Buchs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/books")
async def list_books():
    """Alle verfügbaren Bücher auflisten"""
    
    try:
        async with db_pool.acquire() as conn:
            books = await conn.fetch("""
                SELECT book_id, title, total_pages, total_chunks, created_at
                FROM books
                ORDER BY created_at DESC
            """)
            
            return {
                "books": [
                    {
                        "book_id": book['book_id'],
                        "title": book['title'],
                        "pages": book['total_pages'],
                        "chunks": book['total_chunks'],
                        "uploaded_at": book['created_at'].isoformat()
                    }
                    for book in books
                ]
            }
        
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der Bücherliste: {e}")
        raise HTTPException(status_code=500, detail=str(e))

#######################################################
# upload-books inkl. Hilfsfunktionen
#######################################################

@app.post("/upload-book")
async def upload_book(file: UploadFile = File(...), book_id: str = None):
    if not book_id:
        book_id = file.filename.split('.')[0]

    try:
        async with db_pool.acquire() as conn:
            existing = await conn.fetchval(
                "SELECT book_id FROM books WHERE book_id = $1", book_id
            )
            if existing:
                raise HTTPException(status_code=400, detail=f"Buch '{book_id}' existiert bereits")

            file_bytes = await file.read()

            # Format erkennen
            if file.filename.lower().endswith(".pdf"):
                all_chunks, page_count = chunk_pdf_with_metadata(BytesIO(ile_bytes))
            elif file.filename.lower().endswith(".docx"):
                all_chunks, page_count = chunk_docx_with_metadata(BytesIO(file_bytes))
            else:
                raise HTTPException(status_code=415, detail="Nur PDF und DOCX werden unterstützt")

            # Embeddings
            embeddings = embedder.encode([c['text'] for c in all_chunks])
            for chunk, embedding in zip(all_chunks, embeddings):
                chunk['embedding'] = embedding

            # Speichern
            async with conn.transaction():
                await conn.execute("""
                    INSERT INTO books (book_id, title, total_pages, total_chunks)
                    VALUES ($1, $2, $3, $4)
                """, book_id, file.filename, page_count, len(all_chunks))

                for ac in all_chunks:
                    await conn.execute("""
                        INSERT INTO book_chunks (book_id, chunk_id, content, embedding, page_number)
                        VALUES ($1, $2, $3, $4, $5)
                    """,
                    book_id,
                    ac['chunk_index'],
                    ac['text'],
                    str(ac['embedding'].tolist()),
                    ac['page'] or 0)

            logger.info(f"Buch '{book_id}' erfolgreich verarbeitet: {len(all_chunks)} Chunks")
            return {
                "message": f"Buch '{book_id}' erfolgreich hochgeladen",
                "chunks_created": len(all_chunks),
                "pages_processed": page_count,
                "book_id": book_id
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler beim Verarbeiten des Buchs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

#--------------------------

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extrahiert Text aus einem PDF mit PyMuPDF"""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    text = ""
    for page_num, page in enumerate(doc):
        page_text = page.get_text()
        text += f"\n--- Seite {page_num + 1} ---\n{page_text}"
    return text, len(doc)

def chunk_pdf_with_metadata(pdf_bytes, chunk_size=100):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    all_chunks = []

    for page_num, page in enumerate(doc):
        text = page.get_text()
        if not text.strip():
            continue

        chunks = chunk_text_by_sentences(text, chunk_size=chunk_size)
        for i, chunk in enumerate(chunks):
            all_chunks.append({
                "page": page_num + 1,
                "chunk_index": i,
                "text": chunk
            })

    return all_chunks, len(doc)

#----------------------------------------

def extract_text_from_docx(docx_bytes: bytes) -> str:
    doc = Document(docx_bytes)
    return "\n".join([para.text for para in doc.paragraphs if para.text.strip()])

def chunk_docx_with_metadata(docx_bytes, chunk_size=100):
    text = extract_text_from_docx(docx_bytes)
    chunks = chunk_text_by_sentences(text, chunk_size=chunk_size)
    all_chunks = []
    for i, chunk in enumerate(chunks):
        all_chunks.append({
            "page": None,  # Word hat keine Seiten
            "chunk_index": i,
            "text": chunk
        })
    estimated_pages = max(1, len(text.split()) // 500)
    return all_chunks, estimated_pages

#----------------------------------------

def extract_text_from_txt(txt_bytes: bytes) -> str:
    return txt_bytes.decode("utf-8")

def chunk_txt_with_metadata(txt_bytes, chunk_size=100):
    text = extract_text_from_txt(txt_bytes)
    # Absätze erkennen
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    all_chunks = []
    chunk_index = 0

    for para in paragraphs:
        chunks = chunk_text_by_sentences(para, chunk_size=chunk_size)
        for chunk in chunks:
            all_chunks.append({
                "page": None,
                "chunk_index": chunk_index,
                "text": chunk
            })
            chunk_index += 1

    estimated_pages = max(1, len(text.split()) // 500)
    return all_chunks, estimated_pages

#----------------------------------------

def chunk_text_by_sentences(text, chunk_size=100):
    sentences = sent_tokenize(text)
    chunks = []
    current_chunk = []

    for sentence in sentences:
        current_words = sum(len(s.split()) for s in current_chunk)
        if current_words + len(sentence.split()) > chunk_size:
            chunks.append(" ".join(current_chunk))
            current_chunk = [sentence]
        else:
            current_chunk.append(sentence)

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks

#------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)