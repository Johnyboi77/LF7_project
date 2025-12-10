#!/usr/bin/env python3
"""
🧪 KOMPLETTER HARDWARE-TEST FÜR PITOP 4
Testet alle Komponenten nacheinander mit Pausen

Tests:
1. LEDs (Red, Green, Blue)
2. Buzzer
3. Buttons (1 & 2)
4. CO2 Sensor (SGP30)
5. Step Counter (BMA400)
6. Datenbank (Supabase)
7. Discord Notifications

Autor: Learning Assistant Team
Version: 1.0
"""

import sys
import os
import time
from datetime import datetime

def print_banner(text, char="="):
    """Schöner Banner für Überschriften"""
    width = 70
    print("\n" + char * width)
    print(f"{text:^{width}}")
    print(char * width + "\n")

def print_section(text):
    """Kleinere Überschrift"""
    print(f"\n{'─' * 70}")
    print(f"  {text}")
    print(f"{'─' * 70}\n")

def wait_for_enter(message=""):
    """Wartet auf Enter"""
    if message:
        print(f"\n💡 {message}")
    input("   👉 Drücke ENTER zum Fortfahren...\n")

def print_progress(current, total, name):
    """Zeigt Fortschritt an"""
    percentage = (current / total) * 100
    bar_length = 40
    filled = int(bar_length * current / total)
    bar = "█" * filled + "░" * (bar_length - filled)
    print(f"\n[{bar}] {percentage:.0f}% - Test {current}/{total}: {name}")

def test_system_requirements():
    """Prüft System-Voraussetzungen"""
    print_section("SYSTEM-CHECK")
    
    checks = []
    
    # Python Version
    print("🐍 Python Version:", sys.version.split()[0])
    checks.append(("Python Version", True))
    
    # RPi.GPIO verfügbar?
    try:
        import RPi.GPIO as GPIO
        print("✅ RPi.GPIO verfügbar")
        checks.append(("RPi.GPIO", True))
        gpio_available = True
    except ImportError:
        print("⚠️  RPi.GPIO nicht verfügbar (MOCK MODE)")
        checks.append(("RPi.GPIO", False))
        gpio_available = False
    
    # I2C verfügbar?
    i2c_available = os.path.exists('/dev/i2c-1')
    if i2c_available:
        print("✅ I2C aktiviert (/dev/i2c-1)")
    else:
        print("⚠️  I2C nicht aktiviert")
    checks.append(("I2C", i2c_available))
    
    # Supabase Config
    try:
        import config
        has_supabase = bool(config.SUPABASE_URL and config.SUPABASE_KEY)
        if has_supabase:
            print(f"✅ Supabase konfiguriert")
        else:
            print("⚠️  Supabase nicht konfiguriert (.env)")
        checks.append(("Supabase Config", has_supabase))
    except:
        print("⚠️  config.py nicht gefunden")
        checks.append(("Supabase Config", False))
    
    # Discord Config
    try:
        has_discord = bool(config.DISCORD_WEBHOOK_URL)
        if has_discord:
            print("✅ Discord Webhook konfiguriert")
        else:
            print("⚠️  Discord nicht konfiguriert (.env)")
        checks.append(("Discord Config", has_discord))
    except:
        checks.append(("Discord Config", False))
    
    print(f"\n📊 System-Check: {sum(c[1] for c in checks)}/{len(checks)} OK")
    
    return gpio_available

def run_test_module(test_name, test_file, skip_on_mock=False):
    """Führt ein Test-Modul aus"""
    try:
        # Dynamisch Test-Modul laden
        module_name = test_file.replace('.py', '').replace('test_einzeln/', '').replace('/', '.')
        
        print(f"📦 Lade {test_file}...")
        
        # Teste ob Datei existiert
        if not os.path.exists(test_file):
            print(f"❌ Test-Datei nicht gefunden: {test_file}")
            return False
        
        # Führe Test aus
        exit_code = os.system(f"python3 {test_file}")
        
        success = (exit_code == 0)
        
        if success:
            print(f"\n✅ {test_name} erfolgreich!")
        else:
            print(f"\n❌ {test_name} fehlgeschlagen (Exit Code: {exit_code})")
        
        return success
        
    except Exception as e:
        print(f"❌ Fehler beim Ausführen von {test_name}: {e}")
        return False

def main():
    """Hauptprogramm"""
    start_time = datetime.now()
    
    # HEADER
    print_banner("🚀 PITOP 4 HARDWARE TEST SUITE", "=")
    print("📋 Dieses Script testet alle Hardware-Komponenten nacheinander")
    print("⏱️  Geschätzte Dauer: 10-15 Minuten")
    print("💡 Bei jedem Test kannst du mit ENTER fortfahren\n")
    
    print("🔧 Komponenten:")
    components = [
        "1. LEDs (Red, Green, Blue)",
        "2. Buzzer (Aktiv)",
        "3. Buttons (1 & 2)",
        "4. CO2 Sensor (SGP30)",
        "5. Step Counter (BMA400)",
        "6. Datenbank (Supabase)",
        "7. Discord Notifications"
    ]
    for comp in components:
        print(f"   {comp}")
    
    wait_for_enter("Bereit? Tests starten")
    
    # System-Check
    gpio_available = test_system_requirements()
    
    if not gpio_available:
        print("\n⚠️  WARNUNG: Kein GPIO verfügbar - Tests laufen im MOCK MODE")
        print("   Manche Tests werden simuliert")
        response = input("\n   Trotzdem fortfahren? (j/n): ").lower()
        if response != 'j':
            print("\n👋 Abgebrochen\n")
            return 1
    
    # Test-Konfiguration
    tests = [
        {
            'name': 'LEDs',
            'file': 'test_einzeln/test1_led.py',
            'description': '🔴🟢🔵 Alle LED-Farben testen',
            'skip_on_mock': False
        },
        {
            'name': 'Buzzer',
            'file': 'test_einzeln/test4_buzzer.py',
            'description': '🔊 Akustische Ausgabe testen',
            'skip_on_mock': False
        },
        {
            'name': 'Button 1',
            'file': 'test_einzeln/test2_button1.py',
            'description': '🔘 Session-Management Button',
            'skip_on_mock': False
        },
        {
            'name': 'Button 2',
            'file': 'test_einzeln/test3_button2.py',
            'description': '🔘 Cancel/Storno Button',
            'skip_on_mock': False
        },
        {
            'name': 'CO2 Sensor',
            'file': 'test_einzeln/test5_co2sensor.py',
            'description': '🌡️  Luftqualität messen',
            'skip_on_mock': False
        },
        {
            'name': 'Step Counter',
            'file': 'test_einzeln/05_test_step_counter.py',
            'description': '👣 Schritte zählen',
            'skip_on_mock': False
        },
        {
            'name': 'Discord',
            'file': 'test_einzeln/test.discord.py',
            'description': '📱 Push-Benachrichtigungen',
            'skip_on_mock': True
        }
    ]
    
    results = {}
    total_tests = len(tests)
    
    # Führe Tests durch
    for i, test in enumerate(tests, 1):
        print_progress(i, total_tests, test['name'])
        print_banner(f"TEST {i}/{total_tests}: {test['name'].upper()}", "─")
        
        print(f"📝 {test['description']}")
        
        # Skip bei Mock Mode wenn nötig
        if not gpio_available and test.get('skip_on_mock', False):
            print(f"\n⏭️  Übersprungen (kein GPIO)")
            results[test['name']] = None
            wait_for_enter(f"Weiter zu Test {i+1}")
            continue
        
        # Warte auf User
        wait_for_enter(f"Bereit für {test['name']} Test?")
        
        # Führe Test aus
        success = run_test_module(test['name'], test['file'])
        results[test['name']] = success
        
        # Nach jedem Test kleine Pause
        if i < total_tests:
            print("\n" + "─" * 70)
            time.sleep(1)
            wait_for_enter(f"Weiter zu Test {i+1}/{total_tests}")
    
    # FINALE ZUSAMMENFASSUNG
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print_banner("📊 FINALE TEST-ZUSAMMENFASSUNG", "=")
    
    print("┌────────────────────────────────────────────────────┐")
    print("│  Komponente              Status                    │")
    print("├────────────────────────────────────────────────────┤")
    
    for test_name, result in results.items():
        if result is None:
            status = "⏭️  SKIPPED"
            status_color = "⚪"
        elif result:
            status = "✅ WORKS"
            status_color = "🟢"
        else:
            status = "❌ WORKS NOT"
            status_color = "🔴"
        
        print(f"│  {status_color} {test_name:<24} {status:<20} │")
    
    print("└────────────────────────────────────────────────────┘")
    
    # Statistiken
    total = len([r for r in results.values() if r is not None])
    passed = sum([1 for r in results.values() if r is True])
    failed = sum([1 for r in results.values() if r is False])
    skipped = sum([1 for r in results.values() if r is None])
    
    print(f"\n📈 STATISTIK:")
    print(f"   ✅ Bestanden:    {passed}/{total}")
    print(f"   ❌ Fehler:       {failed}/{total}")
    print(f"   ⏭️  Übersprungen: {skipped}")
    print(f"   ⏱️  Dauer:        {duration:.0f} Sekunden")
    
    # Erfolgsquote
    if total > 0:
        success_rate = (passed / total) * 100
        print(f"\n🎯 Erfolgsquote: {success_rate:.0f}%")
        
        if success_rate == 100:
            print("\n🎉 PERFEKT! Alle Tests bestanden!")
            print("   ✅ System ist bereit für die Präsentation!")
            exit_code = 0
        elif success_rate >= 80:
            print("\n👍 SEHR GUT! Fast alle Tests bestanden")
            print("   ⚠️  Prüfe die fehlgeschlagenen Tests nochmal")
            exit_code = 0
        elif success_rate >= 60:
            print("\n⚠️  OKAY - Mehrere Tests fehlgeschlagen")
            print("   🔧 Bitte Hardware und Verkabelung prüfen")
            exit_code = 1
        else:
            print("\n❌ ZU VIELE FEHLER!")
            print("   🚨 System nicht betriebsbereit")
            print("   🔧 Hardware-Check nötig")
            exit_code = 1
    else:
        print("\n⚠️  Keine Tests durchgeführt")
        exit_code = 1
    
    # Empfehlungen
    print("\n" + "="*70)
    print("📝 NÄCHSTE SCHRITTE:")
    
    if failed > 0:
        print("\n🔧 Fehlerhafte Komponenten:")
        for test_name, result in results.items():
            if result is False:
                print(f"   ❌ {test_name}")
        print("\n💡 Tipps:")
        print("   1. Verkabelung prüfen (Grove-Kabel fest?)")
        print("   2. i2cdetect -y 1 ausführen")
        print("   3. Komponenten umstecken/tauschen")
        print("   4. doc/PIN_WIRING.md konsultieren")
    else:
        print("\n✅ Alle Komponenten funktionieren!")
        print("   👉 Bereit für main_pitop1.py und main_pitop2.py")
        print("   👉 Starte mit: ./start_both.sh")
    
    print("\n📚 Weitere Infos:")
    print("   - Einzeltests: test_einzeln/")
    print("   - Dokumentation: doc/PIN_WIRING.md")
    print("   - Troubleshooting: siehe Doku Abschnitt 'Troubleshooting'")
    
    print("\n" + "="*70)
    print(f"Test abgeschlossen um {end_time.strftime('%H:%M:%S')}")
    print("="*70 + "\n")
    
    return exit_code

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests durch Benutzer abgebrochen")
        print("👋 Auf Wiedersehen!\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ KRITISCHER FEHLER: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)