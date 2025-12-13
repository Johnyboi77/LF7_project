#!/usr/bin/env python3
"""
CO2 Sensor (SGP30 via I2C)
I2C Address: 0x5A (automatisch)
"""

from pitop.pma import SGP30
import config


class CO2Sensor:
    def __init__(self):
        # SGP30 Sensor über I2C (Adresse 0x5A automatisch)
        self.sensor = SGP30()
        print(f"✅ CO2 Sensor (SGP30) auf I2C initialisiert")
    
    def read(self):
        """Liest eCO2 Wert in ppm"""
        return self.sensor.eco2
    
    @property
    def co2_level(self):
        """Aktueller CO2 Level in ppm"""
        return self.sensor.eco2
    
    @property
    def tvoc_level(self):
        """Total Volatile Organic Compounds (TVOC) in ppb"""
        return self.sensor.tvoc
    
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