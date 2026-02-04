
#!/usr/bin/env python3
"""
Step Counter für Grove BMA456
Korrigierte Version mit richtiger Skalierung
"""

import time
from threading import Thread

try:
    from smbus2 import SMBus
    I2C_AVAILABLE = True
except ImportError:
    I2C_AVAILABLE = False
    print("⚠️  smbus2 nicht installiert - pip install smbus2")

# BMA456 Konstanten
BMA456_ADDR_LOW = 0x18
BMA456_ADDR_HIGH = 0x19
BMA456_CHIP_ID = 0x16

# Register
REG_CHIP_ID = 0x00
REG_ACC_X_LSB = 0x12
REG_ACC_CONF = 0x40
REG_ACC_RANGE = 0x41
REG_PWR_CONF = 0x7C
REG_PWR_CTRL = 0x7D
REG_CMD = 0x7E


class StepCounter:
    """Step Counter für Grove BMA456"""
    
    def __init__(self):
        self._steps = 0
        self.running = False
        self._thread = None
        self.sensor_type = None
        self.i2c_addr = None
        self._debug = False
        self._acc_range = 4  # ±4g default
        
        if not I2C_AVAILABLE:
            print("⚠️  Step Counter im Dummy-Modus (smbus2 fehlt)")
            return
        
        self._init_bma456()
    
    def _init_bma456(self):
        """Sucht und initialisiert BMA456"""
        try:
            for addr in [BMA456_ADDR_LOW, BMA456_ADDR_HIGH]:
                try:
                    with SMBus(1) as bus:
                        chip_id = bus.read_byte_data(addr, REG_CHIP_ID)
                        
                        if chip_id == BMA456_CHIP_ID:
                            self.i2c_addr = addr
                            self.sensor_type = "BMA456"
                            print(f"✅ BMA456 gefunden auf 0x{addr:02X} (Chip ID: 0x{chip_id:02X})")
                            self._configure_sensor()
                            return
                except OSError:
                    pass
            
            print("⚠️  BMA456 nicht gefunden")
            self.sensor_type = "Dummy"
            
        except Exception as e:
            print(f"⚠️  I2C Fehler: {e}")
            self.sensor_type = "Dummy"
    
    def _i2c_write(self, reg, value):
        """Sicheres I2C Schreiben mit Retry"""
        for attempt in range(3):
            try:
                with SMBus(1) as bus:
                    bus.write_byte_data(self.i2c_addr, reg, value)
                time.sleep(0.02)  # 20ms Pause nach jedem Schreiben
                return True
            except OSError as e:
                if attempt < 2:
                    time.sleep(0.05)
                else:
                    print(f"⚠️  I2C Write Fehler Reg 0x{reg:02X}: {e}")
                    return False
        return False
    
    def _configure_sensor(self):
        """Konfiguriert BMA456 mit korrektem Timing"""
        if not self.i2c_addr:
            return
        
        try:
            print("   Konfiguriere BMA456...")
            
            # 1. Soft Reset
            self._i2c_write(REG_CMD, 0xB6)
            time.sleep(0.1)  # 100ms nach Reset warten!
            
            # 2. Power: Advanced Power Save deaktivieren
            if not self._i2c_write(REG_PWR_CONF, 0x00):
                return
            time.sleep(0.05)
            
            # 3. Accelerometer einschalten
            if not self._i2c_write(REG_PWR_CTRL, 0x04):
                return
            time.sleep(0.05)
            
            # 4. ACC Config: ODR=100Hz, BWP=normal, filter=perf_opt
            if not self._i2c_write(REG_ACC_CONF, 0xA8):
                return
            
            # 5. ACC Range: ±4g (0x01) - besser für Schrittzählung
            if not self._i2c_write(REG_ACC_RANGE, 0x01):
                return
            self._acc_range = 4
            
            time.sleep(0.05)
            print(f"✅ BMA456 konfiguriert (100Hz, ±{self._acc_range}g)")
            
        except Exception as e:
            print(f"⚠️  Konfiguration fehlgeschlagen: {e}")
    
    def _read_acceleration(self):
        """Liest Beschleunigung in g - KORRIGIERTE SKALIERUNG"""
        if not self.i2c_addr:
            return None
        
        try:
            with SMBus(1) as bus:
                data = bus.read_i2c_block_data(self.i2c_addr, REG_ACC_X_LSB, 6)
                
                # 16-bit signed, Little Endian
                x_raw = (data[1] << 8) | data[0]
                y_raw = (data[3] << 8) | data[2]
                z_raw = (data[5] << 8) | data[4]
                
                # Two's complement für signed
                if x_raw > 32767: x_raw -= 65536
                if y_raw > 32767: y_raw -= 65536
                if z_raw > 32767: z_raw -= 65536
                
                # KORRIGIERTE Skalierung!
                # BMA456: 16-bit signed, Full Scale = ±range
                # Bei ±4g: 32768 LSB = 4g → 1g = 8192 LSB
                # scale = range / 32768
                scale = self._acc_range / 32768.0
                
                x = x_raw * scale
                y = y_raw * scale
                z = z_raw * scale
                
                return (x, y, z)
                
        except Exception:
            return None
    
    def start(self):
        """Step Counting starten"""
        self._steps = 0
        self.running = True
        
        if self.sensor_type == "BMA456":
            self._thread = Thread(target=self._count_steps_loop, daemon=True)
            self._thread.start()
            print("🚶 Step Counter (BMA456) gestartet")
        else:
            print("🚶 Step Counter (Dummy) gestartet")
    
    def _count_steps_loop(self):
        """Verbesserte Schrittzählung"""
        # Glättung
        mag_history = []
        history_size = 5
        
        # Dynamische Baseline
        baseline_samples = []
        baseline_window = 100
        baseline = 1.0
        
        # Schritt-Erkennung
        step_threshold = 0.12      # Abweichung von Baseline
        min_step_interval = 0.35   # Min Zeit zwischen Schritten
        last_step_time = 0
        peak_detected = False
        
        print(f"📊 Schritt-Erkennung (Threshold: ±{step_threshold}g)")
        
        while self.running:
            try:
                accel = self._read_acceleration()
                
                if accel:
                    x, y, z = accel
                    magnitude = (x**2 + y**2 + z**2) ** 0.5
                    
                    # Baseline tracken
                    baseline_samples.append(magnitude)
                    if len(baseline_samples) > baseline_window:
                        baseline_samples.pop(0)
                    baseline = sum(baseline_samples) / len(baseline_samples)
                    
                    # Glätten
                    mag_history.append(magnitude)
                    if len(mag_history) > history_size:
                        mag_history.pop(0)
                    smoothed = sum(mag_history) / len(mag_history)
                    
                    deviation = smoothed - baseline
                    current_time = time.time()
                    
                    if self._debug:
                        print(f"M:{smoothed:.2f} B:{baseline:.2f} D:{deviation:+.3f}")
                    
                    # Peak Detection
                    if deviation > step_threshold:
                        peak_detected = True
                    elif peak_detected and deviation < step_threshold * 0.3:
                        if current_time - last_step_time > min_step_interval:
                            self._steps += 1
                            last_step_time = current_time
                            if self._debug:
                                print(f"  → STEP #{self._steps}")
                        peak_detected = False
                
                time.sleep(0.02)
                
            except Exception:
                time.sleep(0.1)
    
    def stop(self):
        """Stoppen"""
        self.running = False
        if self._thread:
            self._thread.join(timeout=1.0)
            self._thread = None
        steps = self._steps
        print(f"⏹️  Step Counter gestoppt: {steps} Schritte")
        return steps
    
    def read(self):
        return self._steps
    
    def reset(self):
        self._steps = 0
        print("🔄 Step Counter zurückgesetzt")
    
    def get_count(self):
        return self._steps
    
    @property
    def current_steps(self):
        return self._steps
    
    def get_raw_acceleration(self):
        """Debug: Rohdaten"""
        accel = self._read_acceleration()
        if accel:
            x, y, z = accel
            return {
                'x': round(x, 3),
                'y': round(y, 3),
                'z': round(z, 3),
                'magnitude': round((x**2 + y**2 + z**2) ** 0.5, 3)
            }
        return None
    
    def enable_debug(self):
        self._debug = True
    
    def disable_debug(self):
        self._debug = False


if __name__ == "__main__":
    print("\n🧪 BMA456 Step Counter Test")
    print("="*50)
    
    counter = StepCounter()
    
    if counter.sensor_type == "BMA456":
        print("\n📊 Rohdaten (5s) - Sensor ruhig halten:")
        print("-"*50)
        
        for i in range(25):
            data = counter.get_raw_acceleration()
            if data:
                m = data['magnitude']
                # Bei Ruhe sollte ~1.0g sein!
                status = "✅" if 0.9 < m < 1.1 else "⚠️"
                bar = '█' * min(int(m * 20), 40)
                print(f"X:{data['x']:+.2f} Y:{data['y']:+.2f} Z:{data['z']:+.2f} | {m:.2f}g {status} {bar}")
            else:
                print("❌ Keine Daten")
            time.sleep(0.2)
        
        print("\n🚶 Schrittzähler (15s) - JETZT GEHEN!")
        print("-"*50)
        
        counter.start()
        
        for i in range(15):
            time.sleep(1)
            print(f"   [{i+1:2d}s] Schritte: {counter.read()}")
        
        final = counter.stop()
        print(f"\n✅ Ergebnis: {final} Schritte")
    else:
        print("❌ Sensor nicht gefunden")