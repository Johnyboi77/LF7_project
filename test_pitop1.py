#!/usr/bin/env python3
"""
🧪 TEST MODE - pi-top 1
Schnelldurchlauf: 30s Arbeit, 10s Pause
DB speichert hochgerechnete Werte (x60)
"""

import os
import sys

# ⚠️ DEVICE_OVERRIDE MUSS VOR allen anderen Imports stehen!
if '--device=' not in ' '.join(sys.argv):
    os.environ['DEVICE_OVERRIDE'] = 'pitop1'  # Default für diesen Test

import signal
import time
from time import sleep
from datetime import datetime
import config
from hardware import Button1, Button2, LED, Buzzer, CO2Sensor
from services.timer_service import TimerService
from services.notification_service import NotificationService
from database.supabase_manager import SupabaseManager

# 🧪 TEST MODE CONFIGURATION
TEST_WORK_DURATION = 30      # 30 Sekunden (statt 1800s)
TEST_BREAK_DURATION = 10     # 10 Sekunden (statt 600s)
DB_MULTIPLIER = 60           # Werte x60 für DB (als Minuten speichern)


class TestLearningSession:
    def __init__(self):
        print("\n" + "="*60)
        print("🧪 TEST MODE - LEARNING ASSISTANT - pi-top 1")
        print("="*60)
        print("⚡ Schnelldurchlauf aktiviert!")
        print(f"   Arbeitsphase: {TEST_WORK_DURATION}s → DB: {TEST_WORK_DURATION * DB_MULTIPLIER}s")
        print(f"   Pausenphase:  {TEST_BREAK_DURATION}s → DB: {TEST_BREAK_DURATION * DB_MULTIPLIER}s")
        print("="*60 + "\n")
        
        # Hardware
        self.button1 = Button1()
        self.button2 = Button2()
        self.led = LED()
        self.buzzer = Buzzer()
        self.co2 = CO2Sensor()
        
        # Services
        self.notify = NotificationService()
        self.db = self._get_db()
        self.timer = TimerService(self.db, self.notify)
        
        # State Machine
        self.state = "IDLE"
        self.session_id = None
        self.co2_alarm_active = False
        self.last_co2_warning = None
        
        # Test Stats
        self.test_work_time = 0
        self.test_break_time = 0
        
        self._setup_callbacks()
        print(f"✅ Test-Initialisierung abgeschlossen\n")
    
    def _get_db(self):
        return SupabaseManager()
    
    def _setup_callbacks(self):
        self.button1.on_short_press(self._btn1_short)
        self.button1.on_long_press(self._btn1_long)
        self.button1.on_double_click(self._cancel_last_action)
        
        self.button2.on_short_press(self._btn2_short)
        self.button2.on_double_click(self._cancel_last_action)
    
    # ===== BUTTON CALLBACKS =====
    
    def _btn1_short(self):
        if self.state == "IDLE":
            self._start_work_session()
        elif self.state == "BREAK" and not self.timer.is_running:
            self._resume_work_session()
    
    def _btn1_long(self):
        if self.state in ["WORKING", "BREAK"]:
            self._end_session()
    
    def _btn2_short(self):
        if self.state == "WORKING":
            self._start_break()
    
    def _cancel_last_action(self):
        print("↩️  LETZTE AKTION STORNIERT (TEST)")
        if self.state == "WORKING":
            self.timer.reset()
            self.state = "IDLE"
            self.led.off()  # ✅ LED aus bei Reset
        elif self.state == "BREAK":
            self.timer.reset()
            self.state = "IDLE"
            self.led.off()  # ✅ LED aus bei Reset
    
    # ===== WORK SESSION =====
    
    def _start_work_session(self):
        if self.state != "IDLE":
            return
        
        print("\n" + "="*60)
        print("🧪 TEST - ARBEITSPHASE GESTARTET (30s)")
        print("="*60)
        
        self.state = "WORKING"
        
        # Session in DB erstellen
        self.session_id = self.db.create_session()
        self.timer.set_session_id(self.session_id)
        
        # UI Feedback (KEINE LED mehr!)
        self.buzzer.beep(0.2)
        
        # Discord
        self.notify.send_session_start()
        
        # TEST: 30s Timer
        self._run_work_timer()
    
    def _run_work_timer(self):
        """⏱️ TEST Timer: 30 Sekunden"""
        
        start_time = time.time()
        
        try:
            while time.time() - start_time < TEST_WORK_DURATION:
                elapsed = time.time() - start_time
                remaining = TEST_WORK_DURATION - elapsed
                
                print(f"\r⏱️ Arbeit: {int(remaining)}s verbleibend", 
                      end='', flush=True)
                
                sleep(1)
            
            print(f"\n\n⏰ ARBEITSPHASE ABGELAUFEN! (30s = 30 Min simuliert)")
            
            # Speichere in DB mit x60 Multiplikator
            self.test_work_time += TEST_WORK_DURATION
            
            # Buzzer
            self.buzzer.long_beep(1.0)
            
            print("✅ Arbeitsphase beendet - Drücke Button 2 für Pause\n")
        
        except KeyboardInterrupt:
            print(f"\n⚠️ Timer unterbrochen!")
    
    def _resume_work_session(self):
        print("\n" + "="*60)
        print("🧪 TEST - ARBEITSPHASE FORTGESETZT (30s)")
        print("="*60)
        
        self.state = "WORKING"
        # KEINE LED mehr!
        self.buzzer.beep(0.2)
        
        self._run_work_timer()
    
    # ===== BREAK SESSION =====
    
    def _start_break(self):
        if self.state != "WORKING":
            return
        
        print("\n" + "="*60)
        print("🧪 TEST - PAUSENPHASE INITIIERT (10s)")
        print("="*60)
        print("\n📡 Signalisiere Break an PiTop 2...")
        
        self.state = "BREAK"
        
        # Timer stoppen
        self.timer.stop_event.set()
        self.timer.is_running = False
        
        # UI Feedback (KEINE LED mehr!)
        self.buzzer.beep(0.2)
        
        # Discord
        self.notify.send_work_finished()
        
        # DB-Status update
        self._update_break_status('break')
        
        # Warte 10 Sekunden
        self._wait_for_break()
    
    def _update_break_status(self, status):
        if not self.db.client or not self.session_id:
            return
        
        try:
            self.db.client.table('sessions').update({
                'timer_status': status
            }).eq('session_id', self.session_id).execute()
            
            print(f"✅ DB Status: {status} (PiTop 2 sollte jetzt reagieren)")
        
        except Exception as e:
            print(f"⚠️ Status-Update Fehler: {e}")
    
    def _wait_for_break(self):
        """⏱️ TEST: Wartet 10 Sekunden"""
        
        print(f"\n⏱️ Break-Timer: 10 Sekunden (= 10 Min simuliert)")
        print("👣 PiTop 2 zählt jetzt Schritte...\n")
        
        start_time = time.time()
        
        try:
            while time.time() - start_time < TEST_BREAK_DURATION:
                elapsed = time.time() - start_time
                remaining = TEST_BREAK_DURATION - elapsed
                
                print(f"\r⏱️ {int(remaining)}s verbleibend (Break läuft auf beiden PiTops)", 
                      end='', flush=True)
                
                sleep(1)
            
            print(f"\n\n⏰ BREAK ABGELAUFEN!")
            
            # Speichere in DB mit x60 Multiplikator
            self.test_break_time += TEST_BREAK_DURATION
        
        except KeyboardInterrupt:
            print(f"\n\n⚠️ Break unterbrochen!")
        
        finally:
            self._end_break()
    
    def _end_break(self):
        print("\n" + "="*60)
        print("☕ BREAK BEENDET (TEST)")
        print("="*60)
        
        # KEINE LED-Änderung (nur CO2 steuert LED)
        self.buzzer.beep(0.1)
        
        # Update DB
        self._update_break_status('work_ready')
        
        # Discord
        self.notify.send_break_finished()
        
        self.state = "IDLE"
        
        print("✅ Bereit für nächste Arbeitsphase!")
        print("👉 Drücke Button 1 zum Weitermachen\n")
    
    # ===== SESSION BEENDEN =====
    
    def _end_session(self):
        print("\n" + "="*60)
        print("🛑 TEST SESSION BEENDET")
        print("="*60)
        
        self.state = "DONE"
        
        # Timer stoppen
        self.timer.stop_event.set()
        self.timer.is_running = False
        
        # UI
        self.led.off()  # ✅ LED aus bei Session-Ende
        self.buzzer.long_beep(2.0)
        
        # Hochgerechnete Zeiten für DB
        db_work_time = self.test_work_time * DB_MULTIPLIER
        db_break_time = self.test_break_time * DB_MULTIPLIER
        
        print(f"\n📊 TEST STATISTIK:")
        print(f"   Echte Arbeitszeit: {self.test_work_time}s")
        print(f"   DB Arbeitszeit: {db_work_time}s ({db_work_time // 60} Min)")
        print(f"   Echte Pausenzeit: {self.test_break_time}s")
        print(f"   DB Pausenzeit: {db_break_time}s ({db_break_time // 60} Min)\n")
        
        # Report aus DB holen
        report_data = self.db.get_session_report_data(self.session_id)
        
        # Session in DB beenden (mit hochgerechneten Werten)
        self.db.end_session(
            self.session_id,
            db_work_time,
            db_break_time
        )
        
        # Report
        if report_data:
            self.notify.print_terminal_report(report_data)
            self.notify.send_session_report(report_data)
        
        # Reset
        self.session_id = None
        self.test_work_time = 0
        self.test_break_time = 0
        
        print("\n✅ Test abgeschlossen - Ready für neue Session!\n")
    
    # ===== CO2 MONITORING (reduziert für Tests) =====
    
    def _monitor_co2(self):
        """🌡️ CO2-Überwachung - LED NUR für CO2-Warnung!"""
        
        try:
            alarm_status = self.co2.get_alarm_status()
            co2_level = self.co2.read()
            tvoc_level = self.co2.tvoc_level
            
            # ===== CRITICAL (> 800 ppm) =====
            if alarm_status == "critical":
                if not self.co2_alarm_active:
                    print(f"\n🚨 CO2 KRITISCH: {co2_level} ppm")
                    self.led.on()  # ✅ Dauerhaft an (kein Blinken!)
                    self.buzzer.co2_alarm()
                    self.co2_alarm_active = True
            
            # ===== WARNING (600-800 ppm) =====
            elif alarm_status == "warning":
                if not self.co2_alarm_active:
                    print(f"\n⚠️ CO2 WARNING: {co2_level} ppm")
                    self.led.on()  # ✅ Dauerhaft an
                    self.co2_alarm_active = True
            
            # ===== OK (< 600 ppm) =====
            else:
                if self.co2_alarm_active:
                    print(f"✅ CO2 normal: {co2_level} ppm")
                    self.co2_alarm_active = False
                    self.led.off()  # ✅ IMMER aus bei normalem CO2
        
        except Exception as e:
            pass  # Ignoriere CO2-Fehler im Test
    
    # ===== MAIN LOOP =====
    
    def run(self):
        print("✅ TEST System bereit!")
        print(f"📱 User: {config.USER_NAME}")
        print(f"📡 Device: {config.DEVICE_ID}")
        print(f"💾 Supabase: {'✅' if self.db.client else '❌'}")
        print(f"🤖 Discord: {'✅' if self.notify.is_enabled else '❌'}")
        
        print("\n🧪 TEST-MODUS:")
        print(f"   ⚡ Arbeitsphase: {TEST_WORK_DURATION}s (statt 30 Min)")
        print(f"   ⚡ Pausenphase: {TEST_BREAK_DURATION}s (statt 10 Min)")
        print(f"   📊 DB Multiplikator: x{DB_MULTIPLIER}")
        print(f"   💡 LED: NUR für CO2-Warnung (kein Status-Feedback)")
        
        print("\n🎯 KONTROLLEN:")
        print("  🔘 Button 1 kurz  → Lernphase starten")
        print("  🔘 Button 2 kurz  → Pause starten")
        print("  🔘 Button 1 lang  → Session beenden")
        
        print("\n" + "="*60)
        print("👉 Starte Test mit Button 1!\n")
        
        try:
            while True:
                # CO2 überwachen (alle 5s)
                if self.state in ["WORKING", "BREAK"]:
                    self._monitor_co2()
                
                sleep(5)
        
        except KeyboardInterrupt:
            self._cleanup()
    
    def _cleanup(self):
        print("\n\n🛑 Test beendet")
        
        if self.state != "IDLE":
            print("⚠️ Session nicht ordnungsgemäß beendet!")
        
        self.led.off()
        self.buzzer.off()
        self.timer.stop_event.set()
        
        print("✅ Cleanup abgeschlossen\n")


def signal_handler(sig, frame):
    if 'session' in globals():
        session._cleanup()
    sys.exit(0)


if __name__ == "__main__":
    session = TestLearningSession()
    signal.signal(signal.SIGINT, signal_handler)
    session.run()