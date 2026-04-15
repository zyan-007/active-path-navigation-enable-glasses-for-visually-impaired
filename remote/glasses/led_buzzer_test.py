'''
Raspberry Pi - Assistive Glasses Boot Sequence
Flow:
1. Pi boots - RED on, BUZZER beeps at intervals
2. User plugs earphones, presses CHECK button
3. BUZZER long beep, Audio: "Searching for bluetooth"
4. BLE scanning starts
5. Bluetooth connected - RED off, GREEN on, Audio: "Bluetooth connected. Please select a mode."

If check button held anytime - restarts cycle
'''

import RPi.GPIO as GPIO
import time
import subprocess
import threading

# ── PIN DEFINITIONS ───────────────────────────────────────────────────────────
LED_RED      = 17
LED_GREEN    = 22
BUZZER       = 24
CHECK_BUTTON = 27
# ─────────────────────────────────────────────────────────────────────────────

# ── STATE ─────────────────────────────────────────────────────────────────────
bluetooth_connected = False
earphones_confirmed = False
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

# ── HELPER FUNCTIONS ──────────────────────────────────────────────────────────
def beep(duration=0.2):
    GPIO.output(BUZZER, GPIO.HIGH)
    time.sleep(duration)
    GPIO.output(BUZZER, GPIO.LOW)

def long_beep():
    GPIO.output(BUZZER, GPIO.HIGH)
    time.sleep(1.5)
    GPIO.output(BUZZER, GPIO.LOW)

def all_leds_off():
    GPIO.output(LED_RED,   GPIO.LOW)
    GPIO.output(LED_GREEN, GPIO.LOW)

def speak(text):
    # espeak for text to speech, runs in background so code doesnt wait
    subprocess.Popen(['espeak', text])

def is_button_pressed():
    return GPIO.input(CHECK_BUTTON) == GPIO.LOW
# ─────────────────────────────────────────────────────────────────────────────

# ── INSTALL ESPEAK IF NOT PRESENT ─────────────────────────────────────────────
def ensure_espeak():
    result = subprocess.run(['which', 'espeak'], capture_output=True)
    if result.returncode != 0:
        print("Installing espeak...")
        subprocess.run(['sudo', 'apt', 'install', 'espeak', '-y'])
# ─────────────────────────────────────────────────────────────────────────────

# ── PHASE 1 - WAITING FOR EARPHONES ───────────────────────────────────────────
def wait_for_earphones():
    global earphones_confirmed
    print("Phase 1: Waiting for earphones and check button press...")

    all_leds_off()
    GPIO.output(LED_RED, GPIO.HIGH)  # red on

    while True:
        # beep at intervals while waiting
        beep(duration=0.2)
        time.sleep(0.8)  # beep every 1 second

        # check if button pressed
        if is_button_pressed():
            time.sleep(0.05)  # small debounce
            if is_button_pressed():
                print("Check button pressed - earphones confirmed")
                earphones_confirmed = True
                long_beep()
                time.sleep(0.3)
                break

        # check if button held for 3 seconds - restart cycle
        if is_button_held(3):
            print("Button held - restarting cycle")
            restart_cycle()
            return
# ─────────────────────────────────────────────────────────────────────────────

# ── PHASE 2 - BLUETOOTH SCANNING ──────────────────────────────────────────────
def scan_for_bluetooth():
    global bluetooth_connected
    print("Phase 2: Scanning for bluetooth...")

    speak("Searching for bluetooth device")

    while True:
        # scan for bluetooth devices
        result = subprocess.run(
            ['bluetoothctl', 'scan', 'on'],
            capture_output=True, text=True, timeout=5
        )

        # check if any device found and connected
        devices = subprocess.run(
            ['bluetoothctl', 'devices', 'Connected'],
            capture_output=True, text=True
        )

        if devices.stdout.strip():  # if any connected device found
            print("Bluetooth connected")
            bluetooth_connected = True
            break
        else:
            print("No bluetooth device found, retrying...")
            speak("Searching")
            time.sleep(3)  # wait 3 seconds before retrying

        # check if button held - restart cycle
        if is_button_held(3):
            restart_cycle()
            return
# ─────────────────────────────────────────────────────────────────────────────

# ── PHASE 3 - BLUETOOTH CONNECTED ─────────────────────────────────────────────
def on_bluetooth_connected():
    print("Phase 3: Bluetooth connected")

    GPIO.output(LED_RED,   GPIO.LOW)   # red off
    GPIO.output(LED_GREEN, GPIO.HIGH)  # green on

    speak("Bluetooth connected. Please select a mode.")

    # monitor for disconnection
    monitor_connection()
# ─────────────────────────────────────────────────────────────────────────────

# ── MONITOR CONNECTION ────────────────────────────────────────────────────────
def monitor_connection():
    global bluetooth_connected, earphones_confirmed
    print("Monitoring connection...")

    while True:
        time.sleep(2)  # check every 2 seconds

        # check bluetooth still connected
        devices = subprocess.run(
            ['bluetoothctl', 'devices', 'Connected'],
            capture_output=True, text=True
        )

        if not devices.stdout.strip():
            print("Bluetooth disconnected - restarting cycle")
            restart_cycle()
            return

        # check if button held - restart cycle
        if is_button_held(3):
            restart_cycle()
            return
# ─────────────────────────────────────────────────────────────────────────────

# ── BUTTON HELD CHECK ─────────────────────────────────────────────────────────
def is_button_held(seconds):
    if is_button_pressed():
        time.sleep(seconds)
        if is_button_pressed():
            return True
    return False
# ─────────────────────────────────────────────────────────────────────────────

# ── RESTART CYCLE ─────────────────────────────────────────────────────────────
def restart_cycle():
    global bluetooth_connected, earphones_confirmed
    print("Restarting cycle...")

    bluetooth_connected  = False
    earphones_confirmed  = False

    all_leds_off()
    GPIO.output(BUZZER, GPIO.LOW)

    time.sleep(1)
    main()
# ─────────────────────────────────────────────────────────────────────────────

# ── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    ensure_espeak()

    # phase 1 - wait for earphones
    wait_for_earphones()

    # phase 2 - scan for bluetooth
    scan_for_bluetooth()

    # phase 3 - connected
    if bluetooth_connected:
        on_bluetooth_connected()

try:
    main()

except KeyboardInterrupt:
    print("Stopped")

finally:
    GPIO.cleanup()
# ─────────────────────────────────────────────────────────────────────────────