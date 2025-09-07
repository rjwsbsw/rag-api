-- pgvector Extension aktivieren
CREATE EXTENSION IF NOT EXISTS vector;

-- Bücher-Metadaten Tabelle
CREATE TABLE books (
    id SERIAL PRIMARY KEY,
    book_id VARCHAR(100) UNIQUE NOT NULL,
    title VARCHAR(500) NOT NULL,
    total_pages INTEGER,
    total_chunks INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Haupttabelle für Buch-Chunks
CREATE TABLE book_chunks (
    id SERIAL PRIMARY KEY,
    book_id VARCHAR(100) NOT NULL,
    chunk_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    embedding vector(384),  -- all-MiniLM-L6-v2 Dimension
    page_number INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indizes für Performance
CREATE INDEX book_chunks_book_id_idx ON book_chunks(book_id);
CREATE INDEX books_book_id_idx ON books(book_id);

-- Permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO rag_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO rag_user;
