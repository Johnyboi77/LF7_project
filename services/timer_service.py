# services/timer_service.py
"""
Timer Service mit Session-Tracking
Zählt Arbeits- und Pausenzeiten mit
"""

import time
from threading import Thread, Event
from enum import Enum
import config

class TimerMode(Enum):
    IDLE = "idle"
    WORKING = "working"
    BREAK = "break"

class TimerService:
    def __init__(self, buzzer, notification_service, db_manager):
        self.buzzer = buzzer
        self.notification_service = notification_service
        self.db_manager = db_manager
        
        self.mode = TimerMode.IDLE
        self.remaining_time = 0
        self.is_running = False
        self.thread = None
        self.stop_event = Event()
        
        # Session Tracking
        self.total_work_time = 0      # Gesamt gelernte Zeit
        self.total_break_time = 0     # Gesamt pausierte Zeit
        self.work_sessions_count = 0  # Anzahl abgeschlossener Lerneinheiten
        self.break_sessions_count = 0 # Anzahl abgeschlossener Pausen
    
    def start_work_timer(self):
        """Button 1 kurz: Arbeitszeit starten"""
        
        # Laufenden Timer überschreiben
        if self.is_running:
            print(f"⚠️  Laufender Timer wird überschrieben!")
            self.stop_event.set()
            time.sleep(0.1)
        
        # Neuen Timer starten
        self.mode = TimerMode.WORKING
        self.remaining_time = config.WORK_DURATION
        self.is_running = True
        self.stop_event.clear()
        
        print("\n" + "="*50)
        print("🟦 ARBEITSZEIT GESTARTET: 30 Minuten")
        print("="*50)
        
        # Thread starten
        self.thread = Thread(target=self._run_timer, daemon=True)
        self.thread.start()
    
    def start_break_timer(self):
        """Button 2 kurz: Pausenzeit starten"""
        
        if self.is_running:
            print(f"⚠️  Laufender Timer wird überschrieben!")
            self.stop_event.set()
            time.sleep(0.1)
        
        self.mode = TimerMode.BREAK
        self.remaining_time = config.BREAK_DURATION
        self.is_running = True
        self.stop_event.clear()
        
        print("\n" + "="*50)
        print("🟩 PAUSENZEIT GESTARTET: 10 Minuten")
        print("="*50)
        
        self.thread = Thread(target=self._run_timer, daemon=True)
        self.thread.start()
    
    def reset(self):
        """Button 1/2 lang: Reset Timer"""
        if self.is_running or self.remaining_time > 0:
            print("\n" + "="*50)
            print("🔄 RESET - Timer zurückgesetzt")
            print("="*50 + "\n")
        
        self.is_running = False
        self.remaining_time = 0
        self.mode = TimerMode.IDLE
        self.stop_event.set()
    
    def get_session_stats(self):
        """Gibt Session-Statistiken zurück"""
        return {
            'total_work_time': self.total_work_time,
            'total_break_time': self.total_break_time,
            'work_sessions_count': self.work_sessions_count,
            'break_sessions_count': self.break_sessions_count
        }
    
    def reset_session_stats(self):
        """Setzt Session-Statistiken zurück (für neue Session)"""
        self.total_work_time = 0
        self.total_break_time = 0
        self.work_sessions_count = 0
        self.break_sessions_count = 0
    
    def _run_timer(self):
        """Timer Loop mit Live-Countdown"""
        last_display = None
        start_time = time.time()
        
        while self.remaining_time > 0 and not self.stop_event.is_set():
            if self.is_running:
                # Zeit formatieren
                mins = self.remaining_time // 60
                secs = self.remaining_time % 60
                display = f"{mins:02d}:{secs:02d}"
                
                # Countdown ausgeben
                if display != last_display:
                    mode_icon = "🟦" if self.mode == TimerMode.WORKING else "🟩"
                    mode_text = "Arbeitszeit" if self.mode == TimerMode.WORKING else "Pause"
                    
                    print(f"\r{mode_icon} {mode_text}: {display} verbleibend", end="", flush=True)
                    last_display = display
                
                time.sleep(1)
                self.remaining_time -= 1
        
        print()  # Neue Zeile
        
        # Timer abgelaufen → Session-Zeiten aktualisieren
        if self.remaining_time == 0 and self.is_running and not self.stop_event.is_set():
            elapsed_time = int(time.time() - start_time)
            
            if self.mode == TimerMode.WORKING:
                self.total_work_time += elapsed_time
                self.work_sessions_count += 1
            elif self.mode == TimerMode.BREAK:
                self.total_break_time += elapsed_time
                self.break_sessions_count += 1
            
            self._timer_finished()
    
    def _timer_finished(self):
        """Timer abgelaufen"""
        
        if self.mode == TimerMode.WORKING:
            print("\n" + "="*50)
            print("⏰ 30 MINUTEN ARBEITSZEIT VORBEI!")
            print("="*50)
            
            self.buzzer.beep_long()
            self.notification_service.send_work_finished()
        
        elif self.mode == TimerMode.BREAK:
            print("\n" + "="*50)
            print("⏰ 10 MINUTEN PAUSE VORBEI!")
            print("="*50)
            
            self.buzzer.beep_long()
            self.notification_service.send_break_finished()
        
        self.mode = TimerMode.IDLE
        self.is_running = False
    
    def get_status(self):
        """Status für externe Abfragen"""
        mins = self.remaining_time // 60
        secs = self.remaining_time % 60
        
        return {
            "mode": self.mode.value,
            "is_running": self.is_running,
            "remaining": self.remaining_time,
            "display": f"{mins:02d}:{secs:02d}"
        }