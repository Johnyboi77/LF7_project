#!/usr/bin/env python3
"""
test_discord.py - Testet Discord-Benachrichtigungen
Nur noch die essentiellen 3 Nachrichten + CO2 Critical
"""

import sys
from datetime import datetime
from requests import post
from services.notification_service import NotificationService
from services.discord_message_templates import MessageTemplates

def print_header(title):
    print("\n" + "="*60)
    print(f"🧪 {title}")
    print("="*60 + "\n")

def wait_for_input():
    input("👉 Drücke ENTER zum nächsten Test... ")
    print()

def send_to_discord(notify, template):
    """Helper zum Senden an Discord"""
    try:
        payload = {
            "embeds": [{
                "title": template['title'],
                "description": template['description'],
                "color": template['color'],
                "timestamp": datetime.utcnow().isoformat(),
                "footer": {"text": "Learning Assistant - Test"}
            }]
        }
        
        response = post(notify.webhook_url, json=payload, timeout=5)
        
        if response.status_code == 204:
            print("✅ Erfolgreich versendet!")
            return True
        else:
            print(f"⚠️  Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Fehler: {e}")
        return False

# ===== TESTS =====

def test_ready_message():
    """Ready-Message (Deployment-Check)"""
    print_header("TEST 0: READY MESSAGE")
    
    notify = NotificationService()
    
    print("📨 Sende Ready-Message...")
    print(f"   Webhook: {notify.webhook_url[:50]}...")
    print(f"   Status: {'✅ Aktiv' if notify.is_enabled else '❌ Inaktiv'}\n")
    
    try:
        payload = {
            "embeds": [{
                "title": "🤖 Learning Assistant ist bereit!",
                "description": (
                    "**i am ready to serve** 🚀\n\n"
                    "Das System wurde erfolgreich deployed!\n\n"
                    "✅ Supabase verbunden\n"
                    "✅ Discord Webhook aktiv\n"
                    "✅ Hardware konfiguriert\n"
                    "✅ Ready to learn! 🎓"
                ),
                "color": 3066993,  # Grün
                "timestamp": datetime.utcnow().isoformat(),
                "footer": {"text": "Learning Assistant - Deployment Ready"}
            }]
        }
        
        response = post(notify.webhook_url, json=payload, timeout=5)
        
        if response.status_code == 204:
            print("✅ Ready-Message erfolgreich versendet!")
        else:
            print(f"⚠️  Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Fehler: {e}")
    
    wait_for_input()

def test_session_start():
    """1/3: Session Start"""
    print_header("TEST 1: SESSION START (Nachricht 1/3)")
    
    notify = NotificationService()
    template = MessageTemplates.session_start("Alicia")
    
    print(f"📨 Template:")
    print(f"   Titel: {template['title']}")
    print(f"   Farbe: {template['color']} (Blau)")
    print(f"   Beschreibung:\n")
    print(template['description'])
    print()
    
    send_to_discord(notify, template)
    wait_for_input()

def test_break_stats():
    """2/3: Break Stats (nach jeder Pause)"""
    print_header("TEST 2: BREAK STATS (Nachricht 2/3)")
    
    notify = NotificationService()
    
    # Test-Werte
    pause_number = 1
    steps = 1247
    calories = 62
    distance = 935
    
    template = MessageTemplates.break_stats("Alicia", pause_number, steps, calories, distance)
    
    print(f"📨 Template:")
    print(f"   Titel: {template['title']}")
    print(f"   Farbe: {template['color']} (Lila)")
    print(f"   Test-Daten:")
    print(f"     • Pause #{pause_number}")
    print(f"     • {steps:,} Schritte")
    print(f"     • {calories} kcal")
    print(f"     • {distance}m")
    print()
    print(f"   Beschreibung:\n")
    print(template['description'])
    print()
    
    send_to_discord(notify, template)
    wait_for_input()

def test_session_report():
    """3/3: Session Report (Finaler Report)"""
    print_header("TEST 3: SESSION REPORT (Nachricht 3/3)")
    
    notify = NotificationService()
    
    # Test-Daten
    stats = {
        'session': {
            'total_work_time': 5400,  # 90 Min
            'total_pause_time': 1800,  # 30 Min
            'pause_count': 3
        },
        'co2': {
            'avg_co2': 542,
            'min_co2': 420,
            'max_co2': 780,
            'alarm_count': 2
        },
        'movement': {
            'step_count': 3741,
            'calories_burned': 187,
            'distance_meters': 2805
        }
    }
    
    template = MessageTemplates.session_report("Alicia", stats)
    
    print(f"📨 Template:")
    print(f"   Titel: {template['title']}")
    print(f"   Farbe: {template['color']} (Lila)")
    print(f"   Test-Daten:")
    print(f"     • 90 Min Lernzeit")
    print(f"     • 3 Pausen")
    print(f"     • 3.741 Schritte")
    print(f"     • Ø CO2: 542 ppm (Ausgezeichnet)")
    print()
    print(f"   Beschreibung:\n")
    print(template['description'])
    print()
    
    send_to_discord(notify, template)
    wait_for_input()

def test_co2_critical():
    """OPTIONAL: CO2 Critical (nur bei > 800 ppm)"""
    print_header("TEST 4: CO2 CRITICAL (Optional - nur > 800 ppm)")
    
    notify = NotificationService()
    
    # Test-Werte (kritisch)
    co2_level = 950
    tvoc_level = 450
    
    template = MessageTemplates.co2_critical("Alicia", co2_level, tvoc_level)
    
    print(f"📨 Template:")
    print(f"   Titel: {template['title']}")
    print(f"   Farbe: {template['color']} (Rot)")
    print(f"   Test-Daten:")
    print(f"     • eCO2: {co2_level} ppm 🚨")
    print(f"     • TVOC: {tvoc_level} ppb")
    print()
    print(f"   Beschreibung:\n")
    print(template['description'])
    print()
    
    send_to_discord(notify, template)
    wait_for_input()

# ===== MAIN =====

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🧪 DISCORD NACHRICHT TEST-SUITE")
    print("="*60)
    print("\n📋 Reduzierte Benachrichtigungen (Anti-Spam):")
    print("   ✅ 1. Session Start")
    print("   ✅ 2. Break Stats (nach jeder Pause)")
    print("   ✅ 3. Session Report (finaler Report)")
    print("   ⚠️  4. CO2 Critical (nur > 800 ppm)")
    print()
    print("🗑️  ENTFERNT:")
    print("   ❌ Work Finished (redundant)")
    print("   ❌ Break Finished (unnötig)")
    print("   ❌ CO2 Warning (nur noch Critical)")
    print()
    
    try:
        test_ready_message()      # Deployment-Check
        test_session_start()      # 1/3: Start
        test_break_stats()        # 2/3: Nach Pause
        test_session_report()     # 3/3: Final Report
        test_co2_critical()       # Optional: Kritische Werte
        
        print("="*60)
        print("✅ ALLE DISCORD TESTS ABGESCHLOSSEN!")
        print("="*60)
        print("\n📊 ZUSAMMENFASSUNG:")
        print("   • 5 Tests durchgeführt")
        print("   • 3 Haupt-Nachrichten + 2 Optional")
        print("   • Anti-Spam: Nur essenzielle Updates")
        print()
        
    except KeyboardInterrupt:
        print("\n\n🛑 Tests unterbrochen")
        sys.exit(0)