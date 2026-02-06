"""CO2 Sensor (SGP30) - Ultra-robust
   PORT: I2C (einer der I2C Port)
"""
import config
import time

try:
    import board
    import adafruit_sgp30
    SENSOR_AVAILABLE = True
except ImportError:
    SENSOR_AVAILABLE = False

class CO2Sensor:
    def __init__(self):
        self._co2_level = 400
        self._tvoc_level = 0
        self.sensor = None
        self.errors = 0
        self.last_good_read = time.time()
        
        if SENSOR_AVAILABLE:
            try:
                i2c = board.I2C() # HARDCODED (einer der I2C Port)
                self.sensor = adafruit_sgp30.Adafruit_SGP30(i2c)
                self.sensor.iaq_init()
                time.sleep(1)
                self.sensor.set_iaq_baseline(0x8973, 0x8AAE)
                
                # Erste Messung (kann fehlschlagen)
                try:
                    self._co2_level = self.sensor.eCO2
                    self._tvoc_level = self.sensor.TVOC
                except:
                    pass
                
                print(f"✅ CO2 Sensor (SGP30) auf I2C initialisiert")
            except Exception as e:
                print(f"⚠️  SGP30 Init-Fehler: {e} - Dummy-Modus")
                self.sensor = None
        else:
            print(f"⚠️  adafruit_sgp30 nicht verfügbar - Dummy-Modus")
    
    def read(self):
        if self.sensor is None:
            return self._co2_level
        
        if self.errors >= 10:
            if self.sensor:
                print(f"⚠️  CO2 Sensor deaktiviert (zu viele Fehler)")
                self.sensor = None
            return self._co2_level
        
        # Retry bis zu 3x
        for attempt in range(3):
            try:
                self._co2_level = self.sensor.eCO2
                self._tvoc_level = self.sensor.TVOC
                self.errors = 0
                self.last_good_read = time.time()
                return self._co2_level
            except:
                if attempt < 2:
                    time.sleep(0.1)
                else:
                    self.errors += 1
                    if self.errors % 5 == 1:
                        print(f"⚠️  CO2 Read-Fehler ({self.errors}/10)")
        
        return self._co2_level
    
    @property
    def co2_level(self):
        self.read()
        return self._co2_level
    
    @property
    def tvoc_level(self):
        return self._tvoc_level
    
    def get_alarm_status(self):
        level = self.co2_level
        if level >= config.CO2_CRITICAL_THRESHOLD:
            return "critical"
        elif level >= config.CO2_WARNING_THRESHOLD:
            return "warning"
        return "ok"
