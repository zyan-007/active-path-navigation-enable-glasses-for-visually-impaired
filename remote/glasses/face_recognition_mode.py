'''
Face Recognition - Mode 2
Register faces with voice labels
Recognize faces and play back audio
Raspberry Pi Version
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
from config import GEMINI_API_KEY

# ── PATHS ─────────────────────────────────────────────────────────────────────
FACES_DB    = 'faces.pkl'   # stores face encodings
AUDIO_DIR   = 'face_audio'  # stores name audio files
os.makedirs(AUDIO_DIR, exist_ok=True)
# ─────────────────────────────────────────────────────────────────────────────

# ── AUDIO SETTINGS ────────────────────────────────────────────────────────────
RECORD_SECONDS = 3
SAMPLE_RATE    = 44100
CHUNK          = 1024
CHANNELS       = 1
FORMAT         = pyaudio.paInt16
# ─────────────────────────────────────────────────────────────────────────────

# ── LOAD FACES DB ─────────────────────────────────────────────────────────────
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

def speak_async(text):
    print(f">> {text}")
    threading.Thread(target=lambda: os.system(f'espeak -s 140 "{text}"'), daemon=True).start()
# ─────────────────────────────────────────────────────────────────────────────

# ── BEEP ──────────────────────────────────────────────────────────────────────
def beep():
    os.system('speaker-test -t sine -f 1000 -l 1 -s 1 2>/dev/null &')
    time.sleep(0.5)
# ─────────────────────────────────────────────────────────────────────────────

# ── RECORD AUDIO ──────────────────────────────────────────────────────────────
def record_audio(filename):
    p = pyaudio.PyAudio()
    stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=SAMPLE_RATE,
        input=True,
        frames_per_buffer=CHUNK
    )

    print("Recording...")
    frames = []
    for _ in range(0, int(SAMPLE_RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    p.terminate()

    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(b''.join(frames))

    print(f"Audio saved to {filename}")
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
    print("Camera not found")
    return None
# ─────────────────────────────────────────────────────────────────────────────

# ── REGISTER FACE ─────────────────────────────────────────────────────────────
def register_face(cap):
    speak("Look at the camera. Capturing face.")

    # flush buffer
    for _ in range(5):
        ret, frame = cap.read()

    if not ret:
        speak("Failed to capture. Please try again.")
        return

    # detect face
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_frame)

    if not face_locations:
        speak("No face detected. Please try again.")
        return

    # get face encoding
    encodings = face_recognition.face_encodings(rgb_frame, face_locations)
    if not encodings:
        speak("Could not encode face. Please try again.")
        return

    encoding = encodings[0]

    # record name audio
    speak("Face captured. Say the name after the beep.")
    beep()

    face_count = len(load_faces()['names']) + 1
    audio_file = os.path.join(AUDIO_DIR, f'face_{face_count}.wav')
    record_audio(audio_file)

    # save to database
    db = load_faces()
    db['encodings'].append(encoding)
    db['names'].append(f'face_{face_count}')
    db['audio_files'].append(audio_file)
    save_faces(db)

    speak("Face registered successfully.")
    print(f"Face {face_count} registered")
# ─────────────────────────────────────────────────────────────────────────────

# ── RECOGNIZE FACE ────────────────────────────────────────────────────────────
def recognize_face(cap):
    db = load_faces()

    if not db['encodings']:
        speak("No faces registered. Please register faces first.")
        return

    # flush buffer
    for _ in range(5):
        ret, frame = cap.read()

    if not ret:
        speak("Failed to capture. Please try again.")
        return

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_frame)

    if not face_locations:
        speak("No face detected.")
        return

    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces(db['encodings'], face_encoding, tolerance=0.6)
        face_distances = face_recognition.face_distance(db['encodings'], face_encoding)

        if True in matches:
            best_match = np.argmin(face_distances)
            if matches[best_match]:
                audio_file = db['audio_files'][best_match]
                print(f"Recognized: {db['names'][best_match]}")
                threading.Thread(target=lambda: play_audio(audio_file), daemon=True).start()
                return

    speak("Unknown face.")
# ─────────────────────────────────────────────────────────────────────────────

# ── RUN MODE ──────────────────────────────────────────────────────────────────
# mode can be 'register' or 'recognize'
def run_face_mode(mode='register'):
    if mode == 'register':
        speak("Mode 2. Face registration.")
        cap = open_camera()
        if cap:
            speak("Ready. Point camera at face and press confirm to register.")
        else:
            speak("Camera not found.")
        return cap
    else:
        speak("Face recognition mode. Point camera at face and press confirm.")
        cap = open_camera()
        if not cap:
            speak("Camera not found.")
        return cap