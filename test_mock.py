from hardware import Button, LED, Buzzer, IS_PITOP

print(f"Mode: {'REAL' if IS_PITOP else 'MOCK'}")

button1 = Button("D0")
led = LED("D2")

def work_start():
    print("✅ Work Started!")
    led.on()

button1.on_short_press(work_start)

# Simuliere Button-Druck
button1.simulate_short_press()