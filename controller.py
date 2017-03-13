#!/usr/bin/python
# *****************************************************************************************************************
#    Pi Power Controller
#    By John M. Wargo
#    www.johnwargo.com
#
# ********************************************************************************************************************

from __future__ import print_function

import random
import sys
import time
from datetime import datetime

import gpiozero
import numpy as np
import pytz
import requests
import tzlocal

import relay

# 'constants' that define the different time triggers used by the application
# DO NOT MODIFY THESE, you'll mess up the app's logic
SETTIME = -1
SUNRISE = -2
SUNSET = -3

# ============================================================================
# User (that's you) adjustable variables
# ============================================================================
# adjust these variables based on your particular hardware configuration

# set this variable to the button pin used in your implementation
BUTTON_PIN = 19
# set this variable to the GPIO pin the relay is connected to
RELAY_PIN = 18

# Sunrise and sunset times vary depending on location, so...
# If using sunrise or sunset as trigger options, populate the locLat
# and locLong values with the location's latitude and longitude values
# These values are for Charlotte, NC, to get Sunrise/Sunset values for
# your location, replace these strings with the appropriate values for
# your location.
LOC_LAT = "35.227085"
LOC_LONG = "-80.843124"

# default times for sunrise and sunset. If solar data is enabled, the
# code will reach out every day at 12:01 and populate these values with
# the correct values for the current day. If this fails for any reason,
# the values will fall back to the previous day's values, or, finally,
# these values
time_sunrise = 700
time_sunset = 1900

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
# Other variables; Please don't modify any of these.
# ============================================================================
# used to help prettify the output
single_hash = "#"
hashes = "#########################################"
slash_n = "\n"

# variable used throughout the application to indicate whether the
# application's current configuration uses the SUNRISE or SUNSET
# triggers. Starts at False, but will get reset to True if your
# slots use one of the solar options
uses_solar_data = False

# API for determining sunrise and sunset times: http://sunrise-sunset.org/api
# Test URL to retrieve data for Charlotte, NC US
# Usage: http://api.sunrise-sunset.org/json?lat=35.2271&lng=-80.8431&date=today
SOLAR_API_URL = "http://api.sunrise-sunset.org/json"
# Make sure you set the local Timezone on the Raspberry Pi for this to
# work correctly

# initialize the daily slots array. It will be an empty object at start, but will
# be populated every day with the current slots.
daily_slots = []

# Initialize the btn object and connect it to the button pin
btn = gpiozero.Button(BUTTON_PIN)
# initialize the relay object
relay.init(RELAY_PIN)
# initialize the random number generator
random.seed(a=None)


def init_app():
    global uses_solar_data

    # See if any of our slots require solar data (sunrise, sunset)
    # this drives the slot builder that runs every morning at 12:01 AM
    uses_solar_data = check_for_solar_events()
    if uses_solar_data:
        print("\nSolar data enabled")
        # do we have long and lat values?
        if LOC_LAT or LOC_LONG:
            print("Lat and Long values exist")
        else:
            # then we can't run, and we need to terminate
            print("\nINVALID CONFIGURATION: Lat or Long values missing")
            sys.exit(1)
        get_solar_times()

    # build the daily slots array for today
    build_daily_slots_array()

    # are we supposed to be on?
    if is_on_time():
        # then turn the relay on
        print("\nWhoops, we're supposed to be on!")
        relay.set_status(True)


def process_loop():
    # initialize the lastMinute variable to the current time minus 1
    # this subtraction isn't technically accurate, but for this purpose,
    # just trying to understand if the minute changed, it's OK
    last_time = inc_time(get_time_24(), -1)
    # infinite loop to continuously check time values
    while 1:
        # Is the button pushed?
        if btn.is_pressed:
            print("Detected button push")
            # Then toggle the relay
            relay.toggle()
        else:
            # otherwise...
            # get the current time (in 24 hour format)
            current_time = get_time_24()
            # is the time the same as the last time we checked?
            if current_time != last_time:
                # No? OK, so the time changed and we may have work to do...
                print(current_time)

                # reset last_time to the current_time (so this doesn't happen until
                # the next minute change
                last_time = current_time

                # build the daily slots array every day at 12:01 AM
                # that's 1 (001) in 24 hour time
                if current_time == 1:
                    # if one of the solar times is enabled
                    if uses_solar_data:
                        # populate our sunrise and sunset values for the day
                        get_solar_times()
                        # build the list of on/off times for today
                        build_daily_slots_array()

                # finally, check to see if we're supposed to be turning the
                # relay on or off
                for slot in daily_slots:
                    if current_time == slot[0]:
                        relay.set_status(True)
                    if current_time == slot[1]:
                        relay.set_status(False)
            else:
                print("whoa")
        # wait a second then check again
        # You can always increase the sleep value below to check less often
        time.sleep(1)


def validate_slot(slot):
    print("\nValidating slot:", slot)

    # Does the slot use set times and off time is before on time?
    if (slot['onTrigger'] == SETTIME) and (slot['offTrigger'] == SETTIME) and (slot['offTrigger'] < slot['onTrigger']):
        print("Set time: Off time can't be before on time")
        return False

    # Is our solar data delta greater than an hour?
    # this one isn't critical, but when you get into big numbers (multiple hours of time), then the time math
    # gets wonky, so lets just cap it at 60 minutes?
    if ((slot['onTrigger'] < SETTIME) and (slot['onValue'] > 60)) or (
                (slot['offTrigger'] < SETTIME) and (slot['offValue'] > 60)):
        print("Solar Data: Time delta cannot be more than 60 minutes")
        return False

    # we got this far, return True
    print("Slot is valid")
    return True


def validate_slots():
    global slots

    # initialize our error flag
    has_error = False
    # Make sure our slots configuration is valid
    for slot in np.nditer(slots):
        if not validate_slot(slot):
            print("we have an error")
            has_error = True
    return not has_error


def check_for_solar_events():
    # return true if any of the slots use a solar trigger (sunrise or sunset)
    global slots

    # iterate through the slots
    for slot in np.nditer(slots):
        # Do the on or off triggers for this slot use solar?
        if slot['onTrigger'] < SETTIME or slot['offTrigger'] < SETTIME:
            # then we're done, we're solar!
            return True
    return False


def get_solar_times():
    global time_sunrise
    global time_sunset

    # used to convert the string time values from the API into a Python date/time object
    format_str = "%I:%M:%S %p"

    print("\nRequesting solar data from", SOLAR_API_URL)
    payload = {"lat": LOC_LAT, "lng": LOC_LONG, "date": "today"}
    try:
        res = requests.get(SOLAR_API_URL, params=payload)
        # did we get a result?
        if res.status_code == requests.codes.ok:
            data = res.json()
            # time comes in as a string, in UTC time, but with no timezone data.
            # it must be converted into a format we can use...
            time_sunrise = adjust_time_utc(datetime.strptime(data['results']['sunrise'], format_str))
            print("Sunrise:", str(time_sunrise))
            time_sunset = adjust_time_utc(datetime.strptime(data['results']['sunset'], format_str))
            print("Sunset:", str(time_sunset))
        else:
            print("Unable to obtain solar data; server returned", res.status_code)
    except ValueError as e:
        print("Value Error:", e)
    except Exception as e:
        print("Unexpected error:", e)


def adjust_time_utc(time_val):
    # http://stackoverflow.com/questions/4770297/python-convert-utc-datetime-string-to-local-datetime
    # time_val input value is assumed to be coming from the call to the solar data API
    # therefore, the time will be a UTC time, but without the timezone data included with it.
    # convert the time value to local time based on timezone
    # time_val.replace(tzinfo=pytz.utc) adds timezone information (utc) to time_val
    # time_val.astimezone(tzlocal.get_localzone()) returns the time value in the current timezone
    return get_time_24(time_val.replace(tzinfo=pytz.utc).astimezone(tzlocal.get_localzone()))


def get_time_24(time_val=datetime.now()):
    # build the 24 hour time using hours and minutes
    # grab the current time if a time value isn't passed to the function
    # do we have a valid time object?
    if isinstance(time_val, datetime):
        # then format the time
        if time_val.hour > 0:
            return int((time_val.hour * 100) + time_val.minute)
        else:
            return int(time_val.minute)
    else:
        # otherwise return junk
        return -1


def build_daily_slots_array():
    global daily_slots

    print("\nBuilding slots array")
    daily_slots = []
    # iterate through the slots array, adding the on_time and off_time values to the daily_slots array
    for slot in np.nditer(slots):
        # get some data from the slot
        do_random = slot['doRandom']
        on_time = parse_slot_time(slot['onTrigger'], slot['onValue'])
        off_time = parse_slot_time(slot['offTrigger'], slot['offValue'])
        if do_random:
            # https://docs.python.org/3/library/random.html
            # make random slots between on_time and off_time
            # set the initial on time to on_time
            ont = on_time
            # repeat the following until we're past off_time
            while ont < off_time:
                # calculate an off time using a random value from 5 to 60
                oft = inc_time(ont, random.randint(5, 60))
                # is our new off time > off_time?
                if oft > off_time:
                    # then set it to off_time, turn it off at off_time
                    oft = off_time
                # save the  random 'slot' to the array
                daily_slots.append([int(ont), int(oft)])
                # reset on time to the current off time + plus some random int
                # this is when it goes on again next
                ont = inc_time(oft, random.randint(5, 60))
        else:
            # is the on time BEFORE the off time? (can't be equal either)
            if on_time < off_time:
                # then add the slot to the list of daily slots
                daily_slots.append([int(on_time), int(off_time)])
            else:
                print("Skipping slot, on_time is AFTER off_time")
    print("Daily slots:", daily_slots)


def inc_time(time_val, increment):
    # get the number of minutes
    mins = time_val % 100
    # figure out the hours
    hours = (time_val / 100)
    # increment minutes
    new_mins = mins + increment
    # did we go over an hour boundary? (assuming we're adding no more than 60 minutes)
    if new_mins > 59:
        # then decrement the minutes
        new_mins -= 60
        hours += 1
        if hours > 23:
            # return 11:59 PM
            return 2359
    # return our results
    if hours > 0:
        return (hours * 100) + new_mins
    else:
        return new_mins


def parse_slot_time(slot_trigger, slot_val):
    if slot_trigger == SETTIME:
        # return the time value
        return int(slot_val)
    if slot_trigger == SUNRISE:
        # return the calculated solar sunrise time
        return int(inc_time(time_sunrise, slot_val))
    # return the calculated solar sunset time
    return int(inc_time(time_sunset, slot_val))


def is_on_time():
    # Are we in an ON mode? In other words, is the current time between any of the
    # slot's on and off times?
    # Start by getting the current time (in 24 hour format)
    curr_time = get_time_24()
    # look through all of the daily slot values
    for slot in daily_slots:
        # if current time is between on/off times, then we're True
        if slot[0] < curr_time < slot[1]:
            return True
    return False


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
        relay.set_status(False)
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
