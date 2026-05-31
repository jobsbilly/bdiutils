import datetime
import logging
import pathlib

import pytz

class TZAwareFormatter(logging.Formatter):
    """
    A timezone-aware logging formatter (see https://stackoverflow.com/a/76572598).

    By default, Python's `logging` module uses the `time` module for conversion
    of timestamps to time tuples, which doesn't support %f for microsecond formatting
    """
    def __init__(self, tz, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tz = tz

    def converter(self, timestamp):
        return datetime.datetime.fromtimestamp(timestamp, self.tz)

    def formatTime(self, record, datefmt=None):
        dt = self.converter(record.created)
        if datefmt:
            s = dt.strftime(datefmt)
        else:
            s = dt.strftime(self.default_time_format)
            if self.default_msec_format:
                s = self.default_msec_format % (s, record.msecs)
        return s

def log_formatter(fmt: str, zone: str = "America/Los_Angeles") -> logging.Formatter:
    return TZAwareFormatter(tz=pytz.timezone(zone), fmt=fmt, datefmt="%Y-%m-%d %H:%M:%S.%f %Z")
