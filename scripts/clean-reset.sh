#!/bin/bash

echo "🧹 RAG-System Reset (alle Daten löschen)"
echo "======================================="

read -p "⚠️  Dies löscht ALLE Daten und Container. Fortfahren? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Abgebrochen."
    exit 1
fi

echo "🛑 Stoppe alle Container..."
docker-compose down -v

echo "🗑️  Entferne Docker Volumes..."
docker volume rm $(docker volume ls -q | grep -E "rag|buchplattform|pg|ollama") 2>/dev/null || true

echo "🧹 Entferne lokale Verzeichnisse..."
# pg-data mit verschiedenen Methoden löschen
if [ -d "./pg-data" ]; then
    echo "Entferne pg-data..."
    rm -rf ./pg-data 2>/dev/null || \
    docker run --rm -v $(pwd)/pg-data:/data alpine sh -c "rm -rf /data/*" 2>/dev/null || \
    sudo rm -rf ./pg-data 2>/dev/null || \
    echo "⚠️  pg-data konnte nicht gelöscht werden - bitte manuell mit sudo rm -rf ./pg-data"
fi

# Andere Verzeichnisse  
rm -rf ./models 2>/dev/null || true

echo "🐳 Entferne Docker Images..."
docker rmi $(docker images | grep -E "rag|buchplattform" | awk '{print $3}') 2>/dev/null || true

echo "✅ Reset abgeschlossen!"
echo ""
echo "🚀 Für Neustart:"
echo "   ./setup.sh"

echo ""
echo "✅ Setup abgeschlossen!"
echo ""
echo "🌐 Services verfügbar unter:"
echo "   - RAG-API: http://localhost:28080"
echo "   - PostgreSQL: localhost:25432"  
echo "   - Ollama: http://localhost:11434"
echo "   - Web-UI: http://localhost:28081"
echo ""
echo "📚 Nächste Schritte:"
echo "1. Demo-PDF erstellen: python create-demo-data.py"
echo "2. Buch hochladen: curl -X POST -F 'file=@books/demo.pdf' http://localhost:28080/upload-book"
echo "3. Frage stellen: curl -X POST -H 'Content-Type: application/json' -d '{\"question\":\"Wer ist der Mörder?\",\"book_id\":\"demo\"}' http://localhost:28080/ask"
