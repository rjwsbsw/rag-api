#!/bin/bash

BACKUP_DIR="backup/db"
mkdir -p "$BACKUP_DIR"

# 1. PostgreSQL Container starten
docker-compose up -d postgres

# 2. Datenbank wiederherstellen
docker-compose exec -T postgres createdb -U rag_user buchplattform
docker-compose exec -T postgres pg_restore -U rag_user -d buchplattform < "$BACKUP_DIR/database.dump"

# 3. DB-Integrität prüfen
docker-compose exec postgres psql -U rag_user -d buchplattform -c "
SELECT COUNT(*) as books FROM books;
SELECT COUNT(*) as chunks FROM book_chunks;
SELECT pg_size_pretty(pg_database_size('buchplattform')) as db_size;
"