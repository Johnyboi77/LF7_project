"""
Mock Hardware für Entwicklung ohne pi-top
Simuliert pitop API perfekt
"""

from time import sleep, time
from threading import Thread, Timer
import random

# ===== MOCK BUTTON =====
class Button:
    def __init__(self, port):
        self.port = port
        self._short_press_callback = None
        self._long_press_callback = None
        self._double_click_callback = None
        print(f"🔌 Mock Button [{port}] erstellt")
    
    def on_short_press(self, callback):
        self._short_press_callback = callback
        print(f"  → Short Press Callback registriert")
    
    def on_long_press(self, callback):
        self._long_press_callback = callback
        print(f"  → Long Press Callback registriert")
    
    def on_double_click(self, callback):
        self._double_click_callback = callback
        print(f"  → Double Click Callback registriert")
    
    # Test-Helfer
    def simulate_short_press(self):
        print(f"🔘 [{self.port}] SHORT PRESS simuliert")
        if self._short_press_callback:
            self._short_press_callback()
    
    def simulate_long_press(self):
        print(f"🔘 [{self.port}] LONG PRESS simuliert")
        if self._long_press_callback:
            self._long_press_callback()
    
    def simulate_double_click(self):
        print(f"🔘 [{self.port}] DOUBLE CLICK simuliert")
        if self._double_click_callback:
            self._double_click_callback()


# ===== MOCK LED =====
class LED:
    def __init__(self, port):
        self.port = port
        self.state = False
        print(f"💡 Mock LED [{port}] erstellt")
    
    def on(self):
        self.state = True
        print(f"💡 [{self.port}] ON")
    
    def off(self):
        self.state = False
        print(f"💡 [{self.port}] OFF")
    
    def blink(self, on_time=0.5, off_time=0.5, n=None):
        print(f"💡 [{self.port}] BLINK (on={on_time}s, off={off_time}s, n={n})")
        self.state = "blinking"


# ===== MOCK BUZZER =====
class Buzzer:
    def __init__(self, port):
        self.port = port
        self.is_on = False
        print(f"🔊 Mock Buzzer [{port}] erstellt")
    
    def on(self):
        self.is_on = True
        print(f"🔊 [{self.port}] ON")
    
    def off(self):
        self.is_on = False
        print(f"🔊 [{self.port}] OFF")
    
    def beep(self, duration=0.2):
        print(f"🔊 [{self.port}] BEEP ({duration}s)")
        sleep(duration)
    
    def double_beep(self):
        print(f"🔊 [{self.port}] DOUBLE BEEP")
        self.beep(0.1)
        sleep(0.1)
        self.beep(0.1)
    
    def long_beep(self):
        print(f"🔊 [{self.port}] LONG BEEP")
        self.beep(1.0)


# ===== MOCK MINISCREEN =====
class Miniscreen:
    def __init__(self):
        print(f"📺 Mock Miniscreen erstellt")
        self.current_text = ""
    
    def display_multiline_text(self, text):
        self.current_text = text
        print(f"📺 Screen Update:\n{text}\n{'─'*30}")
    
    def clear(self):
        self.current_text = ""
        print(f"📺 Screen cleared")


# ===== MOCK CO2 SENSOR =====
class CO2Sensor:
    def __init__(self):
        self.co2 = 450
        self.tvoc = 50
        print("🌡️ Mock CO2 Sensor (SGP30) erstellt")
    
    def read(self):
        # Simuliere realistische Werte
        self.co2 += random.randint(-30, 50)
        self.co2 = max(400, min(2000, self.co2))
        self.tvoc = random.randint(0, 100)
        return self.co2, self.tvoc
    
    @property
    def co2_level(self):
        self.read()
        return self.co2
    
    @property
    def tvoc_level(self):
        return self.tvoc
    
    def get_alarm_status(self):
        if self.co2 >= 1500:
            return "critical"
        elif self.co2 >= 1000:
            return "warning"
        return "ok"


# ===== MOCK STEP COUNTER =====
class StepCounter:
    def __init__(self):
        self.steps = 0
        self.is_counting = False
        self._step_thread = None
        print("🚶 Mock Step Counter (BMA400) erstellt")
    
    def start_counting(self):
        self.steps = 0
        self.is_counting = True
        print("🚶 Schrittzähler GESTARTET (Mock)")
        
        # Simuliere Schritte im Hintergrund
        def simulate():
            while self.is_counting:
                self.steps += random.randint(0, 3)
                sleep(1)
        
        self._step_thread = Thread(target=simulate, daemon=True)
        self._step_thread.start()
    
    def stop_counting(self):
        self.is_counting = False
        print(f"🚶 Schrittzähler GESTOPPT: {self.steps} Schritte (Mock)")
        return self.steps
    
    def read_steps(self):
        return self.steps
    
    @property
    def current_steps(self):
        return self.steps
    
    def calculate_distance(self, step_length_cm=70):
        distance = (self.steps * step_length_cm) / 100
        return round(distance, 2)
    
    def calculate_calories(self, weight_kg=60):
        calories = self.steps * 0.04 * (weight_kg / 70)
        return round(calories, 1)