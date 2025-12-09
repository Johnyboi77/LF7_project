# main.py
"""
Learning Assistant - Hauptprogramm mit Session-Management
"""

import signal
import sys
import time
import config

from database.db_manager import DatabaseManager
from hardware.buzzer import Buzzer
from hardware.led import LED
from hardware.button1 import Button1
from hardware.button2 import Button2
from hardware.Co2_sensor import CO2Sensor
from hardware.step_counter import StepCounter
from services.timer_service import TimerService
from services.notification_service import NotificationService

class LearningAssistant:
    def __init__(self):
        print("\n" + "="*60)
        print("🚀 LEARNING ASSISTANT")
        print("="*60 + "\n")
        
        # Datenbank
        self.db = DatabaseManager(config.DB_PATH)
        
        # Hardware
        self.buzzer = Buzzer()
        self.led = LED()
        
        # Services
        self.notification_service = NotificationService()
        
        # Timer Service
        self.timer = TimerService(
            self.buzzer,
            self.notification_service,
            self.db
        )
        
        # Sensoren
        self.co2_sensor = CO2Sensor(
            self.buzzer,
            self.led,
            self.notification_service,
            self.db
        )
        
        self.step_counter = StepCounter(self.db)
        
        # Session Management
        self.current_session_id = None
        self.session_active = False
        
        # Buttons
        self.button1 = Button1(
            short_press_callback=self.on_button1_short,
            long_press_callback=self.on_button1_long,
            end_session_callback=self.on_button1_end_session
        )
        
        self.button2 = Button2(
            short_press_callback=self.on_button2_short,
            long_press_callback=self.on_button2_long
        )
        
        print("✅ Alle Komponenten initialisiert\n")
    
    def on_button1_short(self):
        """Button 1 kurz: Arbeitszeit starten"""
        
        # Erste Session starten wenn noch keine läuft
        if not self.session_active:
            self._start_session()
        
        self.timer.start_work_timer()
        self.db.log_button(1, "work_start", self.current_session_id)
    
    def on_button1_long(self):
        """Button 1 lang (2-5s): Reset"""
        self.timer.reset()
        self.db.log_button(1, "reset", self.current_session_id)
    
    def on_button1_end_session(self):
        """Button 1 extra-lang (5+s): Session beenden"""
        if self.session_active:
            self._end_session()
        else:
            print("⚠️  Keine aktive Session zum Beenden!")
    
    def on_button2_short(self):
        """Button 2 kurz: Pausenzeit starten"""
        
        # Session starten falls noch keine läuft
        if not self.session_active:
            self._start_session()
        
        self.timer.start_break_timer()
        self.db.log_button(2, "break_start", self.current_session_id)
    
    def on_button2_long(self):
        """Button 2 lang: Reset"""
        self.timer.reset()
        self.db.log_button(2, "reset", self.current_session_id)
    
    def _start_session(self):
        """Startet eine neue Lern-Session"""
        print("\n" + "="*60)
        print(f"🎓 NEUE SESSION GESTARTET für {config.USER_NAME}")
        print("="*60 + "\n")
        
        # Session in DB erstellen
        self.current_session_id = self.db.create_session()
        self.session_active = True
        
        # Session-Tracking zurücksetzen
        self.timer.reset_session_stats()
        
        # Sensoren mit Session-ID verknüpfen
        self.co2_sensor.session_id = self.current_session_id
        self.step_counter.session_id = self.current_session_id
        
        # Discord-Benachrichtigung
        self.notification_service.send_session_start()
    
    def _end_session(self):
        """Beendet die aktuelle Session und erstellt Report"""
        print("\n" + "="*60)
        print(f"🛑 SESSION BEENDET für {config.USER_NAME}")
        print("="*60 + "\n")
        
        # Timer stoppen falls läuft
        self.timer.reset()
        
        # Session-Daten sammeln
        session_stats = self.timer.get_session_stats()
        
        # Session in DB beenden
        self.db.end_session(
            self.current_session_id,
            session_stats['total_work_time'],
            session_stats['total_break_time'],
            session_stats['work_sessions_count'],
            session_stats['break_sessions_count']
        )
        
        # Statistiken aus DB holen
        stats = self.db.get_session_stats(self.current_session_id)
        
        # Report in Terminal ausgeben
        self._print_session_report(stats)
        
        # Report an Discord senden
        self.notification_service.send_session_report(stats)
        
        # Session beenden
        self.session_active = False
        self.current_session_id = None
        
        print("\n✅ Report wurde an Discord gesendet!\n")
    
    def _print_session_report(self, stats):
        """Gibt Session-Report im Terminal aus"""
        work_mins = stats['session'].get('total_work_time', 0) // 60
        break_mins = stats['session'].get('total_break_time', 0) // 60
        work_count = stats['session'].get('work_sessions_count', 0)
        
        avg_co2 = stats['co2'].get('avg_co2', 0)
        max_co2 = stats['co2'].get('max_co2', 0)
        min_co2 = stats['co2'].get('min_co2', 0)
        warnings = stats.get('warnings', 0)
        
        steps = stats.get('steps', 0)
        
        print("┌─────────────────────────────────────────────┐")
        print("│         📊 SESSION REPORT                   │")
        print("├─────────────────────────────────────────────┤")
        print(f"│ ⏱️  Lernzeit:      {work_mins:3d} Min            │")
        print(f"│ ☕ Pausenzeit:    {break_mins:3d} Min            │")
        print(f"│ 📚 Einheiten:     {work_count:3d}                 │")
        print("├─────────────────────────────────────────────┤")
        print(f"│ 🌡️  eCO2 Ø:       {int(avg_co2):4d} ppm         │")
        print(f"│ 📈 eCO2 Max:     {max_co2:4d} ppm         │")
        print(f"│ ⚠️  Warnungen:    {warnings:3d}                 │")
        print("├─────────────────────────────────────────────┤")
        print(f"│ 👣 Schritte:     {steps:5,}               │")
        print("└─────────────────────────────────────────────┘")
    
    def start(self):
        """Startet alle Services"""
        print("▶️  Starte Monitoring...\n")
        
        # CO2 Monitoring
        self.co2_sensor.start_monitoring(interval=10)
        
        # Step Counter
        self.step_counter.start_monitoring(interval=5)
        
        print("\n" + "="*60)
        print("✅ SYSTEM LÄUFT!")
        print("="*60)
        print(f"\n👤 Nutzer: {config.USER_NAME}")
        print("\n🎮 STEUERUNG:")
        print("   Button 1 (<2s)    → Arbeitszeit starten (30min)")
        print("   Button 1 (2-5s)   → Timer Reset")
        print("   Button 1 (5+s)    → 🛑 SESSION BEENDEN + Report")
        print()
        print("   Button 2 (<2s)    → Pausenzeit starten (10min)")
        print("   Button 2 (2+s)    → Timer Reset")
        print("\n💡 SESSION-MANAGEMENT:")
        print("   - Erste Timer-Start → Session beginnt automatisch")
        print("   - Button 1 (5+s) → Session endet + Report")
        print("\n🌡️  CO2-WARNUNG:")
        print(f"   - Ab {config.CO2_WARNING_THRESHOLD} ppm  → 🔴 LED + Discord")
        print(f"   - Ab {config.CO2_CRITICAL_THRESHOLD} ppm → 🔴 LED + Buzzer + Discord")
        print("\n📱 DISCORD:")
        if self.notification_service.is_enabled:
            print("   - Benachrichtigungen aktiv ✅")
        else:
            print("   - Benachrichtigungen deaktiviert")
        print("="*60)
        print("\n👉 Drücke STRG+C zum Beenden\n")
    
    def stop(self):
        """Cleanup"""
        print("\n\n🛑 Stoppe Learning Assistant...")
        
        # Session beenden falls aktiv
        if self.session_active:
            self._end_session()
        
        self.co2_sensor.stop_monitoring()
        self.step_counter.stop_monitoring()
        self.timer.reset()
        
        self.button1.cleanup()
        self.button2.cleanup()
        self.buzzer.cleanup()
        self.led.cleanup()
        
        print("✅ Cleanup abgeschlossen\n")

def signal_handler(sig, frame):
    """STRG+C Handler"""
    assistant.stop()
    sys.exit(0)

if __name__ == "__main__":
    assistant = LearningAssistant()
    
    signal.signal(signal.SIGINT, signal_handler)
    
    assistant.start()
    
    # Hauptloop
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        assistant.stop()