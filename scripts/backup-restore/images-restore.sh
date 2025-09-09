#!/bin/bash

BACKUP_DIR="backup/images"
mkdir -p "$BACKUP_DIR"

# 1. System-Requirements prüfen
docker --version && docker-compose --version

# 2. Repository wiederherstellen
git clone https://github.com/rjwsbsw/rag-api.git
cd rag-api

# 3. Container Images laden (falls kein Internet)
docker load < "$BACKUP_DIR/rag-api-image.tar.gz"
docker load < "$BACKUP_DIR/ollama-image.tar.gz"
docker load < "$BACKUP_DIR/pgvector-image.tar.gz"