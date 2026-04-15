'''
Raspberry Pi - LED and Buzzer Test
Tests all 3 LEDs blinking and buzzer beep
'''

import RPi.GPIO as GPIO
import time

# ── PIN DEFINITIONS ───────────────────────────────────────────────────────────
LED_RED    = 17
LED_YELLOW = 27
LED_GREEN  = 22
BUZZER     = 24
# ─────────────────────────────────────────────────────────────────────────────

# ── SETUP ─────────────────────────────────────────────────────────────────────
GPIO.setmode(GPIO.BCM)   # use GPIO number not physical pin number
GPIO.setwarnings(False)

GPIO.setup(LED_RED,    GPIO.OUT)
GPIO.setup(LED_YELLOW, GPIO.OUT)
GPIO.setup(LED_GREEN,  GPIO.OUT)
GPIO.setup(BUZZER,     GPIO.OUT)

# all off at start
GPIO.output(LED_RED,    GPIO.LOW)
GPIO.output(LED_YELLOW, GPIO.LOW)
GPIO.output(LED_GREEN,  GPIO.LOW)
GPIO.output(BUZZER,     GPIO.LOW)
# ─────────────────────────────────────────────────────────────────────────────

def beep(duration=0.5):
    GPIO.output(BUZZER, GPIO.HIGH)
    time.sleep(duration)
    GPIO.output(BUZZER, GPIO.LOW)

def blink(pin, times=3, speed=0.3):
    for _ in range(times):
        GPIO.output(pin, GPIO.HIGH)
        time.sleep(speed)
        GPIO.output(pin, GPIO.LOW)
        time.sleep(speed)

try:
    print("Testing RED LED...")
    blink(LED_RED, times=3)
    time.sleep(0.5)

    print("Testing YELLOW LED...")
    blink(LED_YELLOW, times=3)
    time.sleep(0.5)

    print("Testing GREEN LED...")
    blink(LED_GREEN, times=3)
    time.sleep(0.5)

    print("Testing all LEDs together...")
    GPIO.output(LED_RED,    GPIO.HIGH)
    GPIO.output(LED_YELLOW, GPIO.HIGH)
    GPIO.output(LED_GREEN,  GPIO.HIGH)
    time.sleep(2)
    GPIO.output(LED_RED,    GPIO.LOW)
    GPIO.output(LED_YELLOW, GPIO.LOW)
    GPIO.output(LED_GREEN,  GPIO.LOW)
    time.sleep(0.5)

    print("Testing BUZZER...")
    beep(duration=1)  # 1 second beep

    print("All tests done!")

except KeyboardInterrupt:
    print("Test stopped")

finally:
    GPIO.cleanup()  # always cleanup at end to reset all pins