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
PROTOTXT  = 'MobileNetSSD_deploy.prototxt'
CAFFEMODEL = 'MobileNetSSD_deploy.caffemodel'

# MobileNet SSD classes
CLASSES = [
    'background', 'aeroplane', 'bicycle', 'bird', 'boat',
    'bottle', 'bus', 'car', 'cat', 'chair',
    'cow', 'diningtable', 'dog', 'horse', 'motorbike',
    'person', 'pottedplant', 'sheep', 'sofa', 'train', 'tvmonitor'
]

# friendly names for speaking
FRIENDLY_NAMES = {
    'person':      'Person',
    'chair':       'Chair',
    'diningtable': 'Table',
    'bottle':      'Bottle',
    'bicycle':     'Bicycle',
    'motorbike':   'Motorcycle',
    'car':         'Car',
    'bus':         'Bus',
    'sofa':        'Sofa',
    'tvmonitor':   'Screen',
    'pottedplant': 'Plant',
    'boat':        'Boat',
    'train':       'Train',
}
# ─────────────────────────────────────────────────────────────────────────────

# ── STATE ─────────────────────────────────────────────────────────────────────
running       = False
last_message  = ''
last_spoke    = 0
REPEAT_EVERY  = 3  # repeat same warning every 3 seconds
# ─────────────────────────────────────────────────────────────────────────────

# ── SPEAK ─────────────────────────────────────────────────────────────────────
def speak(text):
    print(f">> {text}")
    threading.Thread(target=lambda: os.system(f'espeak -s 140 "{text}"'), daemon=True).start()
# ─────────────────────────────────────────────────────────────────────────────

# ── SMART SPEAK - only speaks when situation changes or every 3 seconds ───────
def smart_speak(message):
    global last_message, last_spoke
    now = time.time()
    if message != last_message or (now - last_spoke) > REPEAT_EVERY:
        speak(message)
        last_message = message
        last_spoke   = now
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

    # get most prominent object name in each zone
    def zone_name(zone_list):
        if not zone_list:
            return None
        return zone_list[0]['name']

    if center and left and right:
        return f"Stop. Obstacles on all sides."
    elif center and left:
        name = zone_name(center)
        return f"{name} ahead. Move right."
    elif center and right:
        name = zone_name(center)
        return f"{name} ahead. Move left."
    elif center:
        name = zone_name(center)
        return f"{name} ahead. Stop."
    elif left and right:
        return "Obstacles on both sides. Move carefully."
    elif left:
        name = zone_name(left)
        return f"{name} on the left. Move right."
    elif right:
        name = zone_name(right)
        return f"{name} on the right. Move left."

    return "Path clear."
# ─────────────────────────────────────────────────────────────────────────────

# ── DETECTION LOOP ────────────────────────────────────────────────────────────
def detection_loop(cap):
    global running

    print("Loading model...")
    net = cv2.dnn.readNetFromCaffe(PROTOTXT, CAFFEMODEL)
    print("Model loaded")
    speak("Navigation active. Scanning for obstacles.")

    while running:
        ret, frame = cap.read()
        if not ret:
            break

        frame_width  = frame.shape[1]
        frame_height = frame.shape[0]

        # prepare frame for model
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

            # get bounding box
            box      = detections_raw[0, 0, i, 3:7] * np.array([frame_width, frame_height, frame_width, frame_height])
            x1, y1, x2, y2 = box.astype(int)
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2

            # ignore objects in top 20% of frame (usually ceiling/sky)
            if center_y < frame_height * 0.2:
                continue

            # get friendly name
            name = FRIENDLY_NAMES.get(class_name, 'Unknown object')
            zone = get_zone(center_x, frame_width)

            detections.append({
                'name':       name,
                'zone':       zone,
                'confidence': confidence,
                'center_x':  center_x
            })

            print(f"Detected: {name} | Zone: {zone} | Confidence: {confidence:.0%}")

        instruction = build_instruction(detections)
        smart_speak(instruction)

        time.sleep(0.1)  # small delay between frames

    print("Detection loop stopped")
# ─────────────────────────────────────────────────────────────────────────────

# ── RUN MODE ──────────────────────────────────────────────────────────────────
def run_navigation_mode():
    global running
    running = False  # reset first
    speak("Mode 1. Active path navigation.")
    cap = open_camera()
    if not cap:
        speak("Camera not found.")
        return None
    speak("Ready. Navigation starting.")
    running = True
    threading.Thread(target=lambda: detection_loop(cap), daemon=True).start()
    return cap

def stop_navigation(cap):
    global running
    running = False
    if cap:
        cap.release()
    speak("Navigation stopped.")
# ─────────────────────────────────────────────────────────────────────────────