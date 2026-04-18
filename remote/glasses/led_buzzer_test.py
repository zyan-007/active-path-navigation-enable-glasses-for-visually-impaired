import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(5,  GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(6,  GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(19, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(25, GPIO.IN, pull_up_down=GPIO.PUD_UP)

buttons = {
    21: "TRIGGER",
    5:  "BUTTON1",
    6:  "BUTTON2",
    13: "BUTTON3",
    19: "BUTTON4",
    25: "BUTTON5",
}

last_press = {}
print("Ready - press any button")

try:
    while True:
        for pin, name in buttons.items():
            if GPIO.input(pin) == GPIO.LOW:
                now = time.time() * 1000
                if pin not in last_press or now - last_press[pin] > 300:
                    last_press[pin] = now
                    print(f"{name} pressed")
        time.sleep(0.05)

except KeyboardInterrupt:
    GPIO.cleanup()