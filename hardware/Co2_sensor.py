"""
CO2 Sensor (SGP30 oder CCS811)
"""

import config
from hardware import CO2Sensor as HardwareCO2, IS_PITOP

class CO2Sensor:
    def __init__(self):
        self.sensor = HardwareCO2()
        print(f"✅ CO2 Sensor initialisiert ({'REAL' if IS_PITOP else 'MOCK'})")
    
    def read(self):
        """Liest eCO2 Wert in ppm"""
        return self.sensor.co2_level
    
    @property
    def co2_level(self):
        return self.sensor.co2_level
    
    @property
    def tvoc_level(self):
        return self.sensor.tvoc_level
    
    def get_alarm_status(self):
        """Gibt 'ok', 'warning' oder 'critical' zurück"""
        level = self.co2_level
        if level >= config.CO2_CRITICAL_THRESHOLD:
            return "critical"
        elif level >= config.CO2_WARNING_THRESHOLD:
            return "warning"
        return "ok"