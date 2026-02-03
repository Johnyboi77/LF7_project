#!/usr/bin/env python3
"""
LED Control - NUR für CO2-Warnungen
PORT: D2 (HARDCODED)
"""

from pitop import LED as PitopLED
import threading
from time import sleep

# Config-Werte mit Fallback
try:
    import config
    LED_BLINK_FAST = config.LED_BLINK_FAST
except ImportError:
    LED_BLINK_FAST = 0.1   # 100ms für kritische Warnung

class LED:
    def __init__(self):
        self.pin_name = "D2"  # HARDCODED
        self.led = PitopLED(self.pin_name)
        self.blink_thread = None
        self.blink_stop = False
        
        print(f"✅ LED auf {self.pin_name} initialisiert")
    
    def on(self):
        """LED dauerhaft einschalten (CO2 Warning)"""
        self.blink_stop = True
        if self.blink_thread and self.blink_thread.is_alive():
            self.blink_thread.join(timeout=0.1)
        self.led.on()
    
    def off(self):
        """LED ausschalten (CO2 normal)"""
        self.blink_stop = True
        if self.blink_thread and self.blink_thread.is_alive():
            self.blink_thread.join(timeout=0.1)
        self.led.off()
    
    def blink_fast(self):
        """LED schnell blinken (CO2 Critical)"""
        self.blink(LED_BLINK_FAST, LED_BLINK_FAST)
    
    def blink(self, on_time=0.1, off_time=0.1):
        """
        LED blinken lassen (asynchron)
        Args:
            on_time: Zeit in Sekunden (LED an)
            off_time: Zeit in Sekunden (LED aus)
        """
        # Stop existing blink
        if self.blink_thread and self.blink_thread.is_alive():
            self.blink_stop = True
            self.blink_thread.join(timeout=0.5)
        
        self.blink_stop = False
        
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
    
    def cleanup(self):
        """Ressourcen freigeben"""
        self.blink_stop = True
        if self.blink_thread and self.blink_thread.is_alive():
            self.blink_thread.join(timeout=1.0)
        self.led.off()
        self.led.close()