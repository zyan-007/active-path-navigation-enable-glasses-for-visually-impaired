import serial
import time

try:
    ser = serial.Serial('/dev/ttyS0', 9600, timeout=1)
    print("Serial port opened successfully")
    
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').strip()
            print(f"Received: '{line}'")
            
except Exception as e:
    print(f"Error: {e}")