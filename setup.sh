#!/bin/bash

echo "🛠️ Entwicklungsumgebung starten (Einfache Version)"
echo "================================================="

# Pre-flight checks
echo "🔍 System-Checks..."

# Docker prüfen
if ! command -v docker &> /dev/null; then
    echo "❌ Docker ist nicht installiert"
    exit 1
fi

# Docker Compose prüfen  
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose ist nicht installiert"
    exit 1
fi

# Docker läuft?
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker ist nicht gestartet"
    exit 1
fi

echo "✅ Docker bereit"

# Ports prüfen
echo "🔍 Port-Checks..."
ports=(11434 28080 25432 28081)
for port in "${ports[@]}"; do
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        echo "⚠️  Port $port ist bereits belegt"
    fi
done

# Services starten
echo "🚀 Starte Services..."
docker-compose up -d --build

# Warten auf Services
echo "⏳ Warte auf Service-Bereitschaft..."
sleep 15

# Health Checks
services=("postgres:25432" "ollama:11434")
for service in "${services[@]}"; do
    host_port=${service}
    service_name=${service%%:*}
    port=${service##*:}
    
    echo "Prüfe $service_name auf Port $port..."
    
    for i in {1..30}; do
        case $service_name in
            "postgres")
                if docker exec postgres pg_isready -U rag_user >/dev/null 2>&1; then
                    echo "✅ PostgreSQL ist bereit"
                    break
                fi
                ;;
            "ollama")
                if curl -s http://localhost:$port/api/tags >/dev/null 2>&1; then
                    echo "✅ Ollama ist bereit"
                    break
                fi
                ;;
        esac
        
        if [ $i -eq 30 ]; then
            echo "❌ $service_name antwortet nicht nach 60 Sekunden"
            docker-compose logs $service_name
        fi
        
        sleep 2
    done
done

# RAG-API prüfen
echo "Prüfe RAG-API..."
for i in {1..30}; do
    if curl -s http://localhost:28080/health >/dev/null 2>&1; then
        echo "✅ RAG-API ist bereit"
        break
    fi
    
    if [ $i -eq 30 ]; then
        echo "❌ RAG-API antwortet nicht"
        docker-compose logs rag-api
    fi
    
    sleep 2
done

# Ollama Modell laden
echo "📥 Prüfe LLM-Modell..."
if docker-compose exec -T ollama ollama list | grep -q "llama3.1:8b"; then
    echo "✅ Llama 3.1 bereits verfügbar"
else
    echo "📥 Lade Llama 3.1 8B (ca. 4.7 GB - das kann dauern)..."
    docker-compose exec -T ollama ollama pull llama3.1:8b
fi

echo ""
echo "🎉 Entwicklungsumgebung bereit!"
echo ""
echo "📊 Service-URLs:"
echo "   RAG-API:     http://localhost:28080"
echo "   PostgreSQL:  localhost:25432 (rag_user/rag_password)"
echo "   Ollama:      http://localhost:11434"  
echo "   Web-UI:      http://localhost:28081"
echo ""
echo "🧪 Test-Befehle:"
echo "   ./scripts/test-system.sh"
echo "   python scripts/bulk-loader.py ./books"
echo ""
echo "🐛 Logs anzeigen:"
echo "   docker-compose logs -f [service-name]"
echo ""
echo "⏹️  Stoppen:"
echo "   docker-compose down"