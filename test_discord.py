#!/usr/bin/env python3
"""
test_discord.py - Testet Discord-Benachrichtigungen
"""

import os
import sys

# ⚠️ WICHTIG: Device Override MUSS VOR import config stehen!
os.environ['DEVICE_OVERRIDE'] = 'pitop1'

from datetime import datetime
from requests import post
from services.discord_templates import NotificationService
from services.discord_templates import MessageTemplates

# ============================================================
# TESTWERTE - HIER ANPASSEN!
# ============================================================

TEST_VALUES = {
    'user_name': 'Alicia',
    
    # Break Stats Test
    'break': {
        'pause_number': 1,
        'steps': 1247,
        'calories': 62,
        'distance': 935  # Meter
    },
    
    # Session Report Test
    'session': {
        'total_work_time': 5400,   # 90 Minuten in Sekunden
        'total_pause_time': 1800,  # 30 Minuten in Sekunden
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
    },
    
    # CO2 Critical Test
    'co2_critical': {
        'co2_level': 950,   # ppm (kritisch!)
        'tvoc_level': 450   # ppb
    }
}

# ============================================================
# HELPER FUNKTIONEN
# ============================================================

def print_header(title, subtitle=None):
    print("\n" + "="*60)
    print(f"🧪 {title}")
    if subtitle:
        print(f"   {subtitle}")
    print("="*60 + "\n")

def wait_for_input():
    input("👉 ENTER für nächsten Test...")
    print()

def send_to_discord(notify, template, test_name):
    """Sendet Template an Discord mit verbessertem Error Handling"""
    try:
        payload = {
            "embeds": [{
                "title": template['title'],
                "description": template['description'],
                "color": template['color'],
                "timestamp": datetime.utcnow().isoformat(),
                "footer": {"text": f"Test: {test_name}"}
            }]
        }
        
        # Längeres Timeout für langsame WSL-Verbindungen
        response = post(notify.webhook_url, json=payload, timeout=30)
        
        if response.status_code == 204:
            print("✅ Erfolgreich versendet!")
            return True
        else:
            print(f"⚠️  Discord Status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Fehler beim Senden: {e}")
        print(f"💡 Tipp: Netzwerkverbindung prüfen oder Timeout erhöhen")
        return False

def show_template_preview(template, test_data=None):
    """Zeigt Template-Vorschau"""
    print(f"📨 Template-Vorschau:")
    print(f"   📋 Titel: {template['title']}")
    print(f"   🎨 Farbe: {template['color']}")
    
    if test_data:
        print(f"\n   📊 Verwendete Testwerte:")
        for key, value in test_data.items():
            print(f"      • {key}: {value}")
    
    print(f"\n   📝 Discord-Nachricht:\n")
    print("   " + "─" * 56)
    for line in template['description'].split('\n'):
        print(f"   {line}")
    print("   " + "─" * 56)
    print()

# ============================================================
# TESTS
# ============================================================

def test_0_ready():
    """Test 0: Deployment Ready Message"""
    print_header("TEST 0: READY MESSAGE", "Prüft ob Discord-Webhook funktioniert")
    
    notify = NotificationService()
    
    print(f"🔗 Webhook: {notify.webhook_url[:50]}...")
    print(f"✅ Status: {'Aktiv' if notify.is_enabled else 'Inaktiv'}\n")
    
    ready_template = {
        "title": "🤖 Learning Assistant - Test gestartet",
        "description": (
            "**Discord Test-Suite läuft** 🚀\n\n"
            "Das System sendet jetzt Testnachrichten...\n\n"
            "✅ Webhook aktiv\n"
            "✅ Verbindung OK\n"
        ),
        "color": 3066993  # Grün
    }
    
    show_template_preview(ready_template)
    send_to_discord(notify, ready_template, "Ready Check")
    wait_for_input()

def test_1_session_start():
    """Test 1: Session Start"""
    print_header("TEST 1: SESSION START", "Wird beim Start der Lerneinheit gesendet")
    
    notify = NotificationService()
    template = MessageTemplates.session_start(TEST_VALUES['user_name'])
    
    test_data = {
        'Benutzer': TEST_VALUES['user_name']
    }
    
    show_template_preview(template, test_data)
    send_to_discord(notify, template, "Session Start")
    wait_for_input()

def test_2_break_stats():
    """Test 2: Break Stats"""
    print_header("TEST 2: BREAK STATS", "Wird nach JEDER Pause gesendet")
    
    notify = NotificationService()
    
    break_vals = TEST_VALUES['break']
    template = MessageTemplates.break_stats(
        TEST_VALUES['user_name'],
        break_vals['pause_number'],
        break_vals['steps'],
        break_vals['calories'],
        break_vals['distance']
    )
    
    test_data = {
        'Pause Nummer': f"#{break_vals['pause_number']}",
        'Schritte': f"{break_vals['steps']:,}",
        'Kalorien': f"{break_vals['calories']} kcal",
        'Distanz': f"{break_vals['distance']} m"
    }
    
    show_template_preview(template, test_data)
    send_to_discord(notify, template, "Break Stats")
    wait_for_input()

def test_3_session_report():
    """Test 3: Session Report"""
    print_header("TEST 3: SESSION REPORT", "Finaler Report am Ende der Session")
    
    notify = NotificationService()
    
    stats = {
        'session': TEST_VALUES['session'],
        'co2': TEST_VALUES['co2'],
        'movement': TEST_VALUES['movement']
    }
    
    template = MessageTemplates.session_report(TEST_VALUES['user_name'], stats)
    
    # Berechne lesbare Zeit
    work_mins = TEST_VALUES['session']['total_work_time'] // 60
    pause_mins = TEST_VALUES['session']['total_pause_time'] // 60
    
    test_data = {
        'Lernzeit': f"{work_mins} Min ({work_mins//60}h {work_mins%60}min)",
        'Pausenzeit': f"{pause_mins} Min",
        'Pausen': TEST_VALUES['session']['pause_count'],
        'Ø CO2': f"{TEST_VALUES['co2']['avg_co2']} ppm",
        'CO2 Alarme': TEST_VALUES['co2']['alarm_count'],
        'Schritte': f"{TEST_VALUES['movement']['step_count']:,}",
        'Kalorien': f"{TEST_VALUES['movement']['calories_burned']} kcal"
    }
    
    show_template_preview(template, test_data)
    send_to_discord(notify, template, "Session Report")
    wait_for_input()

def test_4_co2_critical():
    """Test 4: CO2 Critical Alert"""
    print_header("TEST 4: CO2 CRITICAL", "Wird nur bei kritischen Werten (>800 ppm) gesendet")
    
    notify = NotificationService()
    
    co2_vals = TEST_VALUES['co2_critical']
    template = MessageTemplates.co2_critical(
        TEST_VALUES['user_name'],
        co2_vals['co2_level'],
        co2_vals['tvoc_level']
    )
    
    test_data = {
        'eCO2': f"{co2_vals['co2_level']} ppm 🚨",
        'TVOC': f"{co2_vals['tvoc_level']} ppb",
        'Status': '⚠️ KRITISCH - Sofort lüften!'
    }
    
    show_template_preview(template, test_data)
    send_to_discord(notify, template, "CO2 Critical")
    wait_for_input()

# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🧪 DISCORD MESSAGE TEST SUITE")
    print("="*60)
    print(f"\n👤 Test-Benutzer: {TEST_VALUES['user_name']}")
    print(f"📱 Device: pitop1 (Override aktiv)")
    print()
    
    print("📊 VERWENDETE TESTWERTE:")
    print("─" * 60)
    print(f"  Break Stats:")
    print(f"    • Pause #{TEST_VALUES['break']['pause_number']}")
    print(f"    • {TEST_VALUES['break']['steps']:,} Schritte")
    print(f"    • {TEST_VALUES['break']['calories']} kcal")
    print(f"    • {TEST_VALUES['break']['distance']} m Distanz")
    print()
    print(f"  Session Report:")
    work_mins = TEST_VALUES['session']['total_work_time'] // 60
    pause_mins = TEST_VALUES['session']['total_pause_time'] // 60
    print(f"    • Lernzeit: {work_mins} Min ({work_mins//60}h {work_mins%60}min)")
    print(f"    • Pausenzeit: {pause_mins} Min")
    print(f"    • Pausen: {TEST_VALUES['session']['pause_count']}x")
    print(f"    • Ø CO2: {TEST_VALUES['co2']['avg_co2']} ppm")
    
    try:
        test_0_ready()
        test_1_session_start()
        test_2_break_stats()
        test_3_session_report()
        test_4_co2_critical()
        
        print("="*60)
        print("✅ ALLE TESTS ABGESCHLOSSEN!")
        print("="*60)
        print("\n📊 Zusammenfassung:")
        print("   • 5 Discord-Nachrichten gesendet")
        print("   • Alle Templates getestet")
        print("   • Prüfe Discord-Channel für Ergebnisse")
        print()
        
    except KeyboardInterrupt:
        print("\n\n🛑 Tests abgebrochen (Ctrl+C)")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Unerwarteter Fehler: {e}")
        sys.exit(1)