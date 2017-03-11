#!/usr/bin/python

# A simple Python application for controlling a relay board from a Raspberry Pi
# The application uses the GPIO Zero library (https://gpiozero.readthedocs.io/en/stable/)
# The relay is connected to one of the Pi's GPIO ports, then is defined as an Output device
# in GPIO Zero: https://gpiozero.readthedocs.io/en/stable/api_output.html#outputdevice

import sys
import time

import gpiozero

# used to track the current state of the relay. At the start, the
# application turns the relay off then sets this variable's value
# the application can then later query this to determine what the
# current state is for the relay, in the toggle function for example
_relay_status = False

# change this value based on which GPIO port the relay is connected to
RELAY_PIN = 18

# create a relay object.
# Triggered by the output pin going low: active_high=False.
# Initially off: initial_value=False
relay = gpiozero.OutputDevice(RELAY_PIN, active_high=True, initial_value=False)


def set_status(the_status):
    # sets the relay's status based on the boolean value passed to the function
    # a value of True turns the relay on, a value of False turns the relay off
    global _relay_status

    _relay_status = the_status

    if the_status:
        print("Setting relay: ON")
        relay.on()
    else:
        print("Setting relay: OFF")
        relay.off()


def toggle_relay():
    # toggles the relay's status. If the relay is on, when you call this function,
    # it will turn the relay off. If the relay is off, when you call this function,
    # it will turn the relay on. Easy peasy, right?
    global _relay_status

    # flip our relay status value
    _relay_status = not _relay_status
    if _relay_status:
        print("Toggling relay: ON")
    else:
        print("Toggling relay: OFF")
    relay.toggle()


def main_loop():
    # start by turning the relay off
    set_status(False)
    while 1:
        # then toggle the relay every second until the app closes
        toggle_relay()
        # wait a second
        time.sleep(2)


if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        # turn the relay off
        set_status(False)
        print("\nExiting application\n")
        # exit the application
        sys.exit(0)
