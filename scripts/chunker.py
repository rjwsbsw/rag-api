import fitz  # PyMuPDF
import nltk
import sys
from nltk.tokenize import sent_tokenize

nltk.download('punkt')
nltk.download('punkt_tab')

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

def chunk_pdf_with_metadata(pdf_path, chunk_size=100):
    doc = fitz.open(pdf_path)
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

    return all_chunks

def main():
    if len(sys.argv) < 2:
        print("Usage: python chunk_pdf.py <pdf_path>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    chunks = chunk_pdf_with_metadata(pdf_path, chunk_size=100)

    for chunk in chunks:
        print(f"\n--- Seite {chunk['page']} | Chunk {chunk['chunk_index']} ---\n{chunk['text']}\n")

if __name__ == "__main__":
    main()