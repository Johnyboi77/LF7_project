#!/usr/bin/env python3
"""
🧪 Step Counter Test - Minimalistisch

Terminal: Zeit | Schritte | Ping (alle 2s)
Discord: break_stats Template
"""
import os
import sys

# ⚠️ DEVICE_OVERRIDE MUSS VOR allen anderen Imports stehen!
if '--device=' not in ' '.join(sys.argv):
    os.environ['DEVICE_OVERRIDE'] = 'pitop1'

import time
import subprocess
from datetime import datetime
from hardware import StepCounter
from services.discord_templates import NotificationService


class StepCounterTest:
    def __init__(self):
        print("\n" + "="*55)
        print("🧪 STEP COUNTER TEST - 10 Minuten")
        print("="*55)
        
        # Hardware
        self.step_counter = StepCounter()
        
        # Services
        self.notify = NotificationService()
        
        # State
        self.test_start = time.time()
        self.test_duration = 600  # 10 Minuten
        self.pause_start_time = datetime.now()
        
        # Ping-Statistiken
        self.ping_values = []
        self.timeout_count = 0
        
        print(f"📡 Sensor: {self.step_counter.sensor_type or 'Dummy'}")
        print(f"📱 Discord: {'✅' if self.notify.is_enabled else '⚠️'}")
        print("✅ Bereit\n")
    
    def run_test(self):
        """Führt 10-Minuten Test durch"""
        
        print("🚀 START - 10 Minuten, Update alle 2s\n")
        
        # Einfache Tabelle
        print("=" * 55)
        print(f"{'Zeit':<10} | {'Schritte':<10} | {'Ping':<10}")
        print("=" * 55)
        
        # Step Counter starten
        self.step_counter.start()
        
        try:
            while time.time() - self.test_start < self.test_duration:
                # Schritte lesen und anzeigen
                self._update_display()
                
                # 2 Sekunden warten
                time.sleep(2)
            
            print("\n" + "="*55)
            print("✅ TEST ABGESCHLOSSEN")
            print("="*55)
            
            # Stoppen
            final_steps = self.step_counter.stop()
            
            # Discord senden
            self._send_discord(final_steps)
            
            self._print_summary(final_steps)
        
        except KeyboardInterrupt:
            print("\n\n⚠️  Abgebrochen!")
            final_steps = self.step_counter.stop()
            self._send_discord(final_steps, aborted=True)
            self._cleanup()
    
    def _update_display(self):
        """Zeigt aktuelle Werte (Zeit, Schritte, Ping)"""
        
        # Zeit
        now = datetime.now().strftime("%H:%M:%S")
        
        # Schritte
        steps = self.step_counter.read()
        
        # Ping (mit Verbindungsqualität)
        ping = self._check_ping()
        
        # Ping-Statistiken sammeln
        if ping == "Timeout" or ping == "Error":
            self.timeout_count += 1
            ping_display = f"{ping} ⚠️"
        elif ping != "OK":
            # Extrahiere ms-Wert für Warnung und Statistik
            try:
                ms_value = float(ping.replace('ms', ''))
                self.ping_values.append(ms_value)
                
                if ms_value > 200:
                    ping_display = f"{ping} ⚠️"  # Langsam
                elif ms_value > 100:
                    ping_display = f"{ping} ⚡"  # Mittel
                else:
                    ping_display = f"{ping} ✅"  # Gut
            except:
                ping_display = ping
        else:
            ping_display = f"{ping} ✅"
        
        # Zeile ausgeben
        print(f"{now}   | {steps:<10} | {ping_display}")
    
    def _check_ping(self):
        """Prüft Internet-Verbindung und gibt Ping-Zeit in ms zurück"""
        try:
            # Ping zu 8.8.8.8 (Google DNS) - nur 1 Paket, 1s timeout
            result = subprocess.run(
                ['ping', '-c', '1', '-W', '1', '8.8.8.8'],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                timeout=1,
                text=True
            )
            
            if result.returncode == 0:
                # Parse Ping-Zeit aus Output
                # Format: "time=23.4 ms"
                output = result.stdout
                if 'time=' in output:
                    # Extrahiere Zeit zwischen "time=" und " ms"
                    time_start = output.find('time=') + 5
                    time_end = output.find(' ms', time_start)
                    if time_end > time_start:
                        ping_ms = output[time_start:time_end]
                        return f"{float(ping_ms):.1f}ms"
                
                # Fallback wenn Parsing fehlschlägt
                return "OK"
            else:
                return "Timeout"
        except subprocess.TimeoutExpired:
            return "Timeout"
        except Exception:
            return "Error"
    
    def _send_discord(self, steps, aborted=False):
        """Sendet break_stats an Discord"""
        
        if not self.notify.is_enabled:
            print("\n📱 Discord: Übersprungen")
            return
        
        # Dauer berechnen
        pause_end = datetime.now()
        duration = pause_end - self.pause_start_time
        duration_minutes = int(duration.total_seconds() // 60)
        
        # Kalorien und Distanz berechnen
        # Annahme: ~0.04 kcal/Schritt, ~0.7m/Schritt
        calories = int(steps * 0.04)
        distance = int(steps * 0.7)
        
        print(f"\n📱 Sende Discord (break_stats)...")
        
        try:
            # Nutze das break_stats Template
            self.notify.send_break_stats(
                pause_number=1,  # Test = Pause #1
                steps=steps,
                calories=calories,
                distance=distance,
                aborted=aborted
            )
            print(f"✅ Gesendet!")
        except Exception as e:
            print(f"❌ Fehler: {e}")
    
    def _print_summary(self, final_steps):
        """Zusammenfassung"""
        
        duration_mins = self.test_duration // 60
        
        print(f"\n📊 ZUSAMMENFASSUNG:")
        print(f"   ⏱️  {duration_mins} Minuten")
        print(f"   🚶 {final_steps} Schritte")
        print(f"   📈 {final_steps / duration_mins:.1f} Schritte/min")
        
        # Ping-Statistiken
        if self.ping_values:
            avg_ping = sum(self.ping_values) / len(self.ping_values)
            min_ping = min(self.ping_values)
            max_ping = max(self.ping_values)
            
            print(f"\n📡 VERBINDUNG:")
            print(f"   Ø Ping: {avg_ping:.1f}ms")
            print(f"   Min: {min_ping:.1f}ms")
            print(f"   Max: {max_ping:.1f}ms")
            print(f"   Timeouts: {self.timeout_count}")
            
            # Bewertung
            if avg_ping < 100 and self.timeout_count == 0:
                print(f"   ✅ Exzellente Verbindung!")
            elif avg_ping < 200 and self.timeout_count < 5:
                print(f"   ⚡ Gute Verbindung")
            else:
                print(f"   ⚠️  Instabile Verbindung - näher am Router bleiben!")
        else:
            print(f"\n📡 VERBINDUNG: ⚠️  Keine Daten (nur Timeouts: {self.timeout_count})")
        
        print()
    
    def _cleanup(self):
        """Cleanup"""
        print("\n🛑 Cleanup...")
        try:
            self.step_counter.stop()
        except:
            pass
        print("✅ Beendet\n")


if __name__ == "__main__":
    print("\n🧪 Step Counter Test")
    print("⚠️  STRG+C zum Abbrechen\n")
    
    test = StepCounterTest()
    
    try:
        test.run_test()
    except KeyboardInterrupt:
        test._cleanup()
    finally:
        test._cleanup()