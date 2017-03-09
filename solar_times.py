#!/usr/bin/python

# this is a working application I created to help me write the code for getting solar times
# and converting the results to the local time zone.

import sys
from datetime import datetime

import pytz
import requests

# API for determining sunrise and sunset times; details at http://sunrise-sunset.org/api
# Test URL to retrieve data for Charlotte, NC US:
# http://api.sunrise-sunset.org/json?lat=35.2271&lng=-80.8431&date=today
SOLAR_API_URL = "http://api.sunrise-sunset.org/json"
# Make sure you set the local Timezone on the Raspberry Pi for this to
# work correctly

# Sunrise and sunset times vary depending on location, so...
# Populate the locLat and locLong values with the location's latitude and longitude values
# These values are for Charlotte, NC
LOC_LAT = "35.227085"
LOC_LONG = "-80.843124"

# Set the local timezone
tz = pytz.timezone('US/Eastern')


def get_solar_times():
    format_str = "%I:%M:%S %p"

    print("\nRequesting solar data from", SOLAR_API_URL)
    payload = {"lat": LOC_LAT, "lng": LOC_LONG, "date": "today"}
    try:
        res = requests.get(SOLAR_API_URL, params=payload)
        # did we get a result?
        if res.status_code == requests.codes.ok:
            data = res.json()
            time_val = datetime.strptime(data['results']['sunrise'], format_str)

            time_sunrise = adjust_time_24(time_val)
            print("Sunrise:", data['results']['sunrise'], "(" + str(time_sunrise) + ")")
            time_val = datetime.strptime(data['results']['sunset'], format_str)
            time_sunset = adjust_time_24(time_val)
            print("Sunset:", data['results']['sunset'], "(" + str(time_sunset) + ")")
        else:
            print("Unable to obtain solar data; server returned", res.status_code)
    except ValueError as e:
        print("Value Error:", e)
    except Exception as e:
        print("Unexpected error:", e)


def get_time_24(time_val):
    # build the 24 hour time using hours and minutes
    if time_val.hour > 0:
        return (time_val.hour * 100) + time_val.minute
    else:
        return time_val.minute


def adjust_time_24(time_val):
    # convert the time value to local time based on timezone
    # this is where all the magic is supposed to happen.
    working_time = tz.localize(time_val)
    return get_time_24(working_time)


if __name__ == "__main__":
    try:
        get_solar_times()
    except KeyboardInterrupt:
        print("\nExiting application\n")
        # exit the application
        sys.exit(0)
