#!/bin/bash

BACKUP_DIR="backup/images"
mkdir -p "$BACKUP_DIR"

# Lokale Images exportieren
docker save devop-ai01_web-ui:latest | gzip > "$BACKUP_DIR/rag-api-image.tar.gz"
docker save devop-ai01_rag-api:latest | gzip > "$BACKUP_DIR/rag-api-image.tar.gz"
docker save ollama/ollama:latest | gzip > "$BACKUP_DIR/ollama-image.tar.gz"
docker save ankane/pgvector:latest | gzip > "$BACKUP_DIR/pgvector-image.tar.gz"