#!/usr/bin/env python3
"""
🧪 Step Counter Test - 10 Minuten kontinuierliche Überwachung
Testet: BMA400/IMU Schrittzähler, Bewegungserkennung, Discord-Benachrichtigung
"""
import os
import sys

# ⚠️ DEVICE_OVERRIDE MUSS VOR allen anderen Imports stehen!
if '--device=' not in ' '.join(sys.argv):
    os.environ['DEVICE_OVERRIDE'] = 'pitop1'  # Default für diesen Test

import time
from datetime import datetime

# Importiere den StepCounter
try:
    from hardware import StepCounter
except ImportError:
    # Fallback: Direkter Import
    from step_counter import StepCounter

# Discord Service
try:
    from services.notification_service import NotificationService
    DISCORD_AVAILABLE = True
except ImportError:
    DISCORD_AVAILABLE = False
    print("⚠️  NotificationService nicht verfügbar")


class StepCounterTest:
    def __init__(self):
        print("\n" + "="*60)
        print("🧪 STEP COUNTER TEST - 10 Minuten (Pause-Simulation)")
        print("="*60)
        
        # Hardware
        self.step_counter = StepCounter()
        
        # Services
        if DISCORD_AVAILABLE:
            self.notify = NotificationService()
        else:
            self.notify = None
        
        # State
        self.test_start = time.time()
        self.test_duration = 600  # 10 Minuten (= Pausendauer)
        self.readings = []
        self.last_step_count = 0
        self.steps_per_interval = []
        
        # Pause-Statistiken (für Discord)
        self.pause_start_time = None
        self.pause_end_time = None
        
        print(f"📡 Sensor-Typ: {self.step_counter.sensor_type or 'Dummy'}")
        if self.notify and self.notify.is_enabled:
            print(f"📱 Discord: Aktiviert ✅")
        else:
            print(f"📱 Discord: Nicht verfügbar ⚠️")
        print("✅ Test-Komponenten initialisiert\n")
    
    def run_test(self):
        """Führt 10-Minuten Test durch (simuliert Pause)"""
        
        print("🚀 TEST GESTARTET - Simuliert 10-Minuten Pause")
        print(f"⏱️  Dauer: {self.test_duration // 60} Minuten")
        print(f"📊 Messintervall: 2 Sekunden")
        print(f"🚶 Bewegung: Gehe mit dem Gerät, um Schritte zu zählen")
        print(f"📱 Discord: Sendet break_stats am Ende")
        print(f"📈 Anzeige: Echtzeit-Schrittzählung\n")
        
        print("=" * 70)
        print(f"{'Zeit':<10} | {'Gesamt':<10} | {'Δ Schritte':<12} | {'Rate/min':<10} | {'Status'}")
        print("=" * 70)
        
        # Step Counter starten
        self.step_counter.start()
        self.last_step_count = 0
        self.pause_start_time = datetime.now()
        
        try:
            while time.time() - self.test_start < self.test_duration:
                elapsed = int(time.time() - self.test_start)
                remaining = self.test_duration - elapsed
                
                # Schritte lesen
                self._read_steps(elapsed)
                
                # Fortschritt alle 10 Messungen
                if elapsed % 20 == 0:
                    mins, secs = divmod(remaining, 60)
                    print(f"\n⏱️  Verbleibend: {mins:02d}:{secs:02d} | 💡 Tipp: Bewege das Gerät!\n")
                
                # 2 Sekunden warten
                time.sleep(2)
            
            print("\n\n" + "="*60)
            print("✅ TEST ABGESCHLOSSEN")
            print("="*60)
            
            # Stoppen und finale Schritte holen
            self.pause_end_time = datetime.now()
            final_steps = self.step_counter.stop()
            
            # Discord-Nachricht senden
            self._send_discord_stats(final_steps)
            
            self._print_summary(final_steps)
        
        except KeyboardInterrupt:
            print("\n\n⚠️  Test abgebrochen!")
            self.pause_end_time = datetime.now()
            final_steps = self.step_counter.stop()
            
            # Auch bei Abbruch Discord senden
            self._send_discord_stats(final_steps, aborted=True)
            
            self._print_summary(final_steps)
            self._cleanup()
    
    def _read_steps(self, elapsed_seconds):
        """Liest Schritte und zeigt Status"""
        
        current_steps = self.step_counter.read()
        delta = current_steps - self.last_step_count
        
        # Rate berechnen (Schritte pro Minute)
        if elapsed_seconds > 0:
            rate = (current_steps / elapsed_seconds) * 60
        else:
            rate = 0
        
        # Zeitstempel
        now = datetime.now().strftime("%H:%M:%S")
        
        # Status bestimmen
        if delta > 5:
            status = "🏃 RUNNING"
        elif delta > 2:
            status = "🚶 WALKING"
        elif delta > 0:
            status = "🚶‍♂️ SLOW"
        else:
            status = "🧍 STILL"
        
        # Ausgabe
        print(f"{now}   | {current_steps:<10} | +{delta:<11} | {rate:<10.1f} | {status}")
        
        # Speichern
        self.readings.append({
            'time': elapsed_seconds,
            'total': current_steps,
            'delta': delta,
            'rate': rate
        })
        
        if delta > 0:
            self.steps_per_interval.append(delta)
        
        self.last_step_count = current_steps
    
    def _send_discord_stats(self, steps, aborted=False):
        """Sendet Pause-Statistiken an Discord"""
        
        if not self.notify or not self.notify.is_enabled:
            print("\n📱 Discord: Übersprungen (nicht konfiguriert)")
            return
        
        # Pausendauer berechnen
        if self.pause_start_time and self.pause_end_time:
            duration = self.pause_end_time - self.pause_start_time
            duration_minutes = int(duration.total_seconds() // 60)
            duration_seconds = int(duration.total_seconds() % 60)
        else:
            duration_minutes = self.test_duration // 60
            duration_seconds = 0
        
        # Durchschnittliche Rate
        total_seconds = duration_minutes * 60 + duration_seconds
        if total_seconds > 0:
            steps_per_minute = steps / (total_seconds / 60)
        else:
            steps_per_minute = 0
        
        # Aktivitäts-Level bestimmen
        if steps == 0:
            activity_level = "😴 Keine Bewegung"
            activity_emoji = "😴"
        elif steps < 50:
            activity_level = "🧘 Wenig aktiv"
            activity_emoji = "🧘"
        elif steps < 200:
            activity_level = "🚶 Moderat aktiv"
            activity_emoji = "🚶"
        elif steps < 500:
            activity_level = "🏃 Aktiv"
            activity_emoji = "🏃"
        else:
            activity_level = "🏆 Sehr aktiv!"
            activity_emoji = "🏆"
        
        print(f"\n📱 Sende Discord-Nachricht...")
        
        try:
            # Versuche break_stats zu senden
            self.notify.send_break_stats(
                steps=steps,
                duration_minutes=duration_minutes,
                duration_seconds=duration_seconds,
                steps_per_minute=round(steps_per_minute, 1),
                activity_level=activity_level,
                activity_emoji=activity_emoji,
                aborted=aborted
            )
            print(f"✅ Discord: break_stats gesendet!")
            print(f"   🚶 Schritte: {steps}")
            print(f"   ⏱️  Dauer: {duration_minutes}:{duration_seconds:02d}")
            print(f"   📈 Rate: {steps_per_minute:.1f}/min")
            print(f"   {activity_level}")
        
        except AttributeError:
            # Fallback: Manuelle Nachricht
            print("⚠️  send_break_stats() nicht gefunden, sende manuell...")
            self._send_manual_discord(steps, duration_minutes, duration_seconds, 
                                      steps_per_minute, activity_level, aborted)
        
        except Exception as e:
            print(f"❌ Discord-Fehler: {e}")
    
    def _send_manual_discord(self, steps, duration_min, duration_sec, rate, activity, aborted):
        """Fallback: Manuelle Discord-Nachricht"""
        
        status = "⚠️ Abgebrochen" if aborted else "✅ Abgeschlossen"
        
        message = f"""
**🧪 Step Counter Test {status}**

**📊 Pause-Statistiken:**
🚶 Schritte: {steps}
⏱️ Dauer: {duration_min}:{duration_sec:02d} min
📈 Rate: {rate:.1f} Schritte/min
🎯 Aktivität: {activity}


**💡 Bewertung:**
{"Gut gemacht! Bewegung während der Pause ist wichtig! 💪" if steps > 50 else "Tipp: Versuche dich mehr zu bewegen! 🚶"}
"""
        
        try:
            # Versuche generische send-Methode
            if hasattr(self.notify, 'send'):
                self.notify.send(message)
                print("✅ Manuelle Discord-Nachricht gesendet")
            elif hasattr(self.notify, 'send_message'):
                self.notify.send_message(message)
                print("✅ Manuelle Discord-Nachricht gesendet")
            else:
                print("⚠️  Keine passende Discord-Methode gefunden")
        except Exception as e:
            print(f"❌ Manueller Discord-Fehler: {e}")
    
    def _print_summary(self, final_steps):
        """Gibt Test-Zusammenfassung aus"""
        
        if self.pause_start_time and self.pause_end_time:
            duration = self.pause_end_time - self.pause_start_time
            duration_mins = duration.total_seconds() / 60
        else:
            duration_mins = self.test_duration / 60
        
        avg_rate = (final_steps / duration_mins) if duration_mins > 0 else 0
        
        print("\n📊 TEST ZUSAMMENFASSUNG:")
        print(f"   ⏱️  Testdauer: {int(duration_mins)} Minuten")
        print(f"   📡 Sensor: {self.step_counter.sensor_type or 'Dummy'}")
        print(f"   🚶 Gesamtschritte: {final_steps}")
        print(f"   📈 Durchschnitt: {avg_rate:.1f} Schritte/Minute")
        
        if self.steps_per_interval:
            max_delta = max(self.steps_per_interval)
            print(f"   🏃 Max. Schritte/Intervall: {max_delta}")
        
        # Aktivitäts-Bewertung
        print("\n🎯 AKTIVITÄTS-BEWERTUNG:")
        if final_steps == 0:
            print("   ⚠️  Keine Schritte erkannt")
            print("   💡 Prüfe: Ist der Sensor korrekt verbunden?")
            print("   💡 Prüfe: Wurde das Gerät bewegt?")
        elif final_steps < 50:
            print("   😴 Wenig Aktivität")
        elif final_steps < 200:
            print("   🚶 Moderate Aktivität")
        elif final_steps < 500:
            print("   🏃 Gute Aktivität!")
        else:
            print("   🏆 Sehr aktiv! Toll gemacht!")
        
        # Hardware-Status
        print("\n🔧 HARDWARE STATUS:")
        if self.step_counter.sensor_type == "BMA400":
            print("   ✅ BMA400 Hardware-Schrittzähler: Funktioniert")
        elif self.step_counter.sensor_type == "IMU":
            print("   ⚠️  IMU Software-Schrittzähler: Aktiv (Fallback)")
            print("   💡 BMA400 wäre genauer - prüfe Verfügbarkeit")
        else:
            print("   ❌ Kein Sensor: Dummy-Modus aktiv")
        
        # Discord Status
        print("\n📱 DISCORD STATUS:")
        if self.notify and self.notify.is_enabled:
            print("   ✅ break_stats wurde gesendet")
        else:
            print("   ⚠️  Discord nicht konfiguriert")
        
        print("\n💡 TEST-TIPPS:")
        print("   1. Ruhig halten → Keine Schritte")
        print("   2. Langsam gehen → 1-2 Schritte/Sekunde")
        print("   3. Schnell gehen → 2-3 Schritte/Sekunde")
        print("   4. Auf/Ab bewegen → Simuliert Schritte")
        
        print("\n")
    
    def _cleanup(self):
        """Cleanup"""
        print("\n🛑 Cleanup...")
        try:
            self.step_counter.stop()
        except:
            pass
        print("✅ Test beendet\n")


def quick_test():
    """Schnelltest (1 Minute) mit Discord"""
    print("\n🧪 QUICK TEST - 1 Minute")
    print("="*40)
    
    counter = StepCounter()
    
    # Discord
    notify = None
    if DISCORD_AVAILABLE:
        notify = NotificationService()
    
    counter.start()
    start_time = datetime.now()
    
    print("🚶 Bewege das Gerät für 60 Sekunden...")
    print("   Aktueller Stand wird alle 5 Sekunden angezeigt\n")
    
    for i in range(12):  # 12 x 5 Sekunden = 60 Sekunden
        time.sleep(5)
        steps = counter.read()
        print(f"   [{(i+1)*5:2d}s] Schritte: {steps}")
    
    end_time = datetime.now()
    final = counter.stop()
    
    print(f"\n✅ Ergebnis: {final} Schritte in 1 Minute")
    print(f"📈 Rate: {final} Schritte/Minute")
    
    # Discord senden
    if notify and notify.is_enabled:
        print(f"\n📱 Sende Discord-Nachricht...")
        try:
            notify.send_break_stats(
                steps=final,
                duration_minutes=1,
                duration_seconds=0,
                steps_per_minute=final,
                activity_level="🧪 Quick Test",
                activity_emoji="🧪",
                aborted=False
            )
            print("✅ Discord gesendet!")
        except Exception as e:
            print(f"⚠️  Discord-Fehler: {e}")
    
    print("\n")


if __name__ == "__main__":
    print("\n🧪 Step Counter Test")
    print("=" * 40)
    
    # Argumente prüfen
    if len(sys.argv) > 1 and sys.argv[1] == '--quick':
        quick_test()
    else:
        print("⚠️  Drücke STRG+C zum Abbrechen")
        print("💡 Tipp: Nutze --quick für 1-Minuten-Test\n")
        
        test = StepCounterTest()
        
        try:
            test.run_test()
        except KeyboardInterrupt:
            test._cleanup()
        finally:
            test._cleanup()