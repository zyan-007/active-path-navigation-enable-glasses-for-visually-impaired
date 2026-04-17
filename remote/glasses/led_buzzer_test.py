'''
Raspberry Pi - UART Serial Listener
Reads button signals from ESP32 over wired UART
Simple, reliable, no wireless issues
'''

import serial
import os
import RPi.GPIO as GPIO
import time

# ── SERIAL ────────────────────────────────────────────────────────────────────
SERIAL_PORT = '/dev/serial0'
BAUD_RATE   = 9600
# ─────────────────────────────────────────────────────────────────────────────

# ── PINS ──────────────────────────────────────────────────────────────────────
LED_RED      = 17
LED_GREEN    = 22
BUZZER       = 24
CHECK_BUTTON = 27
# ─────────────────────────────────────────────────────────────────────────────

# ── BUTTON MESSAGES ───────────────────────────────────────────────────────────
BUTTON_MESSAGES = {
    "TRIGGER": "Confirm",
    "BUTTON1": "Mode 1. Active path navigation.",
    "BUTTON2": "Mode 2. Face recognition.",
    "BUTTON3": "Mode 3. Currency identification.",
    "BUTTON4": "Mode 4. Text to speech.",
    "BUTTON5": "Mode 5. World description.",
}
# ─────────────────────────────────────────────────────────────────────────────

# ── GPIO ──────────────────────────────────────────────────────────────────────
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(LED_RED,      GPIO.OUT)
GPIO.setup(LED_GREEN,    GPIO.OUT)
GPIO.setup(BUZZER,       GPIO.OUT)
GPIO.setup(CHECK_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.output(LED_RED,   GPIO.LOW)
GPIO.output(LED_GREEN, GPIO.LOW)
GPIO.output(BUZZER,    GPIO.LOW)
# ─────────────────────────────────────────────────────────────────────────────

# ── HELPERS ───────────────────────────────────────────────────────────────────
def beep(duration=0.2):
    GPIO.output(BUZZER, GPIO.HIGH)
    time.sleep(duration)
    GPIO.output(BUZZER, GPIO.LOW)

def long_beep():
    GPIO.output(BUZZER, GPIO.HIGH)
    time.sleep(1.5)
    GPIO.output(BUZZER, GPIO.LOW)

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
    os.system(f'espeak -s 140 "{text}"')
# ─────────────────────────────────────────────────────────────────────────────

# ── PHASE 1 - WAIT FOR CHECK BUTTON ──────────────────────────────────────────
def phase1_wait_for_check_button():
    print("Phase 1: waiting for check button")
    red_on()

    while True:
        beep(0.2)
        time.sleep(0.8)

        if GPIO.input(CHECK_BUTTON) == GPIO.LOW:
            time.sleep(0.05)
            if GPIO.input(CHECK_BUTTON) == GPIO.LOW:
                print("Check button pressed")
                long_beep()
                time.sleep(0.5)
                return
# ─────────────────────────────────────────────────────────────────────────────

# ── PHASE 2 - LISTEN FOR BUTTON PRESSES ──────────────────────────────────────
def phase2_listen():
    print("Phase 2: opening serial port")

    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"Serial open: {SERIAL_PORT}")

        green_on()
        speak("System ready. Please select a mode.")

        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').strip()

                if not line:
                    continue

                print(f"Received: '{line}'")

                if line in BUTTON_MESSAGES:
                    speak(BUTTON_MESSAGES[line])
                else:
                    print(f"Unknown: '{line}'")

    except serial.SerialException as e:
        print(f"Serial error: {e}")
        print("Check wiring and that UART is enabled on Pi")
        red_on()
# ─────────────────────────────────────────────────────────────────────────────

# ── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    phase1_wait_for_check_button()
    phase2_listen()

try:
    main()
except KeyboardInterrupt:
    print("Stopped")
finally:
    all_off()
    GPIO.cleanup()
# ─────────────────────────────────────────────────────────────────────────────