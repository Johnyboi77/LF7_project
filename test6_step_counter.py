#!/usr/bin/env python3
"""
Test 5: Step Counter (BMA400 / Grove Accelerometer)
Testet Schrittzählung und Bewegungserkennung
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Mock-Modus für Tests ohne Hardware
try:
    from grove.grove_step_counter_bma400 import GroveStepCounter
    MOCK_MODE = False
except ImportError:
    print("⚠️  Grove Library nicht gefunden - MOCK MODE aktiviert\n")
    
    class GroveStepCounter:
        """Mock Step Counter für Tests ohne Hardware"""
        def __init__(self):
            self.steps = 0
            self._running = False
            print("[MOCK] Step Counter initialisiert")
        
        def reset(self):
            self.steps = 0
            print("[MOCK] Step Counter reset")
        
        def start(self):
            self._running = True
            print("[MOCK] Step Counter gestartet")
        
        def stop(self):
            self._running = False
            print("[MOCK] Step Counter gestoppt")
    
    MOCK_MODE = True

import time
import random

class StepCounterTester:
    def __init__(self):
        print("🔄 Initialisiere Step Counter...")
        
        try:
            self.sensor = GroveStepCounter()
            self.sensor.reset()
            print("✅ Sensor initialisiert\n")
        except Exception as e:
            print(f"❌ Fehler bei Initialisierung: {e}\n")
            self.sensor = None
    
    def test_initialization(self):
        """Test 1: Initialisierung"""
        print(f"{'='*60}")
        print("🔧 Test 1: INITIALISIERUNG")
        print(f"{'='*60}\n")
        
        if not self.sensor:
            print("❌ Sensor nicht verfügbar")
            return False
        
        try:
            print("📊 Sensor-Info:")
            print(f"   Typ: BMA400 Accelerometer")
            print(f"   I2C-Adresse: 0x14")
            print(f"   Modus: {'MOCK' if MOCK_MODE else 'REAL'}")
            
            if MOCK_MODE:
                print("\n⚠️  Mock-Modus aktiv - Keine echte Hardware!")
                time.sleep(1)
                return True
            
            # Prüfe ob Sensor antwortet
            initial_steps = self.sensor.steps
            print(f"\n✅ Sensor antwortet (Steps: {initial_steps})")
            return True
            
        except Exception as e:
            print(f"\n❌ Initialisierungs-Fehler: {e}")
            return False
    
    def test_reset(self):
        """Test 2: Reset-Funktion"""
        print(f"\n{'='*60}")
        print("🔄 Test 2: RESET-FUNKTION")
        print(f"{'='*60}\n")
        
        if not self.sensor:
            return False
        
        try:
            print("1️⃣  Reset ausführen...")
            self.sensor.reset()
            time.sleep(0.5)
            
            print("2️⃣  Schritte auslesen...")
            steps = self.sensor.steps if not MOCK_MODE else 0
            
            print(f"\n📊 Ergebnis: {steps} Schritte")
            
            if steps == 0:
                print("✅ Reset erfolgreich - Zähler bei 0")
                return True
            else:
                print(f"⚠️  Reset möglicherweise fehlgeschlagen (Steps: {steps})")
                if not MOCK_MODE:
                    response = input("Trotzdem als OK werten? (j/n): ").lower()
                    return response == 'j'
                return True
                
        except Exception as e:
            print(f"❌ Reset-Fehler: {e}")
            return False
    
    def test_static_reading(self):
        """Test 3: Statische Messung (ohne Bewegung)"""
        print(f"\n{'='*60}")
        print("📊 Test 3: STATISCHE MESSUNG (5 Sekunden)")
        print(f"{'='*60}\n")
        
        if not self.sensor:
            return False
        
        if MOCK_MODE:
            print("⚠️  MOCK: Simuliere statische Messung...")
            for i in range(5):
                print(f"Sekunde {i+1}/5: 0 Schritte (keine Bewegung)")
                time.sleep(1)
            return True
        
        try:
            print("⚠️  WICHTIG: Sensor NICHT bewegen!\n")
            
            self.sensor.reset()
            start_steps = self.sensor.steps
            
            print("Messe 5 Sekunden ohne Bewegung...")
            for i in range(5):
                current_steps = self.sensor.steps
                print(f"   Sekunde {i+1}/5: {current_steps} Schritte")
                time.sleep(1)
            
            end_steps = self.sensor.steps
            difference = end_steps - start_steps
            
            print(f"\n📊 Ergebnis:")
            print(f"   Start:  {start_steps}")
            print(f"   Ende:   {end_steps}")
            print(f"   Diff:   {difference}")
            
            if difference <= 3:  # Max 3 Schritte tolerieren (Rauschen)
                print("\n✅ Sensor stabil - kein falsches Zählen")
                return True
            else:
                print(f"\n⚠️  {difference} Schritte ohne Bewegung erkannt")
                response = input("Sensor bewegt worden? Trotzdem OK? (j/n): ").lower()
                return response == 'j'
                
        except Exception as e:
            print(f"❌ Fehler: {e}")
            return False
    
    def test_movement_detection(self):
        """Test 4: Bewegungserkennung"""
        print(f"\n{'='*60}")
        print("👣 Test 4: BEWEGUNGSERKENNUNG (10 Sekunden)")
        print(f"{'='*60}\n")
        
        if not self.sensor:
            return False
        
        if MOCK_MODE:
            print("⚠️  MOCK: Simuliere Bewegung...\n")
            for i in range(10):
                mock_steps = random.randint(0, 3) * (i + 1)
                print(f"Sekunde {i+1:2d}/10: {mock_steps:3d} Schritte")
                time.sleep(1)
            print("\n✅ Simulation erfolgreich")
            return True
        
        try:
            print("👉 JETZT SENSOR BEWEGEN/SCHÜTTELN!")
            print("   (PiTop bewegen, Sensor schütteln, etc.)\n")
            
            input("Bereit? Drücke ENTER zum Starten... ")
            
            self.sensor.reset()
            print("\n🏃 BEWEGUNG STARTEN! (10 Sekunden)\n")
            
            readings = []
            for i in range(10):
                steps = self.sensor.steps
                readings.append(steps)
                
                # Fortschrittsbalke
                bar = "█" * (i + 1) + "░" * (9 - i)
                print(f"[{bar}] Sekunde {i+1:2d}/10: {steps:3d} Schritte", end='\r')
                time.sleep(1)
            
            print("\n")  # Neue Zeile nach Progress-Bar
            
            final_steps = self.sensor.steps
            
            print(f"\n📊 Ergebnis:")
            print(f"   Finale Schritte: {final_steps}")
            print(f"   Verlauf: {readings}")
            
            # Berechne Statistiken
            if len(readings) > 1:
                steps_per_sec = [(readings[i] - readings[i-1]) for i in range(1, len(readings))]
                avg_per_sec = sum(steps_per_sec) / len(steps_per_sec) if steps_per_sec else 0
                max_per_sec = max(steps_per_sec) if steps_per_sec else 0
                
                print(f"\n📈 Statistik:")
                print(f"   Durchschnitt pro Sekunde: {avg_per_sec:.1f}")
                print(f"   Maximum pro Sekunde: {max_per_sec}")
            
            if final_steps > 0:
                print(f"\n✅ Bewegung erkannt - {final_steps} Schritte gezählt!")
                return True
            else:
                print("\n⚠️  Keine Schritte erkannt!")
                print("\n💡 Mögliche Ursachen:")
                print("   - Sensor nicht fest montiert")
                print("   - Zu wenig Bewegung")
                print("   - Schwellwert zu hoch")
                print("   - I2C-Kommunikation gestört")
                
                response = input("\nSensor wurde bewegt? Test trotzdem OK? (j/n): ").lower()
                return response == 'j'
                
        except Exception as e:
            print(f"\n❌ Fehler: {e}")
            return False
    
    def test_continuous_counting(self):
        """Test 5: Kontinuierliche Zählung"""
        print(f"\n{'='*60}")
        print("🔄 Test 5: KONTINUIERLICHE ZÄHLUNG (15 Sekunden)")
        print(f"{'='*60}\n")
        
        if not self.sensor:
            return False
        
        if MOCK_MODE:
            print("⚠️  MOCK: Simuliere kontinuierliche Zählung...\n")
            total = 0
            for i in range(15):
                total += random.randint(0, 5)
                print(f"Sekunde {i+1:2d}/15: {total} Schritte")
                time.sleep(1)
            return True
        
        try:
            print("👉 Bewege Sensor kontinuierlich für 15 Sekunden!")
            print("   Tipp: Gleichmäßige Gehbewegung simulieren\n")
            
            input("Bereit? Drücke ENTER... ")
            
            self.sensor.reset()
            print("\n🏃 LOS GEHT'S!\n")
            
            prev_steps = 0
            step_increments = []
            
            for i in range(15):
                steps = self.sensor.steps
                increment = steps - prev_steps
                step_increments.append(increment)
                prev_steps = steps
                
                # Visualisierung
                bar = "🟢" if increment > 0 else "⚪"
                print(f"[{i+1:2d}/15] {bar} {steps:3d} Schritte (+{increment})")
                time.sleep(1)
            
            final_steps = self.sensor.steps
            
            print(f"\n📊 FINALE STATISTIK:")
            print(f"{'='*60}")
            print(f"   Gesamte Schritte: {final_steps}")
            print(f"   Durchschnitt/Sek: {final_steps/15:.1f}")
            
            # Konsistenz-Check
            active_seconds = sum(1 for x in step_increments if x > 0)
            print(f"   Aktive Sekunden:  {active_seconds}/15")
            
            if active_seconds >= 10:
                consistency = "🟢 Sehr gut"
            elif active_seconds >= 5:
                consistency = "🟡 OK"
            else:
                consistency = "🔴 Schwach"
            
            print(f"   Konsistenz:       {consistency}")
            
            # Geschätzte Distanz & Kalorien
            distance_m = final_steps * 0.8  # ~0.8m pro Schritt
            calories = final_steps * 0.04   # ~0.04 kcal pro Schritt
            
            print(f"\n💪 GESCHÄTZTE AKTIVITÄT:")
            print(f"   Distanz:   ~{distance_m:.1f} m")
            print(f"   Kalorien:  ~{calories:.1f} kcal")
            
            if final_steps >= 10:
                print(f"\n✅ Kontinuierliche Zählung funktioniert!")
                return True
            else:
                print(f"\n⚠️  Nur {final_steps} Schritte - zu wenig Bewegung?")
                response = input("Test trotzdem als OK werten? (j/n): ").lower()
                return response == 'j'
                
        except Exception as e:
            print(f"\n❌ Fehler: {e}")
            return False
    
    def test_calibration(self):
        """Test 6: Kalibrierungs-Test"""
        print(f"\n{'='*60}")
        print("🎯 Test 6: KALIBRIERUNG (Optional)")
        print(f"{'='*60}\n")
        
        if MOCK_MODE:
            print("⚠️  MOCK: Überspringe Kalibrierung")
            return True
        
        print("📝 Kalibrierungs-Test:")
        print("   Laufe genau 10 Schritte und zähle mit!\n")
        
        response = input("Kalibrierung durchführen? (j/n): ").lower()
        if response != 'j':
            print("⏭️  Übersprungen")
            return True
        
        try:
            input("\nBereit? ENTER drücken und GENAU 10 Schritte laufen... ")
            
            self.sensor.reset()
            print("\n👣 LOS! Zähle laut mit: 1, 2, 3, ...")
            
            # Warte 15 Sekunden für 10 Schritte
            time.sleep(15)
            
            measured_steps = self.sensor.steps
            
            print(f"\n📊 Kalibrierungs-Ergebnis:")
            print(f"   Erwartete Schritte: 10")
            print(f"   Gemessene Schritte: {measured_steps}")
            print(f"   Differenz: {abs(10 - measured_steps)}")
            
            accuracy = (measured_steps / 10.0 * 100) if measured_steps > 0 else 0
            print(f"   Genauigkeit: {accuracy:.1f}%")
            
            if 8 <= measured_steps <= 12:  # ±2 Schritte Toleranz
                print("\n✅ Kalibrierung gut - Sensor arbeitet genau!")
                return True
            else:
                print(f"\n⚠️  Abweichung zu groß - möglicherweise Justierung nötig")
                print("\n💡 Tipps zur Verbesserung:")
                print("   - Sensor fest montieren")
                print("   - Deutliche Schrittbewegung")
                print("   - Sensor-Ausrichtung prüfen")
                return False
                
        except Exception as e:
            print(f"\n❌ Fehler: {e}")
            return False
    
    def run_all_tests(self):
        """Führt alle Tests durch"""
        print("\n" + "="*60)
        print("🚀 STEP COUNTER TEST SUITE")
        print("="*60)
        print(f"\nModus: {'🔶 MOCK (Simulation)' if MOCK_MODE else '🟢 REAL (Hardware)'}")
        
        tests = [
            ("Initialisierung", self.test_initialization),
            ("Reset-Funktion", self.test_reset),
            ("Statische Messung", self.test_static_reading),
            ("Bewegungserkennung", self.test_movement_detection),
            ("Kontinuierliche Zählung", self.test_continuous_counting),
            ("Kalibrierung", self.test_calibration),
        ]
        
        results = {}
        
        for name, test_func in tests:
            results[name] = test_func()
            
            # Bei Fehler fragen ob weiter
            if not results[name] and not MOCK_MODE:
                print(f"\n⚠️  Test '{name}' fehlgeschlagen!")
                response = input("⏭️  Weiter mit nächstem Test? (Enter) oder Abbruch (q): ")
                if response.lower() == 'q':
                    break
        
        # ZUSAMMENFASSUNG
        print("\n" + "="*60)
        print("📊 TEST-ZUSAMMENFASSUNG")
        print("="*60)
        
        for name, result in results.items():
            status = "✅ WORKS" if result else "❌ WORKS NOT"
            print(f"{name:<30} {status}")
        
        print("="*60)
        
        # Gesamt-Erfolgsrate
        total = len(results)
        passed = sum(results.values())
        percentage = (passed / total * 100) if total > 0 else 0
        
        print(f"\n🎯 Erfolgsquote: {passed}/{total} ({percentage:.0f}%)")
        
        if passed == total:
            print("🎉 ALLE TESTS BESTANDEN!\n")
        elif passed >= total * 0.7:
            print("👍 MEISTE TESTS BESTANDEN - System funktionsfähig\n")
        else:
            print("⚠️  ZU VIELE FEHLER - Hardware prüfen!\n")
        
        return all(results.values())

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🏃 STEP COUNTER HARDWARE TEST")
    print("="*60)
    
    if MOCK_MODE:
        print("\n⚠️  MOCK MODE AKTIV")
        print("   - Keine echte Hardware nötig")
        print("   - Alle Tests werden simuliert")
        print("   - Für echte Tests: Grove Library installieren\n")
    else:
        print("\n✅ REAL MODE")
        print("   - BMA400 muss an I2C-1 Port angeschlossen sein")
        print("   - I2C muss aktiviert sein (raspi-config)")
        print("   - Sensor fest montieren für genaue Messung\n")
    
    input("Bereit? ENTER drücken zum Starten...\n")
    
    tester = StepCounterTester()
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)