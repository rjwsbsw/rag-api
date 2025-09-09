#!/bin/bash
# Vollständiger Dump (Struktur + Daten)
docker-compose exec postgres pg_dump -U rag_user -d buchplattform > backup.sql

# Nur Schema (ohne Daten - für Disaster Recovery Tests)
# docker-compose exec postgres pg_dump -U rag_user -d buchplattform --schema-only > schema.sql

# Nur Daten (ohne Schema)
# docker-compose exec postgres pg_dump -U rag_user -d buchplattform --data-only > data.sql


# Custom Format (komprimiert, parallel restore möglich)
docker-compose exec postgres pg_dump -U rag_user -d buchplattform -Fc > backup.dump

# Directory Format (für große DBs mit parallelem Backup)
docker-compose exec postgres pg_dump -U rag_user -d buchplattform -Fd -f backup_dir