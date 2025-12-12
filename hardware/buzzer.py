import threading
from time import sleep
from config import BUZZER_PIN, BUZZER_TIMER_DURATION, BUZZER_CO2_DURATION, BUZZER_CO2_INTERVAL, BUZZER_CO2_REPETITIONS
from . import IS_PITOP, PitopBuzzer

class Buzzer:
    def __init__(self, pin_name=None):
        self.pin_name = pin_name or BUZZER_PIN
        if IS_PITOP:
            self.buzzer = PitopBuzzer(self.pin_name)
        else:
            self.buzzer = None
        self.beep_thread = None
    
    def on(self):
        if self.buzzer:
            self.buzzer.on()
    
    def off(self):
        if self.buzzer:
            self.buzzer.off()
    
    def beep(self, duration=0.2):
        if self.buzzer:
            self.buzzer.on()
            sleep(duration)
            self.buzzer.off()
        print(f"🔊 Beep ({duration}s)")
    
    def long_beep(self, duration=2.0):
        self.beep(duration)
    
    def double_beep(self):
        self.beep(0.2)
        sleep(0.2)
        self.beep(0.2)
    
    def co2_alarm(self):
        thread = threading.Thread(target=self._co2_pattern, daemon=True)
        thread.start()
    
    def _co2_pattern(self):
        for _ in range(BUZZER_CO2_REPETITIONS):
            self.beep(BUZZER_CO2_DURATION)
            sleep(BUZZER_CO2_INTERVAL)
    
    def timer_alarm(self):
        self.long_beep(BUZZER_TIMER_DURATION)