# hardware/step_counter.py
"""
Grove Step Counter (BMA400)
Für PiTop 2 (mobiles System)
"""

import time
from threading import Thread

try:
    from grove.grove_step_counter_bma400 import GroveStepCounter
except ImportError:
    print("⚠️  Grove Library fehlt!")
    print("Installation: curl -sL https://github.com/Seeed-Studio/grove.py/raw/master/install.sh | sudo bash -s -")

class StepCounter:
    def __init__(self):
        self.total_steps = 0
        self.is_monitoring = False
        
        try:
            # Sensor initialisieren (I2C Adresse 0x14)
            self.sensor = GroveStepCounter()
            self.sensor.reset()
            print("✅ Step Counter initialisiert")
            
        except Exception as e:
            print(f"❌ Step Counter Fehler: {e}")
            self.sensor = None
    
    def start_monitoring(self, interval=1):
        """Startet kontinuierliches Monitoring"""
        if self.sensor is None:
            print("❌ Sensor nicht verfügbar")
            return
        
        self.is_monitoring = True
        thread = Thread(target=self._monitor_loop, args=(interval,), daemon=True)
        thread.start()
        print(f"🚶 Step Counter läuft (Update alle {interval}s)")
    
    def _monitor_loop(self, interval):
        """Monitoring Loop"""
        while self.is_monitoring:
            try:
                self.total_steps = self.sensor.steps
            except Exception as e:
                print(f"❌ Step Counter Lesefehler: {e}")
            
            time.sleep(interval)
    
    def get_steps(self):
        """Gibt aktuelle Schrittzahl zurück"""
        if self.sensor is None:
            return 0
        
        try:
            self.total_steps = self.sensor.steps
            return self.total_steps
        except:
            return 0
    
    def reset(self):
        """Setzt Schrittzähler zurück"""
        if self.sensor:
            try:
                self.sensor.reset()
                self.total_steps = 0
                print("🔄 Schrittzähler zurückgesetzt")
            except Exception as e:
                print(f"❌ Reset Fehler: {e}")
    
    def stop_monitoring(self):
        """Stoppt Monitoring"""
        self.is_monitoring = False
        print("🛑 Step Counter gestoppt")
