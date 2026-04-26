'''
Currency Test - Raspberry Pi
Press SPACE to identify currency
Press Q to quit
'''

import cv2
import os
from google import genai
from google.genai import types

# ── GEMINI API ────────────────────────────────────────────────────────────────
os.environ['GEMINI_API_KEY'] = 'YOUR_KEY'
client = genai.Client()
# ─────────────────────────────────────────────────────────────────────────────

def ask_gemini(frame):
    _, buffer = cv2.imencode('.jpg', frame)
    image_bytes = bytes(buffer)

    try:
        print("Sending to Gemini...")
        response = client.models.generate_content(
            model="gemini-2.0-flash-lite",
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
        else:
            return "Error identifying currency. Please try again."

# ── CAMERA ────────────────────────────────────────────────────────────────────
cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

if not cap.isOpened():
    print("Camera not found")
    exit()

print("Camera ready. Press SPACE to identify. Q to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    cv2.imshow("Currency Test - SPACE to capture, Q to quit", frame)

    key = cv2.waitKey(1)

    if key == ord(' '):
        print("Capturing...")
        result = ask_gemini(frame)
        print(f"Result: {result}")

    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print("Done")