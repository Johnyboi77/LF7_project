"""
LED Control
"""

import threading
from time import sleep
import config
from hardware import LED as HardwareLED, IS_PITOP

class LED:
    def __init__(self, pin_name=None):
        self.pin_name = pin_name or config.LED_PORT
        self.led = HardwareLED(self.pin_name)
        self.blink_thread = None
        self.blink_stop = False
        
        print(f"✅ LED [{self.pin_name}] initialisiert ({'REAL' if IS_PITOP else 'MOCK'})")
    
    def on(self):
        self.blink_stop = True
        self.led.on()
    
    def off(self):
        self.blink_stop = True
        self.led.off()
    
    def blink(self, on_time=0.5, off_time=0.5):
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
    
    def _blink_loop(self, on_time, off_time):
        while not self.blink_stop:
            self.led.on()
            sleep(on_time)
            
            if self.blink_stop:
                break
            
            self.led.off()
            sleep(off_time)