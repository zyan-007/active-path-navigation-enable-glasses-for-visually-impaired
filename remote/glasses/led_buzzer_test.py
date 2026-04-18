'''
Raspberry Pi - Direct Button Connection
Buttons connected directly to Pi GPIO
'''

import os
import RPi.GPIO as GPIO
import time

# ── PINS ──────────────────────────────────────────────────────────────────────
BUTTON1   = 5
BUTTON2   = 6
BUTTON3   = 13
BUTTON4   = 19
BUTTON5   = 26
TRIGGER   = 21

LED_RED   = 17
LED_GREEN = 22
# ─────────────────────────────────────────────────────────────────────────────

# ── BUTTON MESSAGES ───────────────────────────────────────────────────────────
BUTTON_MESSAGES = {
    TRIGGER:  "Confirm",
    BUTTON1:  "Mode 1. Active path navigation.",
    BUTTON2:  "Mode 2. Face recognition.",
    BUTTON3:  "Mode 3. Currency identification.",
    BUTTON4:  "Mode 4. Text to speech.",
    BUTTON5:  "Mode 5. World description.",
}
# ─────────────────────────────────────────────────────────────────────────────

# ── GPIO SETUP ────────────────────────────────────────────────────────────────
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(LED_RED,   GPIO.OUT)
GPIO.setup(LED_GREEN, GPIO.OUT)

GPIO.setup(TRIGGER, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUTTON1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUTTON2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUTTON3, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUTTON4, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUTTON5, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.output(LED_RED,   GPIO.LOW)
GPIO.output(LED_GREEN, GPIO.LOW)
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

# ── HELPERS ───────────────────────────────────────────────────────────────────
def red_on():
    GPIO.output(LED_RED,   GPIO.HIGH)
    GPIO.output(LED_GREEN, GPIO.LOW)

def green_on():
    GPIO.output(LED_RED,   GPIO.LOW)
    GPIO.output(LED_GREEN, GPIO.HIGH)

def all_off():
    GPIO.output(LED_RED,   GPIO.LOW)
    GPIO.output(LED_GREEN, GPIO.LOW)

def speak(text):
    print(f">> {text}")
    os.system(f'espeak -s 140 "{text}" &')
# ─────────────────────────────────────────────────────────────────────────────

# ── PHASE 1 - RED BLINK 10 SECONDS ───────────────────────────────────────────
def phase1_blink():
    print("Phase 1: startup sequence")
    start = time.time()

    while time.time() - start < 10:
        GPIO.output(LED_RED, GPIO.HIGH)
        time.sleep(0.5)
        GPIO.output(LED_RED, GPIO.LOW)
        time.sleep(0.5)
# ─────────────────────────────────────────────────────────────────────────────

# ── PHASE 2 - SYNCING ─────────────────────────────────────────────────────────
def phase2_sync():
    print("Phase 2: syncing")
    red_on()
    speak("Syncing remote and setting up audio")
    time.sleep(5)
# ─────────────────────────────────────────────────────────────────────────────

# ── PHASE 3 - READY ───────────────────────────────────────────────────────────
def phase3_ready():
    print("Phase 3: ready")
    green_on()
    speak("Remote synced. Please select a mode.")
    time.sleep(3)
# ─────────────────────────────────────────────────────────────────────────────

# ── PHASE 4 - LISTEN FOR BUTTONS ─────────────────────────────────────────────
def phase4_listen():
    print("Phase 4: listening for buttons")

    buttons = [TRIGGER, BUTTON1, BUTTON2, BUTTON3, BUTTON4, BUTTON5]

    while True:
        for pin in buttons:
            if GPIO.input(pin) == GPIO.LOW and debounce(pin):
                message = BUTTON_MESSAGES.get(pin, "Unknown button")
                print(f"Button pressed: GPIO {pin}")
                speak(message)
        time.sleep(0.05)
# ─────────────────────────────────────────────────────────────────────────────

# ── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    phase1_blink()
    phase2_sync()
    phase3_ready()
    phase4_listen()

try:
    main()
except KeyboardInterrupt:
    print("Stopped")
finally:
    all_off()
    GPIO.cleanup()
# ─────────────────────────────────────────────────────────────────────────────