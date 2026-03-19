"""
📚 LEARNING ASSISTANT - pi-top 1
Hauptsystem: Timer, CO2-Überwachung, Session-Management
Arbeitsphase: 30 Min | Pause: 10 Min
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
from threading import Thread, Event
import config
from hardware import Button1, Button2, LED, Buzzer, CO2Sensor
from services.timer_service import TimerService
from services.discord_templates import NotificationService
from database.supabase_manager import SupabaseManager

# ============================================================
# GPIO CLEANUP - Ressourcen vor Start freigeben
# ============================================================
print("🧹 Bereinige GPIO-Pins vor Start...")
try:
    from gpiozero import Device
    Device.close()
except Exception as e:
    pass

try:
    import lgpio
    # Alle GPIO-Handles schließen
    for handle in range(10):
        try:
            lgpio.gpiochip_close(handle)
        except:
            pass
except:
    pass

print("✅ GPIO-Cleanup abgeschlossen\n")

# ═══════════════════════════════════════════════════════════════
# TIMER KONFIGURATION
# ═══════════════════════════════════════════════════════════════
WORK_DURATION = 30 * 60      # 30 Minuten (1800 Sekunden)
BREAK_DURATION = 10 * 60     # 10 Minuten (600 Sekunden)
CO2_LOG_INTERVAL = 30        # Alle 30 Sekunden CO2 loggen


class LearningSession:
    def __init__(self):
        print("\n" + "="*60)
        print("📚 LEARNING ASSISTANT - pi-top 1")
        print("="*60)
        print(f"   Arbeitsphase: {WORK_DURATION // 60} Minuten")
        print(f"   Pausenphase:  {BREAK_DURATION // 60} Minuten")
        print("="*60 + "\n")
        
        # Hardware
        self.button1 = Button1()
        self.button2 = Button2()
        self.led = LED()
        self.buzzer = Buzzer()
        self.co2 = CO2Sensor()
        
        # Services
        self.notify = NotificationService()
        self.db = SupabaseManager()
        self.timer = TimerService(self.db, self.notify)
        
        # State Machine
        # IDLE = Bereit für neue Session
        # WORKING = Arbeitsphase aktiv (Timer läuft)
        # WORK_DONE = Arbeitsphase beendet, wartet auf Entscheidung
        # BREAK = Pausenphase aktiv
        self.state = "IDLE"
        self.session_id = None
        self.co2_alarm_active = False
        self.last_co2_warning = None
        
        # Timer Control
        self.timer_stop_event = Event()
        self.timer_thread = None
        
        # Action History für Storno
        self.action_history = []
        
        # CO2 Logging Counter
        self.co2_log_counter = 0
        
        # Session Stats
        self.total_work_time = 0
        self.total_break_time = 0
        
        self._setup_callbacks()
        print(f"✅ Initialisierung abgeschlossen\n")
    
    def _setup_callbacks(self):
        """Setup der Button-Logik"""
        
        # Status-Check Callbacks setzen
        self.button1.set_work_active_check(self._is_work_active)
        self.button2.set_work_active_check(self._is_work_active)
        
        # Button 1: Arbeitsphase starten (wenn IDLE oder WORK_DONE)
        self.button1.on_short_press(self._on_button1_press)
        
        # Button 2: Pause, Storno, Session beenden
        self.button2.on_short_press(self._start_break)
        self.button2.on_cancel(self._cancel_last_action)
        self.button2.on_end_session(self._end_session)
    
    def _is_work_active(self):
        """Prüft ob gerade eine Arbeitsphase läuft"""
        return self.state == "WORKING"
    
    def _on_button1_press(self):
        """Button 1 Handler - Arbeitsphase starten"""
        if self.state == "WORKING":
            print("⚠️ Arbeitsphase läuft bereits!")
            return
        
        if self.state == "BREAK":
            print("⚠️ Pause läuft - warte bis sie beendet ist!")
            return
        
        # IDLE oder WORK_DONE -> neue Arbeitsphase starten
        self._start_work_session()
    
    # ═══════════════════════════════════════════════════════════════
    # WORK SESSION
    # ═══════════════════════════════════════════════════════════════
    
    def _start_work_session(self):
        """Startet eine neue Arbeitsphase"""
        
        print("\n" + "="*60)
        print(f"📚 ARBEITSPHASE GESTARTET ({WORK_DURATION // 60} Min)")
        print("="*60)
        
        self.state = "WORKING"
        
        # Timer-Stop Event zurücksetzen
        self.timer_stop_event.clear()
        
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
        
        # Timer in separatem Thread starten (non-blocking!)
        self.timer_thread = Thread(target=self._run_work_timer, daemon=True)
        self.timer_thread.start()
    
    def _run_work_timer(self):
        """⏱️ Work Timer: 30 Minuten (läuft im separaten Thread)"""
        
        start_time = time.time()
        
        while time.time() - start_time < WORK_DURATION:
            # Prüfen ob Timer gestoppt werden soll (Storno/Session Ende)
            if self.timer_stop_event.is_set():
                print("\n⚠️ Timer wurde gestoppt")
                return
            
            # Prüfen ob State noch WORKING
            if self.state != "WORKING":
                print("\n⚠️ Arbeitsphase wurde unterbrochen")
                return
            
            elapsed = time.time() - start_time
            remaining = WORK_DURATION - elapsed
            
            # CO2 während Arbeit überwachen
            self._monitor_co2()
            
            # Fortschritt anzeigen (jede Minute)
            remaining_min = int(remaining // 60)
            remaining_sec = int(remaining % 60)
            print(f"\r⏱️ Arbeit: {remaining_min:02d}:{remaining_sec:02d} verbleibend   ", 
                  end='', flush=True)
            
            sleep(1)
        
        # Timer regulär abgelaufen - NUR wenn noch WORKING
        if self.state == "WORKING":
            self._work_timer_finished()
    
    def _work_timer_finished(self):
        """Wird aufgerufen wenn der Arbeitstimer abgelaufen ist"""
        
        print(f"\n\n" + "="*60)
        print("⏰ ARBEITSPHASE ABGELAUFEN!")
        print("="*60)
        
        # Speichere Arbeitszeit
        self.total_work_time += WORK_DURATION
        
        # Buzzer Signal
        self.buzzer.long_beep(1.0)
        
        # State auf WORK_DONE - wartet auf User-Entscheidung
        self.state = "WORK_DONE"
        
        print("\n🎯 WÄHLE DEINE NÄCHSTE AKTION:")
        print("  ┌─────────────────────────────────────────────┐")
        print(f"  │ Button 1 → Nächste Arbeitsphase ({WORK_DURATION // 60} Min)  │")
        print(f"  │ Button 2 → Pause starten ({BREAK_DURATION // 60} Min)        │")
        print("  │ Button 2 (7s) → Session beenden            │")
        print("  └─────────────────────────────────────────────┘")
        print("\n👉 Warte auf Button-Eingabe...\n")
    
    # ═══════════════════════════════════════════════════════════════
    # BREAK SESSION
    # ═══════════════════════════════════════════════════════════════
    
    def _start_break(self):
        """Pause starten - nur wenn Arbeitsphase beendet (WORK_DONE)"""
        
        if self.state == "WORKING":
            print("\n⚠️ Arbeitsphase läuft noch!")
            print("   Warte bis Timer abgelaufen ist oder halte Button 2 für 3s (Storno)")
            return
        
        if self.state == "BREAK":
            print("⚠️ Pause läuft bereits!")
            return
        
        if self.state == "IDLE" and not self.session_id:
            print("⚠️ Zuerst Arbeitsphase mit Button 1 starten!")
            return
        
        if self.state not in ["WORK_DONE", "IDLE"]:
            print(f"⚠️ Pause nicht möglich im Status: {self.state}")
            return
        
        print("\n" + "="*60)
        print(f"☕ PAUSENPHASE GESTARTET ({BREAK_DURATION // 60} Min)")
        print("="*60)
        print("\n📡 Signalisiere Break an PiTop 2...")
        
        self.state = "BREAK"
        
        # Timer-Stop Event zurücksetzen
        self.timer_stop_event.clear()
        
        # Action History
        self.action_history.append({
            'type': 'break_start',
            'time': time.time()
        })
        
        # UI Feedback
        self.buzzer.beep(0.2)
        
        # Discord
        self.notify.send_work_finished()

        # DB: Pause Count erhöhen
        self.db.increment_pause_count(self.session_id)

        # DB-Status update
        self._update_break_status('break')
        
        # Break-Timer in separatem Thread starten
        break_thread = Thread(target=self._run_break_timer, daemon=True)
        break_thread.start()
    
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
    
    def _run_break_timer(self):
        """⏱️ Break Timer: 10 Minuten (läuft im separaten Thread)"""
        
        print(f"\n⏱️ Break-Timer: {BREAK_DURATION // 60} Minuten")
        print("👣 PiTop 2 zählt jetzt Schritte...\n")
        
        start_time = time.time()
        
        while time.time() - start_time < BREAK_DURATION:
            # Prüfen ob Timer gestoppt werden soll
            if self.timer_stop_event.is_set():
                print("\n⚠️ Break wurde gestoppt")
                return
            
            # Prüfen ob State noch BREAK
            if self.state != "BREAK":
                print("\n⚠️ Pause wurde unterbrochen")
                return
            
            elapsed = time.time() - start_time
            remaining = BREAK_DURATION - elapsed
            
            # Fortschritt anzeigen
            remaining_min = int(remaining // 60)
            remaining_sec = int(remaining % 60)
            print(f"\r⏱️ Pause: {remaining_min:02d}:{remaining_sec:02d} verbleibend   ", 
                  end='', flush=True)
            
            sleep(1)
        
        # Timer regulär abgelaufen
        if self.state == "BREAK":
            self._break_timer_finished()
    
    def _break_timer_finished(self):
        """Wird aufgerufen wenn der Break-Timer abgelaufen ist"""
        
        print(f"\n\n" + "="*60)
        print("☕ PAUSE BEENDET!")
        print("="*60)
        
        # Speichere Pausenzeit
        self.total_break_time += BREAK_DURATION
        
        # Buzzer Signal
        self.buzzer.beep(0.1)
        
        # Update DB
        self._update_break_status('work_ready')
        
        # Discord
        self.notify.send_break_finished()
        
        # State auf IDLE - bereit für nächste Aktion
        self.state = "IDLE"
        
        print("\n🎯 WÄHLE DEINE NÄCHSTE AKTION:")
        print("  ┌─────────────────────────────────────────────┐")
        print(f"  │ Button 1 → Nächste Arbeitsphase ({WORK_DURATION // 60} Min)  │")
        print("  │ Button 2 (7s) → Session beenden            │")
        print("  └─────────────────────────────────────────────┘")
        print("\n👉 Warte auf Button-Eingabe...\n")
    
    # ═══════════════════════════════════════════════════════════════
    # STORNO
    # ═══════════════════════════════════════════════════════════════
    
    def _cancel_last_action(self):
        """Letzte Aktion stornieren (Button 2, 3s)"""
        
        print("\n" + "="*60)
        print("↩️ STORNO - Letzte Aktion wird rückgängig gemacht")
        print("="*60)
        
        # Timer stoppen falls läuft
        self.timer_stop_event.set()
        
        if not self.action_history:
            print("⚠️ Keine Aktion zum Stornieren vorhanden!")
            self.state = "IDLE"
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
        
        print(f"✅ Storno abgeschlossen - Status: {self.state}")
        print("\n🎯 OPTIONEN:")
        print("  Button 1 → Arbeitsphase starten")
        if self.session_id:
            print("  Button 2 → Pause starten (wenn WORK_DONE)")
            print("  Button 2 (7s) → Session beenden")
        print("")
    
    # ═══════════════════════════════════════════════════════════════
    # SESSION BEENDEN
    # ═══════════════════════════════════════════════════════════════
    
    def _end_session(self):
        """Session komplett beenden (Button 2, 7s)"""
        
        print("\n" + "="*60)
        print("🛑 SESSION BEENDET")
        print("="*60)
        
        # Timer stoppen
        self.timer_stop_event.set()
        
        prev_state = self.state
        self.state = "DONE"
        
        # Timer Service stoppen
        self.timer.stop_event.set()
        self.timer.is_running = False
        
        # UI
        self.led.off()
        self.buzzer.long_beep(2.0)
        
        print(f"\n📊 SESSION STATISTIK:")
        print(f"   Vorheriger Status: {prev_state}")
        print(f"   Gesamte Arbeitszeit: {self.total_work_time}s ({self.total_work_time // 60} Min)")
        print(f"   Gesamte Pausenzeit: {self.total_break_time}s ({self.total_break_time // 60} Min)")
        print(f"   Aktionen: {len(self.action_history)}\n")
        
        # Report aus DB holen
        if self.session_id:
            # 1. ZUERST Session in DB beenden (Daten schreiben)
            self.db.end_session(
                self.session_id,
                self.total_work_time,
                self.total_break_time
            )

            # 2. DANN Report holen (mit aktuellen Daten aus DB)
            report_data = self.db.get_session_report_data(self.session_id)

            # 3. Report anzeigen
            if report_data:
                self.notify.print_terminal_report(report_data)
                self.notify.send_session_report(report_data)
        
        # Reset für neue Session
        self.session_id = None
        self.total_work_time = 0
        self.total_break_time = 0
        self.co2_log_counter = 0
        self.action_history.clear()
        self.state = "IDLE"
        
        print("\n" + "="*60)
        print("✅ Session abgeschlossen - Ready für neue Session!")
        print("👉 Drücke Button 1 um neue Session zu starten")
        print("="*60 + "\n")
    
    # ═══════════════════════════════════════════════════════════════
    # CO2 MONITORING
    # ═══════════════════════════════════════════════════════════════
    
    def _monitor_co2(self):
        """🌡️ CO2-Überwachung mit DB-Logging"""
        
        try:
            alarm_status = self.co2.get_alarm_status()
            co2_level = self.co2.read()
            tvoc_level = self.co2.tvoc_level
            
            # Counter erhöhen
            self.co2_log_counter += 1
            
            # Alle 30 Sekunden loggen ODER bei Alarm
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
            pass  # Stille Fehler im Timer-Thread
    
    # ═══════════════════════════════════════════════════════════════
    # MAIN LOOP
    # ═══════════════════════════════════════════════════════════════
    
    def run(self):
        print("✅ System bereit!")
        print(f"📱 User: {config.USER_NAME}")
        print(f"📡 Device: {config.DEVICE_ID}")
        print(f"💾 Supabase: {'✅' if self.db.client else '❌'}")
        print(f"🤖 Discord: {'✅' if self.notify.is_enabled else '❌'}")
        
        print(f"\n⏱️ TIMER-EINSTELLUNGEN:")
        print(f"   Arbeitsphase: {WORK_DURATION // 60} Minuten")
        print(f"   Pausenphase:  {BREAK_DURATION // 60} Minuten")
        
        print("\n🎮 BUTTON-STEUERUNG:")
        print("  ┌─────────────────────────────────────────┐")
        print("  │ BUTTON 1 (D0):                          │")
        print("  │   • Kurz = Arbeitsphase starten         │")
        print("  │     (in IDLE oder nach Timer-Ablauf)    │")
        print("  ├─────────────────────────────────────────┤")
        print("  │ BUTTON 2 (D1):                          │")
        print("  │   • Kurz = Pause starten                │")
        print("  │     (nur nach Arbeitsphase-Ende)        │")
        print("  │   • 3s halten = STORNO                  │")
        print("  │   • 7s halten = SESSION BEENDEN         │")
        print("  └─────────────────────────────────────────┘")
        
        print("\n⚠️ WICHTIG:")
        print("   Nach Timer-Ablauf STOPPT das System!")
        print("   Du musst Button drücken für nächste Aktion.")
        
        print("\n" + "="*60)
        print("👉 Starte Session mit Button 1!")
        print("="*60 + "\n")
        
        try:
            while True:
                # Hauptschleife - Buttons werden via Callbacks verarbeitet
                sleep(0.5)
        
        except KeyboardInterrupt:
            self._cleanup()
    
    def _cleanup(self):
        print("\n\n🛑 System wird beendet...")
        
        # Timer stoppen
        self.timer_stop_event.set()
        
        if self.state not in ["IDLE", "DONE"]:
            print(f"⚠️ Session im Status '{self.state}' beendet!")
        
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