#!/usr/bin/env python3
"""
Erstellt Demo-PDF für Tests
"""

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import sys
import os

def create_demo_pdf(filename: str):
    """Erstellt eine Demo-PDF mit einfachem Inhalt"""
    
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    
    # Seite 1
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, height - 50, "Der Mysteriöse Fall von Schloss Ravenswood")
    
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 80, "Ein Demo-Krimi für RAG-Tests")
    c.drawString(50, height - 100, "Autor: A. Gatha Christie")
    
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 140, "Kapitel 1: Der Tod in der Bibliothek")
    
    c.setFont("Helvetica", 12)
    y = height - 170
    text_lines = [
        "Lord Ravenswood wurde tot in seiner Bibliothek aufgefunden.",
        "Die Tür war von innen verschlossen, und der Schlüssel lag neben der Leiche.",
        "Inspector Holmes untersuchte den Tatort sorgfältig.",
        "",
        "Die Bibliothek war ein großer Raum mit hohen Bücherregalen.",
        "Ein schwerer Schreibtisch stand in der Mitte des Raumes.",
        "Darauf lagen aufgeschlagene Bücher und wichtige Dokumente.",
        "",
        "Der Butler berichtete, dass Lord Ravenswood am Abend allein",
        "in der Bibliothek gearbeitet hatte. Niemand hatte das Zimmer",
        "nach 22 Uhr betreten oder verlassen.",
    ]
    
    for line in text_lines:
        c.drawString(50, y, line)
        y -= 20
    
    c.showPage()
    
    # Seite 2
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 50, "Kapitel 2: Die Befragung")
    
    c.setFont("Helvetica", 12)
    y = height - 80
    text_lines2 = [
        "Inspector Holmes befragte alle Bewohner des Schlosses.",
        "",
        "Die Köchin: 'Lord Ravenswood aß um 19 Uhr zu Abend.'",
        "Der Gärtner: 'Ich sah Licht in der Bibliothek bis spät in die Nacht.'",
        "Die Hausdame: 'Der Lord war in letzter Zeit sehr nervös.'",
        "",
        "Holmes notierte sich alle Aussagen sorgfältig.",
        "Ein Detail fiel ihm besonders auf: Das Fenster der Bibliothek",
        "stand einen Spalt weit offen, obwohl es ein kalter Herbstabend war.",
        "",
        "Bei genauerer Untersuchung fand Holmes seltsame Spuren",
        "auf dem Fensterbrett - Spuren, die nicht von Lord Ravenswood",
        "stammen konnten.",
    ]
    
    for line in text_lines2:
        c.drawString(50, y, line)
        y -= 20
    
    c.showPage()
    
    # Seite 3
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 50, "Kapitel 3: Die Lösung")
    
    c.setFont("Helvetica", 12)
    y = height - 80
    text_lines3 = [
        "Nach sorgfältiger Analyse aller Indizien kam Holmes",
        "zu einem überraschenden Schluss.",
        "",
        "Der Mörder war niemand aus dem Schloss.",
        "Ein Einbrecher war durch das Bibliotheksfenster eingedrungen,",
        "hatte Lord Ravenswood überrascht und in Panik getötet.",
        "",
        "Der Schlüssel lag deshalb neben der Leiche, weil Lord Ravenswood",
        "versucht hatte, die Tür abzuschließen, als er den Eindringling",
        "bemerkte.",
        "",
        "Holmes konnte den Täter drei Tage später verhaften.",
        "Es war ein verschuldeter Spieler, der verzweifelt nach Geld",
        "gesucht hatte.",
    ]
    
    for line in text_lines3:
        c.drawString(50, y, line)
        y -= 20
    
    c.save()
    print(f"✅ Demo-PDF erstellt: {filename}")

def main():
    # Books-Verzeichnis erstellen falls nicht vorhanden
    books_dir = "books"
    if not os.path.exists(books_dir):
        os.makedirs(books_dir)
        print(f"📁 Verzeichnis '{books_dir}' erstellt")
    
    # Demo-PDF erstellen
    demo_file = os.path.join(books_dir, "demo-krimi.pdf")
    
    try:
        create_demo_pdf(demo_file)
        print(f"🎯 Verwenden Sie dieses Buch zum Testen:")
        print(f"   python scripts/bulk-loader.py books")
        print(f"   oder laden Sie es über die Web-UI hoch")
    except ImportError:
        print("❌ reportlab ist nicht installiert.")
        print("   Installieren Sie es mit: pip install reportlab")
        print("   Oder verwenden Sie eine eigene PDF-Datei.")
        sys.exit(1)

if __name__ == "__main__":
    main()