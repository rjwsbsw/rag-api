#!/usr/bin/env python3
"""
Bulk Document Loader für RAG-System (Einfache Version)
"""

import os
import sys
import requests
import argparse
from pathlib import Path

def upload_book(api_url: str, pdf_path: Path, book_id: str = None):
    """Einzelnes Buch hochladen"""
    
    if not book_id:
        book_id = pdf_path.stem
    
    try:
        with open(pdf_path, 'rb') as pdf_file:
            files = {'file': (pdf_path.name, pdf_file, 'application/pdf')}
            
            if book_id != pdf_path.stem:
                data = {'book_id': book_id}
                response = requests.post(f"{api_url}/upload-book", files=files, data=data, timeout=300)
            else:
                response = requests.post(f"{api_url}/upload-book", files=files, timeout=300)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ {pdf_path.name} -> {result['chunks_created']} Chunks")
                return True
            else:
                print(f"❌ {pdf_path.name} -> Fehler: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ {pdf_path.name} -> Exception: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Bulk upload PDFs to RAG system')
    parser.add_argument('directory', help='Directory containing PDF files')
    parser.add_argument('--api-url', default='http://localhost:28080', 
                       help='API base URL')
    parser.add_argument('--prefix', default='', 
                       help='Prefix for book IDs')
    
    args = parser.parse_args()
    
    pdf_dir = Path(args.directory)
    if not pdf_dir.exists():
        print(f"❌ Verzeichnis {pdf_dir} existiert nicht")
        sys.exit(1)
    
    # Alle PDF-Dateien finden
    pdf_files = list(pdf_dir.glob("*.pdf"))
    if not pdf_files:
        print(f"❌ Keine PDF-Dateien in {pdf_dir} gefunden")
        sys.exit(1)
    
    print(f"📚 {len(pdf_files)} PDF-Dateien gefunden")
    
    # API Health Check
    try:
        health_response = requests.get(f"{args.api_url}/health", timeout=10)
        if health_response.status_code != 200:
            print(f"❌ API nicht verfügbar: {args.api_url}")
            sys.exit(1)
        print(f"✅ API verfügbar: {args.api_url}")
    except Exception as e:
        print(f"❌ API nicht erreichbar: {e}")
        sys.exit(1)
    
    # Bücher hochladen
    successful = 0
    for pdf_file in pdf_files:
        book_id = f"{args.prefix}{pdf_file.stem}" if args.prefix else pdf_file.stem
        if upload_book(args.api_url, pdf_file, book_id):
            successful += 1
    
    print(f"\n📊 Ergebnis: {successful}/{len(pdf_files)} Bücher erfolgreich hochgeladen")

if __name__ == "__main__":
    main()