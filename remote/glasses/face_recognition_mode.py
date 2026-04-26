'''
Face Recognition - Mode 2
Raspberry Pi Version
New flow - recognize first, register if unknown
'''

import cv2
import os
import threading
import time
import pickle
import numpy as np
import face_recognition
import pyaudio
import wave

# ── PATHS ─────────────────────────────────────────────────────────────────────
FACES_DB  = 'faces.pkl'
AUDIO_DIR = 'face_audio'
os.makedirs(AUDIO_DIR, exist_ok=True)
# ─────────────────────────────────────────────────────────────────────────────

# ── AUDIO SETTINGS ────────────────────────────────────────────────────────────
RECORD_SECONDS = 3
SAMPLE_RATE    = 16000  # fixed for Pi
CHUNK          = 1024
CHANNELS       = 1
FORMAT         = pyaudio.paInt16
# ─────────────────────────────────────────────────────────────────────────────

# ── STATE ─────────────────────────────────────────────────────────────────────
# states: 'recognize', 'unknown_prompt', 'capture_prompt', 'recording'
face_state     = 'recognize'
pending_frame  = None
# ─────────────────────────────────────────────────────────────────────────────

# ── LOAD / SAVE FACES ─────────────────────────────────────────────────────────
def load_faces():
    if os.path.exists(FACES_DB):
        with open(FACES_DB, 'rb') as f:
            return pickle.load(f)
    return {'encodings': [], 'names': [], 'audio_files': []}

def save_faces(db):
    with open(FACES_DB, 'wb') as f:
        pickle.dump(db, f)
# ─────────────────────────────────────────────────────────────────────────────

# ── SPEAK ─────────────────────────────────────────────────────────────────────
def speak(text):
    print(f">> {text}")
    threading.Thread(target=lambda: os.system(f'espeak -s 140 "{text}"'), daemon=True).start()
    words = len(text.split())
    time.sleep(max(1, words * 0.4))
# ─────────────────────────────────────────────────────────────────────────────

# ── RECORD AUDIO ──────────────────────────────────────────────────────────────
def record_audio(filename):
    p = pyaudio.PyAudio()

    # find working input device
    device_index = None
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        if info['maxInputChannels'] > 0:
            device_index = i
            print(f"Using audio device: {info['name']}")
            break

    if device_index is None:
        speak("No microphone found.")
        p.terminate()
        return False

    try:
        stream = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=SAMPLE_RATE,
            input=True,
            input_device_index=device_index,
            frames_per_buffer=CHUNK
        )

        print("Recording...")
        frames = []
        for _ in range(0, int(SAMPLE_RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK, exception_on_overflow=False)
            frames.append(data)

        stream.stop_stream()
        stream.close()
        p.terminate()

        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(b''.join(frames))

        print(f"Audio saved: {filename}")
        return True

    except Exception as e:
        print(f"Recording error: {e}")
        p.terminate()
        speak("Recording failed. Please try again.")
        return False
# ─────────────────────────────────────────────────────────────────────────────

# ── PLAY AUDIO ────────────────────────────────────────────────────────────────
def play_audio(filename):
    os.system(f'aplay "{filename}" 2>/dev/null')
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

# ── RECOGNIZE ─────────────────────────────────────────────────────────────────
def try_recognize(frame):
    db = load_faces()
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_frame)

    if not face_locations:
        return None, False  # no face found

    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    for face_encoding in face_encodings:
        if not db['encodings']:
            return None, True  # face found but no db

        matches = face_recognition.compare_faces(db['encodings'], face_encoding, tolerance=0.6)
        distances = face_recognition.face_distance(db['encodings'], face_encoding)

        if True in matches:
            best = np.argmin(distances)
            if matches[best]:
                return db['audio_files'][best], True

    return None, True  # face found but not recognized
# ─────────────────────────────────────────────────────────────────────────────

# ── REGISTER ──────────────────────────────────────────────────────────────────
def register_face_with_frame(frame):
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_frame)

    if not face_locations:
        speak("No face detected. Please try again.")
        return False

    encodings = face_recognition.face_encodings(rgb_frame, face_locations)
    if not encodings:
        speak("Could not process face. Please try again.")
        return False

    encoding = encodings[0]

    # countdown before recording
    speak("Say name in")
    speak("3")
    speak("2")
    speak("1")

    face_count = len(load_faces()['names']) + 1
    audio_file = os.path.join(AUDIO_DIR, f'face_{face_count}.wav')

    success = record_audio(audio_file)
    if not success:
        return False

    db = load_faces()
    db['encodings'].append(encoding)
    db['names'].append(f'face_{face_count}')
    db['audio_files'].append(audio_file)
    save_faces(db)

    speak("Face registered.")
    speak("Press button 2 to recognize again.")
    return True
# ─────────────────────────────────────────────────────────────────────────────

# ── RUN MODE ──────────────────────────────────────────────────────────────────
def run_face_mode():
    global face_state, pending_frame
    face_state    = 'recognize'
    pending_frame = None
    speak("Mode 2. Face recognition.")
    cap = open_camera()
    if cap:
        speak("Ready. Point camera at face and press confirm.")
    else:
        speak("Camera not found.")
    return cap

def handle_trigger(cap):
    global face_state, pending_frame

    if face_state == 'recognize':
        # flush buffer
        for _ in range(5):
            ret, frame = cap.read()
        if not ret:
            speak("Failed to capture.")
            return

        audio_file, face_found = try_recognize(frame)

        if not face_found:
            speak("No face detected. Please try again.")
            return

        if audio_file:
            # recognized
            threading.Thread(target=lambda: play_audio(audio_file), daemon=True).start()
        else:
            # unknown face
            pending_frame = frame
            face_state = 'unknown_prompt'
            speak("Unknown face. Press trigger to register or button 2 to cancel.")

    elif face_state == 'unknown_prompt':
        # user pressed trigger - wants to register
        face_state = 'capture_prompt'
        speak("Press confirm to capture face.")

    elif face_state == 'capture_prompt':
        # capture the face now
        for _ in range(5):
            ret, frame = cap.read()
        if not ret:
            speak("Failed to capture.")
            return
        pending_frame = frame
        face_state = 'recognize'  # reset after registration
        threading.Thread(
            target=lambda: register_face_with_frame(pending_frame),
            daemon=True
        ).start()

def handle_button2(cap):
    global face_state, pending_frame
    # cancel and go back to recognize mode
    face_state    = 'recognize'
    pending_frame = None
    speak("Recognition mode. Point camera at face and press confirm.")