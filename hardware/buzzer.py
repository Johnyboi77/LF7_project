#!/usr/bin/env python3
"""
Buzzer für Signale und Alarme
PORT: D3 (HARDCODED)
"""

from pitop import Buzzer as PitopBuzzer
import threading
from time import sleep

# Config-Werte mit Fallback
try:
    import config
    BUZZER_CO2_DURATION = config.BUZZER_CO2_DURATION
    BUZZER_CO2_INTERVAL = config.BUZZER_CO2_INTERVAL
    BUZZER_CO2_REPETITIONS = config.BUZZER_CO2_REPETITIONS
    BUZZER_TIMER_DURATION = config.BUZZER_TIMER_DURATION
except ImportError:
    BUZZER_CO2_DURATION = 0.2
    BUZZER_CO2_INTERVAL = 0.3
    BUZZER_CO2_REPETITIONS = 3
    BUZZER_TIMER_DURATION = 1.0

class Buzzer:
    def __init__(self):
        self.pin_name = "D3"  # 🔒 HARDCODED
        self.buzzer = PitopBuzzer(self.pin_name)
        self.beep_thread = None
        
        print(f"✅ Buzzer auf {self.pin_name} initialisiert")
    
    def on(self):
        """Buzzer dauerhaft einschalten"""
        self.buzzer.on()
    
    def off(self):
        """Buzzer ausschalten"""
        self.buzzer.off()
    
    def beep(self, duration=None):
        """Kurzer Beep"""
        duration = duration or BUZZER_CO2_DURATION  
        self.buzzer.on()
        sleep(duration)
        self.buzzer.off()
    
    def long_beep(self, duration=None):
        """Langer Beep für Timer"""
        duration = duration or BUZZER_TIMER_DURATION  
        self.buzzer.on()
        sleep(duration)
        self.buzzer.off()
    
    def double_beep(self):
        """Doppel-Beep Pattern"""
        self.beep(0.1)
        sleep(0.1)
        self.beep(0.1)
    
    def co2_alarm(self):
        """CO2 Alarm Pattern (asynchron)"""
        thread = threading.Thread(target=self._co2_pattern, daemon=True)
        thread.start()
    
    def _co2_pattern(self):
        """CO2 Alarm: Mehrfach Beep"""
        for _ in range(BUZZER_CO2_REPETITIONS): 
            self.beep(BUZZER_CO2_DURATION)        
            sleep(BUZZER_CO2_INTERVAL)            
    
    def timer_alarm(self):
        """Timer Ende: Langer Beep"""
        self.long_beep(BUZZER_TIMER_DURATION) 
    
    def cleanup(self):
        """Ressourcen freigeben"""
        self.off()
        self.buzzer.close()