#!/usr/bin/env python3
"""
Button 1 - Work Session Control
PORT: D0 (HARDCODED)
- Short Press: Start Work Session
- Long Press (5s): End Session
- Double Click: Cancel
"""

import threading
from time import time
from pitop import Button
import config


class Button1:
    def __init__(self):
        self.pin_name = "D0"  # 🔒 HARDCODED
        self.press_start = None
        self.last_press_time = 0
        self.last_release_time = 0
        self.short_press_cb = None
        self.long_press_cb = None
        self.double_click_cb = None
        self.click_count = 0
        self.double_click_timer = None
        
        # Direkt PiTop Button erstellen
        self.button = Button(self.pin_name)
        self.button.when_pressed = self._on_press
        self.button.when_released = self._on_release
        
        print(f"✅ Button1 auf {self.pin_name} initialisiert")
    
    def _on_press(self):
        self.press_start = time()
    
    def _on_release(self):
        if not self.press_start:
            return
        
        duration = time() - self.press_start
        now = time()
        
        # Long Press (5+ Sekunden)
        if duration >= config.END_SESSION_PRESS:
            self.click_count = 0
            if self.double_click_timer:
                self.double_click_timer.cancel()
            if self.long_press_cb:
                self.long_press_cb()
            self.last_release_time = now
        
        # Short Press
        elif duration <= config.SHORT_PRESS_MAX:
            self.click_count += 1
            
            if self.double_click_timer:
                self.double_click_timer.cancel()
            
            if self.click_count == 1:
                self.double_click_timer = threading.Timer(
                    config.DOUBLE_CLICK_INTERVAL,
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
        if self.click_count == 1 and self.short_press_cb:
            self.short_press_cb()
        self.click_count = 0
    
    def on_short_press(self, callback):
        self.short_press_cb = callback
    
    def on_long_press(self, callback):
        self.long_press_cb = callback
    
    def on_double_click(self, callback):
        self.double_click_cb = callback