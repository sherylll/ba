import time

import RPi.GPIO as GPIO


LED_PIN     = 20
SWITCH_PIN  = 21


class PiThing:
    """Internet 'thing' that can control GPIO on a Raspberry Pi."""

    def __init__(self):
        """Initialize the 'thing'."""
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(LED_PIN, GPIO.OUT)
        GPIO.setup(SWITCH_PIN, GPIO.IN)

    def read_switch(self):
        """Read the switch state and return its current value.
        """
        return GPIO.input(SWITCH_PIN)

    def set_led(self, value):
        """Set the LED to the provided value (True = on, False = off).
        """
        GPIO.output(LED_PIN, value)

# Create the pi thing.
pi_thing = PiThing()

# Print the current switch state.
switch = pi_thing.read_switch()
print('Switch status: {0}'.format(switch))

# Now loop forever blinking the LED.
print('Looping with LED blinking (Ctrl-C to quit)...')
while True:
    pi_thing.set_led(True)
    time.sleep(0.5)
    pi_thing.set_led(False)
    time.sleep(0.5)