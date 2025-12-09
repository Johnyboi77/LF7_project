# hardware/buzzer.py
import RPi.GPIO as GPIO
import time
from threading import Thread
import config

class Buzzer:
    def __init__(self, pin=config.BUZZER_PIN):
        self.pin = pin
        self.is_buzzing = False
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, GPIO.LOW)
    
    def beep_short(self, times=config.BUZZER_CO2_REPETITIONS):
        """Kurze Pieptöne für CO2-Alarm"""
        if self.is_buzzing:
            return
        
        def _beep():
            self.is_buzzing = True
            for _ in range(times):
                GPIO.output(self.pin, GPIO.HIGH)
                time.sleep(config.BUZZER_CO2_DURATION)
                GPIO.output(self.pin, GPIO.LOW)
                time.sleep(config.BUZZER_CO2_INTERVAL)
            self.is_buzzing = False
        
        Thread(target=_beep, daemon=True).start()
    
    def beep_long(self):
        """Langer Piepton für Timer-Ende"""
        if self.is_buzzing:
            return
        
        def _beep():
            self.is_buzzing = True
            GPIO.output(self.pin, GPIO.HIGH)
            time.sleep(config.BUZZER_TIMER_DURATION)
            GPIO.output(self.pin, GPIO.LOW)
            self.is_buzzing = False
        
        Thread(target=_beep, daemon=True).start()
    
    def cleanup(self):
        GPIO.output(self.pin, GPIO.LOW)
        GPIO.cleanup(self.pin)