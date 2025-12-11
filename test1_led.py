#!/usr/bin/env python3
"""
Test 1: LED Test
Testet die rote LED an D2 (GPIO Pin)
"""

import sys
import time

# Mock-Modus wenn nicht auf Pi
try:
    import RPi.GPIO as GPIO
    MOCK_MODE = False
    print("✅ RPi.GPIO geladen - ECHTER MODUS")
except ImportError:
    from mock_hardware import MockGPIO as GPIO
    MOCK_MODE = True
    print("⚠️  MOCK MODE - Keine echte Hardware!")
    print("    Führe das Script auf dem Pi-top aus für echte Tests\n")

class LEDTester:
    def __init__(self):
        # D2 auf Pi-top 4 ist GPIO 2
        self.LED_PIN = 2  # D2
        
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        GPIO.setup(self.LED_PIN, GPIO.OUT)
        GPIO.output(self.LED_PIN, GPIO.LOW)
        
        print(f"✅ LED Pin {self.LED_PIN} (D2) konfiguriert")
    
    def test_led_on_off(self):
        """Testet LED AN/AUS"""
        print(f"\n{'='*50}")
        print(f"🔴 Teste LED AN/AUS (Pin D2)")
        print(f"{'='*50}")
        
        try:
            # LED an
            print("\n💡 LED AN...")
            GPIO.output(self.LED_PIN, GPIO.HIGH)
            time.sleep(1)
            
            if not MOCK_MODE:
                response = input("❓ Leuchtet die LED? (j/n): ").lower()
                if response != 'j':
                    print("❌ FEHLER: LED leuchtet nicht!")
                    return False
            
            # LED aus
            print("\n💡 LED AUS...")
            GPIO.output(self.LED_PIN, GPIO.LOW)
            time.sleep(1)
            
            if not MOCK_MODE:
                response = input("❓ LED ist aus? (j/n): ").lower()
                if response != 'j':
                    print("❌ FEHLER: LED geht nicht aus!")
                    return False
            
            print("\n✅ LED ON/OFF: WORKS" if not MOCK_MODE else "\n✅ LED ON/OFF: SIMULATED")
            return True
            
        except Exception as e:
            print(f"\n❌ FEHLER: {e}")
            return False
    
    def test_led_blink(self):
        """Testet LED Blinken"""
        print(f"\n{'='*50}")
        print(f"💡 Teste LED BLINKEN")
        print(f"{'='*50}")
        
        try:
            print("\n💡 BLINK-TEST (5x)...")
            for i in range(5):
                print(f"  Blink {i+1}/5")
                GPIO.output(self.LED_PIN, GPIO.HIGH)
                time.sleep(0.3)
                GPIO.output(self.LED_PIN, GPIO.LOW)
                time.sleep(0.3)
            
            if not MOCK_MODE:
                response = input("\n❓ Hat die LED 5x geblinkt? (j/n): ").lower()
                if response != 'j':
                    print("❌ FEHLER: Blinken funktioniert nicht!")
                    return False
            
            print("\n✅ Blink Test: WORKS" if not MOCK_MODE else "\n✅ Blink Test: SIMULATED")
            return True
            
        except Exception as e:
            print(f"\n❌ FEHLER: {e}")
            return False
    
    def test_led_fast_blink(self):
        """Testet schnelles Blinken"""
        print(f"\n{'='*50}")
        print(f"⚡ Teste SCHNELLES BLINKEN")
        print(f"{'='*50}")
        
        try:
            print("\n⚡ SCHNELL-BLINK (10x)...")
            for i in range(10):
                GPIO.output(self.LED_PIN, GPIO.HIGH)
                time.sleep(0.1)
                GPIO.output(self.LED_PIN, GPIO.LOW)
                time.sleep(0.1)
            
            if not MOCK_MODE:
                response = input("\n❓ Hat die LED schnell geblinkt? (j/n): ").lower()
                if response != 'j':
                    print("❌ FEHLER: Schnelles Blinken funktioniert nicht!")
                    return False
            
            print("\n✅ Fast Blink Test: WORKS" if not MOCK_MODE else "\n✅ Fast Blink Test: SIMULATED")
            return True
            
        except Exception as e:
            print(f"\n❌ FEHLER: {e}")
            return False
    
    def run_all_tests(self):
        """Führt alle LED-Tests durch"""
        print("\n" + "="*50)
        print("🚀 LED TEST SUITE - Pin D2")
        if MOCK_MODE:
            print("   (MOCK MODE - Simulation)")
        print("="*50)
        
        results = {
            'on_off': self.test_led_on_off(),
            'blink': self.test_led_blink(),
            'fast_blink': self.test_led_fast_blink()
        }
        
        # Zusammenfassung
        print("\n" + "="*50)
        print("📊 TEST ZUSAMMENFASSUNG")
        print("="*50)
        for test_name, result in results.items():
            status = "✅ WORKS" if result else "❌ WORKS NOT"
            mode = " (SIMULATED)" if MOCK_MODE else ""
            print(f"{test_name.upper():<15} {status}{mode}")
        print("="*50 + "\n")
        
        # Aufräumen
        GPIO.output(self.LED_PIN, GPIO.LOW)
        GPIO.cleanup()
        
        return all(results.values())

if __name__ == "__main__":
    try:
        tester = LEDTester()
        success = tester.run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test abgebrochen!")
        GPIO.cleanup()
        sys.exit(1)