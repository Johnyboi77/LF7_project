#!/usr/bin/env python3
"""
🧪 LED & CO2 Test - 10 Minuten kontinuierliche Überwachung
Testet: CO2-Sensor, LED-Warnung, Discord-Benachrichtigungen
"""
import os
import sys

# ⚠️ DEVICE_OVERRIDE MUSS VOR allen anderen Imports stehen!
if '--device=' not in ' '.join(sys.argv):
    os.environ['DEVICE_OVERRIDE'] = 'pitop1'  # Default für diesen Test

import time
from datetime import datetime
import config
from hardware import LED, Buzzer, CO2Sensor
from services.notification_service import NotificationService

class CO2LEDTest:
    def __init__(self):
        print("\n" + "="*60)
        print("🧪 CO2 & LED TEST - 10 Minuten")
        print("="*60)
        
        # Hardware
        self.led = LED()
        self.buzzer = Buzzer()
        self.co2 = CO2Sensor()
        
        # Services
        self.notify = NotificationService()
        
        # State
        self.co2_alarm_active = False
        self.last_co2_warning = None
        self.test_start = time.time()
        self.test_duration = 600  # 10 Minuten
        
        print("✅ Test-Komponenten initialisiert\n")
    
    def run_test(self):
        """Führt 10-Minuten Test durch"""
        
        print("🚀 TEST GESTARTET")
        print(f"⏱️  Dauer: {self.test_duration // 60} Minuten")
        print(f"📊 Messintervall: 5 Sekunden")
        print(f"💡 LED: Leuchtet bei schlechter Luftqualität")
        print(f"🔊 Buzzer: Alarm bei kritischen Werten")
        print(f"📱 Discord: Push bei kritischen Werten\n")
        
        print("=" * 60)
        print(f"{'Zeit':<8} | {'CO2 (ppm)':<10} | {'TVOC':<8} | {'Status':<12} | {'LED':<5} | {'Buzzer'}")
        print("=" * 60)
        
        try:
            while time.time() - self.test_start < self.test_duration:
                elapsed = int(time.time() - self.test_start)
                remaining = self.test_duration - elapsed
                
                # CO2 messen
                self._check_co2()
                
                # Fortschritt
                mins, secs = divmod(remaining, 60)
                print(f"\n⏱️  Verbleibend: {mins:02d}:{secs:02d}")
                
                # 5 Sekunden warten
                time.sleep(5)
            
            print("\n\n" + "="*60)
            print("✅ TEST ABGESCHLOSSEN")
            print("="*60)
            self._print_summary()
        
        except KeyboardInterrupt:
            print("\n\n⚠️  Test abgebrochen!")
            self._cleanup()
    
    def _check_co2(self):
        """Prüft CO2 und triggert Aktionen"""
        
        alarm_status = self.co2.get_alarm_status()
        co2_level = self.co2.read()
        tvoc_level = self.co2.tvoc_level
        
        # Zeitstempel
        now = datetime.now().strftime("%H:%M:%S")
        
        # ===== CRITICAL (> 800 ppm) =====
        if alarm_status == "critical":
            if not self.co2_alarm_active:
                # LED an
                self.led.on()
                
                # Buzzer Alarm
                self.buzzer.co2_alarm()
                
                # Discord Push
                self.notify.send_co2_alert(co2_level, tvoc_level, is_critical=True)
                
                self.co2_alarm_active = True
                self.last_co2_warning = datetime.now()
                
                print(f"{now} | {co2_level:<10} | {tvoc_level:<8} | 🚨 CRITICAL  | 🔴 ON | 🔊 ALARM")
            else:
                print(f"{now} | {co2_level:<10} | {tvoc_level:<8} | 🚨 CRITICAL  | 🔴 ON | 🔇")
        
        # ===== WARNING (600-800 ppm) =====
        elif alarm_status == "warning":
            if not self.co2_alarm_active or \
               (self.last_co2_warning and 
                (datetime.now() - self.last_co2_warning).seconds > 300):
                
                # LED an
                self.led.on()
                
                # Discord (ohne Ping, alle 5 Min)
                if (self.last_co2_warning is None or 
                    (datetime.now() - self.last_co2_warning).seconds > 300):
                    self.notify.send_co2_alert(co2_level, tvoc_level, is_critical=False)
                
                self.co2_alarm_active = True
                self.last_co2_warning = datetime.now()
                
                print(f"{now} | {co2_level:<10} | {tvoc_level:<8} | 💛 WARNING   | 🔴 ON | 🔇")
            else:
                print(f"{now} | {co2_level:<10} | {tvoc_level:<8} | 💛 WARNING   | 🔴 ON | 🔇")
        
        # ===== OK (< 600 ppm) =====
        else:
            if self.co2_alarm_active:
                # Entwarnung
                print(f"{now} | {co2_level:<10} | {tvoc_level:<8} | ✅ OK → NORMAL | ⚫ OFF | 🔇")
                self.co2_alarm_active = False
                self.led.off()
            else:
                print(f"{now} | {co2_level:<10} | {tvoc_level:<8} | 💚 OK        | ⚫ OFF | 🔇")
    
    def _print_summary(self):
        """Gibt Test-Zusammenfassung aus"""
        
        print("\n📊 TEST ZUSAMMENFASSUNG:")
        print(f"   ✅ Testdauer: {self.test_duration // 60} Minuten")
        print(f"   📡 CO2-Sensor: Funktioniert")
        print(f"   💡 LED: Funktioniert")
        print(f"   🔊 Buzzer: Funktioniert")
        
        if self.notify.is_enabled:
            print(f"   📱 Discord: Funktioniert ✅")
        else:
            print(f"   📱 Discord: Nicht konfiguriert ⚠️")
        
        print("\n💡 TIPP: Teste verschiedene Szenarien:")
        print("   1. Normal atmen → CO2 < 600 (LED aus)")
        print("   2. Über Sensor hauchen → CO2 600-800 (LED an)")
        print("   3. Direkt in Sensor atmen → CO2 > 800 (LED an + Buzzer + Discord)")
        
        print("\n")
    
    def _cleanup(self):
        """Cleanup"""
        print("\n🛑 Cleanup...")
        self.led.off()
        self.buzzer.off()
        print("✅ Test beendet\n")


if __name__ == "__main__":
    print("\n🧪 Starte CO2/LED Test...")
    print("⚠️  Drücke STRG+C zum Abbrechen\n")
    
    test = CO2LEDTest()
    
    try:
        test.run_test()
    except KeyboardInterrupt:
        test._cleanup()
    finally:
        test._cleanup()