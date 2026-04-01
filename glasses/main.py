import cv2

cap = cv2.VideoCapture(0)  # 0 = default camera (your laptop webcam)

if not cap.isOpened():
    print("Camera not found!")
else:
    print("Camera working! Press Q to quit.")

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