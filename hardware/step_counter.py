#!/usr/bin/env python3
"""
Step Counter (BMA400 via I2C)
I2C Address: 0x14 (automatisch)
"""

from pitop.pma import BMA400


class StepCounter:
    def __init__(self):
        # BMA400 Accelerometer über I2C (Adresse 0x14 automatisch)
        self.sensor = BMA400()
        self._steps = 0
        print(f"✅ Step Counter (BMA400) auf I2C initialisiert")
    
    def start(self):
        """Step Counting starten"""
        self.sensor.enable_step_counter()
        print("🚶 Step Counter gestartet")
    
    def stop(self):
        """
        Step Counting stoppen und Schritte zurückgeben
        Returns:
            int: Anzahl Schritte
        """
        steps = self.current_steps
        self.sensor.disable_step_counter()
        print(f"⏹️ Step Counter gestoppt: {steps} Schritte")
        return steps
    
    def read(self):
        """Aktuelle Schritte lesen"""
        return self.sensor.step_count
    
    def reset(self):
        """Schrittzähler zurücksetzen"""
        self.sensor.reset_step_counter()
        print("🔄 Step Counter zurückgesetzt")
    
    def get_count(self):
        """Aktuelle Schritte abrufen"""
        return self.sensor.step_count
    
    @property
    def current_steps(self):
        """Property: Aktuelle Schrittanzahl"""
        return self.sensor.step_count