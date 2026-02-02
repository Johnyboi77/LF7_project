#!/usr/bin/env python3
"""
Step Counter (BMA400 via I2C)
I2C Address: 0x14 (automatisch)
Mit Fallback zu IMU falls BMA400 nicht verfügbar
"""

import time
from threading import Thread

# Versuche BMA400 zu laden
try:
    from pitop.pma import BMA400
    SENSOR_TYPE = "BMA400"
    print("✅ Using BMA400")
except ImportError:
    try:
        # Fallback: IMU (verfügbar in pitop.pma)
        from pitop.pma import IMU
        SENSOR_TYPE = "IMU"
        print("⚠️  BMA400 nicht verfügbar, verwende IMU")
    except ImportError:
        SENSOR_TYPE = None
        print("⚠️  Kein Sensor verfügbar - Dummy-Modus")


class StepCounter:
    def __init__(self):
        """Initialisiert Step Counter"""
        self._steps = 0
        self.running = False
        self._thread = None
        
        if SENSOR_TYPE == "BMA400":
            # Originaler BMA400 Code
            try:
                self.sensor = BMA400()
                self.sensor_type = "BMA400"
                print(f"✅ Step Counter (BMA400) auf I2C initialisiert")
            except Exception as e:
                print(f"⚠️  BMA400 Init-Fehler: {e}")
                self.sensor = None
                self.sensor_type = None
        
        elif SENSOR_TYPE == "IMU":
            # Fallback: IMU mit manueller Schrittzählung
            try:
                self.sensor = IMU()
                self.sensor_type = "IMU"
                print(f"✅ Step Counter (IMU Fallback) initialisiert")
            except Exception as e:
                print(f"⚠️  IMU Init-Fehler: {e}")
                self.sensor = None
                self.sensor_type = None
        
        else:
            # Dummy-Modus
            self.sensor = None
            self.sensor_type = None
            print(f"⚠️  Step Counter im Dummy-Modus")
    
    def start(self):
        """Step Counting starten"""
        self._steps = 0
        self.running = True
        
        if self.sensor_type == "BMA400":
            # BMA400 Hardware-Zähler
            self.sensor.enable_step_counter()
            print("🚶 Step Counter (BMA400) gestartet")
        
        elif self.sensor_type == "IMU":
            # IMU Software-Zähler
            self._thread = Thread(target=self._count_steps_imu, daemon=True)
            self._thread.start()
            print("🚶 Step Counter (IMU) gestartet")
        
        else:
            # Dummy
            print("🚶 Step Counter (Dummy) gestartet")
    
    def _count_steps_imu(self):
        """Software-Schrittzählung mit IMU"""
        last_magnitude = 0
        step_threshold = 1.2
        cooldown = 0.3
        last_step_time = 0
        
        while self.running:
            try:
                accel = self.sensor.acceleration
                if accel:
                    x, y, z = accel
                    magnitude = (x**2 + y**2 + z**2) ** 0.5
                    
                    current_time = time.time()
                    if (magnitude > step_threshold and 
                        last_magnitude <= step_threshold and
                        current_time - last_step_time > cooldown):
                        self._steps += 1
                        last_step_time = current_time
                    
                    last_magnitude = magnitude
                
                time.sleep(0.1)
            except:
                time.sleep(0.5)
    
    def stop(self):
        """
        Step Counting stoppen und Schritte zurückgeben
        Returns:
            int: Anzahl Schritte
        """
        self.running = False
        
        if self.sensor_type == "BMA400":
            steps = self.current_steps
            self.sensor.disable_step_counter()
        elif self.sensor_type == "IMU":
            if self._thread:
                self._thread.join(timeout=1.0)
            steps = self._steps
        else:
            steps = self._steps
        
        print(f"⏹️  Step Counter gestoppt: {steps} Schritte")
        return steps
    
    def read(self):
        """Aktuelle Schritte lesen"""
        if self.sensor_type == "BMA400":
            return self.sensor.step_count
        else:
            return self._steps
    
    def reset(self):
        """Schrittzähler zurücksetzen"""
        if self.sensor_type == "BMA400":
            self.sensor.reset_step_counter()
        else:
            self._steps = 0
        print("🔄 Step Counter zurückgesetzt")
    
    def get_count(self):
        """Aktuelle Schritte abrufen"""
        return self.read()
    
    @property
    def current_steps(self):
        """Property: Aktuelle Schrittzahl"""
        return self.read()