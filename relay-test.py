#!/usr/bin/python

# A simple Python application for controlling a relay board from a Raspberry Pi
# The application uses the GPIO Zero library (https://gpiozero.readthedocs.io/en/stable/)
# The relay is connected to one of the Pi's GPIO ports, then is defined as an Output device
# in GPIO Zero: https://gpiozero.readthedocs.io/en/stable/api_output.html#outputdevice

import sys
import time

import gpiozero
import relay


def main_loop():
    # start by turning the relay off
    relay.set_status(False)
    while 1:
        # then toggle the relay every second until the app closes
        relay.toggle()
        # wait a second
        time.sleep(2)


if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        # turn the relay off
        relay.set_status(False)
        print("\nExiting application\n")
        # exit the application
        sys.exit(0)
