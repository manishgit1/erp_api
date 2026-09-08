import logging
from datetime import datetime, timedelta, timezone

NEPAL_TZ = timezone(timedelta(hours=5, minutes=45))


class NepaliTimeFormatter(logging.Formatter):
    """Formats log timestamps in Nepal Time (UTC+5:45), regardless of the host/container's system timezone."""

    def formatTime(self, record, datefmt=None):
        dt = datetime.fromtimestamp(record.created, tz=NEPAL_TZ)
        if datefmt:
            return dt.strftime(datefmt)
        return dt.strftime('%Y-%m-%d %H:%M:%S,%f')[:-3]
