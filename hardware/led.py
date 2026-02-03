#!/usr/bin/env python3
"""
LED Control mit Blink-Support
PORT: D2 (HARDCODED)
"""

from hardware import LED as PitopLED
import threading
from time import sleep

class LED:
    def __init__(self):
        self.pin_name = "D2"  # 🔒 HARDCODED
        self.led = PitopLED(self.pin_name)
        self.blink_thread = None
        self.blink_stop = False
        
        print(f"✅ LED auf {self.pin_name} initialisiert")
    
    def on(self):
        """LED dauerhaft einschalten"""
        self.blink_stop = True
        self.led.on()
    
    def off(self):
        """LED ausschalten"""
        self.blink_stop = True
        self.led.off()
    
    def blink(self, on_time=0.5, off_time=0.5):
        """
        LED blinken lassen (asynchron)
        Args:
            on_time: Zeit in Sekunden (LED an)
            off_time: Zeit in Sekunden (LED aus)
        """
        self.blink_stop = False
        
        # Stop existing blink
        if self.blink_thread and self.blink_thread.is_alive():
            self.blink_stop = True
            self.blink_thread.join()
        
        # Start new blink thread
        self.blink_thread = threading.Thread(
            target=self._blink_loop,
            args=(on_time, off_time),
            daemon=True
        )
        self.blink_thread.start()
    
    def _blink_loop(self, on_time, off_time):
        """Internal blink loop"""
        while not self.blink_stop:
            self.led.on()
            sleep(on_time)
            
            if self.blink_stop:
                break
            
            self.led.off()
            sleep(off_time)
    
    def pulse(self):
        """LED pulsieren lassen (wenn von PiTop unterstützt)"""
        if hasattr(self.led, 'pulse'):
            self.led.pulse()