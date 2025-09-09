#!/bin/bash

set -e

# 🧩 Backup-Verzeichnis als Argument
BACKUP_DIR="$1"

if [ -z "$BACKUP_DIR" ]; then
  echo "❌ Bitte Backup-Verzeichnis angeben!"
  echo "Usage: ./restore-ollama.sh ollama-backup-YYYY-MM-DD_HH-MM"
  exit 1
fi

# 📦 Container stoppen
echo "📦 Stopping Ollama container..."
docker-compose stop ollama

# 📁 Modell-Daten zurückkopieren
echo "📁 Restoring model data to container..."
docker cp "$BACKUP_DIR/ollama-data" devop-ai01_ollama_1:/root/.ollama

# 🚀 Container starten
echo "🚀 Starting Ollama container..."
docker-compose start ollama

# 📝 Optional: Modell neu registrieren
if [ -f "$BACKUP_DIR/llama3.1-modelfile.txt" ]; then
  echo "📝 Re-registering model from Modelfile..."
  docker-compose exec ollama ollama create llama3.1:8b -f /root/.ollama/llama3.1-modelfile.txt
else
  echo "⚠️ Keine Modelfile gefunden – Registrierung übersprungen."
fi

echo "✅ Restore abgeschlossen aus: $BACKUP_DIR"
