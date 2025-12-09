# hardware/led.py
"""
Rote LED für CO2-Warnung
"""

import RPi.GPIO as GPIO
import config

class LED:
    def __init__(self, pin=config.LED_RED_PIN):
        self.pin = pin
        self.is_on = False
        
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, GPIO.LOW)
        
        print(f"✅ LED initialisiert (GPIO {self.pin})")
    
    def on(self):
        """LED einschalten"""
        if not self.is_on:
            GPIO.output(self.pin, GPIO.HIGH)
            self.is_on = True
            print("🔴 Rote LED: AN")
    
    def off(self):
        """LED ausschalten"""
        if self.is_on:
            GPIO.output(self.pin, GPIO.LOW)
            self.is_on = False
            print("⚫ Rote LED: AUS")
    
    def toggle(self):
        """LED umschalten"""
        if self.is_on:
            self.off()
        else:
            self.on()
    
    def blink(self, times=3, duration=0.5):
        """LED blinken lassen"""
        import time
        for _ in range(times):
            self.on()
            time.sleep(duration)
            self.off()
            time.sleep(duration)
    
    def cleanup(self):
        """Cleanup"""
        self.off()
        GPIO.cleanup(self.pin)
    