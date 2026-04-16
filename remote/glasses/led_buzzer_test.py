'''
Raspberry Pi - WiFi TCP Client
Clean rewrite - one thing at a time
1. Check button confirms earphones
2. Wait for ESP32 hotspot
3. Connect and listen for button presses
4. Speak which button was pressed
'''

import socket
import subprocess
import RPi.GPIO as GPIO
import time

# ── NETWORK ───────────────────────────────────────────────────────────────────
ESP32_IP = "192.168.4.1"
PORT     = 8080
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
    subprocess.run(['pkill', 'espeak'], capture_output=True)
    time.sleep(0.1)
    subprocess.Popen(['espeak', '-s', '140', text])
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

# ── PHASE 2 - WAIT FOR ESP32 HOTSPOT ─────────────────────────────────────────
def phase2_wait_for_hotspot():
    print("Phase 2: waiting for ESP32 hotspot")
    speak("Searching for remote")
    red_on()

    while True:
        result = subprocess.run(
            ['ping', '-c', '1', '-W', '2', ESP32_IP],
            capture_output=True
        )
        if result.returncode == 0:
            print("Hotspot found")
            return
        print("Hotspot not found, retrying...")
        time.sleep(2)
# ─────────────────────────────────────────────────────────────────────────────

# ── PHASE 3 - CONNECT TO ESP32 ────────────────────────────────────────────────
def phase3_connect():
    print("Phase 3: connecting to ESP32")

    while True:
        sock = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((ESP32_IP, PORT))
            sock.settimeout(None)

            # connected
            green_on()
            speak("Remote connected. Please select a mode.")
            print("Connected to ESP32")

            # ── LISTEN FOR BUTTON PRESSES ─────────────────────────────────────
            buffer = ""
            while True:
                data = sock.recv(1024)

                if not data:
                    print("ESP32 disconnected")
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
            # ─────────────────────────────────────────────────────────────────

        except Exception as e:
            print(f"Error: {e}")

        finally:
            red_on()
            if sock:
                try:
                    sock.close()
                except:
                    pass

        # disconnected - wait for hotspot to come back then retry
        print("Reconnecting...")
        speak("Remote disconnected")
        phase2_wait_for_hotspot()
# ─────────────────────────────────────────────────────────────────────────────

# ── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    phase1_wait_for_check_button()
    phase2_wait_for_hotspot()
    phase3_connect()

try:
    main()
except KeyboardInterrupt:
    print("Stopped")
finally:
    all_off()
    GPIO.cleanup()
# ─────────────────────────────────────────────────────────────────────────────