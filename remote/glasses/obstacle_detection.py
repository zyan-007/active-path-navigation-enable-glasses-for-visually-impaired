'''
Active Path Navigation - Mode 1
Uses MobileNet SSD with OpenCV for obstacle detection
Works on Python 3.13, no PyTorch needed
Raspberry Pi Version
'''

import cv2
import os
import threading
import time
import numpy as np

# ── MODEL ─────────────────────────────────────────────────────────────────────
PROTOTXT   = 'MobileNetSSD_deploy.prototxt'
CAFFEMODEL = 'MobileNetSSD_deploy.caffemodel'

CLASSES = [
    'background', 'aeroplane', 'bicycle', 'bird', 'boat',
    'bottle', 'bus', 'car', 'cat', 'chair',
    'cow', 'diningtable', 'dog', 'horse', 'motorbike',
    'person', 'pottedplant', 'sheep', 'sofa', 'train', 'tvmonitor'
]
# ─────────────────────────────────────────────────────────────────────────────

# ── STATE ─────────────────────────────────────────────────────────────────────
running         = False
last_message    = ''
last_spoke_time = 0
is_speaking     = False
REPEAT_EVERY    = 4
MIN_GAP         = 3
# ─────────────────────────────────────────────────────────────────────────────

# ── SPEAK ─────────────────────────────────────────────────────────────────────
def speak_navigation(text):
    global is_speaking, last_spoke_time, last_message
    now = time.time()

    if is_speaking:
        return

    if text == last_message and (now - last_spoke_time) < REPEAT_EVERY:
        return

    if (now - last_spoke_time) < MIN_GAP:
        return

    is_speaking     = True
    last_message    = text
    last_spoke_time = now
    print(f">> {text}")

    def _speak():
        global is_speaking
        os.system(f'espeak -s 140 "{text}"')
        is_speaking = False

    threading.Thread(target=_speak, daemon=True).start()
# ─────────────────────────────────────────────────────────────────────────────

# ── OPEN CAMERA ───────────────────────────────────────────────────────────────
def open_camera():
    cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    if cap.isOpened():
        print("Camera opened")
        return cap
    cap.release()
    return None
# ─────────────────────────────────────────────────────────────────────────────

# ── ZONE LOGIC ────────────────────────────────────────────────────────────────
def get_zone(center_x, frame_width):
    if center_x < frame_width // 3:
        return 'left'
    elif center_x > (frame_width * 2) // 3:
        return 'right'
    else:
        return 'center'
# ─────────────────────────────────────────────────────────────────────────────

# ── BUILD INSTRUCTION ─────────────────────────────────────────────────────────
def build_instruction(detections):
    if not detections:
        return "Path clear."

    left   = [d for d in detections if d['zone'] == 'left']
    center = [d for d in detections if d['zone'] == 'center']
    right  = [d for d in detections if d['zone'] == 'right']

    if center and left and right:
        return "Stop. Obstacles on all sides."
    elif center and left:
        return "Obstacle ahead and on the left. Move right."
    elif center and right:
        return "Obstacle ahead and on the right. Move left."
    elif center:
        return "Obstacle ahead. Stop."
    elif left and right:
        return "Obstacles on both sides. Move carefully."
    elif left:
        return "Obstacle on the left. Move right."
    elif right:
        return "Obstacle on the right. Move left."

    return "Path clear."
# ─────────────────────────────────────────────────────────────────────────────

# ── DETECTION LOOP ────────────────────────────────────────────────────────────
def detection_loop(cap):
    global running, is_speaking, last_message, last_spoke_time

    print("Loading model...")
    net = cv2.dnn.readNetFromCaffe(PROTOTXT, CAFFEMODEL)
    print("Model loaded")
    speak_navigation("Navigation active. Scanning for obstacles.")

    while running:
        ret, frame = cap.read()
        if not ret:
            break

        frame_width  = frame.shape[1]
        frame_height = frame.shape[0]

        blob = cv2.dnn.blobFromImage(
            cv2.resize(frame, (300, 300)),
            0.007843,
            (300, 300),
            127.5
        )
        net.setInput(blob)
        detections_raw = net.forward()

        detections = []

        for i in range(detections_raw.shape[2]):
            confidence = detections_raw[0, 0, i, 2]

            if confidence < 0.4:
                continue

            class_id   = int(detections_raw[0, 0, i, 1])
            class_name = CLASSES[class_id]

            if class_name == 'background':
                continue

            box     = detections_raw[0, 0, i, 3:7] * np.array([frame_width, frame_height, frame_width, frame_height])
            x1, y1, x2, y2 = box.astype(int)
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2

            # ignore top 20% of frame
            if center_y < frame_height * 0.2:
                continue

            zone = get_zone(center_x, frame_width)
            detections.append({'zone': zone})

            print(f"Obstacle detected | Zone: {zone} | Confidence: {confidence:.0%}")

        instruction = build_instruction(detections)
        speak_navigation(instruction)

        time.sleep(0.3)

    print("Detection loop stopped")
# ─────────────────────────────────────────────────────────────────────────────

# ── RUN MODE ──────────────────────────────────────────────────────────────────
def run_navigation_mode():
    global running, is_speaking, last_message, last_spoke_time
    running         = True
    is_speaking     = False
    last_message    = ''
    last_spoke_time = 0

    cap = open_camera()
    if not cap:
        os.system('espeak -s 140 "Camera not found."')
        running = False
        return None

    threading.Thread(target=lambda: detection_loop(cap), daemon=True).start()
    return cap

def stop_navigation(cap):
    global running, is_speaking
    running     = False
    is_speaking = False
    if cap:
        cap.release()
# ─────────────────────────────────────────────────────────────────────────────