'''
Raspberry Pi - Classic Bluetooth RFCOMM Client
Connects to ESP32 automatically
Speaks which button was pressed
'''

import bluetooth
import os
import RPi.GPIO as GPIO
import time

# ── BLUETOOTH ─────────────────────────────────────────────────────────────────
DEVICE_NAME = "Assistive-Glasses-Remote"
PORT        = 1  # RFCOMM port
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

# ── PHASE 2 - FIND ESP32 ──────────────────────────────────────────────────────
def phase2_find_device():
    print("Phase 2: scanning for ESP32")
    speak("Searching for remote")
    red_on()

    while True:
        print("Scanning...")
        devices = bluetooth.discover_devices(duration=5, lookup_names=True)

        for address, name in devices:
            if name == DEVICE_NAME:
                print(f"Found: {address}")
                return address

        print("Not found, retrying...")
        time.sleep(2)
# ─────────────────────────────────────────────────────────────────────────────

# ── PHASE 3 - CONNECT AND LISTEN ─────────────────────────────────────────────
def phase3_connect(address):
    print("Phase 3: connecting")

    while True:
        sock = None

        try:
            sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            sock.connect((address, PORT))

            green_on()
            speak("Remote connected. Please select a mode.")
            print("Connected")

            # ── LISTEN ────────────────────────────────────────────────────────
            buffer = ""
            while True:
                data = sock.recv(1024)

                if not data:
                    print("Disconnected")
                    break

                buffer += data.decode('utf-8')

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

        except Exception as e:
            print(f"Error: {e}")

        finally:
            red_on()
            if sock:
                try:
                    sock.close()
                except:
                    pass

        # reconnect
        speak("Remote disconnected. Searching.")
        time.sleep(2)
        address = phase2_find_device()
# ─────────────────────────────────────────────────────────────────────────────

# ── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    phase1_wait_for_check_button()
    address = phase2_find_device()
    phase3_connect(address)

try:
    main()
except KeyboardInterrupt:
    print("Stopped")
finally:
    all_off()
    GPIO.cleanup()
# ─────────────────────────────────────────────────────────────────────────────