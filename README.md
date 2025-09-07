# RAG-API: Retrieval Augmented Generation für Dokumente

Ein vollständiges RAG-System mit PostgreSQL, Ollama und FastAPI sowie Web-UI für intelligente Dokumentenanalyse.

## Features

- PDF/Text Upload und Verarbeitung
- Vector Search mit PostgreSQL + pgvector
- LLM-Integration mit Ollama (Llama 3.1)
- Web-UI für einfache Bedienung
- Docker Compose Setup

## Quick Start

```bash
# Repository klonen
git clone https://github.com/rjwsbsw/rag-api.git
cd rag-api

# System starten
chmod +x setup.sh
./setup.sh

# RAG-API öffnen
open http://localhost:28080
# Web-UI öffnen
open http://localhost:28081
```
