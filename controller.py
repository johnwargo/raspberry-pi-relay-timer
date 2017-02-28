#!/usr/bin/python
# *****************************************************************************************************************
#    Pi Power Controller
#    By John M. Wargo
#    www.johnwargo.com
#
# ********************************************************************************************************************

from __future__ import print_function

import datetime
import sys
import time

import numpy as np

# ============================================================================
# String constants
# ============================================================================
single_hash = "#"
hashes = "#########################################"
slash_n = "\n"

uses_solar_data = False
relay_status = False

SETTIME = -1
SUNRISE = -2
SUNSET = -3

# Slots array defines time windows and behavior for the relay
# format: [ OnTrigger, OnValue, OffTrigger, OffValue, Random]
slots = np.array(
    [
        (SETTIME, 700, SETTIME, 900, False),
        (SETTIME, 1700, SETTIME, 2300, True),
        (SUNRISE, 15, SUNSET, -10, True)
    ],
    dtype=[
        ('onTrigger', np.dtype(int)),
        ('onValue', np.dtype(int)),
        ('offTrigger', np.dtype(int)),
        ('offValue', np.dtype(int)),
        ('doRandom', np.dtype(bool))
    ]
)


def validate_slot(slot):
    return True


def validate_slots_array():
    # Make sure our slots configuration is valid
    return True


def init_app():
    global uses_solar_data

    # See if any of our slots require solar data (sunrise, sunset)
    # this drives the slot builder that runs every morning at 12:01 AM
    uses_solar_data = check_for_solar_events()
    if uses_solar_data:
        print("Solar data enabled")

    build_daily_slots_array()

    # are we supposed to be on?
    if is_on_time():
        # then turn the relay on
        print("\nWhoops, we're supposed to be on!")
        set_relay(True)


def process_loop():
    # initialize the lastMinute variable to the current time to start
    last_minute = datetime.datetime.now().minute
    # on startup, just use the previous minute as lastMinute
    if last_minute == 0:
        last_minute = 59
    else:
        last_minute -= 1
    # infinite loop to continuously check time values
    while 1:
        # Was the button pushed? Then toggle the relay

        # get the current minute
        current_minute = datetime.datetime.now().minute
        # is it the same minute as the last time we checked?
        if current_minute != last_minute:
            # reset last_minute to the current_minute
            last_minute = current_minute

            # startTime - turns all ports on
            # end time - turns all ports off

        # wait a second then check again
        # You can always increase the sleep value below to check less often
        time.sleep(1)


def check_for_solar_events():
    return False


def build_daily_slots_array():
    pass


def is_on_time():
    return False


def get_time_24():
    return 700


def toggle_relay():
    global relay_status

    # flip the status value we're using to keep track of the relay status
    relay_status = not relay_status
    # then use that value to set the relay status
    set_relay(relay_status)


def set_relay(status):
    global relay_status

    if status:
        print("Turning the relay ON")
        # todo: Do whatever it is you have to do to turn the relay on

    else:
        print("Turning the relay OFF")
        # todo: Do whatever it is you have to do to turn the relay off

    relay_status = status


# ============================================================================
# here's where we start doing stuff
# ============================================================================
print(slash_n + hashes)
print(single_hash, "Pi Relay Controller                  ", single_hash)
print(single_hash, "By John M. Wargo (www.johnwargo.com) ", single_hash)
print(hashes)

if __name__ == "__main__":
    try:
        # Turn the relay off to start (just to make sure)
        set_relay(False)
        # do we have a valid set of slots?
        if validate_slots_array():
            init_app()
            process_loop()
        else:
            # then we can't run, and we need to terminate
            print("\nINVALID SLOT(S) DEFINITION")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\nExiting application\n")
        sys.exit(0)
