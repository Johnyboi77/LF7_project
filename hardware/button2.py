# hardware/button2.py
"""
Button 2 - Pausenzeit
- Kurz (< 2s):    Start Pausenzeit
- Doppelt (kurz): Reset Timer + Report
"""

import RPi.GPIO as GPIO
import time
import config

class Button2:
    def __init__(self, pin=config.BUTTON2_PIN, 
                 short_press_callback=None, 
                 double_click_callback=None):
        self.pin = pin
        self.short_press_callback = short_press_callback
        self.double_click_callback = double_click_callback
        
        # Tracking
        self.press_start_time = None
        self.last_press_time = 0
        self.click_count = 0
        self.is_pressed = False
        
        # GPIO Setup
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        # Event Detection
        GPIO.add_event_detect(
            self.pin, 
            GPIO.BOTH, 
            callback=self._handle_event, 
            bouncetime=50
        )
        
        print(f"✅ Button 2 initialisiert (GPIO {self.pin})")
        print("   < 2s: Pausenzeit | 2x: Reset")
    
    def _handle_event(self, channel):
        """Erkennt Kurz und Doppel"""
        
        if GPIO.input(self.pin) == GPIO.LOW:
            # Button gedrückt
            self.press_start_time = time.time()
            self.is_pressed = True
            
        else:
            # Button losgelassen
            if self.press_start_time is not None and self.is_pressed:
                press_duration = time.time() - self.press_start_time
                current_time = time.time()
                
                # Kurz: < 2 Sekunden
                if press_duration < config.SHORT_PRESS_MAX:
                    # Doppelklick-Erkennung
                    time_since_last = current_time - self.last_press_time
                    
                    if time_since_last < config.DOUBLE_CLICK_INTERVAL:
                        # DOPPELKLICK!
                        self.click_count += 1
                        
                        if self.click_count >= 2:
                            print(f"🔴 Button 2 DOPPELKLICK → RESET + REPORT")
                            self.click_count = 0
                            
                            if self.double_click_callback:
                                self.double_click_callback()
                    else:
                        # Erster Klick - warten auf zweiten
                        self.click_count = 1
                        self.last_press_time = current_time
                        
                        # Timer für verzögerte Ausführung
                        import threading
                        threading.Timer(
                            config.DOUBLE_CLICK_INTERVAL + 0.1, 
                            self._check_single_click
                        ).start()
                
                # Lang: 2+ Sekunden (ignorieren bei Button 2)
                else:
                    print(f"⚠️  Button 2: {press_duration:.1f}s (zu lang)")
                
                self.press_start_time = None
                self.is_pressed = False
    
    def _check_single_click(self):
        """Prüft ob es ein einzelner Klick war"""
        if self.click_count == 1:
            print(f"🟩 Button 2 KURZ → PAUSENZEIT")
            self.click_count = 0
            
            if self.short_press_callback:
                self.short_press_callback()
    
    def cleanup(self):
        """Cleanup GPIO"""
        try:
            GPIO.remove_event_detect(self.pin)
            GPIO.cleanup(self.pin)
        except:
            pass
