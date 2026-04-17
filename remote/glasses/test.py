import serial
import os
import time

# pre-configure port before opening
os.system('sudo stty -F /dev/ttyS0 9600 cs8 -cstopb -parenb')
time.sleep(0.5)

try:
    ser = serial.Serial('/dev/ttyS0', 9600, timeout=1)
    print("Serial port opened")

    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').strip()
            print(f"Received: '{line}'")

except Exception as e:
    print(f"Error: {e}")