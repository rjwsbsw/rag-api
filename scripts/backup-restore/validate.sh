# 1. System Health Check
./scripts/test-system.sh

# 2. Datenintegrität prüfen
curl -s http://localhost:28080/books | jq '.books | length'

# 3. RAG-Funktionalität testen
curl -X POST -H "Content-Type: application/json" \
  -d '{"question":"Test-Frage","book_id":"demo-krimi"}' \
  http://localhost:28080/ask

# 4. Upload-Test mit kleiner Datei
echo "Test-Dokument" > test.txt
curl -X POST -F "file=@test.txt" http://localhost:28080/upload-book