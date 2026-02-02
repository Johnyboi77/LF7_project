#!/usr/bin/env python3
"""
CO2 Sensor (SGP30 via I2C)
Verwendet adafruit_sgp30 (system-weit verfügbar)
I2C Address: 0x58
"""

import config

try:
    import board
    import adafruit_sgp30
    SENSOR_AVAILABLE = True
except ImportError:
    SENSOR_AVAILABLE = False
    print("⚠️  adafruit_sgp30 nicht verfügbar - Dummy-Modus")


class CO2Sensor:
    def __init__(self):
        """Initialisiert CO2 Sensor"""
        self._co2_level = 400
        self._tvoc_level = 0
        self.sensor = None
        
        if SENSOR_AVAILABLE:
            try:
                i2c = board.I2C()
                self.sensor = adafruit_sgp30.Adafruit_SGP30(i2c)
                self.sensor.iaq_init()
                self.sensor.set_iaq_baseline(0x8973, 0x8AAE)
                print(f"✅ CO2 Sensor (SGP30) auf I2C initialisiert")
            except Exception as e:
                print(f"⚠️  SGP30 Hardware nicht gefunden: {e}")
                print(f"💡 Sensor läuft im Dummy-Modus")
                self.sensor = None
    
    def read(self):
        """Liest eCO2 Wert in ppm"""
        if self.sensor is None:
            return self._co2_level
        
        try:
            self._co2_level = self.sensor.eCO2
            self._tvoc_level = self.sensor.TVOC
        except Exception as e:
            print(f"⚠️  CO2 Read-Fehler: {e}")
        
        return self._co2_level
    
    @property
    def co2_level(self):
        """Aktueller CO2 Level in ppm"""
        self.read()
        return self._co2_level
    
    @property
    def tvoc_level(self):
        """Total Volatile Organic Compounds (TVOC) in ppb"""
        return self._tvoc_level
    
    def get_alarm_status(self):
        """
        Gibt Alarm-Status zurück:
        - 'ok': CO2 < WARNING_THRESHOLD
        - 'warning': CO2 >= WARNING_THRESHOLD
        - 'critical': CO2 >= CRITICAL_THRESHOLD
        """
        level = self.co2_level
        
        if level >= config.CO2_CRITICAL_THRESHOLD:
            return "critical"
        elif level >= config.CO2_WARNING_THRESHOLD:
            return "warning"
        return "ok"