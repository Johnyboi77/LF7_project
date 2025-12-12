#!/usr/bin/env python3
"""
test_discord.py - Testet Discord-Benachrichtigungen
Sendet verschiedene Nachrichtentypen
"""

import sys
from datetime import datetime
from services.notification_service import NotificationService
from services.discord_message_templates import MessageTemplates

def print_header(title):
    print("\n" + "="*60)
    print(f"🧪 {title}")
    print("="*60 + "\n")

def wait_for_input():
    input("👉 Drücke ENTER zum nächsten Test... ")
    print()

def test_session_start():
    print_header("TEST 1: SESSION START")
    
    notify = NotificationService()
    template = MessageTemplates.session_start("Alicia")
    
    print(f"📨 Sende Nachricht:")
    print(f"   Titel: {template['title']}")
    print(f"   Beschreibung: {template['description'][:50]}...")
    print(f"   Farbe: {template['color']}")
    
    # Senden
    from requests import post
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
        
        response = post(
            notify.webhook_url,
            json=payload,
            timeout=5
        )
        
        if response.status_code == 204:
            print(f"✅ Erfolgreich versendet!")
        else:
            print(f"⚠️  Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Fehler: {e}")
    
    wait_for_input()

def test_work_finished():
    print_header("TEST 2: WORK FINISHED")
    
    template = MessageTemplates.work_finished("Alicia")
    
    print(f"📨 Sende Nachricht:")
    print(f"   Titel: {template['title']}")
    print(f"   Beschreibung:\n{template['description']}")
    
    notify = NotificationService()
    from requests import post
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
        
        response = post(notify.webhook_url, json=payload, timeout=5)
        
        if response.status_code == 204:
            print(f"✅ Erfolgreich versendet!")
        else:
            print(f"⚠️  Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Fehler: {e}")
    
    wait_for_input()

def test_break_finished():
    print_header("TEST 3: BREAK FINISHED")
    
    template = MessageTemplates.break_finished("Alicia")
    
    print(f"📨 Sende Nachricht:")
    print(f"   Titel: {template['title']}")
    print(f"   Beschreibung:\n{template['description']}")
    
    notify = NotificationService()
    from requests import post
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
        
        response = post(notify.webhook_url, json=payload, timeout=5)
        
        if response.status_code == 204:
            print(f"✅ Erfolgreich versendet!")
        else:
            print(f"⚠️  Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Fehler: {e}")
    
    wait_for_input()

def test_break_stats():
    print_header("TEST 4: BREAK STATISTICS")
    
    template = MessageTemplates.break_stats("Alicia", 1, 1247, 65, 950)
    
    print(f"📨 Sende Nachricht:")
    print(f"   Titel: {template['title']}")
    print(f"   Beschreibung:\n{template['description']}")
    
    notify = NotificationService()
    from requests import post
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
        
        response = post(notify.webhook_url, json=payload, timeout=5)
        
        if response.status_code == 204:
            print(f"✅ Erfolgreich versendet!")
        else:
            print(f"⚠️  Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Fehler: {e}")
    
    wait_for_input()

def test_co2_warning():
    print_header("TEST 5: CO2 WARNING")
    
    template = MessageTemplates.co2_warning("Alicia", 650, 200)
    
    print(f"📨 Sende Nachricht:")
    print(f"   Titel: {template['title']}")
    print(f"   Beschreibung:\n{template['description']}")
    
    notify = NotificationService()
    from requests import post
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
        
        response = post(notify.webhook_url, json=payload, timeout=5)
        
        if response.status_code == 204:
            print(f"✅ Erfolgreich versendet!")
        else:
            print(f"⚠️  Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Fehler: {e}")
    
    wait_for_input()

def test_co2_critical():
    print_header("TEST 6: CO2 CRITICAL")
    
    template = MessageTemplates.co2_critical("Alicia", 950, 450)
    
    print(f"📨 Sende Nachricht:")
    print(f"   Titel: {template['title']}")
    print(f"   Beschreibung:\n{template['description']}")
    
    notify = NotificationService()
    from requests import post
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
        
        response = post(notify.webhook_url, json=payload, timeout=5)
        
        if response.status_code == 204:
            print(f"✅ Erfolgreich versendet!")
        else:
            print(f"⚠️  Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Fehler: {e}")
    
    wait_for_input()

def test_session_report():
    print_header("TEST 7: SESSION REPORT")
    
    # Mock-Daten
    stats = {
        'session': {
            'total_work_time': 5400,  # 90 min
            'total_pause_time': 1800,  # 30 min
            'pause_count': 3
        },
        'co2': {
            'avg_co2': 542,
            'min_co2': 420,
            'max_co2': 780,
            'alarm_count': 2
        },
        'movement': {
            'step_count': 1247,
            'calories_burned': 65,
            'distance_meters': 950
        }
    }
    
    template = MessageTemplates.session_report("Alicia", stats)
    
    print(f"📨 Sende Nachricht:")
    print(f"   Titel: {template['title']}")
    print(f"   Beschreibung:\n{template['description']}")
    
    notify = NotificationService()
    from requests import post
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
        
        response = post(notify.webhook_url, json=payload, timeout=5)
        
        if response.status_code == 204:
            print(f"✅ Erfolgreich versendet!")
        else:
            print(f"⚠️  Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Fehler: {e}")
    
    wait_for_input()

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🧪 DISCORD NACHRICHT TEST-SUITE")
    print("="*60)
    print("\nTeste alle Discord-Nachrichtentypen")
    print("Jeder Test sendet eine echte Nachricht zu Discord!\n")
    
    try:
        test_session_start()
        test_work_finished()
        test_break_finished()
        test_break_stats()
        test_co2_warning()
        test_co2_critical()
        test_session_report()
        
        print("="*60)
        print("✅ ALLE DISCORD TESTS ABGESCHLOSSEN!")
        print("="*60 + "\n")
        
    except KeyboardInterrupt:
        print("\n\n🛑 Tests unterbrochen")
        sys.exit(0)