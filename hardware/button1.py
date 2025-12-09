# hardware/button1.py
"""
Button 1 - Arbeitszeit + Session Management
- Kurz (< 2s):     Start Arbeitszeit
- Lang (2-5s):     Reset Timer
- Extra-Lang (5+s): Session beenden + Report
"""

import RPi.GPIO as GPIO
import time
import config

class Button1:
    def __init__(self, pin=config.BUTTON1_PIN, 
                 short_press_callback=None, 
                 long_press_callback=None,
                 end_session_callback=None):
        self.pin = pin
        self.short_press_callback = short_press_callback
        self.long_press_callback = long_press_callback
        self.end_session_callback = end_session_callback
        
        self.press_start_time = None
        self.is_pressed = False
        
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        # Events für Drücken und Loslassen
        GPIO.add_event_detect(self.pin, GPIO.BOTH, 
                             callback=self._handle_event, 
                             bouncetime=50)
        
        print(f"✅ Button 1 initialisiert (GPIO {self.pin})")
        print("   < 2s: Arbeitszeit | 2-5s: Reset | 5+s: Session beenden")
    
    def _handle_event(self, channel):
        """Erkennt 3 verschiedene Drucklängen"""
        
        if GPIO.input(self.pin) == GPIO.LOW:
            # Button wurde gedrückt (runter)
            self.press_start_time = time.time()
            self.is_pressed = True
            
        else:
            # Button wurde losgelassen (hoch)
            if self.press_start_time is not None and self.is_pressed:
                press_duration = time.time() - self.press_start_time
                
                # Extra-Lang: 5+ Sekunden → Session beenden
                if press_duration >= config.END_SESSION_PRESS:
                    print(f"🛑 Button 1 EXTRA-LANG ({press_duration:.1f}s) → SESSION BEENDEN")
                    if self.end_session_callback:
                        self.end_session_callback()
                
                # Lang: 2-5 Sekunden → Reset
                elif press_duration >= config.LONG_PRESS_MIN:
                    print(f"🔴 Button 1 LANG ({press_duration:.1f}s) → RESET")
                    if self.long_press_callback:
                        self.long_press_callback()
                
                # Kurz: < 2 Sekunden → Arbeitszeit starten
                else:
                    print(f"🟦 Button 1 KURZ ({press_duration:.1f}s) → ARBEITSZEIT")
                    if self.short_press_callback:
                        self.short_press_callback()
                
                self.press_start_time = None
                self.is_pressed = False
    
    def cleanup(self):
        GPIO.remove_event_detect(self.pin)
        GPIO.cleanup(self.pin)