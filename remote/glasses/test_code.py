'''
Currency Test - Raspberry Pi
Press TRIGGER button to identify currency
Press Ctrl+C to quit
'''

import cv2
import os
import threading
import RPi.GPIO as GPIO
import time
from google import genai
from google.genai import types

# ── GEMINI API ────────────────────────────────────────────────────────────────
os.environ['GEMINI_API_KEY'] = 'YOUR_KEY'
client = genai.Client()
# ─────────────────────────────────────────────────────────────────────────────

# ── GPIO ──────────────────────────────────────────────────────────────────────
TRIGGER = 21
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(TRIGGER, GPIO.IN, pull_up_down=GPIO.PUD_UP)
# ─────────────────────────────────────────────────────────────────────────────

# ── DEBOUNCE ──────────────────────────────────────────────────────────────────
last_press = 0
DEBOUNCE_MS = 300

def debounce():
    global last_press
    now = time.time() * 1000
    if now - last_press > DEBOUNCE_MS:
        last_press = now
        return True
    return False
# ─────────────────────────────────────────────────────────────────────────────

def speak(text):
    print(f">> {text}")
    threading.Thread(target=lambda: os.system(f'espeak -s 140 "{text}"'), daemon=True).start()

def ask_gemini(frame):
    _, buffer = cv2.imencode('.jpg', frame)
    image_bytes = bytes(buffer)

    try:
        print("Sending to Gemini...")
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite-preview",
            contents=[
                types.Content(
                    role="user",
                    parts=[
                        types.Part(
                            inline_data=types.Blob(
                                mime_type="image/jpeg",
                                data=image_bytes
                            )
                        ),
                        types.Part(
                            text="Look at this image and identify Indian currency notes. List each note denomination you can see and how many of each. Then give the total amount in rupees. Be concise. Format your response as: '[count] [denomination] rupee note, total [amount] rupees'. If no currency is visible say 'No currency detected'. If the image is blurry or unclear say 'Image not clear. Please try again'."
                        )
                    ]
                )
            ]
        )
        print("Got response")
        return response.text.strip()

    except Exception as e:
        error = str(e).lower()
        print(f"Full error: {e}")
        if '429' in str(e) or 'quota' in error or 'exhausted' in error:
            return "API limit reached. Please try again later."
        elif '403' in str(e) or 'permission' in error or 'leaked' in error:
            return "API key error. Please check your key."
        elif 'timeout' in error:
            return "Connection timed out. Please try again."
        elif 'network' in error or 'connection' in error:
            return "No internet connection. Please check your network."
        else:
            return "Error. Please try again."

# ── CAMERA ────────────────────────────────────────────────────────────────────
cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

if not cap.isOpened():
    print("Camera not found")
    speak("Camera not found")
    GPIO.cleanup()
    exit()

print("Camera ready. Press TRIGGER to identify.")
speak("Camera ready. Press confirm to identify currency.")

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        cv2.imshow("Currency Test", frame)
        cv2.waitKey(1)

        if GPIO.input(TRIGGER) == GPIO.LOW and debounce():
            print("Trigger pressed")
            speak("Identifying. Please wait.")
            result = ask_gemini(frame)
            print(f"Result: {result}")
            speak(result)

except KeyboardInterrupt:
    print("Stopped")

finally:
    cap.release()
    cv2.destroyAllWindows()
    GPIO.cleanup()