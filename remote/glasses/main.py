'''
Raspberry Pi - Assistive Glasses
4 Buttons + Trigger directly connected to Pi
'''

import os
import threading
import time
import RPi.GPIO as GPIO
from currency import run_currency_mode, capture_and_identify
from tts import run_tts_mode, capture_and_read
from face_recognition_mode import run_face_mode, register_face, recognize_face

# ── GLOBAL STATE ──────────────────────────────────────────────────────────────
cap          = None
current_mode = None
face_mode    = 'register'
# ─────────────────────────────────────────────────────────────────────────────

# ── PINS ──────────────────────────────────────────────────────────────────────
TRIGGER = 21
BUTTON1 = 5
BUTTON2 = 6
BUTTON3 = 13
BUTTON4 = 19

LED_RED   = 17
LED_GREEN = 22
# ─────────────────────────────────────────────────────────────────────────────

# ── BUTTON MESSAGES ───────────────────────────────────────────────────────────
BUTTON_MESSAGES = {
    TRIGGER: "Confirm",
    BUTTON1: "Mode 1. Active path navigation.",
    BUTTON2: "Mode 2. Face recognition.",
    BUTTON3: "Mode 3. Currency identification.",
    BUTTON4: "Mode 4. Text to speech.",
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
    threading.Thread(target=lambda: os.system(f'espeak -s 140 "{text}"'), daemon=True).start()
    words = len(text.split())
    time.sleep(max(1, words * 0.4))

def speak_async(text):
    print(f">> {text}")
    threading.Thread(target=lambda: os.system(f'espeak -s 140 "{text}"'), daemon=True).start()
# ─────────────────────────────────────────────────────────────────────────────

# ── PHASE 1 - RED BLINK 10 SECONDS ───────────────────────────────────────────
def phase1_blink():
    print("Phase 1: startup")
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
    time.sleep(2)
# ─────────────────────────────────────────────────────────────────────────────

# ── PHASE 3 - READY ───────────────────────────────────────────────────────────
def phase3_ready():
    print("Phase 3: ready")
    green_on()
    speak("Remote synced. Please select a mode.")
    time.sleep(1)
# ─────────────────────────────────────────────────────────────────────────────

# ── PHASE 4 - LISTEN ──────────────────────────────────────────────────────────
def phase4_listen():
    global cap, current_mode, face_mode
    print("Phase 4: listening")
    buttons = [TRIGGER, BUTTON1, BUTTON2, BUTTON3, BUTTON4]

    while True:
        for pin in buttons:
            if GPIO.input(pin) == GPIO.LOW and debounce(pin):
                print(f"Button pressed: GPIO {pin}")

                if pin == BUTTON2:
                    if cap:
                        cap.release()
                        cap = None
                    if current_mode != 'face':
                        current_mode = 'face'
                        face_mode = 'register'
                    else:
                        face_mode = 'recognize'
                    def start_face():
                        global cap
                        cap = run_face_mode(face_mode)
                    threading.Thread(target=start_face, daemon=True).start()

                elif pin == BUTTON3:
                    if cap:
                        cap.release()
                        cap = None
                    current_mode = "currency"
                    def start_currency():
                        global cap
                        cap = run_currency_mode()
                    threading.Thread(target=start_currency, daemon=True).start()

                elif pin == BUTTON4:
                    if cap:
                        cap.release()
                        cap = None
                    current_mode = "tts"
                    def start_tts():
                        global cap
                        cap = run_tts_mode()
                    threading.Thread(target=start_tts, daemon=True).start()

                elif pin == TRIGGER:
                    if current_mode == "currency" and cap:
                        threading.Thread(
                            target=lambda: capture_and_identify(cap),
                            daemon=True
                        ).start()
                    elif current_mode == "tts" and cap:
                        threading.Thread(
                            target=lambda: capture_and_read(cap),
                            daemon=True
                        ).start()
                    elif current_mode == "face" and cap:
                        if face_mode == 'register':
                            threading.Thread(
                                target=lambda: register_face(cap),
                                daemon=True
                            ).start()
                        else:
                            threading.Thread(
                                target=lambda: recognize_face(cap),
                                daemon=True
                            ).start()
                    else:
                        speak_async(BUTTON_MESSAGES[TRIGGER])

                else:
                    if cap:
                        cap.release()
                        cap = None
                    current_mode = None
                    message = BUTTON_MESSAGES.get(pin, "Unknown")
                    speak_async(message)

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
    if cap:
        cap.relative()
    all_off()
    GPIO.cleanup()