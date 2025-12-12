"""
Mock Hardware für Entwicklung ohne pi-top
Simuliert pitop API perfekt
"""

from time import sleep, time
from threading import Thread, Timer
import random

# ===== MOCK BUTTON =====
class Button:
    """Mock Button - Simuliert Button-Verhalten"""
    
    def __init__(self, port):
        self.port = port
        self.press_callbacks = []
        self.release_callbacks = []
        print(f"🎮 Mock Button [{port}] erstellt")
    
    def when_pressed(self, callback):
        """Registriert Press-Callback"""
        self.press_callbacks.append(callback)
    
    def when_released(self, callback):
        """Registriert Release-Callback"""
        self.release_callbacks.append(callback)
    
    def simulate_press(self, duration=0.5):
        """Simuliert Button-Druck"""
        print(f"👇 [{self.port}] PRESS")
        for cb in self.press_callbacks:
            cb()
    
    def simulate_release(self):
        """Simuliert Button-Release"""
        print(f"👆 [{self.port}] RELEASE")
        for cb in self.release_callbacks:
            cb()


class LED:
    """Mock LED - Simuliert LED-Verhalten"""
    
    def __init__(self, port="D2"):
        self.port = port
        self.is_on = False
        self.blinking = False
        print(f"💡 Mock LED [{port}] erstellt")
    
    def on(self):
        """LED anschalten"""
        self.is_on = True
        self.blinking = False
        print(f"💡 [{self.port}] ON")
    
    def off(self):
        """LED ausschalten"""
        self.is_on = False
        self.blinking = False
        print(f"💡 [{self.port}] OFF")
    
    def blink(self, on_time=0.5, off_time=0.5):
        """LED blinken"""
        self.blinking = True
        print(f"💡 [{self.port}] BLINK (on={on_time}s, off={off_time}s)")


class Buzzer:
    """Mock Buzzer - Simuliert Buzzer-Verhalten"""
    
    def __init__(self, port="D3"):
        self.port = port
        self.is_active = False
        print(f"🔊 Mock Buzzer [{port}] erstellt")
    
    def on(self):
        """Buzzer anschalten"""
        self.is_active = True
        print(f"🔊 [{self.port}] ON")
    
    def off(self):
        """Buzzer ausschalten"""
        self.is_active = False
        print(f"🔊 [{self.port}] OFF")
    
    def beep(self, duration=0.2):
        """Kurzer Beep"""
        print(f"🔊 [{self.port}] BEEP ({duration}s)")
    
    def double_beep(self):
        """Doppelbeep"""
        print(f"🔊 [{self.port}] DOUBLE BEEP")
        self.beep(0.1)
        self.beep(0.1)
    
    def long_beep(self, duration=2.0):
        """Langer Beep - KORRIGIERT"""
        print(f"🔊 [{self.port}] LONG BEEP ({duration}s)")
    
    def co2_alarm(self):
        """CO2 Alarm-Pattern"""
        print(f"🚨 [{self.port}] CO2 ALARM (Beep-Beep-Beep...)")


class CO2Sensor:
    """Mock CO2 Sensor"""
    
    def __init__(self):
        self.co2_level = 450  # Normal
        self.tvoc_level = 50
        print("🌡️  Mock CO2 Sensor erstellt")
    
    def read(self):
        """Liest CO2-Wert"""
        return self.co2_level
    
    def get_alarm_status(self):
        """Gibt Alarm-Status zurück"""
        if self.co2_level >= 800:
            return "critical"
        elif self.co2_level >= 600:
            return "warning"
        return "ok"
    
    def simulate_high_co2(self):
        """Simuliert hohe CO2-Werte"""
        self.co2_level = 850
        print("🌡️  [CO2] Simuliere CRITICAL: 850 ppm")
    
    def simulate_warning_co2(self):
        """Simuliert Warn-CO2-Werte"""
        self.co2_level = 650
        print("🌡️  [CO2] Simuliere WARNING: 650 ppm")
    
    def reset_co2(self):
        """Reset zu Normalwert"""
        self.co2_level = 450
        print("🌡️  [CO2] RESET zu Normal: 450 ppm")


class StepCounter:
    """Mock Step Counter"""
    
    def __init__(self):
        self.steps = 0
        self.is_counting = False
        print("👣 Mock Step Counter erstellt")
    
    def start(self):
        """Schrittzähler starten"""
        self.is_counting = True
        self.steps = 0
        print("👣 Step Counter STARTED")
    
    def stop(self):
        """Schrittzähler stoppen"""
        self.is_counting = False
        print(f"👣 Step Counter STOPPED: {self.steps} Schritte")
        return self.steps
    
    def read(self):
        """Aktuelle Schritte lesen"""
        return self.steps
    
    def reset(self):
        """Reset"""
        self.steps = 0
        print("👣 Step Counter RESET")
    
    def simulate_steps(self, count):
        """Simuliert Schritte"""
        if self.is_counting:
            self.steps += count
            print(f"👣 +{count} Schritte → Total: {self.steps}")
        else:
            print("⚠️  Step Counter nicht aktiv!")