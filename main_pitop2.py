"""
🚶 BREAK STATION - pi-top 2
Pausensystem: Schrittzähler, Break-Tracking
Pausenphase: 10 Min | Holt CO2-Daten aus DB
"""

import os
import sys

# DEVICE_OVERRIDE MUSS VOR allen anderen Imports stehen!
if '--device=' not in ' '.join(sys.argv):
    os.environ['DEVICE_OVERRIDE'] = 'pitop2'

import signal
import time
from datetime import datetime
from threading import Thread
import config
from hardware import StepCounter
from services.discord_templates import NotificationService
from database.supabase_manager import SupabaseManager

# ═══════════════════════════════════════════════════════════════
# TIMER KONFIGURATION
# ═══════════════════════════════════════════════════════════════
BREAK_DURATION = 10 * 60     # 10 Minuten (600 Sekunden)


class BreakStation:
    def __init__(self):
        print("\n" + "="*60)
        print("🚶 BREAK STATION - pi-top 2")
        print("="*60)
        print(f"   Pausenphase: {BREAK_DURATION // 60} Minuten")
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
        
        # Break kann von außen abgebrochen werden
        self.break_cancelled = False
        
        print(f"✅ Initialisierung abgeschlossen\n")
    
    # ═══════════════════════════════════════════════════════════════
    # POLLING
    # ═══════════════════════════════════════════════════════════════
    
    def start_polling(self):
        print("⏳ Starte Datenbank-Polling...")
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
                    self.pause_number = session.get('pause_count', 0) + 1
                    self.user_name = session.get('user_name', 'User')
                    
                    print(f"\n✅ BREAK-SIGNAL ERKANNT!")
                    print(f"   Session: {session_id[:8]}...")
                    print(f"   User: {self.user_name}")
                    print(f"   Pause #{self.pause_number}\n")
                    
                    self._start_break(self.user_name)
                    
                    self.last_session_id = None
                
                # SESSION BEENDET - Reset
                elif status in ['ended', 'cancelled']:
                    if self.state == "BREAK":
                        print("\n⚠️ Session wurde von PiTop 1 beendet!")
                        self.break_cancelled = True
                    self.last_session_id = None
                
                time.sleep(poll_interval)
            
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"⚠️ Polling Fehler: {e}")
                time.sleep(poll_interval)
    
    # ═══════════════════════════════════════════════════════════════
    # CO2 DATA FROM DB
    # ═══════════════════════════════════════════════════════════════
    
    def _get_co2_stats(self):
        """🌡️ Holt CO2-Statistiken aus der Datenbank"""
        if not self.db.client or not self.session_id:
            return None
        
        try:
            result = self.db.client.table('co2_measurements')\
                .select('co2_level, tvoc_level, is_alarm')\
                .eq('session_id', self.session_id)\
                .execute()
            
            if not result.data:
                print("ℹ️  Keine CO2-Daten gefunden")
                return None
            
            co2_values = [row['co2_level'] for row in result.data if row['co2_level']]
            tvoc_values = [row['tvoc_level'] for row in result.data if row.get('tvoc_level')]
            alarm_count = sum(1 for row in result.data if row.get('is_alarm'))
            
            if not co2_values:
                return None
            
            stats = {
                'avg_co2': int(sum(co2_values) / len(co2_values)),
                'min_co2': min(co2_values),
                'max_co2': max(co2_values),
                'avg_tvoc': int(sum(tvoc_values) / len(tvoc_values)) if tvoc_values else 0,
                'alarm_count': alarm_count,
                'measurement_count': len(co2_values)
            }
            
            print(f"📊 CO2-Daten geladen: {len(co2_values)} Messungen")
            return stats
        
        except Exception as e:
            print(f"⚠️ CO2-Daten Fehler: {e}")
            return None
    
    # ═══════════════════════════════════════════════════════════════
    # BREAK SESSION
    # ═══════════════════════════════════════════════════════════════
    
    def _start_break(self, user_name):
        print("="*60)
        print(f"☕ PAUSE #{self.pause_number} GESTARTET ({BREAK_DURATION // 60} Min)")
        print("="*60)
        print(f"\n👤 User: {user_name}")
        print(f"⏱️  Dauer: {BREAK_DURATION // 60} Minuten")
        print(f"👣 Schrittzähler aktiv\n")
        
        self.state = "BREAK"
        self.break_cancelled = False
        self.pause_start_time = time.time()
        
        # Schrittzähler starten
        print("🎯 Starte Schrittzähler...\n")
        self.steps.start()
        
        # 10 Minuten Timer
        start_time = time.time()
        
        try:
            while time.time() - start_time < BREAK_DURATION:
                # Check ob Break von PiTop 1 abgebrochen wurde
                if self.break_cancelled:
                    print("\n\n⚠️ Break wurde extern abgebrochen!")
                    break
                
                elapsed = time.time() - start_time
                remaining = BREAK_DURATION - elapsed
                
                steps = self.steps.read()
                
                # Fortschritt anzeigen
                remaining_min = int(remaining // 60)
                remaining_sec = int(remaining % 60)
                print(f"\r⏱️ {remaining_min:02d}:{remaining_sec:02d} verbleibend | 👣 {steps:,} Schritte", 
                      end='', flush=True)
                
                time.sleep(1)
            
            if not self.break_cancelled:
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
        calories = int(steps * config.CALORIES_PER_STEP)
        distance = int(steps * config.METERS_PER_STEP)
        
        # CO2-Daten aus DB holen
        co2_stats = self._get_co2_stats()
        
        print("\n" + "="*60)
        print(f"📊 PAUSE #{self.pause_number} STATISTIK")
        print("="*60)
        print(f"\n👣 Schritte:     {steps:,}")
        print(f"🔥 Kalorien:     ~{calories} kcal")
        print(f"📏 Distanz:      ~{distance}m")
        
        # CO2-Stats anzeigen
        if co2_stats:
            print(f"\n💨 CO2 Durchschnitt: {co2_stats['avg_co2']} ppm")
            print(f"💨 CO2 Min/Max:      {co2_stats['min_co2']}/{co2_stats['max_co2']} ppm")
            if co2_stats['avg_tvoc']:
                print(f"🌿 TVOC Durchschnitt: {co2_stats['avg_tvoc']} ppb")
            if co2_stats['alarm_count'] > 0:
                print(f"⚠️  Alarme:          {co2_stats['alarm_count']}")
        
        print(f"\n💾 Pausenzeit: {BREAK_DURATION}s ({BREAK_DURATION // 60} Min)\n")
        
        # Nur speichern wenn nicht abgebrochen
        if not self.break_cancelled:
            # DB speichern
            self._save_break_data(steps, calories, distance)
            
            # Discord mit CO2-Daten
            self._send_break_notification(user_name, steps, calories, distance, co2_stats)
            
            # Status update
            self._update_session_status('work_ready')
        else:
            print("⚠️ Break wurde abgebrochen - keine Daten gespeichert")
        
        # Reset
        self.steps.reset()
        self.break_cancelled = False
        
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
                'device_id': config.DEVICE_ID,
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
            # Auch pause_count erhöhen
            self.db.client.table('sessions').update({
                'timer_status': status,
                'pause_count': self.pause_number
            }).eq('session_id', self.session_id).execute()
            
            print(f"📊 Session Status: {status}")
        
        except Exception as e:
            print(f"⚠️ Status-Update Fehler: {e}")
    
    def _send_break_notification(self, user_name, steps, calories, distance, co2_stats=None):
        """📱 Discord-Benachrichtigung mit CO2-Daten"""
        if not self.notify.is_enabled:
            return
        
        try:
            from requests import post
            
            description = f"""
👤 **User:** {user_name}
⏱️ **Pause:** #{self.pause_number} ({BREAK_DURATION // 60} Min)

**🏃 Bewegung:**
👣 Schritte: **{steps:,}**
🔥 Kalorien: ~{calories} kcal
📏 Distanz: ~{distance}m
"""
            
            if co2_stats:
                description += f"""
**💨 Luftqualität:**
📊 CO2 Ø: **{co2_stats['avg_co2']} ppm**
📉 Min: {co2_stats['min_co2']} ppm | 📈 Max: {co2_stats['max_co2']} ppm
"""
                if co2_stats['avg_tvoc']:
                    description += f"🌿 TVOC Ø: {co2_stats['avg_tvoc']} ppb\n"
                
                if co2_stats['alarm_count'] > 0:
                    description += f"⚠️ **{co2_stats['alarm_count']} Luftqualitäts-Alarm(e)**\n"
                
                avg_co2 = co2_stats['avg_co2']
                if avg_co2 < 600:
                    description += "\n✅ **Luftqualität: Sehr gut!**"
                elif avg_co2 < 800:
                    description += "\n🟡 **Luftqualität: Okay**"
                else:
                    description += "\n🔴 **Luftqualität: Lüften empfohlen!**"
            
            color = 0x00FF00
            if co2_stats:
                if co2_stats['avg_co2'] >= 800:
                    color = 0xFF0000
                elif co2_stats['avg_co2'] >= 600:
                    color = 0xFFAA00
            
            payload = {
                "embeds": [{
                    "title": f"☕ Pause #{self.pause_number} beendet!",
                    "description": description,
                    "color": color,
                    "timestamp": datetime.utcnow().isoformat(),
                    "footer": {"text": "Break Station - PiTop 2"}
                }]
            }
            
            response = post(self.notify.webhook_url, json=payload, timeout=5)
            
            if response.status_code == 204:
                print("✅ Discord-Benachrichtigung versendet")
        
        except Exception as e:
            print(f"⚠️ Discord-Fehler: {e}")
    
    # ═══════════════════════════════════════════════════════════════
    # MAIN
    # ═══════════════════════════════════════════════════════════════
    
    def start(self):
        print("\n" + "="*60)
        print("✅ BREAK STATION AKTIV")
        print("="*60)
        print(f"\n🔧 Device: {config.DEVICE_ID}")
        print(f"📡 Supabase: {'✅' if self.db.client else '❌'}")
        print(f"🤖 Discord: {'✅' if self.notify.is_enabled else '❌'}")
        print(f"📊 Schrittzähler: ✅")
        
        print(f"\n⏱️ TIMER-EINSTELLUNGEN:")
        print(f"   Pausenphase: {BREAK_DURATION // 60} Minuten")
        print(f"   💨 CO2-Daten: Werden aus DB geladen")
        
        print("\n💡 FUNKTIONSWEISE:")
        print("   1. 🔄 Pollt DB (jede Sekunde)")
        print("   2. ✅ Erkennt timer_status='break'")
        print("   3. 🏃 Startet Schrittzähler")
        print(f"   4. ⏱️ Läuft {BREAK_DURATION // 60} Minuten")
        print("   5. 💨 Holt CO2-Daten aus DB")
        print("   6. 💾 Speichert Break-Daten")
        print("   7. 📱 Sendet Discord (mit CO2)")
        
        print("\n⚠️ HINWEIS:")
        print("   PiTop 2 hat KEINE Buttons!")
        print("   Steuerung erfolgt über PiTop 1")
        
        print("\n" + "="*60)
        print("👉 Warte auf Break-Signal von PiTop 1...")
        print("="*60 + "\n")
        
        self.start_polling()
        
        try:
            while True:
                time.sleep(1)
        
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        print("\n\n🛑 Break Station wird gestoppt...")
        
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
    station = BreakStation()
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        station.start()
    except KeyboardInterrupt:
        station.stop()
        sys.exit(0)