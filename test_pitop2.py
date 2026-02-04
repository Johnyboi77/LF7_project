#!/usr/bin/env python3
"""
🧪 TEST MODE - pi-top 2
Schnelldurchlauf: 10s Pause
DB speichert hochgerechnete Werte (x60)
"""

import os
import sys

# ⚠️ DEVICE_OVERRIDE MUSS VOR allen anderen Imports stehen!
if '--device=' not in ' '.join(sys.argv):
    os.environ['DEVICE_OVERRIDE'] = 'pitop2'  # Default für diesen Test

import signal
import time
from datetime import datetime
from threading import Thread
import config
from hardware import StepCounter
from services.discord_templates import NotificationService
from database.supabase_manager import SupabaseManager

# 🧪 TEST MODE CONFIGURATION
TEST_BREAK_DURATION = 10     # 10 Sekunden (statt 600s)
DB_MULTIPLIER = 60           # Werte x60 für DB


class TestBreakStation:
    def __init__(self):
        print("\n" + "="*60)
        print("🧪 TEST MODE - BREAK STATION - pi-top 2")
        print("="*60)
        print("⚡ Schnelldurchlauf aktiviert!")
        print(f"   Pausenphase: {TEST_BREAK_DURATION}s → DB: {TEST_BREAK_DURATION * DB_MULTIPLIER}s")
        print("="*60 + "\n")
        
        # Hardware
        self.steps = StepCounter()
        
        # Services
        self.notify = NotificationService()
        self.db = SupabaseManager()
        
        # State
        self.state = "IDLE"
        self.session_id = None
        self.pause_number = 0
        self.pause_start_time = None
        self.user_name = "User"
        
        # Polling
        self.polling_active = True
        self.polling_thread = None
        self.last_session_id = None
        
        print(f"✅ Test-Initialisierung abgeschlossen\n")
    
    # ===== POLLING =====
    
    def start_polling(self):
        print("⏳ Starte Datenbank-Polling (TEST)...")
        print("   → Suche nach timer_status='break' alle 1 Sekunde\n")
        
        self.polling_thread = Thread(target=self._polling_loop, daemon=True)
        self.polling_thread.start()
    
    def _polling_loop(self):
        poll_interval = 1
        
        while self.polling_active:
            try:
                if not self.db.client:
                    time.sleep(poll_interval)
                    continue
                
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
                
                # BREAK SIGNAL
                if status == 'break' and session_id != self.last_session_id:
                    self.last_session_id = session_id
                    
                    self.session_id = session_id
                    self.pause_number = session.get('pause_count', 0)
                    self.user_name = session.get('user_name', 'User')
                    
                    print(f"\n✅ BREAK-SIGNAL ERKANNT (TEST)!")
                    print(f"   Session: {session_id[:8]}...")
                    print(f"   User: {self.user_name}")
                    print(f"   Pause #{self.pause_number}\n")
                    
                    self._start_break(self.user_name)
                    
                    self.last_session_id = None
                
                time.sleep(poll_interval)
            
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"⚠️ Polling Fehler: {e}")
                time.sleep(poll_interval)
    
    # ===== BREAK SESSION =====
    
    def _start_break(self, user_name):
        print("="*60)
        print(f"🧪 TEST - PAUSE #{self.pause_number} GESTARTET (10s)")
        print("="*60)
        print(f"\n👤 User: {user_name}")
        print(f"⏱️  Dauer: {TEST_BREAK_DURATION}s (= 10 Min simuliert)")
        print(f"👣 Schrittzähler aktiv\n")
        
        self.state = "BREAK"
        self.pause_start_time = time.time()
        
        # Schrittzähler starten
        print("🎯 Starte StepCounter AUTOMATISCH...\n")
        self.steps.start()
        
        # 10 Sekunden Timer
        start_time = time.time()
        
        try:
            while time.time() - start_time < TEST_BREAK_DURATION:
                elapsed = time.time() - start_time
                remaining = TEST_BREAK_DURATION - elapsed
                
                steps = self.steps.read()
                
                print(f"\r⏱️ {int(remaining)}s verbleibend | 👣 {steps:,} Schritte", 
                      end='', flush=True)
                
                time.sleep(1)
            
            print(f"\n\n⏰ PAUSE ABGELAUFEN!")
        
        except KeyboardInterrupt:
            print(f"\n\n⚠️ Pause unterbrochen!")
        
        finally:
            self._end_break(user_name)
    
    def _end_break(self, user_name):
        self.state = "IDLE"
        
        # Schrittzähler stoppen
        steps = self.steps.stop()
        
        # Statistiken
        calories = int(steps * 0.05)
        distance = int(steps * 0.75)
        
        print("\n" + "="*60)
        print(f"📊 TEST - PAUSE #{self.pause_number} STATISTIK")
        print("="*60)
        print(f"\n👣 Schritte:     {steps:,}")
        print(f"🔥 Kalorien:     ~{calories} kcal")
        print(f"📏 Distanz:      ~{distance}m")
        print(f"\n💾 Echte Zeit: {TEST_BREAK_DURATION}s")
        print(f"💾 DB Zeit: {TEST_BREAK_DURATION * DB_MULTIPLIER}s ({TEST_BREAK_DURATION * DB_MULTIPLIER // 60} Min)\n")
        
        # DB speichern
        self._save_break_data(steps, calories, distance)
        
        # Discord
        self._send_break_notification(user_name, steps, calories, distance)
        
        # Status update
        self._update_session_status('work_ready')
        
        # Reset
        self.steps.reset()
        
        print("✅ Break-Daten gespeichert (TEST)")
        print("✅ Bereit für nächste Pause!\n")
    
    def _save_break_data(self, steps, calories, distance):
        if not self.db.client or not self.session_id:
            print("⚠️ Kann Break-Daten nicht speichern")
            return
        
        try:
            data = {
                'session_id': self.session_id,
                'pause_number': self.pause_number,
                'step_count': steps,
                'calories_burned': calories,
                'distance_meters': distance,
                'device_id': config.DEVICE_ID + "_TEST",
                'created_at': datetime.utcnow().isoformat()
            }
            
            result = self.db.client.table('breakdata').insert(data).execute()
            
            if result.data:
                print("✅ Break-Daten in DB gespeichert")
        
        except Exception as e:
            print(f"❌ DB-Fehler: {e}")
    
    def _update_session_status(self, status):
        if not self.db.client or not self.session_id:
            return
        
        try:
            self.db.client.table('sessions').update({
                'timer_status': status
            }).eq('session_id', self.session_id).execute()
            
            print(f"📊 Session Status: {status}")
        
        except Exception as e:
            print(f"⚠️ Status-Update Fehler: {e}")
    
    def _send_break_notification(self, user_name, steps, calories, distance):
        if not self.notify.is_enabled:
            return
        
        from services.discord_templates import MessageTemplates
        
        template = MessageTemplates.break_stats(user_name, self.pause_number, steps, calories, distance)
        
        try:
            from requests import post
            
            # Füge TEST-Hinweis hinzu
            template['description'] += "\n\n🧪 **TEST MODE** (10s = 10 Min)"
            
            payload = {
                "embeds": [{
                    "title": template['title'],
                    "description": template['description'],
                    "color": template['color'],
                    "timestamp": datetime.utcnow().isoformat(),
                    "footer": {"text": "Break Station - PiTop 2 [TEST]"}
                }]
            }
            
            response = post(self.notify.webhook_url, json=payload, timeout=5)
            
            if response.status_code == 204:
                print("✅ Discord-Benachrichtigung versendet (TEST)")
        
        except Exception as e:
            print(f"⚠️ Discord-Fehler: {e}")
    
    # ===== MAIN =====
    
    def start(self):
        print("\n" + "="*60)
        print("✅ TEST BREAK STATION AKTIV")
        print("="*60)
        print(f"\n🔧 Device: {config.DEVICE_ID}")
        print(f"📡 Supabase: {'✅' if self.db.client else '❌'}")
        print(f"🤖 Discord: {'✅' if self.notify.is_enabled else '❌'}")
        print(f"📊 Schrittzähler: ✅")
        
        print("\n🧪 TEST-MODUS:")
        print(f"   ⚡ Pausenphase: {TEST_BREAK_DURATION}s (statt 10 Min)")
        print(f"   📊 DB Multiplikator: x{DB_MULTIPLIER}")
        print(f"   💾 DB speichert als: {TEST_BREAK_DURATION * DB_MULTIPLIER}s")
        
        print("\n💡 FUNKTIONSWEISE:")
        print("   1. 🔄 Pollt DB (jede Sekunde)")
        print("   2. ✅ Erkennt timer_status='break'")
        print("   3. 🏃 Startet StepCounter")
        print("   4. ⏱️ Läuft 10 Sekunden")
        print("   5. 💾 Speichert Daten (als 10 Min)")
        print("   6. 📱 Sendet Discord")
        
        print("\n" + "="*60)
        print("👉 Warte auf Break-Signal von PiTop 1...\n")
        
        # Starte Polling
        self.start_polling()
        
        try:
            while True:
                time.sleep(1)
        
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        print("\n\n🛑 Test Break Station wird gestoppt...")
        
        self.polling_active = False
        
        if self.state == "BREAK":
            self.steps.stop()
        
        if self.polling_thread and self.polling_thread.is_alive():
            self.polling_thread.join(timeout=2)
        
        print("✅ Cleanup abgeschlossen\n")


def signal_handler(sig, frame):
    if 'station' in globals():
        station.stop()
    sys.exit(0)


if __name__ == "__main__":
    station = TestBreakStation()
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        station.start()
    except KeyboardInterrupt:
        station.stop()
        sys.exit(0)