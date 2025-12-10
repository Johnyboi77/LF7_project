#!/usr/bin/env python3
"""
Test 1: LED Test
Testet alle 3 LEDs einzeln
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Mock-Modus wenn nicht auf Pi
try:
    import RPi.GPIO as GPIO
    MOCK_MODE = False
except:
    from mock_hardware import MockGPIO as GPIO
    MOCK_MODE = True
    print("⚠️  MOCK MODE - Keine echte Hardware!\n")

import time
import config

class LEDTester:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        self.pins = {
            'red': config.LED_RED_PIN,
            'green': config.LED_GREEN_PIN,
            'blue': config.LED_BLUE_PIN
        }
        
        for color, pin in self.pins.items():
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)
    
    def test_led(self, color):
        """Testet eine LED"""
        print(f"\n{'='*50}")
        print(f"🔴 Teste {color.upper()} LED (Pin {self.pins[color]})")
        print(f"{'='*50}")
        
        pin = self.pins[color]
        
        try:
            # LED an
            print("💡 LED AN...")
            GPIO.output(pin, GPIO.HIGH)
            
            if not MOCK_MODE:
                response = input("\n❓ Leuchtet die LED? (j/n): ").lower()
                if response != 'j':
                    print("❌ FEHLER: LED leuchtet nicht!")
                    return False
            else:
                time.sleep(1)
            
            # LED aus
            print("\n💡 LED AUS...")
            GPIO.output(pin, GPIO.LOW)
            
            if not MOCK_MODE:
                response = input("❓ LED ist aus? (j/n): ").lower()
                if response != 'j':
                    print("❌ FEHLER: LED geht nicht aus!")
                    return False
            else:
                time.sleep(0.5)
            
            # Blink-Test
            print("\n💡 BLINK-TEST (3x)...")
            for i in range(3):
                GPIO.output(pin, GPIO.HIGH)
                time.sleep(0.3)
                GPIO.output(pin, GPIO.LOW)
                time.sleep(0.3)
            
            if not MOCK_MODE:
                response = input("❓ Hat die LED 3x geblinkt? (j/n): ").lower()
                if response != 'j':
                    print("❌ FEHLER: Blinken funktioniert nicht!")
                    return False
            
            print(f"\n✅ {color.upper()} LED: WORKS")
            return True
            
        except Exception as e:
            print(f"\n❌ FEHLER: {e}")
            return False
        finally:
            GPIO.output(pin, GPIO.LOW)
    
    def run_all_tests(self):
        """Führt alle LED-Tests durch"""
        print("\n" + "="*50)
        print("🚀 LED TEST SUITE")
        print("="*50)
        
        results = {}
        
        for color in ['red', 'green', 'blue']:
            results[color] = self.test_led(color)
            
            if not results[color] and not MOCK_MODE:
                response = input("\n⏭️  Weiter zum nächsten Test? (Enter) oder Abbruch (q): ")
                if response.lower() == 'q':
                    break
        
        # Zusammenfassung
        print("\n" + "="*50)
        print("📊 TEST ZUSAMMENFASSUNG")
        print("="*50)
        for color, result in results.items():
            status = "✅ WORKS" if result else "❌ WORKS NOT"
            print(f"{color.upper():<10} {status}")
        print("="*50 + "\n")
        
        GPIO.cleanup()
        
        return all(results.values())

if __name__ == "__main__":
    tester = LEDTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)