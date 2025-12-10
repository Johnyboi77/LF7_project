# hardware/button1.py
"""
Button 1 - Arbeitszeit + Session Management
- Kurz (< 2s):     Start Arbeitszeit
- Doppelt (kurz):  Reset Timer + Report
- Extra-Lang (5+s): Session beenden + Report
"""

import RPi.GPIO as GPIO
import time
import config

class Button1:
    def __init__(self, pin=config.BUTTON1_PIN, 
                 short_press_callback=None, 
                 double_click_callback=None,
                 long_press_callback=None):
        self.pin = pin
        self.short_press_callback = short_press_callback
        self.double_click_callback = double_click_callback
        self.long_press_callback = long_press_callback
        
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
        
        print(f"✅ Button 1 initialisiert (GPIO {self.pin})")
        print("   < 2s: Arbeitszeit | 2x: Reset | 5+s: Session Ende")
    
    def _handle_event(self, channel):
        """Erkennt Kurz, Doppel, Extra-Lang"""
        
        if GPIO.input(self.pin) == GPIO.LOW:
            # Button gedrückt
            self.press_start_time = time.time()
            self.is_pressed = True
            
        else:
            # Button losgelassen
            if self.press_start_time is not None and self.is_pressed:
                press_duration = time.time() - self.press_start_time
                current_time = time.time()
                
                # Extra-Lang: 5+ Sekunden → Session beenden
                if press_duration >= config.END_SESSION_PRESS:
                    print(f"🛑 Button 1 EXTRA-LANG ({press_duration:.1f}s) → SESSION BEENDEN")
                    self.click_count = 0  # Reset Click-Counter
                    
                    if self.long_press_callback:
                        self.long_press_callback()
                
                # Kurz: < 2 Sekunden
                elif press_duration < config.SHORT_PRESS_MAX:
                    # Doppelklick-Erkennung
                    time_since_last = current_time - self.last_press_time
                    
                    if time_since_last < config.DOUBLE_CLICK_INTERVAL:
                        # DOPPELKLICK!
                        self.click_count += 1
                        
                        if self.click_count >= 2:
                            print(f"🔴 Button 1 DOPPELKLICK → RESET + REPORT")
                            self.click_count = 0
                            
                            if self.double_click_callback:
                                self.double_click_callback()
                    else:
                        # Erster Klick - warten auf zweiten
                        self.click_count = 1
                        self.last_press_time = current_time
                        
                        # Timer für verzögerte Ausführung (falls kein zweiter Klick kommt)
                        import threading
                        threading.Timer(
                            config.DOUBLE_CLICK_INTERVAL + 0.1, 
                            self._check_single_click
                        ).start()
                
                # 2-5 Sekunden: Ignorieren (zwischen Kurz und Extra-Lang)
                else:
                    print(f"⚠️  Button 1: {press_duration:.1f}s (zu lang für Kurz, zu kurz für Session-Ende)")
                
                self.press_start_time = None
                self.is_pressed = False
    
    def _check_single_click(self):
        """Prüft ob es ein einzelner Klick war (kein Doppelklick)"""
        if self.click_count == 1:
            print(f"🟦 Button 1 KURZ → ARBEITSZEIT")
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
