#!/bin/bash

BACKUP_DIR="backup/db"
mkdir -p "$BACKUP_DIR"

# Vollständiger Dump (Struktur + Daten)
docker-compose exec postgres pg_dump -U rag_user -d buchplattform > "$BACKUP_DIR/backup.sql"

# Nur Schema (ohne Daten - für Disaster Recovery Tests)
# docker-compose exec postgres pg_dump -U rag_user -d buchplattform --schema-only > "$BACKUP_DIR/schema.sql"

# Nur Daten (ohne Schema)
# docker-compose exec postgres pg_dump -U rag_user -d buchplattform --data-only > "$BACKUP_DIR/data.sql"


# Custom Format (komprimiert, parallel restore möglich)
#docker-compose exec postgres pg_dump -U rag_user -d buchplattform -Fc > "$BACKUP_DIR/backup.dump"

# Directory Format (für große DBs mit parallelem Backup)
#docker-compose exec postgres pg_dump -U rag_user -d buchplattform -Fd -f "$BACKUP_DIR/backup_dir"