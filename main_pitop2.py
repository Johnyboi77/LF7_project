#!/usr/bin/env python3
"""
pi-top 2 - Pausenstation mit Schrittzähler
AUTOMATISCHER StepCounter-Start via Datenbank-Polling
"""

import signal
import sys
import time
from datetime import datetime
from threading import Thread, Event

import config
from hardware.step_counter import StepCounter
from services.notification_service import NotificationService
from database.supabase_manager import SupabaseManager


class BreakStation:
    def __init__(self):
        print("\n" + "="*60)
        print("☕ BREAK STATION - pi-top 2")
        print("="*60)
        
        # Hardware (NUR Schrittzähler)
        self.steps = StepCounter()
        
        # Services
        self.notify = NotificationService()
        self.db = SupabaseManager()
        
        # State
        self.state = "IDLE"  # IDLE → BREAK → IDLE
        self.session_id = None
        self.pause_number = 0
        self.pause_start_time = None
        self.user_name = "User"
        
        # Polling
        self.polling_active = True
        self.polling_thread = None
        self.last_session_id = None
        
        print(f"✅ Initialisierung abgeschlossen\n")
    
    # ===== POLLING (Kontinuierliche DB-Abfrage) =====
    
    def start_polling(self):
        """🔄 Startet Polling-Thread (kontinuierliche DB-Abfrage)"""
        
        print("⏳ Starte Datenbank-Polling...")
        print("   → Suche nach timer_status='break' alle 1 Sekunde\n")
        
        self.polling_thread = Thread(target=self._polling_loop, daemon=True)
        self.polling_thread.start()
    
    def _polling_loop(self):
        """🔄 Polling-Hauptschleife (läuft in separatem Thread)"""
        
        poll_interval = 1  # Jede Sekunde checken
        
        while self.polling_active:
            try:
                if not self.db.client:
                    time.sleep(poll_interval)
                    continue
                
                # Hole letzte Session
                result = self.db.client.table('sessions')\
                    .select('session_id, pause_count, user_name, timer_status')\
                    .order('start_time', desc=True)\
                    .limit(1)\
                    .execute()
                
                if not result.data:
                    time.sleep(poll_interval)
                    continue
                
                session = result.data[0]
                session_id = session['session_id']
                status = session.get('timer_status', 'idle')
                
                # ===== BREAK SIGNAL ERKANNT =====
                if status == 'break' and session_id != self.last_session_id:
                    self.last_session_id = session_id
                    
                    # Neue Session mit Break-Status
                    self.session_id = session_id
                    self.pause_number = session.get('pause_count', 0)
                    self.user_name = session.get('user_name', 'User')
                    
                    print(f"\n✅ BREAK-SIGNAL ERKANNT!")
                    print(f"   Session: {session_id[:8]}...")
                    print(f"   Status: {status}")
                    print(f"   User: {self.user_name}")
                    print(f"   Pause #{self.pause_number}\n")
                    
                    # Starte Break sofort
                    self._start_break(self.user_name)
                    
                    # Danach wieder warten
                    self.last_session_id = None
                
                # ===== WORK_READY (Break vorbei) =====
                elif status == 'work_ready' and session_id == self.last_session_id:
                    # Wurde bereits durch _end_break() abgehandelt
                    pass
                
                time.sleep(poll_interval)
            
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"⚠️  Polling Fehler: {e}")
                time.sleep(poll_interval)
    
    # ===== BREAK SESSION =====
    
    def _start_break(self, user_name):
        """☕ Startet Break-Phase (10 Min)"""
        
        print("="*60)
        print(f"☕ PAUSE #{self.pause_number} GESTARTET")
        print("="*60)
        print(f"\n👤 User: {user_name}")
        print(f"⏱️  Dauer: {config.BREAK_DURATION // 60} Minuten")
        print(f"👣 Schrittzähler aktiv\n")
        
        self.state = "BREAK"
        self.pause_start_time = time.time()
        
        # ===== SCHRITTZÄHLER STARTEN (AUTOMATISCH) =====
        print("🎯 Starte StepCounter AUTOMATISCH...\n")
        self.steps.start()
        
        # 10 Minuten Timer
        break_duration = config.BREAK_DURATION
        start_time = time.time()
        
        try:
            while time.time() - start_time < break_duration:
                elapsed = time.time() - start_time
                remaining = break_duration - elapsed
                
                mins, secs = divmod(int(remaining), 60)
                steps = self.steps.read()
                
                print(f"\r⏱️  {mins:02d}:{secs:02d} verbleibend | 👣 {steps:,} Schritte", 
                      end='', flush=True)
                
                time.sleep(1)
            
            print(f"\n\n⏰ PAUSE ABGELAUFEN!")
        
        except KeyboardInterrupt:
            print(f"\n\n⚠️  Pause unterbrochen!")
        
        finally:
            self._end_break(user_name)
    
    def _end_break(self, user_name):
        """☕ Beendet Break und speichert Daten"""
        
        self.state = "IDLE"
        
        # Schrittzähler stoppen
        steps = self.steps.stop()
        
        # Berechne Statistiken
        calories = int(steps * 0.05)  # ~0.05 kcal pro Schritt
        distance = int(steps * 0.75)  # ~0.75m pro Schritt
        
        print("\n" + "="*60)
        print(f"📊 PAUSE #{self.pause_number} STATISTIK")
        print("="*60)
        print(f"\n👣 Schritte:     {steps:,}")
        print(f"🔥 Kalorien:     ~{calories} kcal")
        print(f"📏 Distanz:      ~{distance}m\n")
        
        # In DB speichern
        self._save_break_data(steps, calories, distance)
        
        # Discord Benachrichtigung
        self._send_break_notification(user_name, steps, calories, distance)
        
        # Session Status zurück auf 'ready'
        self._update_session_status('work_ready')
        
        # Schrittzähler zurücksetzen
        self.steps.reset()
        
        print("✅ Break-Daten gespeichert")
        print("✅ Bereit für nächste Pause!\n")
    
    def _save_break_data(self, steps, calories, distance):
        """💾 Speichert Break-Daten in DB"""
        
        if not self.db.client or not self.session_id:
            print("⚠️  Kann Break-Daten nicht speichern (DB nicht verfügbar)")
            return
        
        try:
            data = {
                'session_id': self.session_id,
                'pause_number': self.pause_number,
                'step_count': steps,
                'calories_burned': calories,
                'distance_meters': distance,
                'timestamp': datetime.utcnow().isoformat(),
                'device_id': config.DEVICE_ID
            }
            
            result = self.db.client.table('breakdata').insert(data).execute()
            
            if result.data:
                print("✅ Break-Daten in DB gespeichert")
            else:
                print("⚠️  DB-Insert fehlgeschlagen")
        
        except Exception as e:
            print(f"❌ DB-Fehler: {e}")
    
    def _update_session_status(self, status):
        """📊 Aktualisiert Session-Status in DB"""
        
        if not self.db.client or not self.session_id:
            return
        
        try:
            self.db.client.table('sessions').update({
                'timer_status': status
            }).eq('session_id', self.session_id).execute()
            
            print(f"📊 Session Status: {status}")
        
        except Exception as e:
            print(f"⚠️  Status-Update Fehler: {e}")
    
    def _send_break_notification(self, user_name, steps, calories, distance):
        """📱 Sendet Discord Push nach Break"""
        
        if not self.notify.is_enabled:
            return
        
        from services.discord_message_templates import MessageTemplates
        
        template = MessageTemplates.break_stats(user_name, self.pause_number, steps, calories, distance)
        
        try:
            from requests import post
            
            payload = {
                "embeds": [{
                    "title": template['title'],
                    "description": template['description'],
                    "color": template['color'],
                    "timestamp": datetime.utcnow().isoformat(),
                    "footer": {"text": "Break Station - PiTop 2"}
                }]
            }
            
            response = post(self.notify.webhook_url, json=payload, timeout=5)
            
            if response.status_code == 204:
                print("✅ Discord-Benachrichtigung versendet")
            else:
                print(f"⚠️  Discord Status: {response.status_code}")
        
        except Exception as e:
            print(f"⚠️  Discord-Fehler: {e}")
    
    # ===== MAIN =====
    
    def start(self):
        """Startet Break-Station"""
        
        print("\n" + "="*60)
        print("✅ BREAK STATION AKTIV")
        print("="*60)
        print(f"\n🔧 Device: {config.DEVICE_ID}")
        print(f"📡 Supabase: {'✅' if self.db.client else '❌'}")
        print(f"🤖 Discord: {'✅' if self.notify.is_enabled else '❌'}")
        print(f"📊 Schrittzähler: ✅")
        
        print("\n💡 FUNKTIONSWEISE:")
        print("   1. 🔄 Pollt DB kontinuierlich (jede Sekunde)")
        print("   2. ✅ Erkennt timer_status='break' automatisch")
        print("   3. 🏃 Startet StepCounter SOFORT")
        print("   4. 👣 Zählt Schritte während 10-Min Pause")
        print("   5. 💾 Speichert Daten in DB")
        print("   6. 📱 Sendet Discord-Push")
        print("   7. 🔄 Bereit für nächste Pause")
        
        print("\n📱 DISCORD:")
        if self.notify.is_enabled:
            print("   ✅ Push-Benachrichtigungen aktiviert")
        else:
            print("   ⚠️  Webhook nicht konfiguriert")
        
        print("\n⚡ POLLING:")
        print("   ⏱️  Interval: 1 Sekunde")
        print("   🎯 Reaktionszeit: <1 Sekunde nach DB-Update")
        
        print("\n" + "="*60)
        print("👉 Drücke STRG+C zum Beenden\n")
        
        # Starte Polling-Thread
        self.start_polling()
        
        # Halte Hauptprogramm am Leben
        try:
            while True:
                time.sleep(1)
        
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        """Cleanup"""
        
        print("\n\n🛑 Break Station wird gestoppt...")
        
        self.polling_active = False
        
        if self.state == "BREAK":
            self.steps.stop()
        
        if self.polling_thread and self.polling_thread.is_alive():
            self.polling_thread.join(timeout=2)
        
        print("✅ Cleanup abgeschlossen\n")


def signal_handler(sig, frame):
    """STRG+C Handler"""
    if 'station' in globals():
        station.stop()
    sys.exit(0)


if __name__ == "__main__":
    station = BreakStation()
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        station.start()
    except KeyboardInterrupt:
        station.stop()
        sys.exit(0)