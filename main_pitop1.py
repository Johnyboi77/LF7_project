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
    os.environ['DEVICE_OVERRIDE'] = 'pitop1'

import signal
import time
from time import sleep
from datetime import datetime
import config
from hardware import Button1, Button2, LED, Buzzer, CO2Sensor
from services.timer_service import TimerService
from services.discord_templates import NotificationService
from database.supabase_manager import SupabaseManager

# 🧪 TEST MODE CONFIGURATION
WORK_DURATION = 1800      # 30 Minuten (statt 1800s)
BREAK_DURATION = 600     # 10 Minuten (statt 600s)
DB_MULTIPLIER = 1           # Werte x60 für DB (als Minuten speichern)
CO2_LOG_INTERVAL = 6         # Alle 6 Aufrufe loggen (bei 5s Loop = alle 30s)


class LearningSession:
    def __init__(self):
        print("\n" + "="*60)
        print("🧪 TEST MODE - LEARNING ASSISTANT - pi-top 1")
        print("="*60)
        print("⚡ Schnelldurchlauf aktiviert!")
        print(f"   Arbeitsphase: {WORK_DURATION}s → DB: {WORK_DURATION * DB_MULTIPLIER}s")
        print(f"   Pausenphase:  {BREAK_DURATION}s → DB: {BREAK_DURATION * DB_MULTIPLIER}s")
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
        
        # Action History für Storno
        self.action_history = []
        
        # CO2 Logging Counter
        self.co2_log_counter = 0
        
        # Test Stats
        self.total_work_time = 0
        self.total_break_time = 0
        
        self._setup_callbacks()
        print(f"✅ Initialisierung abgeschlossen\n")
    
    def _get_db(self):
        return SupabaseManager()
    
    def _setup_callbacks(self):
        """Setup der neuen Button-Logik"""
        
        # Status-Check Callbacks setzen
        self.button1.set_work_active_check(self._is_work_active)
        self.button2.set_work_active_check(self._is_work_active)
        
        # Button 1: Nur Arbeitsphase starten
        self.button1.on_short_press(self._start_work_session)
        
        # Button 2: Pause, Storno, Session beenden
        self.button2.on_short_press(self._start_break)
        self.button2.on_cancel(self._cancel_last_action)
        self.button2.on_end_session(self._end_session)
    
    def _is_work_active(self):
        """Prüft ob gerade eine Arbeitsphase läuft"""
        return self.state == "WORKING"
    
    # ===== WORK SESSION =====
    
    def _start_work_session(self):
        if self.state == "WORKING":
            print("⚠️ Arbeitsphase läuft bereits!")
            return
        
        print("\n" + "="*60)
        print("🧪 TEST - ARBEITSPHASE GESTARTET (30s)")
        print("="*60)
        
        self.state = "WORKING"
        
        # Action History
        self.action_history.append({
            'type': 'work_start',
            'time': time.time()
        })
        
        # CO2 Counter zurücksetzen
        self.co2_log_counter = 0
        
        # Session in DB erstellen (nur wenn noch keine existiert)
        if not self.session_id:
            self.session_id = self.db.create_session()
            self.timer.set_session_id(self.session_id)
            # Discord nur bei erster Arbeitsphase
            self.notify.send_session_start()
        
        # UI Feedback
        self.buzzer.beep(0.2)
        
        # TEST: 30s Timer
        self._run_work_timer()
    
    def _run_work_timer(self):
        """⏱️ TEST Timer: 30 Minuten"""
        
        start_time = time.time()
        
        try:
            while time.time() - start_time < WORK_DURATION:
                # Prüfen ob State noch WORKING (könnte durch Storno geändert worden sein)
                if self.state != "WORKING":
                    print("\n⚠️ Arbeitsphase wurde unterbrochen")
                    return
                
                elapsed = time.time() - start_time
                remaining = WORK_DURATION - elapsed
                
                # CO2 während Arbeit überwachen
                self._monitor_co2()
                
                print(f"\r⏱️ Arbeit: {int(remaining)}s verbleibend", 
                      end='', flush=True)
                
                sleep(5)  # 5s Intervall für CO2
            
            # Timer regulär abgelaufen
            if self.state == "WORKING":
                print(f"\n\n⏰ ARBEITSPHASE ABGELAUFEN! (30s = 30 Min simuliert)")
                
                # Speichere in DB mit x60 Multiplikator
                self.total_work_time += WORK_DURATION
                
                # Buzzer
                self.buzzer.long_beep(1.0)
                
                # State auf WORK_DONE - wartet auf Pause
                self.state = "WORK_DONE"
                
                print("✅ Arbeitsphase beendet - Drücke Button 2 für Pause\n")
        
        except KeyboardInterrupt:
            print(f"\n⚠️ Timer unterbrochen!")
    
    # ===== BREAK SESSION =====
    
    def _start_break(self):
        """Pause starten - nur wenn keine Arbeitsphase aktiv"""
        
        if self.state == "WORKING":
            print("⚠️ Arbeitsphase läuft noch - zuerst beenden lassen!")
            return
        
        if self.state not in ["WORK_DONE", "IDLE"]:
            print(f"⚠️ Pause nicht möglich im Status: {self.state}")
            return
        
        # Wenn IDLE und keine Session, erstmal Session starten
        if self.state == "IDLE" and not self.session_id:
            print("⚠️ Zuerst Arbeitsphase mit Button 1 starten!")
            return
        
        print("\n" + "="*60)
        print("🧪 TEST - PAUSENPHASE INITIIERT (10s)")
        print("="*60)
        print("\n📡 Signalisiere Break an PiTop 2...")
        
        self.state = "BREAK"
        
        # Action History
        self.action_history.append({
            'type': 'break_start',
            'time': time.time()
        })
        
        # UI Feedback
        self.buzzer.beep(0.2)
        
        # Discord
        self.notify.send_work_finished()
        
        # DB-Status update
        self._update_break_status('break')
        
        # Warte 10 Minuten
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
        """⏱️ TEST: Wartet 10 Minuten"""
        
        print(f"\n⏱️ Break-Timer: 10 Minuten (= 10 Min simuliert)")
        print("👣 PiTop 2 zählt jetzt Schritte...\n")
        
        start_time = time.time()
        
        try:
            while time.time() - start_time < BREAK_DURATION:
                # Prüfen ob State noch BREAK
                if self.state != "BREAK":
                    print("\n⚠️ Pause wurde unterbrochen")
                    return
                
                elapsed = time.time() - start_time
                remaining = BREAK_DURATION - elapsed
                
                print(f"\r⏱️ {int(remaining)}s verbleibend (Break läuft auf beiden PiTops)", 
                      end='', flush=True)
                
                sleep(1)
            
            print(f"\n\n⏰ BREAK ABGELAUFEN!")
            
            # Speichere in DB mit x60 Multiplikator
            self.total_break_time += BREAK_DURATION
        
        except KeyboardInterrupt:
            print(f"\n\n⚠️ Break unterbrochen!")
        
        finally:
            if self.state == "BREAK":
                self._end_break()
    
    def _end_break(self):
        print("\n" + "="*60)
        print("☕ BREAK BEENDET (TEST)")
        print("="*60)
        
        self.buzzer.beep(0.1)
        
        # Update DB
        self._update_break_status('work_ready')
        
        # Discord
        self.notify.send_break_finished()
        
        self.state = "IDLE"
        
        print("✅ Bereit für nächste Arbeitsphase!")
        print("👉 Drücke Button 1 zum Weitermachen")
        print("👉 Oder Button 2 (7s) zum Session beenden\n")
    
    # ===== STORNO =====
    
    def _cancel_last_action(self):
        """Letzte Aktion stornieren (Button 2, 3s)"""
        
        print("\n" + "="*60)
        print("↩️ STORNO - Letzte Aktion wird rückgängig gemacht")
        print("="*60)
        
        if not self.action_history:
            print("⚠️ Keine Aktion zum Stornieren vorhanden!")
            return
        
        last_action = self.action_history.pop()
        action_type = last_action['type']
        
        if action_type == 'work_start':
            print("↩️ Arbeitsphase storniert")
            self.state = "IDLE"
            self.led.off()
            # Wenn es die erste Arbeitsphase war, Session-ID zurücksetzen
            if len(self.action_history) == 0:
                self.session_id = None
        
        elif action_type == 'break_start':
            print("↩️ Pause storniert")
            self.state = "WORK_DONE"
            self._update_break_status('work_ready')
        
        self.buzzer.beep(0.1)
        print(f"✅ Storno abgeschlossen - Status: {self.state}\n")
    
    # ===== SESSION BEENDEN =====
    
    def _end_session(self):
        """Session komplett beenden (Button 2, 7s)"""
        
        print("\n" + "="*60)
        print("🛑 TEST SESSION BEENDET")
        print("="*60)
        
        self.state = "DONE"
        
        # Timer stoppen falls läuft
        self.timer.stop_event.set()
        self.timer.is_running = False
        
        # UI
        self.led.off()
        self.buzzer.long_beep(2.0)
        
        # Hochgerechnete Zeiten für DB
        db_work_time = self.total_work_time * DB_MULTIPLIER
        db_break_time = self.total_break_time * DB_MULTIPLIER
        
        print(f"\n📊 TEST STATISTIK:")
        print(f"   Echte Arbeitszeit: {self.total_work_time}s")
        print(f"   DB Arbeitszeit: {db_work_time}s ({db_work_time // 60} Min)")
        print(f"   Echte Pausenzeit: {self.total_break_time}s")
        print(f"   DB Pausenzeit: {db_break_time}s ({db_break_time // 60} Min)")
        print(f"   Aktionen: {len(self.action_history)}\n")
        
        # Report aus DB holen
        if self.session_id:
            report_data = self.db.get_session_report_data(self.session_id)
            
            # Session in DB beenden
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
        self.total_work_time = 0
        self.total_break_time = 0
        self.co2_log_counter = 0
        self.action_history.clear()
        self.state = "IDLE"
        
        print("\n✅ Session abgeschlossen - Ready für neue Session!\n")
    
    # ===== CO2 MONITORING =====
    
    def _monitor_co2(self):
        """🌡️ CO2-Überwachung mit DB-Logging alle 30s"""
        
        try:
            alarm_status = self.co2.get_alarm_status()
            co2_level = self.co2.read()
            tvoc_level = self.co2.tvoc_level
            
            # Counter erhöhen
            self.co2_log_counter += 1
            
            # Nur alle 6 Aufrufe loggen (30s) ODER bei Alarm
            is_alarm = alarm_status in ["warning", "critical"]
            should_log = (self.co2_log_counter >= CO2_LOG_INTERVAL) or is_alarm
            
            if self.session_id and co2_level and should_log:
                self.db.log_co2(
                    session_id=self.session_id,
                    co2_level=co2_level,
                    tvoc_level=tvoc_level,
                    is_alarm=is_alarm,
                    alarm_type=alarm_status if is_alarm else None
                )
                self.co2_log_counter = 0
                print(f"\n💨 CO2 geloggt: {co2_level} ppm")
            
            # CRITICAL (> 800 ppm)
            if alarm_status == "critical":
                if not self.co2_alarm_active:
                    print(f"\n🚨 CO2 KRITISCH: {co2_level} ppm")
                    self.led.on()
                    self.buzzer.co2_alarm()
                    self.co2_alarm_active = True
            
            # WARNING (600-800 ppm)
            elif alarm_status == "warning":
                if not self.co2_alarm_active:
                    print(f"\n⚠️ CO2 WARNING: {co2_level} ppm")
                    self.led.on()
                    self.co2_alarm_active = True
            
            # OK (< 600 ppm)
            else:
                if self.co2_alarm_active:
                    print(f"\n✅ CO2 normal: {co2_level} ppm")
                    self.co2_alarm_active = False
                    self.led.off()
        
        except Exception as e:
            print(f"\n⚠️ CO2-Monitoring Fehler: {e}")
    
    # ===== MAIN LOOP =====
    
    def run(self):
        print("✅ TEST System bereit!")
        print(f"📱 User: {config.USER_NAME}")
        print(f"📡 Device: {config.DEVICE_ID}")
        print(f"💾 Supabase: {'✅' if self.db.client else '❌'}")
        print(f"🤖 Discord: {'✅' if self.notify.is_enabled else '❌'}")
        
        print("\n🧪 TEST-MODUS:")
        print(f"   ⚡ Arbeitsphase: {WORK_DURATION}s (statt 30 Min)")
        print(f"   ⚡ Pausenphase: {BREAK_DURATION}s (statt 10 Min)")
        print(f"   📊 DB Multiplikator: x{DB_MULTIPLIER}")
        print(f"   💨 CO2 Logging: alle {CO2_LOG_INTERVAL * 5}s")
        
        print("\n🎮 NEUE BUTTON-STEUERUNG:")
        print("  ┌─────────────────────────────────────────┐")
        print("  │ BUTTON 1 (D0):                          │")
        print("  │   • Kurz drücken = Arbeitsphase starten │")
        print("  │     (nur wenn keine läuft)              │")
        print("  ├─────────────────────────────────────────┤")
        print("  │ BUTTON 2 (D1):                          │")
        print("  │   • Kurz drücken = Pause starten        │")
        print("  │     (nur wenn Arbeit beendet)           │")
        print("  │   • 3s halten = STORNO letzte Aktion    │")
        print("  │   • 7s halten = SESSION BEENDEN         │")
        print("  └─────────────────────────────────────────┘")
        
        print("\n" + "="*60)
        print("👉 Starte Test mit Button 1!\n")
        
        try:
            while True:
                sleep(1)
        
        except KeyboardInterrupt:
            self._cleanup()
    
    def _cleanup(self):
        print("\n\n🛑 System beendet")
        
        if self.state not in ["IDLE", "DONE"]:
            print("⚠️ Session nicht ordnungsgemäß beendet!")
        
        self.led.off()
        self.buzzer.off()
        self.timer.stop_event.set()
        self.button1.cleanup()
        self.button2.cleanup()
        
        print("✅ Cleanup abgeschlossen\n")


def signal_handler(sig, frame):
    if 'session' in globals():
        session._cleanup()
    sys.exit(0)


if __name__ == "__main__":
    session = LearningSession()
    signal.signal(signal.SIGINT, signal_handler)
    session.run()