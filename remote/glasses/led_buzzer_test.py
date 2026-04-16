'''
Raspberry Pi - BLE Listener
Automatically connects to ESP32 remote
Speaks which button was pressed and what mode is selected
'''

import asyncio
import subprocess
from bleak import BleakScanner, BleakClient

# ── BLE DEFINITIONS ───────────────────────────────────────────────────────────
DEVICE_NAME         = "Assistive-Glasses-Remote"
CHARACTERISTIC_UUID = "abcd1234-ab12-ab12-ab12-abcdef123456"
# ─────────────────────────────────────────────────────────────────────────────

# ── BUTTON MESSAGES ───────────────────────────────────────────────────────────
BUTTON_MESSAGES = {
    "TRIGGER": "Confirm button pressed",
    "BUTTON1": "Button 1 pressed. Mode 1 selected. Active path navigation.",
    "BUTTON2": "Button 2 pressed. Mode 2 selected. Face registration and recognition.",
    "BUTTON3": "Button 3 pressed. Mode 3 selected. Currency identification.",
    "BUTTON4": "Button 4 pressed. Mode 4 selected. Text to speech.",
    "BUTTON5": "Button 5 pressed. Mode 5 selected. World description.",
}
# ─────────────────────────────────────────────────────────────────────────────

# ── SPEAK ─────────────────────────────────────────────────────────────────────
def speak(text):
    print(f">> {text}")
    subprocess.Popen(['espeak', text])
# ─────────────────────────────────────────────────────────────────────────────

# ── NOTIFICATION HANDLER ──────────────────────────────────────────────────────
def on_button_press(sender, data):
    signal = data.decode('utf-8').strip()
    print(f"Received signal: {signal}")
    if signal in BUTTON_MESSAGES:
        speak(BUTTON_MESSAGES[signal])
    else:
        print(f"Unknown signal: {signal}")
# ─────────────────────────────────────────────────────────────────────────────

# ── DISCONNECT CALLBACK ───────────────────────────────────────────────────────
def on_disconnect(client):
    print("Remote disconnected")
    speak("Remote disconnected. Searching again.")
# ─────────────────────────────────────────────────────────────────────────────

# ── SCAN AND CONNECT ──────────────────────────────────────────────────────────
async def connect_to_remote():
    while True:
        print("Scanning for ESP32 remote...")
        speak("Searching for remote")

        # scan for devices
        target = await BleakScanner.find_device_by_name(DEVICE_NAME, timeout=10)

        if target is None:
            print("Remote not found, retrying in 3 seconds...")
            await asyncio.sleep(3)
            continue

        print(f"Found remote: {target.address}")

        # connect manually without context manager
        client = BleakClient(target.address, disconnected_callback=on_disconnect)

        try:
            await client.connect()
            print("Connected to remote!")
            speak("Remote connected. Please select a mode.")

            # subscribe to button notifications
            await client.start_notify(CHARACTERISTIC_UUID, on_button_press)

            # keep alive loop - just wait while connected
            while client.is_connected:
                await asyncio.sleep(0.5)

            # if we get here connection dropped
            print("Connection lost - restarting scan")
            await asyncio.sleep(2)

        except Exception as e:
            print(f"Connection error: {e}")
            await asyncio.sleep(3)

        finally:
            if client.is_connected:
                await client.disconnect()
# ─────────────────────────────────────────────────────────────────────────────

# ── MAIN ──────────────────────────────────────────────────────────────────────
async def main():
    await connect_to_remote()

try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("Stopped")
# ─────────────────────────────────────────────────────────────────────────────