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
from gpiozero import Button
from urllib2 import Request, urlopen, URLError

# 'constants' that define the different time triggers used by the application
# DO NOT MODIFY
SETTIME = -1
SUNRISE = -2
SUNSET = -3

# ============================================================================
# User (that's you) adjustable variables
# ============================================================================
# adjust these variables based on your particular hardware configuration

# set this variable to the button pin used in your implementation
BUTTON_PIN = 4

# Slots array defines time windows and behavior for the relay
# format: [ OnTrigger, OnValue, OffTrigger, OffValue, doRandom]
slots = np.array(
    # ONLY modify the following array with your time settings
    [
        (SETTIME, 700, SETTIME, 900, False),
        (SETTIME, 1700, SETTIME, 2300, True),
        (SUNRISE, 15, SUNSET, -10, True)
    ],
    # leave the rest of this alone
    dtype=[
        ('onTrigger', np.dtype(int)),
        ('onValue', np.dtype(int)),
        ('offTrigger', np.dtype(int)),
        ('offValue', np.dtype(int)),
        ('doRandom', np.dtype(bool))
    ]
)
# ============================================================================

# ============================================================================
# Other variables; Please don't modify these.
# ============================================================================
# used to help prettify the output
single_hash = "#"
hashes = "#########################################"
slash_n = "\n"

# variable used throughout the application to indicate whether the
# application's current configuration uses the SUNRISE or SUNSET
# triggers
uses_solar_data = False

# API for determining sunrise and sunset times: http://sunrise-sunset.org/api
# Test URL to retrieve data for Charlotte, NC US
# Usage: http://api.sunrise-sunset.org/json?lat=35.2271&lng=-80.8431&date=today
SOLAR_API_URL = "http://api.sunrise-sunset.org/json"

# Sunrise and sunset times vary depending on location, so...
# If using sunrise or sunset as trigger options, populate the locLat
# and locLong values with the location's latitude and longitude values
# These values are for Charlotte, NC, to get Sunrise/Sunset values for
# your location, replace these strings with the appropriate values for
# your location.
LOC_LAT = "35.227085";
LOC_LONG = "-80.843124";

# used to track the current state of the relay. At the start, the
# application turns the relay off then sets this variable's value
# the application can then later query this to determine what the
# current state is for the relay, in the toggle function for example
relay_status = False

# Initialize the btn object and connect it to the button pin
btn = Button(BUTTON_PIN)


def validate_slot(slot):
    # todo: validate a slot
    print(slot)
    return True


def validate_slots():
    global slots
    # todo: setup return value
    # Make sure our slots configuration is valid
    for slot in np.nditer(slots):
        validate_slot(slot)
    return True


def init_app():
    global uses_solar_data

    # See if any of our slots require solar data (sunrise, sunset)
    # this drives the slot builder that runs every morning at 12:01 AM
    uses_solar_data = check_for_solar_events()
    if uses_solar_data:
        print("Solar data enabled")
        # todo: validate long and lat if solar data is enabled
        # if LOC_LAT == "" or LOC_LONG == "":


    # build the daily slots array
    build_daily_slots_array()

    # are we supposed to be on?
    if is_on_time():
        # then turn the relay on
        print("\nWhoops, we're supposed to be on!")
        set_relay(True)


def process_loop():
    # initialize the lastMinute variable to the current time minus 1
    # this subtraction isn't technically accurate, but for this purpose,
    # just trying to understand if the minute changed, it's OK
    last_time = get_time_24() - 1
    # infinite loop to continuously check time values
    while 1:
        # Is the button pushed?
        if btn.is_pressed:
            # Then toggle the relay
            toggle_relay()
        else:
            # otherwise...
            # get the current time (in 24 hour format)
            current_time = get_time_24()
            # is the time the same as the last time we checked?
            if current_time != last_time:
                # No? OK, so the time changed and we may have work to do...

                # reset last_time to the current_time (so this doesn't happen until
                # the next minute change
                last_time = current_time

                # build the daily slots array every day at 12:01 AM
                # that's 1 (001) in 24 hour time
                if current_time == 1:
                    build_daily_slots_array()

        # wait a second then check again
        # You can always increase the sleep value below to check less often
        time.sleep(1)


def check_for_solar_events():
    return False


def get_solar_times():
    request = Request(SOLAR_API_URL)

    try:
        response = urlopen(request)
        kittens = response.read()
        print(kittens[559:1000])
    except URLError, e:
        print('No kittez. Got an error code:', e)


def build_daily_slots_array():
    print("Building slots array")
    pass


def is_on_time():
    return False


def get_time_24():
    # return the current time in 24 hour format
    the_time = datetime.datetime.now()
    # build the 24 hour time using hours and minutes
    if the_time.hour > 0:
        return (the_time.hour * 100) + the_time.minute
    else:
        return the_time.minute


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
        if validate_slots():
            init_app()
            process_loop()
        else:
            # then we can't run, and we need to terminate
            print("\nINVALID SLOT(S) DEFINITION")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\nExiting application\n")
        sys.exit(0)
