'''
Text to Speech - Mode 4
Uses Gemini Vision API to read text from images
Raspberry Pi Version
'''

import cv2
import os
import threading
import time
from google import genai
from google.genai import types
from config import GEMINI_API_KEY

# ── GEMINI API ────────────────────────────────────────────────────────────────
os.environ['GEMINI_API_KEY'] = GEMINI_API_KEY
client = genai.Client()
# ─────────────────────────────────────────────────────────────────────────────

def speak(text):
    print(f">> {text}")
    threading.Thread(target=lambda: os.system(f'espeak -s 140 "{text}"'), daemon=True).start()
    words = len(text.split())
    time.sleep(max(1, words * 0.4))

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
                            text="Read all the text you can see in this image. Just read the text exactly as it appears, nothing else. If there is no text say 'No text found'. If the image is blurry say 'Image not clear. Please try again'."
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

def open_camera():
    cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    if cap.isOpened():
        print("Camera opened")
        return cap
    cap.release()
    print("Camera not found")
    return None

def capture_and_read(cap):
    print("Capturing frame...")
    for _ in range(5):
        ret, frame = cap.read()
    if not ret:
        speak("Failed to capture image. Please try again.")
        return
    print("Frame captured")
    speak("Reading text. Please wait.")
    result = ask_gemini(frame)
    print(f"Gemini says: {result}")
    speak(result)

def run_tts_mode():
    speak("Mode 4 selected. Text to speech.")
    cap = open_camera()
    if cap:
        speak("Ready. Point camera at text and press confirm.")
    else:
        speak("Camera not found.")
    return cap