'''
Raspberry Pi - Assistive Glasses
UART Serial Communication with ESP32
'''

import serial
import os
import RPi.GPIO as GPIO
import time

# ── SERIAL PORT SETUP - runs before anything else ─────────────────────────────
os.system('sudo systemctl stop getty@ttyS0.service')
os.system('sudo systemctl stop serial-getty@ttyS0.service')
os.system('sudo stty -F /dev/ttyS0 9600 cs8 -cstopb -parenb')
time.sleep(1)
# ─────────────────────────────────────────────────────────────────────────────

# ── SERIAL ────────────────────────────────────────────────────────────────────
SERIAL_PORT = '/dev/ttyS0'
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

# ── PHASE 2 - OPEN SERIAL PORT ────────────────────────────────────────────────
def phase2_open_serial():
    print("Phase 2: opening serial port")
    speak("Connecting to remote")

    while True:
        try:
            ser = serial.Serial(
                SERIAL_PORT,
                BAUD_RATE,
                timeout=1,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
            print("Serial port opened")
            green_on()
            speak("Remote connected. Please select a mode.")
            return ser

        except Exception as e:
            print(f"Serial error: {e}")
            red_on()
            time.sleep(2)
# ─────────────────────────────────────────────────────────────────────────────

# ── PHASE 3 - LISTEN ──────────────────────────────────────────────────────────
def phase3_listen(ser):
    print("Phase 3: listening")
    buffer = ""

    while True:
        try:
            if ser.in_waiting > 0:
                raw = ser.read(ser.in_waiting)
                buffer += raw.decode('utf-8', errors='ignore')

                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    signal = line.strip()

                    if not signal:
                        continue

                    print(f"Received: '{signal}'")

                    if signal in BUTTON_MESSAGES:
                        speak(BUTTON_MESSAGES[signal])
                    else:
                        print(f"Unknown: '{signal}'")

            time.sleep(0.05)

        except Exception as e:
            print(f"Error: {e}")
            red_on()
            speak("Connection lost. Reconnecting.")
            ser.close()
            time.sleep(2)
            os.system('sudo stty -F /dev/ttyS0 9600 cs8 -cstopb -parenb')
            time.sleep(0.5)
            ser = phase2_open_serial()
# ─────────────────────────────────────────────────────────────────────────────

# ── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    phase1_wait_for_check_button()
    ser = phase2_open_serial()
    phase3_listen(ser)

try:
    main()
except KeyboardInterrupt:
    print("Stopped")
finally:
    all_off()
    GPIO.cleanup()
# ─────────────────────────────────────────────────────────────────────────────