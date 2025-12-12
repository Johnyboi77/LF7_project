#!/usr/bin/env python3
"""
test_report.py - Teste Session-Report mit echten Datenbank-Daten
Liest letzte Session und erstellt Report
"""

import sys
from database.supabase_manager import SupabaseManager
from services.notification_service import NotificationService
from notifications.message_templates import MessageTemplates

def test_report():
    print("\n" + "="*60)
    print("🧪 SESSION-REPORT TEST")
    print("="*60 + "\n")
    
    db = SupabaseManager()
    notify = NotificationService()
    
    if not db.client:
        print("❌ Keine Datenbankverbindung!")
        return
    
    # Hole letzte Session
    print("📊 Lade letzte Session aus Datenbank...")
    
    try:
        session_response = db.client.table('sessions')\
            .select('*')\
            .order('created_at', desc=True)\
            .limit(1)\
            .execute()
        
        if not session_response.data:
            print("⚠️  Keine Sessions gefunden!")
            print("\n💡 Hinweis: Starten Sie eine echte Lerneinheit um Daten zu generieren")
            return
        
        session = session_response.data[0]
        session_id = session.get('session_id')
        
        print(f"✅ Session gefunden: {session_id[:8]}...")
        print(f"   User: {session.get('user_name')}")
        print(f"   Arbeitszeit: {session.get('total_work_time', 0)}s")
        print(f"   Pausenzeit: {session.get('total_pause_time', 0)}s")
        
        # Hole vollständige Report-Daten
        print("\n📈 Lade Report-Daten...")
        report_data = db.get_session_report_data(session_id)
        
        if not report_data:
            print("❌ Report-Daten konnten nicht geladen werden!")
            return
        
        # Erstelle Nachricht
        print("\n✉️ Erstelle Discord-Nachricht...")
        template = MessageTemplates.session_report(
            session.get('user_name', 'User'),
            report_data
        )
        
        print(f"\n{'='*60}")
        print("📊 NACHRICHT VORSCHAU")
        print(f"{'='*60}\n")
        
        print(f"**{template['title']}**\n")
        print(template['description'])
        
        print(f"\n{'='*60}")
        print("Einstellungen:")
        print(f"  Titel: {template['title']}")
        print(f"  Farbe: {template['color']}")
        print(f"  Emoji: {template['emoji']}")
        print(f"{'='*60}\n")
        
        # Versenden?
        if notify.is_enabled:
            response = input("📤 Nachricht zu Discord versenden? (j/n): ").lower()
            
            if response == 'j':
                from requests import post
                from datetime import datetime
                
                try:
                    payload = {
                        "embeds": [{
                            "title": template['title'],
                            "description": template['description'],
                            "color": template['color'],
                            "timestamp": datetime.utcnow().isoformat(),
                            "footer": {"text": "Learning Assistant"}
                        }]
                    }
                    
                    result = post(notify.webhook_url, json=payload, timeout=5)
                    
                    if result.status_code == 204:
                        print("✅ Nachricht erfolgreich versendet!")
                    else:
                        print(f"⚠️  Status: {result.status_code}")
                
                except Exception as e:
                    print(f"❌ Fehler: {e}")
        else:
            print("⚠️  Discord nicht konfiguriert (MOCK-Modus)")
    
    except Exception as e:
        print(f"❌ Fehler: {e}")

if __name__ == "__main__":
    try:
        test_report()
    except KeyboardInterrupt:
        print("\n\n🛑 Abgebrochen\n")
        sys.exit(0)