"""
Mock Hardware Module
Simuliert GPIO für Entwicklung ohne Raspberry Pi
"""

class MockGPIO:
    BCM = "BCM"
    BOARD = "BOARD"
    OUT = "OUT"
    IN = "IN"
    HIGH = 1
    LOW = 0
    PUD_UP = "PUD_UP"
    PUD_DOWN = "PUD_DOWN"
    RISING = "RISING"
    FALLING = "FALLING"
    BOTH = "BOTH"
    
    _mode = None
    _warnings = True
    _pins = {}
    _callbacks = {}
    
    @staticmethod
    def setmode(mode):
        MockGPIO._mode = mode
        print(f"🔧 Mock: GPIO Mode = {mode}")
    
    @staticmethod
    def setwarnings(flag):
        MockGPIO._warnings = flag
    
    @staticmethod
    def setup(pin, mode, pull_up_down=None):
        MockGPIO._pins[pin] = {
            'mode': mode,
            'state': MockGPIO.LOW,
            'pull': pull_up_down
        }
        print(f"🔧 Mock: Setup Pin {pin} als {mode}")
    
    @staticmethod
    def output(pin, state):
        if pin in MockGPIO._pins:
            MockGPIO._pins[pin]['state'] = state
            state_str = "HIGH (AN)" if state == MockGPIO.HIGH else "LOW (AUS)"
            print(f"💡 Mock: Pin {pin} -> {state_str}")
    
    @staticmethod
    def input(pin):
        if pin in MockGPIO._pins:
            state = MockGPIO._pins[pin]['state']
            print(f"📥 Mock: Pin {pin} gelesen -> {state}")
            return state
        return MockGPIO.LOW
    
    @staticmethod
    def add_event_detect(pin, edge, callback=None, bouncetime=None):
        MockGPIO._callbacks[pin] = callback
        print(f"🔔 Mock: Event Detection auf Pin {pin} ({edge})")
    
    @staticmethod
    def cleanup(pin=None):
        if pin:
            if pin in MockGPIO._pins:
                del MockGPIO._pins[pin]
            print(f"🧹 Mock: Pin {pin} cleanup")
        else:
            MockGPIO._pins.clear()
            MockGPIO._callbacks.clear()
            print("🧹 Mock: Alle Pins cleanup")
