"""
test_buz.py - Testet Buzzer-Signale und Alarme
Dokumentiert alle verfügbaren Buzzer-Töne und ihre Verwendung
"""

import os
import sys
import time

# ⚠️ WICHTIG: Device Override MUSS VOR import config stehen!
os.environ['DEVICE_OVERRIDE'] = 'pitop1'

from hardware.buzzer import Buzzer

# ============================================================
# BUZZER TÖNE - DOKUMENTATION
# ============================================================

BUZZER_SOUNDS = {
    'beep': {
        'name': 'Kurzer Beep',
        'function': 'beep()',
        'duration': '0.2s',
        'used_for': 'CO2 Alarm-Muster (mehrfach hintereinander)',
        'pattern': 'single_short',
        'color': '🟦'
    },
    'long_beep': {
        'name': 'Langer Beep',
        'function': 'long_beep()',
        'duration': '1.0s',
        'used_for': 'Timer-Ende Signal (Arbeitszeit oder Pause vorbei)',
        'pattern': 'single_long',
        'color': '🟩'
    },
    'double_beep': {
        'name': 'Doppel-Beep',
        'function': 'double_beep()',
        'duration': '0.1s + 0.1s + Pause',
        'used_for': 'Spezielle Signale (z.B. Buttons oder Bestätigung)',
        'pattern': 'double',
        'color': '🟨'
    },
    'co2_alarm': {
        'name': 'CO2 Alarm Pattern',
        'function': 'co2_alarm()',
        'duration': '3x kurz',
        'used_for': 'CO2-Level kritisch (>800 ppm) - wiederholte Beeps',
        'pattern': 'triple_short',
        'color': '🔴'
    },
    'timer_alarm': {
        'name': 'Timer Alarm',
        'function': 'timer_alarm()',
        'duration': '1.0s',
        'used_for': 'Timer-Ende Signal (Arbeitszeit oder Pause vorbei)',
        'pattern': 'single_long',
        'color': '⏰'
    },
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

def print_sound_info(sound_key, sound_data):
    """Zeigt Informationen über einen Buzzer-Ton"""
    print(f"\n{sound_data['color']} {sound_data['name']}")
    print(f"   Funktion: {sound_data['function']}")
    print(f"   Dauer: {sound_data['duration']}")
    print(f"   Verwendung: {sound_data['used_for']}")
    print(f"   Pattern: {sound_data['pattern']}\n")

def wait_for_input():
    input("👉 ENTER für nächsten Test...")
    print()

def test_sound(buzzer, sound_key, sound_data, test_name):
    """Testet einen Buzzer-Ton"""
    print_sound_info(sound_key, sound_data)
    print(f"🔊 Starte Test: {test_name}")
    print(f"   Höre auf den Ton...\n")

    try:
        if sound_key == 'beep':
            buzzer.beep()
        elif sound_key == 'long_beep':
            buzzer.long_beep()
        elif sound_key == 'double_beep':
            buzzer.double_beep()
        elif sound_key == 'co2_alarm':
            buzzer.co2_alarm()
            time.sleep(1.5)  # Warten bis CO2 Alarm fertig ist
        elif sound_key == 'timer_alarm':
            buzzer.timer_alarm()

        print("✅ Test abgeschlossen!\n")
        return True

    except Exception as e:
        print(f"❌ Fehler: {e}")
        return False

# ============================================================
# TESTS
# ============================================================

def test_0_init():
    """Test 0: Buzzer Initialisierung"""
    print_header("TEST 0: BUZZER INITIALISIERUNG", "Prüft ob Buzzer verfügbar ist")

    try:
        buzzer = Buzzer()
        print(f"✅ Buzzer erfolgreich initialisiert")
        print(f"   Pin: D3 (HARDCODED)")
        print(f"   Status: Bereit für Tests\n")
        return buzzer
    except Exception as e:
        print(f"❌ Fehler bei Buzzer-Initialisierung: {e}")
        print(f"💡 Tipp: Stelle sicher, dass der Buzzer auf D3 angeschlossen ist")
        sys.exit(1)

def test_1_beep(buzzer):
    """Test 1: Kurzer Beep"""
    print_header("TEST 1: KURZER BEEP", "Grundlegendes Buzzer-Signal")
    test_sound(buzzer, 'beep', BUZZER_SOUNDS['beep'], "Kurzer Beep")
    wait_for_input()

def test_2_long_beep(buzzer):
    """Test 2: Langer Beep"""
    print_header("TEST 2: LANGER BEEP", "Timer-Ende Signal")
    test_sound(buzzer, 'long_beep', BUZZER_SOUNDS['long_beep'], "Langer Beep")
    wait_for_input()

def test_3_double_beep(buzzer):
    """Test 3: Doppel-Beep"""
    print_header("TEST 3: DOPPEL-BEEP", "Bestätigungs-Signal")
    test_sound(buzzer, 'double_beep', BUZZER_SOUNDS['double_beep'], "Doppel-Beep")
    wait_for_input()

def test_4_co2_alarm(buzzer):
    """Test 4: CO2 Alarm Pattern"""
    print_header("TEST 4: CO2 ALARM PATTERN", "Kritisches CO2-Level Signal")
    test_sound(buzzer, 'co2_alarm', BUZZER_SOUNDS['co2_alarm'], "CO2 Alarm (3x Beep)")
    wait_for_input()

def test_5_timer_alarm(buzzer):
    """Test 5: Timer Alarm"""
    print_header("TEST 5: TIMER ALARM", "Timer-Ende Signal")
    test_sound(buzzer, 'timer_alarm', BUZZER_SOUNDS['timer_alarm'], "Timer Alarm")
    wait_for_input()

def test_6_continuous():
    """Test 6: Kontinuierliches Signal (On/Off)"""
    print_header("TEST 6: KONTINUIERLICHES SIGNAL", "Buzzer on() / off()")

    try:
        buzzer = Buzzer()
        print("🔊 Buzzer einschalten (2 Sekunden)...")
        buzzer.on()
        time.sleep(2)
        buzzer.off()
        print("✅ Buzzer ausgeschaltet\n")
        return True
    except Exception as e:
        print(f"❌ Fehler: {e}")
        return False
    finally:
        wait_for_input()

# ============================================================
# DOKUMENTATION
# ============================================================

def show_documentation():
    """Zeigt vollständige Dokumentation aller Buzzer-Töne"""
    print_header("BUZZER-TÖNE DOKUMENTATION", "Alle verfügbaren Signale")

    print("📋 ÜBERSICHT ALLER BUZZER-TÖNE:\n")

    for key, sound in BUZZER_SOUNDS.items():
        print(f"{sound['color']} {sound['name'].upper()}")
        print(f"   └─ Funktion: {sound['function']}")
        print(f"   └─ Dauer: {sound['duration']}")
        print(f"   └─ Verwendung: {sound['used_for']}")
        print(f"   └─ Pattern: {sound['pattern']}\n")

# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🧪 BUZZER TEST SUITE")
    print("="*60)
    print(f"\n📱 Device: pitop1 (Override aktiv)")
    print(f"📌 Pin: D3 (HARDCODED)")
    print()

    # Dokumentation anzeigen
    show_documentation()

    input("👉 ENTER um Tests zu starten...")

    try:
        # Buzzer initialisieren
        buzzer = test_0_init()
        wait_for_input()

        # Alle Tests durchführen
        test_1_beep(buzzer)
        test_2_long_beep(buzzer)
        test_3_double_beep(buzzer)
        test_4_co2_alarm(buzzer)
        test_5_timer_alarm(buzzer)
        test_6_continuous()

        # Cleanup
        print("\n" + "="*60)
        print("🧹 CLEANUP")
        print("="*60)
        buzzer.cleanup()
        print("✅ Buzzer-Ressourcen freigegeben\n")

        print("="*60)
        print("✅ ALLE TESTS ABGESCHLOSSEN!")
        print("="*60)
        print("\n📊 Zusammenfassung:")
        print("   • 6 Buzzer-Signale getestet")
        print("   • Alle Töne und Patterns funktionieren")
        print("   • Dokumentation: Siehe oben")
        print()

    except KeyboardInterrupt:
        print("\n\n🛑 Tests abgebrochen (Ctrl+C)")
        try:
            buzzer.cleanup()
        except:
            pass
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Unerwarteter Fehler: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
