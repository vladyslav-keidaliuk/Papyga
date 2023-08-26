import logging

import pytz
from datetime import datetime, time, timedelta


def to_utc(time_obj):
    try:

        time_str = time_obj.strftime("%H:%M")

        time = to_utc_from_str(time_str)
        return time
    except Exception as e:
        logging.error(f"Error in tz.py - to_utc: {e}")


def to_utc_from_str(time_str):
    local_tz = pytz.timezone('Europe/Kiev')

    hours, minutes = map(int, time_str.split(':'))
    ukraine_now = pytz.datetime.datetime.now(local_tz).date()
    dt = pytz.datetime.datetime.combine(ukraine_now, pytz.datetime.time.min) + timedelta(hours=hours, minutes=minutes)

    localized_time = local_tz.localize(dt)

    utc_time = localized_time.astimezone(pytz.utc)

    return utc_time


def get_utc_str_hh_mm_from_str(time_string):
    time_utc = to_utc_from_str(time_string)
    time_utc_hh_mm = time_utc.strftime("%H:%M")
    return time_utc_hh_mm


def get_utc_offset_hours():
    ukraine_timezone = pytz.timezone('Europe/Kiev')
    current_time = datetime.now()
    utc_offset = ukraine_timezone.utcoffset(current_time)
    utc_offset_hours = utc_offset.total_seconds() / 3600
    return int(utc_offset_hours)
