'''
Raspberry Pi - WiFi TCP Client
Connects to ESP32 hotspot automatically
Receives button signals and speaks them
'''

import socket
import subprocess
import RPi.GPIO as GPIO
import time
import threading

# ── NETWORK DEFINITIONS ───────────────────────────────────────────────────────
ESP32_IP   = "192.168.4.1"
PORT       = 8080
# ─────────────────────────────────────────────────────────────────────────────

# ── PIN DEFINITIONS ───────────────────────────────────────────────────────────
LED_RED      = 17
LED_GREEN    = 22
BUZZER       = 24
CHECK_BUTTON = 27
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

# ── STATE ─────────────────────────────────────────────────────────────────────
is_connected = False
# ─────────────────────────────────────────────────────────────────────────────

# ── GPIO SETUP ────────────────────────────────────────────────────────────────
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
    global is_connected
    if not is_connected:
        GPIO.output(LED_RED,   GPIO.HIGH)
        GPIO.output(LED_GREEN, GPIO.LOW)

def set_connected():
    GPIO.output(LED_RED,   GPIO.LOW)
    GPIO.output(LED_GREEN, GPIO.HIGH)
# ─────────────────────────────────────────────────────────────────────────────

# ── SPEAK ─────────────────────────────────────────────────────────────────────
def speak(text):
    print(f">> {text}")
    subprocess.run(['pkill', 'espeak'], capture_output=True)
    time.sleep(0.1)
    subprocess.Popen(['espeak', '-s', '140', text])
# ─────────────────────────────────────────────────────────────────────────────

# ── PHASE 1 - WAIT FOR CHECK BUTTON ──────────────────────────────────────────
def wait_for_check_button():
    print("Waiting for check button press...")
    all_leds_off()
    GPIO.output(LED_RED, GPIO.HIGH)

    while True:
        beep(duration=0.2)
        time.sleep(0.8)

        if GPIO.input(CHECK_BUTTON) == GPIO.LOW:
            time.sleep(0.05)
            if GPIO.input(CHECK_BUTTON) == GPIO.LOW:
                print("Check button pressed - earphones confirmed")
                long_beep()
                time.sleep(0.3)
                return
# ─────────────────────────────────────────────────────────────────────────────

# ── PHASE 2 - WAIT FOR WIFI ───────────────────────────────────────────────────
def wait_for_wifi():
    print("Waiting for WiFi connection to ESP32 hotspot...")
    speak("Waiting for network")

    while True:
        result = subprocess.run(
            ['ping', '-c', '1', '-W', '1', ESP32_IP],
            capture_output=True
        )
        if result.returncode == 0:
            print("ESP32 hotspot reachable")
            return
        else:
            print("ESP32 not reachable yet, retrying...")
            time.sleep(2)
# ─────────────────────────────────────────────────────────────────────────────

# ── PHASE 3 - CONNECT AND LISTEN ─────────────────────────────────────────────
def connect_and_listen():
    global is_connected

    while True:
        is_connected = False
        set_searching()
        speak("Searching for remote")
        print("Connecting to ESP32...")

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((ESP32_IP, PORT))
            sock.settimeout(None)  # remove timeout after connected

            is_connected = True
            set_connected()  # green on red off
            speak("Remote connected. Please select a mode.")
            print("Connected to ESP32!")

            # listen for button signals
            while True:
                data = sock.recv(1024)
                if not data:
                    print("Connection lost")
                    break

                signal = data.decode('utf-8').strip()
                print(f"Received: {signal}")

                if signal in BUTTON_MESSAGES:
                    speak(BUTTON_MESSAGES[signal])
                else:
                    print(f"Unknown signal: {signal}")

        except Exception as e:
            print(f"Connection error: {e}")

        finally:
            is_connected = False
            set_searching()
            try:
                sock.close()
            except:
                pass
            speak("Remote disconnected. Searching again.")
            time.sleep(3)
# ─────────────────────────────────────────────────────────────────────────────

# ── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    # phase 1 - wait for check button
    wait_for_check_button()

    # phase 2 - wait for wifi
    wait_for_wifi()

    # phase 3 - connect and listen forever
    connect_and_listen()

try:
    main()
except KeyboardInterrupt:
    print("Stopped")
finally:
    GPIO.cleanup()
# ─────────────────────────────────────────────────────────────────────────────