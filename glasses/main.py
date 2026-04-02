'''
Active Path Navigation - Obstacle Detection
Windows: uses default backend
Pi: uncomment CAP_V4L2 line
'''

import cv2
from ultralytics import YOLO

# Load YOLOv8 nano model
model = YOLO('yolov8n.pt')

# ── CAMERA SETUP ──────────────────────────────────────────────────────────────
# Windows
cap = cv2.VideoCapture(0)

# Raspberry Pi - uncomment below, comment above
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

    frame_width = frame.shape[1]  # total width of frame in pixels

    # ── ZONE BOUNDARIES ───────────────────────────────────────────────────────
    # Divide frame into 3 equal zones
    left_boundary  = frame_width // 3        # 0 to 213
    right_boundary = (frame_width * 2) // 3  # 213 to 426, 426 to 640

    # Draw zone lines on frame (visual reference)
    cv2.line(frame, (left_boundary, 0),  (left_boundary, 480),  (255, 0, 0), 2)
    cv2.line(frame, (right_boundary, 0), (right_boundary, 480), (255, 0, 0), 2)

    # Zone labels on frame
    cv2.putText(frame, "LEFT",   (10, 30),               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
    cv2.putText(frame, "CENTER", (left_boundary + 10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
    cv2.putText(frame, "RIGHT",  (right_boundary + 10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
    # ─────────────────────────────────────────────────────────────────────────

    # ── YOLO DETECTION ────────────────────────────────────────────────────────
    results = model(frame, verbose=False)

    obstacle_left   = False
    obstacle_center = False
    obstacle_right  = False

    for result in results:
        for box in result.boxes:
            confidence = float(box.conf[0])

            if confidence < 0.5:
                continue

            x1, y1, x2, y2 = map(int, box.xyxy[0])
            class_id   = int(box.cls[0])
            class_name = model.names[class_id]

            # Find center X of the detected object
            center_x = (x1 + x2) // 2

            # Determine which zone the object is in
            if center_x < left_boundary:
                zone = "LEFT"
                obstacle_left = True
            elif center_x > right_boundary:
                zone = "RIGHT"
                obstacle_right = True
            else:
                zone = "CENTER"
                obstacle_center = True

            # Draw box around object
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            # Label with name, confidence, zone
            label = f"{class_name} {confidence:.0%} [{zone}]"
            cv2.putText(frame, label, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    # ─────────────────────────────────────────────────────────────────────────

    # ── NAVIGATION LOGIC ──────────────────────────────────────────────────────
    if obstacle_center and obstacle_left and obstacle_right:
        instruction = "STOP - Obstacles everywhere"
    elif obstacle_center and obstacle_left:
        instruction = "Move RIGHT - Obstacle ahead and on left"
    elif obstacle_center and obstacle_right:
        instruction = "Move LEFT - Obstacle ahead and on right"
    elif obstacle_center:
        instruction = "STOP - Obstacle directly ahead"
    elif obstacle_left:
        instruction = "Move RIGHT - Obstacle on left"
    elif obstacle_right:
        instruction = "Move LEFT - Obstacle on right"
    else:
        instruction = "Path Clear"
    # ─────────────────────────────────────────────────────────────────────────

    # Print instruction to console
    print(f">> {instruction}")

    # Show instruction on frame
    cv2.putText(frame, instruction, (10, 460),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    cv2.imshow("Active Path Navigation", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()