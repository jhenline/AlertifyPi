import RPi.GPIO as GPIO
import time

# Set up GPIO pins for LEDs
GPIO.setmode(GPIO.BCM)
YELLOW_PIN = 17
ORANGE_PIN = 27
RED_PIN = 22

# Set up GPIO pins
GPIO.setup(YELLOW_PIN, GPIO.OUT)
GPIO.setup(ORANGE_PIN, GPIO.OUT)
GPIO.setup(RED_PIN, GPIO.OUT)

def turn_on_led(pin):
    GPIO.output(pin, GPIO.HIGH)
    print(f"LED on GPIO {pin} is ON.")

def turn_off_led(pin):
    GPIO.output(pin, GPIO.LOW)
    print(f"LED on GPIO {pin} is OFF.")

try:
    # Test each LED by turning it on for 5 seconds and then off
    print("Testing Yellow LED")
    turn_on_led(YELLOW_PIN)
    time.sleep(5)
    turn_off_led(YELLOW_PIN)

    print("Testing Orange LED")
    turn_on_led(ORANGE_PIN)
    time.sleep(5)
    turn_off_led(ORANGE_PIN)

    print("Testing Red LED")
    turn_on_led(RED_PIN)
    time.sleep(5)
    turn_off_led(RED_PIN)

finally:
    GPIO.cleanup()  # Clean up GPIO settings when done
