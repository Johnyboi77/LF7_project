#!/usr/bin/env python3
"""
PiTop 2 - Pausenstation mit Schrittzähler
KORRIGIERT für deine Hardware-Klassen
"""

import signal
import sys
import time
from datetime import datetime
import config

from database.supabase_manager import SupabaseManager
from hardware.led import LED
from hardware.step_counter import StepCounter
from services.notification_service import NotificationService

class PiTop2BreakStation:
    def __init__(self):
        print("\n" + "="*60)
        print("☕ PITOP 2 - PAUSENSTATION")
        print("="*60 + "\n")
        
        if config.DEVICE_TYPE != "break_station":
            print(f"⚠️  WARNUNG: Hostname '{config.HOSTNAME}' passt nicht zu PiTop 2!")
            print("   Bitte hostname auf 'pitop2' setzen!")
        
        # Datenbank
        self.db = SupabaseManager()
        
        # Hardware
        self.led = LED()
        
        # Schrittzähler - KORRIGIERT: Keine Parameter!
        self.step_counter = StepCounter()
        
        # Services
        self.notification_service = NotificationService()
        
        # State
        self.current_session_id = None
        self.current_pause_id = None
        self.pause_number = 0
        self.pause_active = False
        
        print("✅ Alle Komponenten initialisiert\n")
    
    def wait_for_signal(self):
        """Wartet auf Start-Signal von PiTop 1"""
        print("⏳ Warte auf Signal von PiTop 1...\n")
        
        last_check = None
        
        while True:
            try:
                if not self.db.client:
                    print("\r⚠️  Keine DB-Verbindung", end='', flush=True)
                    time.sleep(5)
                    continue
                
                # Prüfe DB auf aktive Session mit Status 'break'
                result = self.db.client.table('sessions')\
                    .select('*')\
                    .eq('timer_status', 'break')\
                    .order('start_time', desc=True)\
                    .limit(1)\
                    .execute()
                
                if result.data:
                    session = result.data[0]
                    session_id = session['id']
                    
                    # Verhindere Doppel-Start
                    if session_id != last_check:
                        last_check = session_id
                        
                        print(f"\n✅ SIGNAL EMPFANGEN!")
                        print(f"   Session ID: {session_id[:8]}...")
                        
                        self.current_session_id = session_id
                        self.pause_number = session.get('pause_count', 0)
                        
                        # Starte Pause
                        self._start_break()
                        
                        # Nach Pause wieder warten
                        print("\n⏳ Warte auf nächstes Signal...\n")
                        last_check = None  # Reset für nächste Pause
                
                # Status-Anzeige
                print(f"\r⏳ Polling DB... [{datetime.now().strftime('%H:%M:%S')}]", end='', flush=True)
                
                time.sleep(2)
                
            except KeyboardInterrupt:
                raise
            except Exception as e:
                print(f"\n❌ Fehler beim DB-Polling: {e}")
                time.sleep(5)
    
    def _start_break(self):
        """Startet Pausenphase mit Schrittzählung"""
        print("\n" + "="*60)
        print(f"☕ PAUSENPHASE #{self.pause_number} GESTARTET")
        print("="*60)
        print("\n⏱️  Dauer: 10 Minuten")
        print("👣 Schrittzähler aktiv\n")
        
        self.pause_active = True
        
        # LED: Blau = Pause aktiv
        self.led.set_blue()
        
        # Hole Pause-ID aus DB
        if self.db.client:
            try:
                breaks_result = self.db.client.table('breakdata')\
                    .select('*')\
                    .eq('session_id', self.current_session_id)\
                    .eq('pause_number', self.pause_number)\
                    .execute()
                
                if breaks_result.data:
                    self.current_pause_id = breaks_result.data[0]['id']
                    print(f"✅ Pause-ID: {self.current_pause_id[:8]}...")
            except Exception as e:
                print(f"⚠️  DB-Fehler: {e}")
        
        # KORRIGIERT: Setze session_id und pause_id als Attribute
        self.step_counter.session_id = self.current_session_id
        self.step_counter.pause_id = self.current_pause_id
        
        # Schrittzähler starten
        self.step_counter.start_monitoring(interval=config.STEP_MEASURE_INTERVAL)
        
        # 10 Minuten Timer
        start_time = time.time()
        duration = config.BREAK_DURATION
        
        try:
            while time.time() - start_time < duration:
                elapsed = time.time() - start_time
                remaining = duration - elapsed
                
                mins, secs = divmod(int(remaining), 60)
                steps = self.step_counter.total_steps
                
                print(f"\r⏱️  {mins:02d}:{secs:02d} | 👣 {steps} Schritte", end='', flush=True)
                
                time.sleep(1)
            
            print("\n\n⏰ PAUSE BEENDET!")
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Pause unterbrochen!")
        
        finally:
            self._end_break()
    
    def _end_break(self):
        """Beendet Pause und sendet Push"""
        self.pause_active = False
        
        # Schrittzähler stoppen
        self.step_counter.stop_monitoring()
        
        # Finale Statistiken
        steps = self.step_counter.total_steps
        calories = int(steps * config.CALORIES_PER_STEP)
        distance = int(steps * config.METERS_PER_STEP)
        
        print(f"\n📊 PAUSE-STATISTIK:")
        print(f"   👣 Schritte:  {steps}")
        print(f"   🔥 Kalorien:  ~{calories} kcal")
        print(f"   📏 Distanz:   ~{distance}m\n")
        
        # In DB aktualisieren
        if self.db.client and self.current_pause_id:
            try:
                self.db.client.table('breakdata').update({
                    'step_count': steps,
                    'calories_burned': calories,
                    'distance_meters': distance,
                    'end_time': datetime.now().isoformat()
                }).eq('id', self.current_pause_id).execute()
                
                print("✅ Statistiken in DB gespeichert")
            except Exception as e:
                print(f"⚠️  DB-Update Fehler: {e}")
        
        # Discord Push
        if config.NOTIFY_BREAK_END:
            self._send_break_notification(steps, calories, distance)
        
        # Session-Status zurück auf 'ready'
        if self.db.client:
            try:
                self.db.client.table('sessions').update({
                    'timer_status': 'ready'
                }).eq('id', self.current_session_id).execute()
            except:
                pass
        
        # LED aus
        self.led.off()
        
        # Schritte zurücksetzen
        if self.step_counter.sensor:
            self.step_counter.sensor.reset()
        self.step_counter.total_steps = 0
        
        print("✅ Bereit für nächste Arbeitsphase!\n")
    
    def _send_break_notification(self, steps, calories, distance):
        """Sendet Discord Push nach Pause"""
        message = f"""
🔔 **Pause #{self.pause_number} beendet!**

⏱️ Zeit ist um - zurück an die Arbeit! 💪

📊 **Deine Pause-Stats:**
👣 Schritte: **{steps:,}**
🔥 Kalorien: **~{calories} kcal**
📏 Distanz: **~{distance}m**

{self._get_motivation_message(steps)}

Viel Erfolg in der nächsten Arbeitsphase! 🎯
        """
        
        try:
            self.notification_service.send_message(message)
            print("📱 Push-Nachricht gesendet!")
        except Exception as e:
            print(f"⚠️  Push-Nachricht fehlgeschlagen: {e}")
    
    def _get_motivation_message(self, steps):
        """Motivierende Nachricht basierend auf Schritten"""
        if steps >= 1000:
            return "🏆 Wow, super aktive Pause!"
        elif steps >= 500:
            return "💪 Gute Bewegung!"
        elif steps >= 200:
            return "👍 Schön bewegt!"
        elif steps > 0:
            return "🚶 Jeder Schritt zählt!"
        else:
            return "💤 Nächstes Mal etwas mehr Bewegung?"
    
    def start(self):
        """Startet Pausenstation"""
        print("\n" + "="*60)
        print("✅ PITOP 2 LÄUFT!")
        print("="*60)
        print(f"\n🔧 Device: {config.DEVICE_ID}")
        print(f"📡 Verbunden mit Supabase")
        print("\n⏳ Warte auf Signal von PiTop 1...")
        print("\n💡 INFO:")
        print("   - PiTop 2 startet automatisch wenn PiTop 1")
        print("     eine Pause signalisiert")
        print("   - Schritte werden während Pause getrackt")
        print("   - Nach 10 Min: Discord Push + zurück zu PiTop 1")
        print("\n📱 DISCORD:")
        if config.DISCORD_ENABLED:
            print("   - Benachrichtigungen aktiv ✅")
        else:
            print("   - Benachrichtigungen deaktiviert")
        print("="*60)
        print("\n👉 Drücke STRG+C zum Beenden\n")
        
        # Starte Polling-Loop
        self.wait_for_signal()
    
    def stop(self):
        """Cleanup"""
        print("\n\n🛑 Stoppe PiTop 2...")
        
        if self.pause_active:
            self.step_counter.stop_monitoring()
        
        self.led.cleanup()
        
        print("✅ Cleanup abgeschlossen\n")

def signal_handler(sig, frame):
    pitop2.stop()
    sys.exit(0)

if __name__ == "__main__":
    if not config.validate_config():
        sys.exit(1)
    
    pitop2 = PiTop2BreakStation()
    signal.signal(signal.SIGINT, signal_handler)
    
    pitop2.start()