#!/usr/bin/env python3
"""
PiTop 1 - Arbeitsstation mit CO2-Überwachung
KORRIGIERT für deine Hardware-Klassen
"""

import signal
import sys
import time
from datetime import datetime
import uuid
import config

from database.supabase_manager import SupabaseManager
from hardware.buzzer import Buzzer
from hardware.led import LED
from hardware.button1 import Button1
from hardware.button2 import Button2
from hardware.Co2_sensor import CO2Sensor
from services.timer_service import TimerService
from services.notification_service import NotificationService

class PiTop1WorkStation:
    def __init__(self):
        print("\n" + "="*60)
        print("🚀 PITOP 1 - ARBEITSSTATION")
        print("="*60 + "\n")
        
        # Prüfe Device Type
        if config.DEVICE_TYPE != "work_station":
            print(f"⚠️  WARNUNG: Hostname '{config.HOSTNAME}' passt nicht zu PiTop 1!")
            print("   Bitte hostname auf 'pitop1' setzen!")
        
        # Datenbank
        self.db = SupabaseManager()
        
        # Hardware
        self.buzzer = Buzzer()
        self.led = LED()
        
        # Services
        self.notification_service = NotificationService()
        
        # Timer Service - KORRIGIERT: nur 2 Parameter
        self.timer = TimerService(
            self.db,
            self.notification_service
        )
        
        # CO2 Sensor - Parameter passen ✅
        self.co2_sensor = CO2Sensor(
            self.buzzer,
            self.led,
            self.notification_service,
            self.db
        )
        
        # Session State
        self.current_session_id = None
        self.session_active = False
        self.pause_count = 0
        self.work_start_time = None
        
        # Buttons - KORRIGIERT: long_press ist session beenden
        self.button1 = Button1(
            pin=config.BUTTON1_PIN,
            short_press_callback=self.on_button1_short,
            double_click_callback=self.on_button1_double,
            long_press_callback=self.on_button1_long  # Das ist Session beenden!
        )
        
        self.button2 = Button2(
            pin=config.BUTTON2_PIN,
            short_press_callback=self.on_button2_cancel,
            long_press_callback=self.on_button2_cancel
        )
        
        print("✅ Alle Komponenten initialisiert\n")
    
    def on_button1_short(self):
        """Button 1 kurz: Arbeitsphase starten/fortsetzen"""
        if not self.session_active:
            self._start_session()
        
        print("\n▶️  ARBEITSPHASE STARTET (30 Min)")
        self.work_start_time = time.time()
        
        # In DB loggen
        if self.db.client:
            try:
                self.db.client.table('button_logs').insert({
                    'session_id': self.current_session_id,
                    'button_number': 1,
                    'action': 'work_start',
                    'timestamp': datetime.now().isoformat()
                }).execute()
            except:
                pass
        
        # Grüne LED an
        self.led.set_green()
        
        # Warte auf Timer-Ende
        self._wait_for_work_timer()
    
    def on_button1_double(self):
        """Button 1 doppelt: Timer Reset"""
        print("\n🔄 Timer Reset")
        self.work_start_time = None
        self.led.off()
        
        if self.db.client:
            try:
                self.db.client.table('button_logs').insert({
                    'session_id': self.current_session_id,
                    'button_number': 1,
                    'action': 'reset',
                    'timestamp': datetime.now().isoformat()
                }).execute()
            except:
                pass
    
    def on_button1_long(self):
        """Button 1 lang (5+s): Session beenden"""
        if self.session_active:
            print("\n🛑 SESSION WIRD BEENDET...")
            self._end_session()
        else:
            print("\n⚠️  Keine aktive Session!")
    
    def on_button2_cancel(self):
        """Button 2: Letzte Pause stornieren"""
        if self.session_active and self.pause_count > 0:
            print(f"\n↩️  STORNIERE letzte Pause (#{self.pause_count})")
            
            if self.db.client:
                try:
                    # Hole letzte Pause
                    breaks_result = self.db.client.table('breakdata')\
                        .select('*')\
                        .eq('session_id', self.current_session_id)\
                        .order('pause_number', desc=True)\
                        .limit(1)\
                        .execute()
                    
                    if breaks_result.data:
                        last_break = breaks_result.data[0]
                        # Als storniert markieren
                        self.db.client.table('breakdata')\
                            .update({
                                'cancelled': True,
                                'cancelled_at': datetime.now().isoformat()
                            })\
                            .eq('id', last_break['id'])\
                            .execute()
                        
                        print("✅ Pause in DB storniert")
                except Exception as e:
                    print(f"⚠️  DB-Fehler: {e}")
            
            self.pause_count -= 1
            print("✅ Pause storniert, Timer kann neu gestartet werden")
        else:
            print("\n⚠️  Keine Pause zum Stornieren!")
    
    def _start_session(self):
        """Startet neue Lern-Session"""
        print("\n" + "="*60)
        print(f"🎓 NEUE SESSION GESTARTET")
        print(f"👤 Nutzer: {config.USER_NAME}")
        print("="*60 + "\n")
        
        self.current_session_id = str(uuid.uuid4())
        
        if self.db.client:
            try:
                self.db.client.table('sessions').insert({
                    'id': self.current_session_id,
                    'device_id': config.DEVICE_ID,
                    'start_time': datetime.now().isoformat(),
                    'user_name': config.USER_NAME,
                    'timer_status': 'ready',
                    'pause_count': 0
                }).execute()
                
                print(f"✅ Session in DB erstellt (ID: {self.current_session_id[:8]}...)")
            except Exception as e:
                print(f"❌ DB-Fehler: {e}")
        
        self.session_active = True
        self.pause_count = 0
        
        # CO2 Sensor mit Session verknüpfen
        self.co2_sensor.set_session_id(self.current_session_id)
        
        # Discord Notification
        if config.NOTIFY_SESSION_START:
            try:
                self.notification_service.send_session_start()
            except:
                pass
    
    def _wait_for_work_timer(self):
        """Wartet 30 Minuten Arbeitszeit"""
        duration = config.WORK_DURATION
        start = self.work_start_time
        
        try:
            while time.time() - start < duration:
                elapsed = time.time() - start
                remaining = duration - elapsed
                
                mins, secs = divmod(int(remaining), 60)
                print(f"\r⏱️  Arbeit: {mins:02d}:{secs:02d}", end='', flush=True)
                
                time.sleep(1)
            
            print("\n\n🎉 ARBEITSPHASE BEENDET!")
            self.buzzer.beep(2)
            
            self._start_break()
            
        except KeyboardInterrupt:
            raise
    
    def _start_break(self):
        """Startet Pausenphase auf PiTop 2"""
        self.pause_count += 1
        
        print("\n" + "="*60)
        print(f"☕ PAUSENPHASE #{self.pause_count} STARTET (10 Min)")
        print("="*60)
        print("\n📡 Signal an PiTop 2 wird gesendet...")
        
        if self.db.client:
            try:
                # Pause in DB anlegen
                pause_id = str(uuid.uuid4())
                self.db.client.table('breakdata').insert({
                    'id': pause_id,
                    'session_id': self.current_session_id,
                    'pause_number': self.pause_count,
                    'timestamp': datetime.now().isoformat(),
                    'step_count': 0,
                    'device_id': 'pitop2_break',
                    'cancelled': False
                }).execute()
                
                # Session-Status auf 'break' setzen
                self.db.client.table('sessions').update({
                    'pause_count': self.pause_count,
                    'timer_status': 'break',
                    'current_pause_start': datetime.now().isoformat()
                }).eq('id', self.current_session_id).execute()
                
                print("✅ Pause-Signal in DB gesetzt")
            except Exception as e:
                print(f"❌ DB-Fehler: {e}")
        
        self.led.off()
        
        # Notification
        if config.NOTIFY_BREAK_START:
            try:
                self.notification_service.send_message(
                    f"☕ **Pause #{self.pause_count} gestartet**\n\n"
                    f"⏱️ 10 Minuten Pause\n"
                    f"👣 Bewegung wird auf PiTop 2 getrackt\n\n"
                    f"💪 Entspann dich!"
                )
            except:
                pass
        
        print("\n💡 OPTIONEN:")
        print("   Button 1 (kurz)  → Nächste Arbeitsphase starten")
        print("   Button 1 (5+s)   → Session beenden + Report")
        print("   Button 2         → Letzte Pause stornieren\n")
        print("⏸️  Warte auf Fortsetzung...\n")
    
    def _end_session(self):
        """Beendet Session und erstellt Report"""
        print("\n" + "="*60)
        print("🛑 SESSION WIRD BEENDET")
        print("="*60 + "\n")
        
        if self.db.client:
            try:
                self.db.client.table('sessions').update({
                    'end_time': datetime.now().isoformat(),
                    'timer_status': 'ended'
                }).eq('id', self.current_session_id).execute()
            except:
                pass
        
        # Statistiken sammeln
        session_stats = self._calculate_session_stats()
        
        # Report anzeigen
        self._show_session_report(session_stats)
        
        # Discord Report
        if config.NOTIFY_SESSION_END:
            try:
                self.notification_service.send_session_report(session_stats)
            except:
                pass
        
        # Cleanup
        self.session_active = False
        self.current_session_id = None
        self.pause_count = 0
        self.work_start_time = None
        self.led.off()
        
        print("\n✅ Session beendet!\n")
    
    def _calculate_session_stats(self):
        """Sammelt Session-Statistiken aus DB"""
        stats = {
            'start_time': datetime.now(),
            'end_time': datetime.now(),
            'total_work_time': 0,
            'total_pause_time': 0,
            'pause_count': 0,
            'avg_co2': 0,
            'max_co2': 0,
            'warnings': 0,
            'total_steps': 0,
            'calories': 0,
            'distance': 0
        }
        
        if not self.db.client:
            return stats
        
        try:
            # Session-Daten
            session_result = self.db.client.table('sessions').select('*').eq('id', self.current_session_id).execute()
            if session_result.data:
                session = session_result.data[0]
                stats['start_time'] = session.get('start_time')
                stats['end_time'] = session.get('end_time')
                stats['pause_count'] = session.get('pause_count', 0)
            
            # Pausen-Daten (nur nicht-stornierte)
            breaks_result = self.db.client.table('breakdata')\
                .select('*')\
                .eq('session_id', self.current_session_id)\
                .eq('cancelled', False)\
                .execute()
            
            if breaks_result.data:
                breaks = breaks_result.data
                stats['total_steps'] = sum([b.get('step_count', 0) for b in breaks])
                stats['total_pause_time'] = len(breaks) * config.BREAK_DURATION
            
            # CO2-Daten
            co2_result = self.db.client.table('co2_measurements')\
                .select('*')\
                .eq('session_id', self.current_session_id)\
                .execute()
            
            if co2_result.data:
                co2_data = co2_result.data
                co2_levels = [m.get('co2_level', 0) for m in co2_data if m.get('co2_level')]
                if co2_levels:
                    stats['avg_co2'] = sum(co2_levels) / len(co2_levels)
                    stats['max_co2'] = max(co2_levels)
                    stats['warnings'] = sum([1 for m in co2_data if m.get('is_alarm', False)])
            
            # Zeiten
            stats['total_work_time'] = stats['pause_count'] * config.WORK_DURATION
            
            # Kalorien & Distanz
            stats['calories'] = int(stats['total_steps'] * config.CALORIES_PER_STEP)
            stats['distance'] = int(stats['total_steps'] * config.METERS_PER_STEP)
            
        except Exception as e:
            print(f"⚠️  Fehler beim Statistik-Sammeln: {e}")
        
        return stats
    
    def _show_session_report(self, stats):
        """Zeigt detaillierten Session Report"""
        work_mins = stats['total_work_time'] // 60
        break_mins = stats['total_pause_time'] // 60
        work_count = stats['pause_count']
        avg_co2 = stats['avg_co2']
        max_co2 = stats['max_co2']
        warnings = stats['warnings']
        steps = stats['total_steps']
        calories = stats['calories']
        distance = stats['distance']
        
        # Datum formatieren
        start_time = stats['start_time']
        if isinstance(start_time, str):
            try:
                start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            except:
                start_time = datetime.now()
        
        date_str = start_time.strftime("%d.%m.%Y")
        time_str = start_time.strftime("%H:%M")
        
        # Produktivität
        total = work_mins + break_mins
        productivity = (work_mins / total * 100) if total > 0 else 0
        
        print("\n" + "="*60)
        print("┌──────────────────────────────────────────────────────┐")
        print("│              📊 SESSION REPORT                       │")
        print("├──────────────────────────────────────────────────────┤")
        print(f"│ 📅 Datum:          {date_str}                     │")
        print(f"│ 🕐 Startzeit:      {time_str}                        │")
        print("├──────────────────────────────────────────────────────┤")
        print(f"│ ⏱️  Lernzeit:        {work_mins:3d} Min                │")
        print(f"│ ☕ Pausenzeit:      {break_mins:3d} Min                │")
        print(f"│ 📚 Einheiten:       {work_count:3d}                     │")
        print(f"│ ⚡ Produktivität:   {productivity:3.0f}%                │")
        print("├──────────────────────────────────────────────────────┤")
        print(f"│ 🌡️  eCO2 Ø:         {int(avg_co2):4d} ppm             │")
        print(f"│ 📈 eCO2 Max:       {int(max_co2):4d} ppm             │")
        print(f"│ ⚠️  Warnungen:      {warnings:3d}                     │")
        print("├──────────────────────────────────────────────────────┤")
        print(f"│ 👣 Schritte:       {steps:5,}                   │")
        print(f"│ 🔥 Kalorien:       ~{calories:3d} kcal              │")
        print(f"│ 📏 Distanz:        ~{distance}m                  │")
        print("└──────────────────────────────────────────────────────┘")
        print("="*60 + "\n")
    
    def start(self):
        """Startet alle Services"""
        print("▶️  Starte Monitoring...\n")
        
        # CO2 Monitoring starten
        self.co2_sensor.start_monitoring(interval=config.CO2_MEASURE_INTERVAL)
        
        print("\n" + "="*60)
        print("✅ PITOP 1 LÄUFT!")
        print("="*60)
        print(f"\n👤 Nutzer: {config.USER_NAME}")
        print(f"🔧 Device: {config.DEVICE_ID}")
        print("\n🎮 STEUERUNG:")
        print("   Button 1 (kurz)   → Arbeitszeit starten (30min)")
        print("   Button 1 (2x)     → Timer Reset")
        print("   Button 1 (lang)   → 🛑 SESSION BEENDEN + Report")
        print()
        print("   Button 2          → Letzte Pause stornieren")
        print("\n🔄 WORKFLOW:")
        print("   1. Button 1 drücken → Session startet, 30min Timer")
        print("   2. Nach 30min → PiTop 2 übernimmt (10min Pause)")
        print("   3. Button 1 drücken → Nächste 30min Arbeitsphase")
        print("   4. Button 1 (lang) → Session beenden + Report")
        print("\n🌡️  CO2-WARNUNG:")
        print(f"   - Ab {config.CO2_WARNING_THRESHOLD} ppm  → 🔴 LED + Discord")
        print(f"   - Ab {config.CO2_CRITICAL_THRESHOLD} ppm → 🔴 LED + Buzzer")
        print("\n📱 DISCORD:")
        if config.DISCORD_ENABLED:
            print("   - Benachrichtigungen aktiv ✅")
        else:
            print("   - Benachrichtigungen deaktiviert")
        print("="*60)
        print("\n👉 Drücke STRG+C zum Beenden\n")
    
    def stop(self):
        """Cleanup"""
        print("\n\n🛑 Stoppe PiTop 1...")
        
        if self.session_active:
            self._end_session()
        
        self.co2_sensor.stop_monitoring()
        self.button1.cleanup()
        self.button2.cleanup()
        self.buzzer.cleanup()
        self.led.cleanup()
        
        print("✅ Cleanup abgeschlossen\n")

def signal_handler(sig, frame):
    pitop1.stop()
    sys.exit(0)

if __name__ == "__main__":
    if not config.validate_config():
        sys.exit(1)
    
    pitop1 = PiTop1WorkStation()
    signal.signal(signal.SIGINT, signal_handler)
    
    pitop1.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pitop1.stop()