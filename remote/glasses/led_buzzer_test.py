'''
Raspberry Pi - WiFi TCP Client
Connects to ESP32 hotspot automatically
Receives button signals and speaks them
'''

import socket
import subprocess
import RPi.GPIO as GPIO
import time

# ── NETWORK DEFINITIONS ───────────────────────────────────────────────────────
ESP32_IP = "192.168.4.1"
PORT     = 8080
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
def set_searching():
    GPIO.output(LED_RED,   GPIO.HIGH)
    GPIO.output(LED_GREEN, GPIO.LOW)

def set_connected():
    GPIO.output(LED_RED,   GPIO.LOW)
    GPIO.output(LED_GREEN, GPIO.HIGH)

def all_leds_off():
    GPIO.output(LED_RED,   GPIO.LOW)
    GPIO.output(LED_GREEN, GPIO.LOW)
# ─────────────────────────────────────────────────────────────────────────────

# ── SPEAK ─────────────────────────────────────────────────────────────────────
def speak(text):
    print(f">> {text}")
    subprocess.run(['pkill', 'espeak'], capture_output=True)
    time.sleep(0.1)
    subprocess.Popen(['espeak', '-s', '140', text])
# ─────────────────────────────────────────────────────────────────────────────

# ── WAIT FOR CHECK BUTTON ─────────────────────────────────────────────────────
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
                print("Check button pressed")
                long_beep()
                time.sleep(0.3)
                return
# ─────────────────────────────────────────────────────────────────────────────

# ── WAIT FOR WIFI ─────────────────────────────────────────────────────────────
def wait_for_wifi():
    print("Waiting for WiFi connection to ESP32 hotspot...")
    while True:
        result = subprocess.run(
            ['ping', '-c', '1', '-W', '2', ESP32_IP],
            capture_output=True
        )
        if result.returncode == 0:
            print("ESP32 hotspot reachable")
            return
        print("ESP32 not reachable yet, retrying...")
        time.sleep(2)
# ─────────────────────────────────────────────────────────────────────────────

# ── CONNECT AND LISTEN ────────────────────────────────────────────────────────
def connect_and_listen():

    while True:
        # ── SET SEARCHING STATE ───────────────────────────────────────────────
        set_searching()
        print("Connecting to ESP32...")

        # only speak searching once per attempt not every loop
        spoke_searching = False

        # ── WAIT FOR WIFI BEFORE ATTEMPTING CONNECTION ────────────────────────
        wait_for_wifi()

        if not spoke_searching:
            speak("Searching for remote")
            spoke_searching = True

        sock = None

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((ESP32_IP, PORT))

            # connected successfully
            sock.settimeout(10)  # timeout for receiving data
            set_connected()
            speak("Remote connected. Please select a mode.")
            print("Connected to ESP32!")

            # ── LISTEN LOOP ───────────────────────────────────────────────────
            buffer = ""
            while True:
                try:
                    data = sock.recv(1024)

                    if not data:
                        # empty data means connection closed
                        print("Connection closed by ESP32")
                        break

                    # decode and clean the signal
                    buffer += data.decode('utf-8')

                    # process complete lines
                    while '\n' in buffer:
                        line, buffer = buffer.split('\n', 1)
                        signal = line.strip()  # remove all whitespace and \r

                        if signal == "":
                            continue  # skip empty lines

                        print(f"Received: '{signal}'")

                        if signal in BUTTON_MESSAGES:
                            speak(BUTTON_MESSAGES[signal])
                        else:
                            print(f"Unknown signal: '{signal}'")

                except socket.timeout:
                    # no data received - check if still connected
                    try:
                        sock.send(b'')  # send empty to check connection
                    except:
                        print("Connection lost - timeout")
                        break

        except ConnectionRefusedError:
            print("ESP32 server not ready yet, retrying...")

        except OSError as e:
            print(f"Network error: {e}")

        except Exception as e:
            print(f"Connection error: {e}")

        finally:
            # always clean up socket and set searching state
            set_searching()
            if sock:
                try:
                    sock.close()
                except:
                    pass
            print("Disconnected - retrying in 3 seconds...")
            time.sleep(3)
# ─────────────────────────────────────────────────────────────────────────────

# ── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    wait_for_check_button()
    wait_for_wifi()
    connect_and_listen()

try:
    main()
except KeyboardInterrupt:
    print("Stopped")
finally:
    all_leds_off()
    GPIO.cleanup()
# ─────────────────────────────────────────────────────────────────────────────