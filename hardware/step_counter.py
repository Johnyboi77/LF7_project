from . import IS_PITOP

class StepCounter:
    def __init__(self):
        self.steps = 0
        self.is_counting = False
        
        if IS_PITOP:
            try:
                import board
                import busio
                from adafruit_bma400 import Adafruit_BMA400_I2C
                
                i2c = busio.I2C(board.SCL, board.SDA)
                self.sensor = Adafruit_BMA400_I2C(i2c)
            except:
                self.sensor = None
        else:
            self.sensor = None
    
    def start(self):
        self.is_counting = True
        self.steps = 0
    
    def stop(self):
        self.is_counting = False
        return self.steps
    
    def read(self):
        if self.sensor and self.is_counting:
            try:
                accel = self.sensor.acceleration
                # Vereinfachte Schritterkennung
                magnitude = sum(x**2 for x in accel) ** 0.5
                if magnitude > 15:
                    self.steps += 1
            except:
                pass
        return self.steps
    
    def reset(self):
        self.steps = 0
    
    def get_count(self):
        return self.steps