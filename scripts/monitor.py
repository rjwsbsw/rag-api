#!/usr/bin/env python3
"""
Einfaches Monitoring für RAG-System
Überwacht API-Performance und Ressourcenverbrauch
"""

import time
import requests
import psutil
import json
from datetime import datetime
import argparse

class RAGMonitor:
    def __init__(self, api_url: str, interval: int = 30):
        self.api_url = api_url
        self.interval = interval
        self.stats = []
    
    def check_api_health(self):
        """API Gesundheitscheck"""
        try:
            start_time = time.time()
            response = requests.get(f"{self.api_url}/health", timeout=10)
            response_time = (time.time() - start_time) * 1000  # ms
            
            return {
                "timestamp": datetime.now().isoformat(),
                "api_status": "healthy" if response.status_code == 200 else "unhealthy",
                "response_time_ms": round(response_time, 2),
                "status_code": response.status_code
            }
        except Exception as e:
            return {
                "timestamp": datetime.now().isoformat(),
                "api_status": "error",
                "response_time_ms": None,
                "error": str(e)
            }
    
    def get_system_stats(self):
        """System-Ressourcen überwachen"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_used_gb": round(memory.used / (1024**3), 2),
                "memory_total_gb": round(memory.total / (1024**3), 2),
                "disk_percent": disk.percent,
                "disk_free_gb": round(disk.free / (1024**3), 2)
            }
        except Exception as e:
            return {"error": str(e)}
    
    def test_query_performance(self):
        """Test-Query Performance messen"""
        test_query = {
            "question": "Was ist das Hauptthema?",
            "book_id": "demo"
        }
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{self.api_url}/ask",
                json=test_query,
                timeout=60
            )
            query_time = (time.time() - start_time) * 1000  # ms
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "query_time_ms": round(query_time, 2),
                    "success": True,
                    "chunks_used": result.get("context_chunks_used", 0)
                }
            else:
                return {
                    "query_time_ms": round(query_time, 2),
                    "success": False,
                    "error": response.text
                }
        except Exception as e:
            return {
                "query_time_ms": None,
                "success": False,
                "error": str(e)
            }
    
    def run_monitoring(self):
        """Kontinuierliches Monitoring"""
        print(f"🔍 Starte Monitoring für {self.api_url}")
        print(f"📊 Intervall: {self.interval} Sekunden")
        print("-" * 60)
        
        try:
            while True:
                # Statistiken sammeln
                stats = {
                    "timestamp": datetime.now().isoformat(),
                    "api": self.check_api_health(),
                    "system": self.get_system_stats(),
                    "performance": self.test_query_performance()
                }
                
                self.stats.append(stats)
                
                # Ausgabe
                api_status = stats["api"]["api_status"]
                response_time = stats["api"].get("response_time_ms", "N/A")
                cpu = stats["system"].get("cpu_percent", "N/A")
                memory = stats["system"].get("memory_percent", "N/A")
                query_time = stats["performance"].get("query_time_ms", "N/A")
                
                status_icon = "✅" if api_status == "healthy" else "❌"
                
                print(f"{stats['timestamp'][:19]} {status_icon} "
                      f"API: {response_time}ms | "
                      f"CPU: {cpu}% | "
                      f"RAM: {memory}% | "
                      f"Query: {query_time}ms")
                
                time.sleep(self.interval)
                
        except KeyboardInterrupt:
            print(f"\n📈 Monitoring gestoppt. {len(self.stats)} Datenpunkte gesammelt.")
            self.save_stats()
    
    def save_stats(self):
        """Statistiken in Datei speichern"""
        filename = f"monitor_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(self.stats, f, indent=2)
        print(f"💾 Statistiken gespeichert in: {filename}")

def main():
    parser = argparse.ArgumentParser(description='Monitor RAG system performance')
    parser.add_argument('--api-url', default='http://localhost:8080',
                       help='API base URL')
    parser.add_argument('--interval', type=int, default=30,
                       help='Monitoring interval in seconds')
    
    args = parser.parse_args()
    
    monitor = RAGMonitor(args.api_url, args.interval)
    monitor.run_monitoring()

if __name__ == "__main__":
    main()