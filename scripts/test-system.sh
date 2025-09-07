#!/bin/bash

echo "🧪 RAG-System Tests"
echo "=================="

BASE_URL="http://localhost:28080"

# 1. Health Check
echo "1. Health Check..."
health_response=$(curl -s ${BASE_URL}/health)
echo "Response: $health_response"

if [[ $health_response == *"healthy"* ]]; then
    echo "✅ API ist gesund"
else
    echo "❌ API nicht verfügbar - prüfen Sie docker-compose logs rag-api"
    exit 1
fi

# 2. PostgreSQL Check
echo -e "\n2. PostgreSQL Verbindung..."
docker-compose exec -T postgres psql -U rag_user -d buchplattform -c "SELECT version();" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ PostgreSQL erreichbar"
else
    echo "❌ PostgreSQL nicht erreichbar"
    exit 1
fi

# 3. Ollama Check
echo -e "\n3. Ollama Modell Check..."
ollama_response=$(curl -s http://localhost:11434/api/tags)
if [[ $ollama_response == *"llama3.1:8b"* ]]; then
    echo "✅ Llama 3.1 Modell verfügbar"
else
    echo "⚠️  Llama 3.1 Modell nicht verfügbar"
    # Versuche Modell zu laden
    echo "🔄 Versuche Modell zu laden..."
    docker-compose exec -T ollama ollama pull llama3.1:8b > /dev/null 2>&1
fi

# 4. Bücher auflisten
echo -e "\n4. Verfügbare Bücher..."
books_response=$(curl -s ${BASE_URL}/books)
book_count=$(echo $books_response | grep -o '"book_id"' | wc -l)
echo "📚 $book_count Bücher gefunden"

# 5. Test-Upload (falls Demo-Dateien vorhanden)
for test_file in "./books/demo-krimi.txt" "./books/demo-krimi.pdf" "./books/demo.pdf"; do
    if [ -f "$test_file" ]; then
        echo -e "\n5. Test-Upload: $(basename $test_file)..."
        upload_response=$(curl -s -X POST \
            -F "file=@$test_file" \
            ${BASE_URL}/upload-book)
        
        if [[ $upload_response == *"erfolgreich"* ]]; then
            echo "✅ Upload erfolgreich"
            
            # Test-Frage stellen
            book_id=$(basename "$test_file" | cut -d. -f1)
            echo "🤔 Teste Frage an $book_id..."
            question_response=$(curl -s -X POST ${BASE_URL}/ask \
                -H "Content-Type: application/json" \
                -d "{\"question\":\"Worum geht es in diesem Text?\",\"book_id\":\"$book_id\"}")
            
            if [[ $question_response == *"answer"* ]]; then
                echo "✅ RAG-Antwort funktioniert"
            else
                echo "❌ RAG-Antwort fehlgeschlagen"
            fi
        else
            echo "⚠️  Upload fehlgeschlagen: $upload_response"
        fi
        break
    fi
done

# 6. Web-UI Check
echo -e "\n6. Web-UI Check..."
ui_response=$(curl -s http://localhost:28081/ | head -1)
if [[ $ui_response == *"DOCTYPE"* ]]; then
    echo "✅ Web-UI erreichbar"
else
    echo "⚠️  Web-UI nicht erreichbar"
fi

echo -e "\n✅ Tests abgeschlossen!"
echo -e "\n🌐 Services:"
echo "   - RAG-API: http://localhost:28080"
echo "   - Web-UI: http://localhost:28081"
echo "   - PostgreSQL: localhost:25432"
echo "   - Ollama: http://localhost:11434"
echo -e "\n📋 Manuelle Tests:"
echo "1. python create-demo-data.py"
echo "2. python scripts/bulk-loader.py books"
echo "3. curl -X POST -H 'Content-Type: application/json' -d '{\"question\":\"Wer ist der Mörder?\",\"book_id\":\"demo-krimi\"}' http://localhost:28080/ask"