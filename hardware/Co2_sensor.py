from config import CO2_WARNING_THRESHOLD, CO2_CRITICAL_THRESHOLD
from . import IS_PITOP

class CO2Sensor:
    def __init__(self):
        self.co2_level = 400
        self.tvoc_level = 0
        self.is_alarm = False
        
        if IS_PITOP:
            try:
                import board
                import busio
                from adafruit_ccs811 import Adafruit_CCS811
                
                i2c = busio.I2C(board.SCL, board.SDA)
                self.sensor = Adafruit_CCS811(i2c)
            except:
                self.sensor = None
        else:
            self.sensor = None
    
    def read(self):
        if self.sensor:
            try:
                if self.sensor.data_ready:
                    self.co2_level = self.sensor.eco2
                    self.tvoc_level = self.sensor.tvoc
            except:
                pass
        return self.co2_level
    
    def get_alarm_status(self):
        level = self.read()
        if level >= CO2_CRITICAL_THRESHOLD:
            return "critical"
        elif level >= CO2_WARNING_THRESHOLD:
            return "warning"
        return "ok"