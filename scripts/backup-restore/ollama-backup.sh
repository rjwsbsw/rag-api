#!/bin/bash

set -e

TIMESTAMP=$(date +"%Y-%m-%d_%H-%M")
BACKUP_DIR="backup/models/ollama-backup-$TIMESTAMP"
mkdir -p "$BACKUP_DIR"

echo "📝 Saving Modelfile..."
docker-compose exec ollama ollama show llama3.1:8b --modelfile > "$BACKUP_DIR/llama3.1-modelfile.txt"

echo "📦 Stopping Ollama container..."
docker-compose stop ollama

echo "📁 Copying model data from container..."
docker cp devop-ai01_ollama_1:/root/.ollama "$BACKUP_DIR/ollama-data"

echo "🚀 Starting Ollama container..."
docker-compose start ollama

echo "✅ Backup complete: $BACKUP_DIR"
