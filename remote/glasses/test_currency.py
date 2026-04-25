from currency import open_camera, capture_and_identify, speak

cap = open_camera()
if cap:
    speak("Press enter to capture")
    input()  # wait for enter key
    capture_and_identify(cap)
    cap.release()