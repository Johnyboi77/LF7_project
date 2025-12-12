import threading
from time import time, sleep
from config import SHORT_PRESS_MAX, END_SESSION_PRESS, DOUBLE_CLICK_INTERVAL
from . import IS_PITOP, PitopButton

class Button:
    def __init__(self, pin_name):
        self.pin_name = pin_name
        self.press_start = None
        self.last_press_time = 0
        self.last_release_time = 0
        self.short_press_cb = None
        self.long_press_cb = None
        self.double_click_cb = None
        self.click_count = 0
        self.double_click_timer = None
        
        if IS_PITOP:
            self.button = PitopButton(pin_name)
            self.button.when_pressed = self._on_press
            self.button.when_released = self._on_release
        else:
            self.button = None
    
    def _on_press(self):
        self.press_start = time()
    
    def _on_release(self):
        if not self.press_start:
            return
        
        duration = time() - self.press_start
        now = time()
        
        # Long Press (5+ Sekunden)
        if duration >= END_SESSION_PRESS:
            self.click_count = 0
            if self.double_click_timer:
                self.double_click_timer.cancel()
            if self.long_press_cb:
                self.long_press_cb()
            self.last_release_time = now
        
        # Short Press
        elif duration <= SHORT_PRESS_MAX:
            self.click_count += 1
            
            # Cancel old timer
            if self.double_click_timer:
                self.double_click_timer.cancel()
            
            # Check für Doppelklick
            if self.click_count == 1:
                # Warte auf 2. Klick
                self.double_click_timer = threading.Timer(
                    DOUBLE_CLICK_INTERVAL,
                    self._single_click_timeout
                )
                self.double_click_timer.start()
            
            elif self.click_count == 2:
                self.double_click_timer.cancel()
                if self.double_click_cb:
                    self.double_click_cb()
                self.click_count = 0
            
            self.last_release_time = now
        
        self.press_start = None
    
    def _single_click_timeout(self):
        """Timeout für Single-Click"""
        if self.click_count == 1 and self.short_press_cb:
            self.short_press_cb()
        self.click_count = 0
    
    def on_short_press(self, callback):
        self.short_press_cb = callback
    
    def on_long_press(self, callback):
        self.long_press_cb = callback
    
    def on_double_click(self, callback):
        self.double_click_cb = callback
    
    def simulate_short_press(self):
        """Für Testing"""
        self.press_start = time()
        sleep(0.5)
        self._on_release()
    
    def simulate_long_press(self):
        """Für Testing"""
        self.press_start = time()
        sleep(5.1)
        self._on_release()