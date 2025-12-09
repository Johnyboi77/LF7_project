# hardware/step_counter.py
"""
Grove Step Counter (SKU: 101020583)
Verwendet BMA400 3-Achsen Beschleunigungssensor
"""

import time
from threading import Thread

try:
    from grove.grove_step_counter_bma400 import GroveStepCounter
except ImportError:
    print("⚠️  Grove Library fehlt!")
    print("Installation: curl -sL https://github.com/Seeed-Studio/grove.py/raw/master/install.sh | sudo bash -s -")

class StepCounter:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.total_steps = 0
        self.is_monitoring = False
        self.session_id = None
        
        try:
            # Sensor initialisieren (I2C Adresse 0x14)
            self.sensor = GroveStepCounter()
            print("✅ Step Counter initialisiert")
            
            # Reset Step Counter
            self.sensor.reset()
            
        except Exception as e:
            print(f"❌ Step Counter Fehler: {e}")
            self.sensor = None
    
    def start_monitoring(self, interval=5):
        """Startet kontinuierliches Monitoring"""
        if self.sensor is None:
            return
        
        self.is_monitoring = True
        thread = Thread(target=self._monitor_loop, args=(interval,), daemon=True)
        thread.start()
        print(f"🚶 Step Counter Monitoring gestartet (alle {interval}s)")
    
    def _monitor_loop(self, interval):
        """Monitoring Loop"""
        last_steps = 0
        
        while self.is_monitoring:
            try:
                # Schritte auslesen
                current_steps = self.sensor.steps
                
                # Nur loggen wenn sich etwas geändert hat
                if current_steps != last_steps:
                    self.total_steps = current_steps
                    print(f"👣 Schritte: {self.total_steps}")
                    
                    # In Datenbank speichern
                    self.db_manager.log_steps(self.total_steps, self.session_id)
                    
                    last_steps = current_steps
                
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