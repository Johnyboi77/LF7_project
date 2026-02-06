"""
Button 1 - Work Session Start
PORT: D0 (HARDCODED)
- Short Press: Start Work Session (nur wenn keine aktiv)
"""

from pitop import Button
from time import time

try:
    import config
    SHORT_PRESS_MAX = config.SHORT_PRESS_MAX
except ImportError:
    SHORT_PRESS_MAX = 0.5


class Button1:
    def __init__(self):
        self.pin_name = "D0"  # HARDCODED
        self.press_start = None
        self.short_press_cb = None
        
        # Status-Check Callback (wird von außen gesetzt)
        self.is_work_active_cb = None
        
        # PiTop Button erstellen
        self.button = Button(self.pin_name)
        self.button.when_pressed = self._on_press
        self.button.when_released = self._on_release
        
        print(f"✅ Button1 auf {self.pin_name} initialisiert")
        print(f"   📋 Short Press = Arbeitsphase starten")
    
    def _on_press(self):
        self.press_start = time()
    
    def _on_release(self):
        if not self.press_start:
            return
        
        duration = time() - self.press_start
        self.press_start = None
        
        # Short Press Check
        if duration <= SHORT_PRESS_MAX:
            # Prüfen ob Arbeitsphase bereits aktiv
            if self.is_work_active_cb and self.is_work_active_cb():
                print("⚠️ Button1: Arbeitsphase bereits aktiv - ignoriert")
                return
            
            if self.short_press_cb:
                self.short_press_cb()
    
    def on_short_press(self, callback):
        """Callback für kurzen Tastendruck - Arbeitsphase starten"""
        self.short_press_cb = callback
    
    def set_work_active_check(self, callback):
        """Callback zum Prüfen ob Arbeitsphase aktiv ist"""
        self.is_work_active_cb = callback
    
    def cleanup(self):
        """Ressourcen freigeben"""
        self.button.close()