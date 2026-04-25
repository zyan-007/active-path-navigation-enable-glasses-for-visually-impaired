'''
Currency Identification - Mode 3
Uses Gemini Vision API to identify Indian currency notes
Raspberry Pi Version
'''

import cv2
import os
from google import genai
from google.genai import types

# ── GEMINI API ────────────────────────────────────────────────────────────────
os.environ['GEMINI_API_KEY'] = 'YOUR_KEY'
client = genai.Client()
# ─────────────────────────────────────────────────────────────────────────────

def speak(text):
    print(f">> {text}")
    os.system(f'espeak -s 140 "{text}" &')

def ask_gemini(frame):
    _, buffer = cv2.imencode('.jpg', frame)
    image_bytes = bytes(buffer)

    try:
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
                            text="Look at this image and identify Indian currency notes. List each note denomination you can see and how many of each. Then give the total amount in rupees. Be concise. Format your response as: '[count] [denomination] rupee note, total [amount] rupees'. If no currency is visible say 'No currency detected'."
                        )
                    ]
                )
            ]
        )
        return response.text.strip()

    except Exception as e:
        print(f"Error: {e}")
        return "Error identifying currency. Please try again."

def open_camera():
    for index in [0, 1, 2]:
        cap = cv2.VideoCapture(index, cv2.CAP_V4L2)  # Pi uses V4L2
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        if cap.isOpened():
            print(f"Camera opened at index {index}")
            return cap
        cap.release()

    speak("Camera not found.")
    return None

def capture_and_identify(cap):
    ret, frame = cap.read()
    if not ret:
        speak("Failed to capture image.")
        return

    speak("Identifying. Please wait.")
    result = ask_gemini(frame)
    print(f"Gemini says: {result}")
    speak(result)

def run_currency_mode():
    speak("Mode 3 selected. Currency identification.")
    cap = open_camera()
    if cap:
        speak("Ready. Point camera at notes and press confirm.")
    return cap