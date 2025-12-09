# hardware/button2.py
"""
Button 2 - Pausenzeit
- Kurz (< 2s): Start Pausenzeit
- Lang (2+s):  Reset Timer
"""

import RPi.GPIO as GPIO
import time
import config

class Button2:
    def __init__(self, pin=config.BUTTON2_PIN, 
                 short_press_callback=None, 
                 long_press_callback=None):
        self.pin = pin
        self.short_press_callback = short_press_callback
        self.long_press_callback = long_press_callback
        
        self.press_start_time = None
        self.is_pressed = False
        
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        GPIO.add_event_detect(self.pin, GPIO.BOTH, 
                             callback=self._handle_event, 
                             bouncetime=50)
        
        print(f"✅ Button 2 initialisiert (GPIO {self.pin})")
        print("   < 2s: Pausenzeit | 2+s: Reset")
    
    def _handle_event(self, channel):
        """Erkennt 2 verschiedene Drucklängen"""
        
        if GPIO.input(self.pin) == GPIO.LOW:
            # Button gedrückt
            self.press_start_time = time.time()
            self.is_pressed = True
            
        else:
            # Button losgelassen
            if self.press_start_time is not None and self.is_pressed:
                press_duration = time.time() - self.press_start_time
                
                # Lang: 2+ Sekunden → Reset
                if press_duration >= config.LONG_PRESS_MIN:
                    print(f"🔴 Button 2 LANG ({press_duration:.1f}s) → RESET")
                    if self.long_press_callback:
                        self.long_press_callback()
                
                # Kurz: < 2 Sekunden → Pausenzeit
                else:
                    print(f"🟩 Button 2 KURZ ({press_duration:.1f}s) → PAUSENZEIT")
                    if self.short_press_callback:
                        self.short_press_callback()
                
                self.press_start_time = None
                self.is_pressed = False
    
    def cleanup(self):
        GPIO.remove_event_detect(self.pin)
        GPIO.cleanup(self.pin)