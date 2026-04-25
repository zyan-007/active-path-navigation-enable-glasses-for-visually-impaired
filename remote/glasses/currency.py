'''
Currency Identification - Mode 3
Uses Gemini Vision API to identify Indian currency notes
Raspberry Pi Version
'''

import cv2
import os
from google import genai
from google.genai import types
from config import GEMINI_API_KEY

# ── GEMINI API ────────────────────────────────────────────────────────────────
os.environ['GEMINI_API_KEY'] = GEMINI_API_KEY
client = genai.Client()
# ─────────────────────────────────────────────────────────────────────────────

def speak(text):
    print(f">> {text}")
    os.system(f'espeak -s 140 "{text}" &')

def ask_gemini(frame):
    _, buffer = cv2.imencode('.jpg', frame)
    image_bytes = bytes(buffer)

    try:
        print("Sending to Gemini...")
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
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
        print("Got response from Gemini")
        return response.text.strip()

    except Exception as e:
        error = str(e).lower()
        print(f"Full error: {e}")
        if 'quota' in error:
            return "API limit reached. Please try again later."
        elif 'timeout' in error:
            return "Connection timed out. Please try again."
        elif 'network' in error or 'connection' in error:
            return "No internet connection. Please check your network."
        elif '403' in error or 'permission' in error:
            return "API key error. Please check your key."
        else:
            return "Error identifying currency. Please try again."

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

def capture_and_identify(cap):
    print("Capturing frame...")
    ret, frame = cap.read()
    if not ret:
        speak("Failed to capture image. Please try again.")
        return
    print("Frame captured")
    speak("Identifying. Please wait.")
    result = ask_gemini(frame)
    print(f"Gemini says: {result}")
    speak(result)

def run_currency_mode():
    speak("Mode 3 selected. Currency identification.")
    cap = open_camera()
    if cap:
        speak("Ready. Point camera at notes and press confirm.")
    else:
        speak("Camera not found.")
    return cap