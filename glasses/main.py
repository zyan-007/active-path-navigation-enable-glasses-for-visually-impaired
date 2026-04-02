'''just a normal test program to open camera, not yet tested on raspberry pi'''
import cv2

cap = cv2.VideoCapture(0)  # 0 = default camera (your laptop webcam)

if not cap.isOpened():
    print("Camera not found!")
else:
    print("Camera working! Press Q to quit.")
'''
Obstacle Detection - Camera Test with YOLO
Test on Windows first, then pull to Pi and swap comments
'''

import cv2
from ultralytics import YOLO

# Load YOLOv8 nano model (smallest and fastest, good for Pi)
# First run will auto download the model weights (~6MB)
model = YOLO('yolov8n.pt')

# ── CAMERA SETUP ──────────────────────────────────────────────────────────────
# Windows - comment this out when running on Pi
cap = cv2.VideoCapture(0)

# Raspberry Pi - uncomment this when running on Pi, comment out Windows line above
# cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
# ─────────────────────────────────────────────────────────────────────────────

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 30)

if not cap.isOpened():
    print("Camera not found!")
else:
    print("Camera working! Press Q to quit.")

while True:
    ret, frame = cap.read()

    if not ret:
        print("Failed to grab frame")
        break

    # ── YOLO DETECTION ────────────────────────────────────────────────────────
    results = model(frame, verbose=False)  # verbose=False stops YOLO spamming terminal

    for result in results:
        for box in result.boxes:
            # Get confidence score
            confidence = float(box.conf[0])

            # Only process if confidence is above 50%
            if confidence < 0.5:
                continue

            # Get bounding box coordinates
            x1, y1, x2, y2 = map(int, box.xyxy[0])

            # Get class name (person, chair, car etc.)
            class_id = int(box.cls[0])
            class_name = model.names[class_id]

            # Draw box around detected object
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            # Write label above the box
            label = f"{class_name} {confidence:.0%}"
            cv2.putText(frame, label, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            # Print to console
            print(f"Detected: {class_name} | Confidence: {confidence:.0%}")
    # ─────────────────────────────────────────────────────────────────────────

    cv2.imshow("Obstacle Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
while True:
    ret, frame = cap.read()
    
    if not ret:
        print("Failed to grab frame")
        break

    cv2.imshow("Camera Feed", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()