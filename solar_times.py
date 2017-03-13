#!/usr/bin/python

# this is a working application I created to help me write the code for getting solar times
# and converting the results to the local time zone.

import sys
from datetime import datetime

import pytz
import requests
import tzlocal

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


def get_solar_times():
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
    # time_val.replace(tzinfo=pytz.utc) adds timezone data to time_val 
    # time_val.astimezone(tzlocal.get_localzone()) returns the time value in the current timezone
    return get_time_24(time_val.replace(tzinfo=pytz.utc).astimezone(tzlocal.get_localzone()))


def get_time_24(time_val=datetime.now()):
    # build the 24 hour time using hours and minutes
    # grab the current time if a time value isn't passed to the function
    # do we have a valid time object?
    if isinstance(time_val, datetime):
        # then format the time
        if time_val.hour > 0:
            return (time_val.hour * 100) + time_val.minute
        else:
            return time_val.minute
    else:
        # otherwise return junk
        return -1


if __name__ == "__main__":
    try:
        print(get_time_24(23))
        get_solar_times()
    except KeyboardInterrupt:
        print("\nExiting application\n")
        # exit the application
        sys.exit(0)
