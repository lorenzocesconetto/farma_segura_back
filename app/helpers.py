from datetime import datetime, timedelta, tzinfo


class simple_utc(tzinfo):
    def tzname(self, **kwargs):
        return "UTC"

    def utcoffset(self, dt):
        return timedelta(0)

    @staticmethod
    def add_utc_info(date: datetime):
        return date.replace(tzinfo=simple_utc()).isoformat()
