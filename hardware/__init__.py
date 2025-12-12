"""
Hardware Abstraction Layer
Automatische Erkennung: pi-top Hardware vs. Mock
"""

import os
import sys

# Prüfe ob wir auf echtem pi-top sind
IS_PITOP = os.path.exists('/etc/pi-top') or os.path.exists('/usr/lib/python3/dist-packages/pitop')

if IS_PITOP:
    print("🤖 Echte pi-top Hardware erkannt!")
    
    try:
        from pitop import Button as PitopButton
        from pitop import LED as PitopLED
        from pitop import Buzzer as PitopBuzzer
        from pitop.miniscreen import Miniscreen as PitopMiniscreen
        
        Button = PitopButton
        LED = PitopLED
        Buzzer = PitopBuzzer
        Miniscreen = PitopMiniscreen
        
    except ImportError as e:
        print(f"⚠️ pitop Import Fehler: {e}")
        print("→ Fallback zu Mock")
        IS_PITOP = False

if not IS_PITOP:
    print("💻 Mock-Modus (Laptop/WSL)")
    
    from mock_hardware import (
        Button,
        LED,
        Buzzer,
        Miniscreen,
    )

# Custom Sensoren (nur wenn sie existieren)
try:
    from hardware.Co2_sensor import CO2Sensor
except ImportError:
    print("⚠️ Co2_sensor.py nicht gefunden, nutze Mock")
    from mock_hardware import CO2Sensor

try:
    from hardware.step_counter import StepCounter
except ImportError:
    print("⚠️ step_counter.py nicht gefunden, nutze Mock")
    from mock_hardware import StepCounter

# Exports
__all__ = [
    'Button',
    'LED', 
    'Buzzer',
    'Miniscreen',
    'CO2Sensor',
    'StepCounter',
    'IS_PITOP'
]