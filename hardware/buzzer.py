"""
Buzzer für Signale
"""

import threading
from time import sleep
import config
from hardware import Buzzer as HardwareBuzzer, IS_PITOP

class Buzzer:
    def __init__(self, pin_name=None):
        self.pin_name = pin_name or config.BUZZER_PORT
        self.buzzer = HardwareBuzzer(self.pin_name)
        self.beep_thread = None
        
        print(f"✅ Buzzer [{self.pin_name}] initialisiert ({'REAL' if IS_PITOP else 'MOCK'})")
    
    def on(self):
        self.buzzer.on()
    
    def off(self):
        self.buzzer.off()
    
    def beep(self, duration=None):
        duration = duration or config.BUZZER_CO2_DURATION
        self.buzzer.beep(duration)
    
    def long_beep(self, duration=None):
        duration = duration or config.BUZZER_TIMER_DURATION
        self.buzzer.beep(duration)
    
    def double_beep(self):
        self.buzzer.double_beep()
    
    def co2_alarm(self):
        """CO2 Alarm Pattern (asynchron)"""
        thread = threading.Thread(target=self._co2_pattern, daemon=True)
        thread.start()
    
    def _co2_pattern(self):
        for _ in range(config.BUZZER_CO2_REPETITIONS):
            self.beep(config.BUZZER_CO2_DURATION)
            sleep(config.BUZZER_CO2_INTERVAL)
    
    def timer_alarm(self):
        self.long_beep(config.BUZZER_TIMER_DURATION)