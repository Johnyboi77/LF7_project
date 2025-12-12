#!/usr/bin/env python3
"""
LED Control
PiTop steuert Farben selbst - wir nur ein/aus/blink
"""

import threading
from time import sleep
from . import IS_PITOP, PitopLED

class LED:
    def __init__(self):
        self.blink_thread = None
        self.blink_stop = False
        
        if IS_PITOP:
            self.led = PitopLED("D2")
        else:
            self.led = None
    
    def on(self):
        """LED einschalten"""
        if self.led:
            self.led.on()
        self.blink_stop = True
        print("🔴 LED an")
    
    def off(self):
        """LED ausschalten"""
        if self.led:
            self.led.off()
        self.blink_stop = True
        print("⬜ LED aus")
    
    def blink(self, on_time=0.5, off_time=0.5):
        """LED blinken lassen"""
        self.blink_stop = False
        
        if self.blink_thread and self.blink_thread.is_alive():
            self.blink_stop = True
            self.blink_thread.join()
        
        self.blink_thread = threading.Thread(
            target=self._blink_loop,
            args=(on_time, off_time),
            daemon=True
        )
        self.blink_thread.start()
        print(f"💡 LED blinkt ({on_time}s an, {off_time}s aus)")
    
    def _blink_loop(self, on_time, off_time):
        """Interne Blink-Schleife"""
        while not self.blink_stop:
            if self.led:
                self.led.on()
            sleep(on_time)
            
            if self.blink_stop:
                break
            
            if self.led:
                self.led.off()
            sleep(off_time)