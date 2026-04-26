'''
Active Path Navigation - Mode 1
Press TRIGGER to scan once and get directions
Uses clock positions for obstacle location
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
net         = None
is_busy     = False
model_ready = False
# ─────────────────────────────────────────────────────────────────────────────

# ── SPEAK ─────────────────────────────────────────────────────────────────────
def speak(text):
    print(f">> {text}")
    os.system(f'espeak -s 140 "{text}"')
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

# ── CLOCK POSITION ────────────────────────────────────────────────────────────
def get_clock_position(center_x, frame_width):
    ratio = center_x / frame_width
    if ratio < 0.14:
        return "9 o clock"
    elif ratio < 0.28:
        return "10 o clock"
    elif ratio < 0.42:
        return "11 o clock"
    elif ratio < 0.58:
        return "12 o clock"
    elif ratio < 0.72:
        return "1 o clock"
    elif ratio < 0.86:
        return "2 o clock"
    else:
        return "3 o clock"
# ─────────────────────────────────────────────────────────────────────────────

# ── BOX SIZE TO STEPS ─────────────────────────────────────────────────────────
def get_steps(box_width, frame_width):
    ratio = box_width / frame_width
    if ratio > 0.5:
        return 0
    elif ratio > 0.3:
        return 2
    elif ratio > 0.15:
        return 4
    else:
        return 6
# ─────────────────────────────────────────────────────────────────────────────

# ── BUILD INSTRUCTION ─────────────────────────────────────────────────────────
def build_instruction(detections):
    if not detections:
        return "Path clear. You can walk forward."

    left   = [d for d in detections if d['zone'] == 'left']
    center = [d for d in detections if d['zone'] == 'center']
    right  = [d for d in detections if d['zone'] == 'right']

    if center and left and right:
        return "Stop. Obstacles on all sides. Do not move."
    elif center and left:
        steps = center[0]['steps']
        clock = center[0]['clock']
        if steps == 0:
            return f"Stop. Obstacle very close at {clock}. Move right."
        return f"Obstacle at {clock}. Move {steps} steps right."
    elif center and right:
        steps = center[0]['steps']
        clock = center[0]['clock']
        if steps == 0:
            return f"Stop. Obstacle very close at {clock}. Move left."
        return f"Obstacle at {clock}. Move {steps} steps left."
    elif center:
        steps = center[0]['steps']
        clock = center[0]['clock']
        if steps == 0:
            return f"Stop. Obstacle very close at {clock}."
        return f"Obstacle at {clock}. Move {steps} steps to avoid."
    elif left and right:
        return "Obstacles on both sides. Move carefully forward."
    elif left:
        clock = left[0]['clock']
        return f"Obstacle at {clock}. Move right to avoid."
    elif right:
        clock = right[0]['clock']
        return f"Obstacle at {clock}. Move left to avoid."

    return "Path clear. You can walk forward."
# ─────────────────────────────────────────────────────────────────────────────

# ── SCAN ONCE ─────────────────────────────────────────────────────────────────
def scan_once(cap):
    global net, is_busy, model_ready

    if not model_ready:
        os.system('espeak -s 140 "Please wait. Still loading."')
        return

    if is_busy:
        return

    is_busy = True

    def _scan():
        global is_busy

        for _ in range(5):
            ret, frame = cap.read()

        if not ret:
            speak("Failed to capture.")
            is_busy = False
            return

        frame_width  = frame.shape[1]
        frame_height = frame.shape[0]

        speak("Scanning.")

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
            center_x  = (x1 + x2) // 2
            center_y  = (y1 + y2) // 2
            box_width = x2 - x1

            if center_y < frame_height * 0.2:
                continue

            zone  = get_zone(center_x, frame_width)
            clock = get_clock_position(center_x, frame_width)
            steps = get_steps(box_width, frame_width)

            detections.append({
                'zone':       zone,
                'clock':      clock,
                'steps':      steps,
                'confidence': confidence,
            })

            print(f"Obstacle | Zone: {zone} | Clock: {clock} | Steps: {steps} | Confidence: {confidence:.0%}")

        instruction = build_instruction(detections)
        speak(instruction)
        is_busy = False

    threading.Thread(target=_scan, daemon=True).start()
# ─────────────────────────────────────────────────────────────────────────────

# ── RUN MODE ──────────────────────────────────────────────────────────────────
def run_navigation_mode():
    global net, is_busy, model_ready
    is_busy     = False
    model_ready = False

    speak("Mode 1. Active path navigation.")
    cap = open_camera()
    if not cap:
        speak("Camera not found.")
        return None

    print("Loading model...")
    net = cv2.dnn.readNetFromCaffe(PROTOTXT, CAFFEMODEL)
    print("Model loaded")
    model_ready = True

    speak("Ready. Press confirm to scan.")
    return cap

def stop_navigation(cap):
    global is_busy, model_ready
    is_busy     = False
    model_ready = False
    if cap:
        cap.release()
# ─────────────────────────────────────────────────────────────────────────────