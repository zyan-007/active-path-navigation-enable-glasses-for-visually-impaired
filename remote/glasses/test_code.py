import cv2
import os
os.environ['GEMINI_API_KEY'] = 'YOUR_KEY'

from google import genai
from google.genai import types

client = genai.Client()

def ask_gemini(frame):
    _, buffer = cv2.imencode('.jpg', frame)
    image_bytes = bytes(buffer)

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

cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

print("Camera ready. Press SPACE to identify. Q to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    cv2.imshow("Currency Test", frame)

    key = cv2.waitKey(1)

    if key == ord(' '):
        print("Identifying...")
        result = ask_gemini(frame)
        print(f"Result: {result}")

    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()