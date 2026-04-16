'''
Raspberry Pi - BLE Listener with LED and Buzzer
Boot sequence:
1. RED on, BUZZER beeps at intervals - waiting for check button
2. Check button pressed - long beep, starts BLE scan
3. BLE connected - RED off, GREEN on, Audio: "Remote connected"
4. If disconnected - RED on, GREEN off, restart scan
'''

import asyncio
import subprocess
import RPi.GPIO as GPIO
import threading
import time
from bleak import BleakScanner, BleakClient

# ── PIN DEFINITIONS ───────────────────────────────────────────────────────────
LED_RED      = 17
LED_GREEN    = 22
BUZZER       = 24
CHECK_BUTTON = 27
# ─────────────────────────────────────────────────────────────────────────────

# ── BLE DEFINITIONS ───────────────────────────────────────────────────────────
DEVICE_NAME         = "Assistive-Glasses-Remote"
CHARACTERISTIC_UUID = "abcd1234-ab12-ab12-ab12-abcdef123456"
# ─────────────────────────────────────────────────────────────────────────────

# ── BUTTON MESSAGES ───────────────────────────────────────────────────────────
BUTTON_MESSAGES = {
    "TRIGGER": "Confirm button pressed",
    "BUTTON1": "Button 1 pressed. Mode 1 selected. Active path navigation.",
    "BUTTON2": "Button 2 pressed. Mode 2 selected. Face registration and recognition.",
    "BUTTON3": "Button 3 pressed. Mode 3 selected. Currency identification.",
    "BUTTON4": "Button 4 pressed. Mode 4 selected. Text to speech.",
    "BUTTON5": "Button 5 pressed. Mode 5 selected. World description.",
}
# ─────────────────────────────────────────────────────────────────────────────

# ── GPIO SETUP ────────────────────────────────────────────────────────────────
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(LED_RED,      GPIO.OUT)
GPIO.setup(LED_GREEN,    GPIO.OUT)
GPIO.setup(BUZZER,       GPIO.OUT)
GPIO.setup(CHECK_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# all off at start
GPIO.output(LED_RED,   GPIO.LOW)
GPIO.output(LED_GREEN, GPIO.LOW)
GPIO.output(BUZZER,    GPIO.LOW)
# ─────────────────────────────────────────────────────────────────────────────

# ── BUZZER HELPERS ────────────────────────────────────────────────────────────
def beep(duration=0.2):
    GPIO.output(BUZZER, GPIO.HIGH)
    time.sleep(duration)
    GPIO.output(BUZZER, GPIO.LOW)

def long_beep():
    GPIO.output(BUZZER, GPIO.HIGH)
    time.sleep(1.5)
    GPIO.output(BUZZER, GPIO.LOW)
# ─────────────────────────────────────────────────────────────────────────────

# ── LED HELPERS ───────────────────────────────────────────────────────────────
def all_leds_off():
    GPIO.output(LED_RED,   GPIO.LOW)
    GPIO.output(LED_GREEN, GPIO.LOW)

def set_searching():
    # red on, green off - searching for remote
    GPIO.output(LED_RED,   GPIO.HIGH)
    GPIO.output(LED_GREEN, GPIO.LOW)

def set_connected():
    # green on, red off - remote connected
    GPIO.output(LED_RED,   GPIO.LOW)
    GPIO.output(LED_GREEN, GPIO.HIGH)
# ─────────────────────────────────────────────────────────────────────────────

# ── SPEAK ─────────────────────────────────────────────────────────────────────
def speak(text):
    print(f">> {text}")
    subprocess.Popen(['espeak', text])
# ─────────────────────────────────────────────────────────────────────────────

# ── NOTIFICATION HANDLER ──────────────────────────────────────────────────────
def on_button_press(sender, data):
    signal = data.decode('utf-8').strip()
    print(f"Received signal: {signal}")
    if signal in BUTTON_MESSAGES:
        speak(BUTTON_MESSAGES[signal])
    else:
        print(f"Unknown signal: {signal}")
# ─────────────────────────────────────────────────────────────────────────────

# ── DISCONNECT CALLBACK ───────────────────────────────────────────────────────
def on_disconnect(client):
    print("Remote disconnected")
    set_searching()  # red on green off
    speak("Remote disconnected. Searching again.")
# ─────────────────────────────────────────────────────────────────────────────

# ── PHASE 1 - WAIT FOR CHECK BUTTON ──────────────────────────────────────────
def wait_for_check_button():
    print("Waiting for earphones and check button press...")
    all_leds_off()
    GPIO.output(LED_RED, GPIO.HIGH)  # red on while waiting

    while True:
        beep(duration=0.2)
        time.sleep(0.8)  # beep every second

        if GPIO.input(CHECK_BUTTON) == GPIO.LOW:
            time.sleep(0.05)  # debounce
            if GPIO.input(CHECK_BUTTON) == GPIO.LOW:
                print("Check button pressed - earphones confirmed")
                long_beep()
                time.sleep(0.3)
                return
# ─────────────────────────────────────────────────────────────────────────────

# ── PHASE 2 - SCAN AND CONNECT ────────────────────────────────────────────────
async def connect_to_remote():
    while True:
        print("Scanning for ESP32 remote...")
        set_searching()  # red on green off
        speak("Searching for remote")

        target = await BleakScanner.find_device_by_name(DEVICE_NAME, timeout=10)

        if target is None:
            print("Remote not found, retrying in 3 seconds...")
            await asyncio.sleep(3)
            continue

        print(f"Found remote: {target.address}")

        client = BleakClient(target.address, disconnected_callback=on_disconnect)

        try:
            await client.connect()
            print("Connected to remote!")
            set_connected()  # green on red off
            speak("Remote connected. Please select a mode.")

            await client.start_notify(CHARACTERISTIC_UUID, on_button_press)

            # keep alive loop
            while client.is_connected:
                await asyncio.sleep(0.5)

            print("Connection lost - restarting scan")
            await asyncio.sleep(2)

        except Exception as e:
            print(f"Connection error: {e}")
            set_searching()
            await asyncio.sleep(3)

        finally:
            if client.is_connected:
                await client.disconnect()
# ─────────────────────────────────────────────────────────────────────────────

# ── MAIN ──────────────────────────────────────────────────────────────────────
async def main():
    # phase 1 - wait for check button (runs in sync before async loop)
    wait_for_check_button()

    # phase 2 - scan and connect
    await connect_to_remote()

try:
    asyncio.run(main())

except KeyboardInterrupt:
    print("Stopped")

finally:
    GPIO.cleanup()
# ─────────────────────────────────────────────────────────────────────────────