"""
Button 2 - Pause & Storno Control
PORT: D1 (HARDCODED)
- Short Press: Start Break (nur wenn keine Arbeitsphase aktiv)
- Long Press (3s): Letzte Aktion stornieren
- Very Long Press (7s): Session komplett beenden
"""

from pitop import Button
import threading
from time import time

try:
    import config
    SHORT_PRESS_MAX = config.SHORT_PRESS_MAX
    CANCEL_PRESS = config.CANCEL_PRESS
    END_SESSION_PRESS = config.END_SESSION_PRESS
except ImportError:
    SHORT_PRESS_MAX = 0.5
    CANCEL_PRESS = 3.0
    END_SESSION_PRESS = 7.0


class Button2:
    def __init__(self):
        self.pin_name = "D1"  # HARDCODED
        self.press_start = None
        
        # Callbacks
        self.short_press_cb = None      # Pause starten
        self.cancel_cb = None           # Letzte Aktion stornieren
        self.end_session_cb = None      # Session beenden
        
        # Status-Check Callbacks
        self.is_work_active_cb = None
        
        # Feedback während Long Press
        self.long_press_timer = None
        self.feedback_3s_given = False
        self.feedback_7s_given = False
        
        # PiTop Button erstellen
        self.button = Button(self.pin_name)
        self.button.when_pressed = self._on_press
        self.button.when_released = self._on_release
        
        print(f"✅ Button2 auf {self.pin_name} initialisiert")
        print(f"   📋 Short Press = Pause starten")
        print(f"   📋 Long Press ({CANCEL_PRESS}s) = Stornieren")
        print(f"   📋 Very Long Press ({END_SESSION_PRESS}s) = Session beenden")
    
    def _on_press(self):
        self.press_start = time()
        self.feedback_3s_given = False
        self.feedback_7s_given = False
        self._start_hold_monitoring()
    
    def _start_hold_monitoring(self):
        """Überwacht wie lange Button gehalten wird für Feedback"""
        def check_hold():
            if self.press_start is None:
                return
            
            duration = time() - self.press_start
            
            if duration >= END_SESSION_PRESS:
                if not self.feedback_7s_given:
                    print(f"\n🔴 Button2: {END_SESSION_PRESS}s erreicht - Session wird beendet!")
                    self.feedback_7s_given = True
                # Nicht mehr weiter überwachen
                return
            
            elif duration >= CANCEL_PRESS:
                if not self.feedback_3s_given:
                    print(f"\n🟡 Button2: {CANCEL_PRESS}s erreicht - Storno bereit (weiter halten für Session-Ende)")
                    self.feedback_3s_given = True
                # Weiter überwachen für 7s
                self.long_press_timer = threading.Timer(0.1, check_hold)
                self.long_press_timer.start()
            
            else:
                # Weiter überwachen
                self.long_press_timer = threading.Timer(0.1, check_hold)
                self.long_press_timer.start()
        
        self.long_press_timer = threading.Timer(0.1, check_hold)
        self.long_press_timer.start()
    
    def _on_release(self):
        if not self.press_start:
            return
        
        # Timer stoppen
        if self.long_press_timer:
            self.long_press_timer.cancel()
            self.long_press_timer = None
        
        duration = time() - self.press_start
        self.press_start = None
        
        # Very Long Press (7+ Sekunden) - Session beenden
        if duration >= END_SESSION_PRESS:
            print("🔴 Button2: Session beenden ausgelöst")
            if self.end_session_cb:
                self.end_session_cb()
            return
        
        # Long Press (3-7 Sekunden) - Stornieren
        if duration >= CANCEL_PRESS:
            print("🟡 Button2: Storno ausgelöst")
            if self.cancel_cb:
                self.cancel_cb()
            return
        
        # Short Press - Pause starten
        if duration <= SHORT_PRESS_MAX:
            
            # Prüfen ob Arbeitsphase aktiv - Pause nur möglich wenn KEINE Arbeit läuft
            work_active = self.is_work_active_cb() if self.is_work_active_cb else False
            
            if work_active:
                print("⚠️ Button2: Arbeitsphase läuft noch - Pause nicht möglich")
                return
            
            if self.short_press_cb:
                self.short_press_cb()
    
    def on_short_press(self, callback):
        """Callback für kurzen Tastendruck - Pause starten"""
        self.short_press_cb = callback
    
    def on_cancel(self, callback):
        """Callback für Long Press (3s) - Letzte Aktion stornieren"""
        self.cancel_cb = callback
    
    def on_end_session(self, callback):
        """Callback für Very Long Press (7s) - Session beenden"""
        self.end_session_cb = callback
    
    def set_work_active_check(self, callback):
        """Callback zum Prüfen ob Arbeitsphase aktiv ist"""
        self.is_work_active_cb = callback
    
    def cleanup(self):
        """Ressourcen freigeben"""
        if self.long_press_timer:
            self.long_press_timer.cancel()
        self.button.close()