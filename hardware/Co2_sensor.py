# hardware/Co2_sensor.py
"""
Grove VOC and eCO2 Gas Sensor mit LED-Warnung
"""

import time
from threading import Thread
import config

try:
    import board
    import busio
    import adafruit_sgp30
except ImportError:
    print("⚠️  SGP30 Library fehlt!")

class CO2Sensor:
    def __init__(self, buzzer, led, notification_service, db_manager):
        self.buzzer = buzzer
        self.led = led
        self.notification_service = notification_service
        self.db_manager = db_manager
        self.session_id = None 
        self.co2_level = 0
        self.tvoc_level = 0
        self.is_monitoring = False
        self.last_warning_time = 0
        self.warning_state = None  # None, 'warning', 'critical'
        
        try:
            i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)
            self.sensor = adafruit_sgp30.Adafruit_SGP30(i2c)
            
            print("🔄 SGP30 Sensor wird initialisiert...")
            self.sensor.iaq_init()
            self.sensor.set_iaq_baseline(0x8973, 0x8AAE)
            
            print("✅ eCO2/VOC Sensor bereit")
            
        except Exception as e:
            print(f"❌ CO2 Sensor Fehler: {e}")
            self.sensor = None
    
    def start_monitoring(self, interval=10):
        """Startet kontinuierliches Monitoring"""
        self.is_monitoring = True
        thread = Thread(target=self._monitor_loop, args=(interval,), daemon=True)
        thread.start()
        print(f"🔍 eCO2/VOC Monitoring gestartet (alle {interval}s)")
    
    def _monitor_loop(self, interval):
        """Monitoring Loop mit Warm-up"""
        # Warm-up Phase
        print("⏳ Sensor Warm-up (15 Sekunden)...")
        for i in range(15):
            if self.sensor:
                try:
                    self.sensor.iaq_measure()
                except:
                    pass
            time.sleep(1)
        
        print("✅ Warm-up abgeschlossen\n")
        
        while self.is_monitoring:
            self.read()
            time.sleep(interval)
    
    def read(self):
        """Liest eCO2 und TVOC - steuert LED und Buzzer"""
        if self.sensor is None:
            self.db_manager.log_co2(self.co2_level, self.session_id)
            return None
        
        try:
            # Messung
            self.co2_level = self.sensor.eCO2
            self.tvoc_level = self.sensor.TVOC
            
            print(f"🌡️  eCO2: {self.co2_level} ppm | TVOC: {self.tvoc_level} ppb")
            
            # In Datenbank speichern
            self.db_manager.log_co2(self.co2_level)
            
            # Schwellenwerte prüfen + LED/Buzzer steuern
            self._check_thresholds()
            
            return {
                'co2': self.co2_level,
                'tvoc': self.tvoc_level
            }
            
        except Exception as e:
            print(f"❌ Sensor Lesefehler: {e}")
            return None
    
    def _check_thresholds(self):
        """Prüft Schwellenwerte und steuert LED + Buzzer"""
        current_time = time.time()
        
        # KRITISCH (>800 ppm) - Rote LED + Buzzer
        if self.co2_level >= config.CO2_CRITICAL_THRESHOLD:
            
            # LED anschalten
            self.led.on()
            
            # Status-Änderung oder alle 5 Minuten
            if self.warning_state != 'critical' or (current_time - self.last_warning_time > 300):
                print(f"\n🚨 KRITISCHER eCO2-WERT: {self.co2_level} ppm!")
                
                # Buzzer: Kurze Pieptöne
                self.buzzer.beep_short()
                
                # Benachrichtigung
                message = (
                    f"🚨 **KRITISCHER eCO2-WERT!**\n\n"
                    f"eCO2: {self.co2_level} ppm\n"
                    f"TVOC: {self.tvoc_level} ppb\n\n"
                    f"⚠️ Bitte sofort lüften!"
                )
                self.notification_service.send(message, "co2_critical")
                self.db_manager.log_notification("co2_critical", message, True)
                
                self.warning_state = 'critical'
                self.last_warning_time = current_time
        
        # WARNUNG (>600 ppm) - Nur rote LED
        elif self.co2_level >= config.CO2_WARNING_THRESHOLD:
            
            # LED anschalten
            self.led.on()
            
            # Status-Änderung oder alle 10 Minuten
            if self.warning_state != 'warning' or (current_time - self.last_warning_time > 600):
                print(f"\n⚠️  ERHÖHTER eCO2-WERT: {self.co2_level} ppm")
                
                # Benachrichtigung (ohne Buzzer!)
                message = (
                    f"⚠️ **Erhöhter eCO2-Wert**\n\n"
                    f"eCO2: {self.co2_level} ppm\n"
                    f"TVOC: {self.tvoc_level} ppb\n\n"
                    f"🔴 Rote LED leuchtet - Bitte bald lüften."
                )
                self.notification_service.send(message, "co2_warning")
                
                self.warning_state = 'warning'
                self.last_warning_time = current_time
        
        # NORMAL (<600 ppm) - LED aus
        else:
            if self.warning_state is not None:
                print(f"\n✅ eCO2-Wert wieder normal: {self.co2_level} ppm")
                self.led.off()
                self.warning_state = None
    
    def get_current_value(self):
        """Aktuelle Werte"""
        return {
            'co2': self.co2_level,
            'tvoc': self.tvoc_level
        }
    
    def stop_monitoring(self):
        """Stoppt Monitoring"""
        self.is_monitoring = False
        self.led.off()