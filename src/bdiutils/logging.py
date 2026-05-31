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

def init_loggers(log_file_path: str | pathlib.Path | None, level=logging.INFO, attr: str = "name") -> None:
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(log_formatter(f"%(created)f %(levelname)8s [%({attr})7s:%(lineno)-3d] %(message)s"))

    handlers = [console_handler]

    min_level = level if level < logging.INFO else logging.INFO

    if log_file_path is not None:
        log_file_path = pathlib.Path(log_file_path)
        if not log_file_path.exists():
            raise FileNotFoundError(log_file_path)
        # Append a separator line with a blank line before and after.
        with open(log_file_path, mode="a", encoding="utf-8") as log_file:
            log_file.write("\n".join(["_" * 80, "_" * 80, "\n"]))
        file_handler = logging.FileHandler(log_file_path, mode="a", encoding="utf-8")
        file_handler.setLevel(min_level)
        file_handler.setFormatter(log_formatter(f"%(asctime)s %(levelname)8s [%({attr})10s:%(lineno)-3d] %(message)s"))
        handlers.append(file_handler)

    logging.basicConfig(level=min_level, handlers=handlers, force=True)
