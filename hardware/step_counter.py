"""
Step Counter (BMA400)
"""

import config
from hardware import StepCounter as HardwareSteps, IS_PITOP

class StepCounter:
    def __init__(self):
        self.sensor = HardwareSteps()
        print(f"✅ Step Counter initialisiert ({'REAL' if IS_PITOP else 'MOCK'})")
    
    def start(self):
        self.sensor.start_counting()
    
    def stop(self):
        return self.sensor.stop_counting()
    
    def read(self):
        return self.sensor.current_steps
    
    def reset(self):
        self.sensor.steps = 0
    
    def get_count(self):
        return self.sensor.current_steps
    
    @property
    def current_steps(self):
        return self.sensor.current_steps