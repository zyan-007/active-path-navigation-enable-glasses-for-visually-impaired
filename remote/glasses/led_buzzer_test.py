import os
import RPi.GPIO as GPIO
import time

# ── PINS ──────────────────────────────────────────────────────────────────────
BUTTON1 = 5
BUTTON2 = 6
BUTTON3 = 13
BUTTON4 = 19
BUTTON5 = 26
TRIGGER = 21
# ─────────────────────────────────────────────────────────────────────────────

# ── GPIO SETUP ────────────────────────────────────────────────────────────────
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(TRIGGER, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUTTON1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUTTON2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUTTON3, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUTTON4, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUTTON5, GPIO.IN, pull_up_down=GPIO.PUD_UP)
# ─────────────────────────────────────────────────────────────────────────────

# ── DEBOUNCE ──────────────────────────────────────────────────────────────────
last_press = {}
DEBOUNCE_MS = 300

def debounce(pin):
    now = time.time() * 1000
    if pin not in last_press or now - last_press[pin] > DEBOUNCE_MS:
        last_press[pin] = now
        return True
    return False
# ─────────────────────────────────────────────────────────────────────────────

print("Ready - press any button")

buttons = [TRIGGER, BUTTON1, BUTTON2, BUTTON3, BUTTON4, BUTTON5]

try:
    while True:
        for pin in buttons:
            if GPIO.input(pin) == GPIO.LOW and debounce(pin):
                print(f"Button pressed: GPIO {pin}")
        time.sleep(0.05)

except KeyboardInterrupt:
    print("Stopped")

finally:
    GPIO.cleanup()