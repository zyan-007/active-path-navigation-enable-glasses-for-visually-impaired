'''
Raspberry Pi - BLE Listener
Fixed version - was working before
Only fix: connection stability
'''

import asyncio
import os
import RPi.GPIO as GPIO
import time
from bleak import BleakScanner, BleakClient

# ── BLE ───────────────────────────────────────────────────────────────────────
DEVICE_NAME         = "Assistive-Glasses-Remote"
CHARACTERISTIC_UUID = "abcd1234-ab12-ab12-ab12-abcdef123456"
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

# ── NOTIFICATION HANDLER ──────────────────────────────────────────────────────
def on_button_press(sender, data):
    signal = data.decode('utf-8').strip()
    print(f"Received: '{signal}'")
    if signal in BUTTON_MESSAGES:
        speak(BUTTON_MESSAGES[signal])
    else:
        print(f"Unknown: '{signal}'")
# ─────────────────────────────────────────────────────────────────────────────

# ── PHASE 2 - SCAN AND CONNECT ────────────────────────────────────────────────
async def phase2_connect():
    while True:
        print("Scanning for ESP32...")
        red_on()

        try:
            # scan until found - no timeout so it waits forever
            device = None
            while device is None:
                device = await BleakScanner.find_device_by_name(
                    DEVICE_NAME, timeout=10
                )
                if device is None:
                    print("Not found, retrying...")

            print(f"Found: {device.address}")

            # connect
            client = BleakClient(device.address)
            await client.connect()

            if not client.is_connected:
                print("Failed to connect, retrying...")
                await asyncio.sleep(2)
                continue

            # stable connection confirmed
            green_on()
            speak("Remote connected. Please select a mode.")
            print("Connected")

            await client.start_notify(CHARACTERISTIC_UUID, on_button_press)

            # keep alive - ping every second to detect drops
            while True:
                if not client.is_connected:
                    print("Connection dropped")
                    break
                await asyncio.sleep(1)

            # disconnected
            await client.disconnect()

        except Exception as e:
            print(f"Error: {e}")

        # disconnected - restart scan
        red_on()
        speak("Remote disconnected. Searching.")
        await asyncio.sleep(2)
# ─────────────────────────────────────────────────────────────────────────────

# ── MAIN ──────────────────────────────────────────────────────────────────────
async def main():
    phase1_wait_for_check_button()
    speak("Searching for remote")
    await phase2_connect()

try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("Stopped")
finally:
    all_off()
    GPIO.cleanup()
# ─────────────────────────────────────────────────────────────────────────────