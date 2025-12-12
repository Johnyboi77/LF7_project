#!/usr/bin/env python3
"""
pi-top 1 - Effektiver Lernen mit State Machine
Button 1 + Button 2 + LED + Buzzer + CO2 Sensor
KEIN Schrittzähler (läuft auf PiTop 2)
"""

import signal
import sys
from time import sleep
from datetime import datetime

import config
from hardware.button1 import Button
from hardware.button2 import Button2
from hardware.led import LED
from hardware.buzzer import Buzzer
from hardware.Co2_sensor import CO2Sensor
from services.timer_service import TimerService
from services.notification_service import NotificationService
from database.supabase_manager import SupabaseManager


class LearningSession:
    def __init__(self):
        print("\n" + "="*60)
        print("🎓 LEARNING ASSISTANT - pi-top 1")
        print("="*60)
        
        # Hardware (OHNE Schrittzähler)
        self.button1 = Button("D0")
        self.button2 = Button2("D1")
        self.led = LED("D2")
        self.buzzer = Buzzer("D3")
        self.co2 = CO2Sensor() 
        # ggf I2C Address 0x5A hardcoded -> übergabe passiert aber eigentlich automatisch durch hardware/Co2_sensor.py
        
        # Services
        self.timer = TimerService(self._get_db(), NotificationService())
        self.notify = NotificationService()
        self.db = self._get_db()
        
        # State Machine
        self.state = "IDLE"  # IDLE → WORKING → BREAK → WORKING → DONE
        self.session_id = None
        self.co2_alarm_active = False
        self.last_co2_warning = None
        
        self._setup_callbacks()
        print(f"✅ Initialisierung abgeschlossen\n")
    
    def _get_db(self):
        """Lazy-Init für DB"""
        return SupabaseManager()
    
    def _setup_callbacks(self):
        """Registriert Button-Callbacks"""
        self.button1.on_short_press(self._btn1_short)
        self.button1.on_long_press(self._btn1_long)
        self.button1.on_double_click(self._cancel_last_action)
        
        self.button2.on_short_press(self._btn2_short)
        self.button2.on_double_click(self._cancel_last_action)
    
    # ===== BUTTON CALLBACKS =====
    
    def _btn1_short(self):
        """Button 1 kurz: Start Work oder Resume nach Pause"""
        if self.state == "IDLE":
            self._start_work_session()
        elif self.state == "BREAK" and not self.timer.is_running:
            self._resume_work_session()
    
    def _btn1_long(self):
        """Button 1 lang (5+s): Session beenden"""
        if self.state in ["WORKING", "BREAK"]:
            self._end_session()
    
    def _btn2_short(self):
        """Button 2 kurz: Start Break"""
        if self.state == "WORKING":
            self._start_break()
    
    def _cancel_last_action(self):
        """Button 1+2 2x: Letzte Aktion stornieren"""
        print("↩️  LETZTE AKTION STORNIERT")
        if self.state == "WORKING":
            self.timer.reset()
            self.state = "IDLE"
            self.led.off()
        elif self.state == "BREAK":
            self.timer.reset()
            self.state = "IDLE"
            self.led.off()
    
    # ===== WORK SESSION =====
    
    def _start_work_session(self):
        """🎓 Startet neue Arbeitsphase (30 Min)"""
        
        if self.state != "IDLE":
            return
        
        print("\n" + "="*60)
        print("🎓 ARBEITSPHASE GESTARTET")
        print("="*60)
        
        self.state = "WORKING"
        
        # Session in DB erstellen
        self.session_id = self.db.create_session()
        self.timer.set_session_id(self.session_id)
        
        # UI Feedback
        self.led.on()  # Weiß/Grün
        self.buzzer.beep(0.2)
        
        # Discord Benachrichtigung
        self.notify.send_session_start()
        
        # Timer starten (30 Min)
        self.timer.start_work_timer()
    
    def _resume_work_session(self):
        """💪 Nach Pause weiterarbeiten"""
        
        print("\n" + "="*60)
        print("💪 ARBEITSPHASE FORTGESETZT")
        print("="*60)
        
        self.state = "WORKING"
        self.led.on()
        self.buzzer.beep(0.2)
        
        # Neue Arbeitsphase (30 Min)
        self.timer.start_work_timer()
    
    # ===== BREAK SESSION =====
    
    def _start_break(self):
        """☕ Pausenphase signalisieren (nur DB-Status, nicht lokal)"""
        
        if self.state != "WORKING":
            return
        
        print("\n" + "="*60)
        print("☕ PAUSENPHASE INITIIERT")
        print("="*60)
        print("\n📡 Signalisiere Break an PiTop 2...")
        
        self.state = "BREAK"
        
        # Work-Zeit speichern
        work_elapsed = self.timer.remaining_time
        print(f"⏱️  Arbeitszeit gespeichert: {work_elapsed}s")
        
        # Timer stoppen (lokal, nicht starten)
        self.timer.stop_event.set()
        self.timer.is_running = False
        
        # UI Feedback
        self.led.blink(0.5, 0.5)  # Blinken = Break aktiv
        self.buzzer.beep(0.2)
        
        # Discord: Break vorbei
        self.notify.send_work_finished()
        
        # Update DB-Status zu 'break'
        # → PiTop 2 erkennt das Signal und startet Schrittzähler
        self._update_break_status('break')
        
        # Warte 10 Minuten lokal (synchron mit PiTop 2)
        self._wait_for_break()
    
    def _update_break_status(self, status):
        """📊 Aktualisiert Break-Status in DB"""
        
        if not self.db.client or not self.session_id:
            return
        
        try:
            self.db.client.table('sessions').update({
                'timer_status': status
            }).eq('session_id', self.session_id).execute()
            
            print(f"✅ DB Status: {status} (PiTop 2 sollte jetzt reagieren)")
        
        except Exception as e:
            print(f"⚠️  Status-Update Fehler: {e}")
    
    def _wait_for_break(self):
        """⏱️ Wartet 10 Minuten lokal während PiTop 2 Schritte zählt"""
        
        print(f"\n⏱️  Break-Timer: 10 Minuten")
        print("👣 PiTop 2 zählt jetzt Schritte...\n")
        
        break_duration = config.BREAK_DURATION
        start_time = sleep.__doc__  # Trick zur Zeitmessung
        import time
        start_time = time.time()
        
        try:
            while time.time() - start_time < break_duration:
                elapsed = time.time() - start_time
                remaining = break_duration - elapsed
                
                mins, secs = divmod(int(remaining), 60)
                
                print(f"\r⏱️  {mins:02d}:{secs:02d} verbleibend (Break läuft auf beiden PiTops)", 
                      end='', flush=True)
                
                sleep(1)
            
            print(f"\n\n⏰ BREAK ABGELAUFEN!")
        
        except KeyboardInterrupt:
            print(f"\n\n⚠️  Break unterbrochen!")
        
        finally:
            # Break beenden
            self._end_break()
    
    def _end_break(self):
        """☕ Beendet Break-Phase"""
        
        print("\n" + "="*60)
        print("☕ BREAK BEENDET")
        print("="*60)
        
        # LED aus / normal
        self.led.off()
        self.buzzer.beep(0.1)
        
        # Update DB-Status zu 'work_ready'
        # → PiTop 2 speichert Daten und wartet auf nächsten Break
        self._update_break_status('work_ready')
        
        # Discord: Break vorbei, zurück zur Arbeit
        self.notify.send_break_finished()
        
        # Zurück zu IDLE (User kann Button 1 drücken zum weitermachen)
        self.state = "IDLE"
        
        print("✅ Bereit für nächste Arbeitsphase!")
        print("👉 Drücke Button 1 zum Weitermachen\n")
    
    # ===== SESSION BEENDEN =====
    
    def _end_session(self):
        """🛑 Ganze Lerneinheit beendet"""
        
        print("\n" + "="*60)
        print("🛑 SESSION BEENDET")
        print("="*60)
        
        self.state = "DONE"
        
        # Timer stoppen
        self.timer.stop_event.set()
        self.timer.is_running = False
        
        # UI Feedback
        self.led.off()
        self.buzzer.long_beep(2.0)
        
        # Statistiken aus Services
        session_stats = self.timer.get_session_stats()
        
        # Report aus DB holen
        report_data = self.db.get_session_report_data(self.session_id)
        
        # Session in DB als beendet markieren
        self.db.end_session(
            self.session_id,
            session_stats['total_work_time'],
            session_stats['total_break_time']
        )
        
        # Report ausgeben
        if report_data:
            self.notify.print_terminal_report(report_data)
            self.notify.send_session_report(report_data)
        
        # Reset
        self.session_id = None
        self.timer.reset_session_stats()
        self.timer.reset()
        
        print("\n✅ Ready für neue Session!\n")
    
    # ===== CO2 MONITORING =====
    
    def _monitor_co2(self):
        """🌡️ Überwacht CO2 und triggert Alarme"""
        
        alarm_status = self.co2.get_alarm_status()
        co2_level = self.co2.read()
        tvoc_level = self.co2.tvoc_level
        
        # ===== CRITICAL (> 800 ppm) =====
        if alarm_status == "critical":
            if not self.co2_alarm_active:
                print(f"\n🚨 KRITISCHE CO2-WERTE: {co2_level} ppm")
                
                # LED: Schnelles Rot blinken
                self.led.blink(0.1, 0.1)
                
                # Buzzer: Doppelbeep
                self.buzzer.co2_alarm()
                
                # Discord
                self.notify.send_co2_alert(co2_level, tvoc_level, is_critical=True)
                
                # DB Log
                self.db.log_co2(self.session_id, co2_level, tvoc_level, 
                               is_alarm=True, alarm_type="critical")
                
                self.co2_alarm_active = True
                self.last_co2_warning = datetime.now()
        
        # ===== WARNING (600-800 ppm) =====
        elif alarm_status == "warning":
            if not self.co2_alarm_active or \
               (self.last_co2_warning and 
                (datetime.now() - self.last_co2_warning).seconds > 300):
                
                print(f"\n⚠️  WARNUNG CO2-WERTE: {co2_level} ppm")
                
                # LED: An (Gelb/Orange)
                self.led.on()
                
                # Discord (kein Ping)
                if (self.last_co2_warning is None or 
                    (datetime.now() - self.last_co2_warning).seconds > 300):
                    self.notify.send_co2_alert(co2_level, tvoc_level, is_critical=False)
                
                # DB Log
                self.db.log_co2(self.session_id, co2_level, tvoc_level,
                               is_alarm=True, alarm_type="warning")
                
                self.co2_alarm_active = True
                self.last_co2_warning = datetime.now()
        
        # ===== OK (< 600 ppm) =====
        else:
            if self.co2_alarm_active:
                print(f"✅ CO2 normal: {co2_level} ppm")
                self.co2_alarm_active = False
                
                # LED aus (wenn nicht gerade arbeitet)
                if self.state == "IDLE":
                    self.led.off()
                elif self.state == "WORKING":
                    self.led.on()
                elif self.state == "BREAK":
                    self.led.blink(0.5, 0.5)
            
            # Normale Messung loggen
            if self.session_id and self.state in ["WORKING", "BREAK"]:
                self.db.log_co2(self.session_id, co2_level, tvoc_level,
                               is_alarm=False, alarm_type=None)
    
    # ===== MAIN LOOP =====
    
    def run(self):
        """Hauptschleife"""
        
        print("✅ System bereit!")
        print(f"📱 User: {config.USER_NAME}")
        print(f"📡 Device: {config.DEVICE_ID}")
        print(f"💾 Supabase: {'✅' if self.db.client else '❌'}")
        print(f"🤖 Discord: {'✅' if self.notify.is_enabled else '❌'}")
        print(f"👣 Schrittzähler: ❌ (läuft auf PiTop 2)")
        
        print("\n🎯 KONTROLLEN:")
        print("  🔘 Button 1 kurz  → Lernphase starten")
        print("  🔘 Button 2 kurz  → Pause starten (während Lernen)")
        print("  🔘 Button 1 lang  → Session beenden")
        print("  🔘 Button 1+2 2x  → Letzte Aktion stornieren")
        
        print("\n📊 STATE:")
        print(f"  Status: {self.state}")
        
        print("\n🔗 VERBINDUNGEN:")
        print("  PiTop 1 ↔ PiTop 2: Über Supabase DB")
        print("  PiTop 1 → Discord: Push-Benachrichtigungen")
        print("  PiTop 2 → Discord: Break-Statistiken")
        
        print("\n" + "="*60)
        print("👉 Starte eine Lernphase mit Button 1!\n")
        
        try:
            while True:
                # CO2 überwachen (alle 5 Sekunden)
                if self.state in ["WORKING", "BREAK"]:
                    self._monitor_co2()
                
                sleep(5)
        
        except KeyboardInterrupt:
            self._cleanup()
    
    def _cleanup(self):
        """Cleanup beim Beenden"""
        print("\n\n🛑 Programm beendet")
        
        if self.state != "IDLE":
            print("⚠️  Session nicht ordnungsgemäß beendet!")
        
        self.led.off()
        self.buzzer.off()
        self.timer.stop_event.set()
        
        print("✅ Cleanup abgeschlossen\n")


def signal_handler(sig, frame):
    """STRG+C Handler"""
    if 'session' in globals():
        session._cleanup()
    sys.exit(0)


if __name__ == "__main__":
    session = LearningSession()
    signal.signal(signal.SIGINT, signal_handler)
    session.run()