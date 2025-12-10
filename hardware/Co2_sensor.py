# hardware/Co2_sensor.py
"""
Grove VOC and eCO2 Gas Sensor (SGP30)
Mit Supabase-Integration und LED/Buzzer-Steuerung
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
    print("Installation: pip3 install adafruit-circuitpython-sgp30")

class CO2Sensor:
    def __init__(self, buzzer, led, notification_service, db_manager):
        self.buzzer = buzzer
        self.led = led
        self.notification_service = notification_service
        self.db_manager = db_manager
        
        self.co2_level = 0
        self.tvoc_level = 0
        self.is_monitoring = False
        self.session_id = None
        
        # Alarm-Tracking (1 Alarm-Periode, nicht einzelne Messungen)
        self.warning_active = False
        self.last_warning_time = 0
        
        try:
            # I2C initialisieren
            i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)
            self.sensor = adafruit_sgp30.Adafruit_SGP30(i2c)
            
            print("🔄 SGP30 Sensor wird initialisiert...")
            self.sensor.iaq_init()
            self.sensor.set_iaq_baseline(0x8973, 0x8AAE)
            
            print("✅ eCO2/VOC Sensor bereit")
            
        except Exception as e:
            print(f"❌ CO2 Sensor Fehler: {e}")
            self.sensor = None
    
    def set_session_id(self, session_id):
        """Setzt aktuelle Session ID"""
        self.session_id = session_id
        print(f"📊 CO2 Sensor: Session {session_id[:8]}...")
    
    def start_monitoring(self, interval=None):
        """Startet kontinuierliches Monitoring"""
        if interval is None:
            interval = config.CO2_MEASUREMENT_INTERVAL
        
        self.is_monitoring = True
        thread = Thread(target=self._monitor_loop, args=(interval,), daemon=True)
        thread.start()
        print(f"🔍 CO2 Monitoring gestartet (alle {interval}s)")
    
    def _monitor_loop(self, interval):
        """Monitoring Loop mit Warm-up"""
        
        # Warm-up Phase (15 Sekunden)
        print("⏳ Sensor Warm-up (15 Sekunden)...")
        for i in range(15):
            if self.sensor:
                try:
                    self.sensor.iaq_measure()
                except:
                    pass
            time.sleep(1)
        
        print("✅ Warm-up abgeschlossen, Messung startet\n")
        
        while self.is_monitoring:
            self.read()
            time.sleep(interval)
    
    def read(self):
        """Liest eCO2 und TVOC, prüft Schwellenwerte"""
        if self.sensor is None:
            return None
        
        try:
            # Messung
            self.co2_level = self.sensor.eCO2
            self.tvoc_level = self.sensor.TVOC
            
            print(f"��️  eCO2: {self.co2_level} ppm | TVOC: {self.tvoc_level} ppb")
            
            # In Supabase speichern
            if self.session_id:
                is_alarm = self.co2_level >= config.CO2_CRITICAL_THRESHOLD
                alarm_type = 'critical' if is_alarm else None
                
                self.db_manager.log_co2(
                    self.session_id,
                    self.co2_level,
                    self.tvoc_level,
                    is_alarm,
                    alarm_type
                )
            
            # Schwellenwerte prüfen
            self._check_thresholds()
            
            return {
                'co2': self.co2_level,
                'tvoc': self.tvoc_level
            }
            
        except Exception as e:
            print(f"❌ Sensor Lesefehler: {e}")
            return None
    
    def _check_thresholds(self):
        """
        Prüft CO2-Schwellenwerte:
        - > 800 ppm: LED + Buzzer + Discord (kritisch)
        - > 600 ppm: LED + Discord (erhöht)
        - < 600 ppm: Alles aus
        """
        current_time = time.time()
        
        # KRITISCH: > 800 ppm
        if self.co2_level >= config.CO2_CRITICAL_THRESHOLD:
            
            # LED an
            self.led.on()
            
            # Nur beim ersten Mal dieser Alarm-Periode
            if not self.warning_active:
                print(f"\n🚨 KRITISCHER CO2-WERT: {self.co2_level} ppm!")
                
                # Buzzer: KURZE Pieptöne
                self.buzzer.beep_short()
                
                # Discord Benachrichtigung
                self.notification_service.send_co2_alert(
                    self.co2_level, 
                    self.tvoc_level, 
                    is_critical=True
                )
                
                # Alarm aktiv setzen
                self.warning_active = True
                self.last_warning_time = current_time
            
            # Alle 5 Minuten erneut warnen (optional)
            elif current_time - self.last_warning_time > 300:
                print(f"⚠️  CO2 weiterhin kritisch: {self.co2_level} ppm")
                self.last_warning_time = current_time
        
        # ERHÖHT: > 600 ppm (aber < 800)
        elif self.co2_level >= config.CO2_WARNING_THRESHOLD:
            
            # LED an
            self.led.on()
            
            # Nur beim ersten Mal
            if not self.warning_active:
                print(f"\n⚠️  ERHÖHTER CO2-WERT: {self.co2_level} ppm")
                
                # NUR Discord, KEIN Buzzer
                self.notification_service.send_co2_alert(
                    self.co2_level, 
                    self.tvoc_level, 
                    is_critical=False
                )
                
                # Warnung aktiv
                self.warning_active = True
                self.last_warning_time = current_time
        
        # NORMAL: < 600 ppm
        else:
            # War vorher Warnung aktiv?
            if self.warning_active:
                print(f"\n✅ CO2-Wert wieder normal: {self.co2_level} ppm")
                
                # LED AUS
                self.led.off()
                
                # Warnung beenden
                self.warning_active = False
    
    def get_current_value(self):
        """Gibt aktuelle Werte zurück"""
        return {
            'co2': self.co2_level,
            'tvoc': self.tvoc_level
        }
    
    def stop_monitoring(self):
        """Stoppt Monitoring"""
        self.is_monitoring = False
        self.led.off()
        print("🛑 CO2 Monitoring gestoppt")
