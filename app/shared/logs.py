import logging as pylogging
from datetime import datetime, timedelta, timezone

from uvicorn import logging


class UTC8DefaultFormatter(logging.DefaultFormatter):
    def converter(self, timestamp):
        return datetime.fromtimestamp(timestamp, timezone(timedelta(hours=8)))

    def formatTime(self, record, datefmt=None):
        dt = self.converter(record.created)
        if datefmt:
            s = dt.strftime(datefmt)
        else:
            s = dt.strftime("%Y-%m-%d %H:%M:%S %Z")
        return s


class UTC8AccessFormatter(logging.AccessFormatter):
    def converter(self, timestamp):
        return datetime.fromtimestamp(timestamp, timezone(timedelta(hours=8)))

    def formatTime(self, record, datefmt=None):
        dt = self.converter(record.created)
        if datefmt:
            s = dt.strftime(datefmt)
        else:
            s = dt.strftime("%Y-%m-%d %H:%M:%S %Z")
        return s


console = pylogging.getLogger("uvicorn.error")
