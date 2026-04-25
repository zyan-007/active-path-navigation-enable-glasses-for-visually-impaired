import cv2
from currency import open_camera, capture_and_identify, speak

cap = open_camera()

if not cap:
    print("Camera not found")
else:
    speak("Camera ready. Press SPACE to identify. Q to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        cv2.imshow("Currency Test - SPACE to capture, Q to quit", frame)

        key = cv2.waitKey(1)

        if key == ord(' '):
            capture_and_identify(cap)
        elif key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()