#!/usr/bin/env python3
"""
test_mock.py - Testet Mock Hardware
Für lokale Tests OHNE echten PiTop
"""

import sys
import time
from mock_hardware import Button, LED, Buzzer, CO2Sensor, StepCounter

def print_section(title):
    """Druckt schöne Überschrift"""
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print(f"{'='*60}\n")

def test_led():
    """LED Test"""
    print_section("LED TEST")
    
    led = LED("D2")
    
    print("1️⃣  LED einschalten...")
    led.on()
    time.sleep(0.5)
    
    print("\n2️⃣  LED ausschalten...")
    led.off()
    time.sleep(0.5)
    
    print("\n3️⃣  LED blinken (3 Sekunden)...")
    led.blink(0.3, 0.3)
    time.sleep(3)
    led.off()
    
    print("\n✅ LED Test abgeschlossen\n")

def test_buzzer():
    """Buzzer Test"""
    print_section("BUZZER TEST")
    
    buzzer = Buzzer("D3")
    
    print("1️⃣  Kurzer Beep...")
    buzzer.beep(0.2)
    time.sleep(0.5)
    
    print("\n2️⃣  Doppel-Beep...")
    buzzer.double_beep()
    time.sleep(0.5)
    
    print("\n3️⃣  Langer Beep...")
    buzzer.long_beep(1.0)
    time.sleep(1.5)
    
    print("\n4️⃣  CO2 Alarm...")
    buzzer.co2_alarm()
    
    print("\n✅ Buzzer Test abgeschlossen\n")

def test_co2():
    """CO2 Sensor Test"""
    print_section("CO2 SENSOR TEST")
    
    co2 = CO2Sensor()
    
    print("1️⃣  Normal-Werte (OK)...")
    level = co2.read()
    status = co2.get_alarm_status()
    print(f"   eCO2: {level} ppm")
    print(f"   Status: {status}")
    print(f"   ✅ OK - Alles normal\n")
    
    time.sleep(1)
    
    print("2️⃣  Warnung-Werte (Warning)...")
    co2.simulate_warning_co2()
    level = co2.read()
    status = co2.get_alarm_status()
    print(f"   eCO2: {level} ppm")
    print(f"   Status: {status}")
    print(f"   ⚠️  WARNUNG - Lüften!\n")
    
    time.sleep(1)
    
    print("3️⃣  Kritische Werte (Critical)...")
    co2.simulate_high_co2()
    level = co2.read()
    status = co2.get_alarm_status()
    print(f"   eCO2: {level} ppm")
    print(f"   Status: {status}")
    print(f"   🚨 KRITISCH - SOFORT LÜFTEN!\n")
    
    time.sleep(1)
    
    print("4️⃣  Reset zu Normal...")
    co2.reset_co2()
    level = co2.read()
    status = co2.get_alarm_status()
    print(f"   eCO2: {level} ppm")
    print(f"   Status: {status}")
    
    print("\n✅ CO2 Sensor Test abgeschlossen\n")

def test_step_counter():
    """Step Counter Test"""
    print_section("STEP COUNTER TEST")
    
    steps = StepCounter()
    
    print("1️⃣  Starte Schrittzähler...")
    steps.start()
    time.sleep(0.5)
    
    print("\n2️⃣  Simuliere Schritte (Pause läuft 5 Sekunden)...")
    for i in range(5):
        steps.simulate_steps(250)
        print(f"   {i+1}s: Total {steps.read()} Schritte")
        time.sleep(1)
    
    print("\n3️⃣  Stoppe Schrittzähler...")
    final_steps = steps.stop()
    
    # Berechne Statistiken
    calories = int(final_steps * 0.05)
    distance = int(final_steps * 0.75)
    
    print(f"\n   📊 STATISTIK:")
    print(f"   👣 Schritte: {final_steps:,}")
    print(f"   🔥 Kalorien: ~{calories} kcal")
    print(f"   📏 Distanz: ~{distance}m")
    
    print("\n✅ Step Counter Test abgeschlossen\n")

def test_button():
    """Button Test"""
    print_section("BUTTON TEST")
    
    button = Button("D0")
    
    print("1️⃣  Registriere Callbacks...")
    
    def on_press():
        print("   ✅ Button PRESS erkannt!")
    
    def on_release():
        print("   ✅ Button RELEASE erkannt!")
    
    button.when_pressed(on_press)
    button.when_released(on_release)
    
    print("\n2️⃣  Simuliere Button-Druck...")
    button.simulate_press(duration=0.5)
    time.sleep(0.5)
    button.simulate_release()
    
    print("\n3️⃣  Nochmal simulieren...")
    button.simulate_press(duration=0.5)
    time.sleep(0.5)
    button.simulate_release()
    
    print("\n✅ Button Test abgeschlossen\n")

def test_all_together():
    """Simuliert eine komplette Lern-Session"""
    print_section("KOMPLETTE SESSION SIMULATION")
    
    # Initialisiere Hardware
    btn1 = Button("D0")
    btn2 = Button("D1")
    led = LED("D2")
    buzzer = Buzzer("D3")
    co2 = CO2Sensor()
    steps = StepCounter()
    
    print("📱 Starte Lern-Session Simulation (30 Sekunden)...\n")
    
    # Arbeitsphase startet
    print("🎓 PHASE 1: ARBEITSPHASE STARTET")
    btn1.simulate_press()
    time.sleep(0.5)
    btn1.simulate_release()
    
    led.on()
    buzzer.beep(0.2)
    time.sleep(1)
    
    print("✅ Arbeite für 10 Sekunden...")
    for i in range(10):
        co2_val = co2.read()
        print(f"  {i+1}s: CO2 = {co2_val} ppm")
        time.sleep(1)
    
    # Pause startet
    print("\n☕ PHASE 2: PAUSENPHASE STARTET")
    btn2.simulate_press()
    time.sleep(0.5)
    btn2.simulate_release()
    
    led.blink(0.5, 0.5)
    buzzer.beep(0.2)
    steps.start()
    
    print("✅ Pausiere für 10 Sekunden, zähle Schritte...")
    for i in range(10):
        steps.simulate_steps(50)
        step_count = steps.read()
        print(f"  {i+1}s: {step_count} Schritte")
        time.sleep(1)
    
    final_steps = steps.stop()
    
    # Session ende
    print("\n🛑 PHASE 3: SESSION BEENDET")
    led.off()
    buzzer.long_beep(1.0)
    
    print(f"\n📊 FINAL STATISTIK:")
    print(f"   👣 Schritte in Pause: {final_steps:,}")
    print(f"   🔥 Kalorien: ~{int(final_steps * 0.05)} kcal")
    print(f"   📏 Distanz: ~{int(final_steps * 0.75)}m")
    
    print("\n✅ Session-Simulation abgeschlossen\n")

if __name__ == "__main__":
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*15 + "🎭 MOCK HARDWARE TEST SUITE" + " "*16 + "║")
    print("╚" + "="*58 + "╝")
    
    try:
        # Einzelne Tests
        test_led()
        input("👉 Drücke ENTER für nächsten Test...")
        
        test_buzzer()
        input("👉 Drücke ENTER für nächsten Test...")
        
        test_co2()
        input("👉 Drücke ENTER für nächsten Test...")
        
        test_step_counter()
        input("👉 Drücke ENTER für nächsten Test...")
        
        test_button()
        input("👉 Drücke ENTER für komplette Simulation...")
        
        # Komplette Simulation
        test_all_together()
        
        print("="*60)
        print("✅ ALLE TESTS ABGESCHLOSSEN!")
        print("="*60 + "\n")
        
    except KeyboardInterrupt:
        print("\n\n🛑 Tests unterbrochen")
        sys.exit(0)