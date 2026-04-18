import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(5,  GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(6,  GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(19, GPIO.IN, pull_up_down=GPIO.PUD_UP)

buttons = [21, 5, 6, 13, 19]

print("Ready")

last_press = {}

try:
    while True:
        for pin in buttons:
            if GPIO.input(pin) == GPIO.LOW:
                now = time.time() * 1000
                if pin not in last_press or now - last_press[pin] > 300:
                    last_press[pin] = now
                    print(f"GPIO {pin}")
        time.sleep(0.05)

except KeyboardInterrupt:
    GPIO.cleanup()