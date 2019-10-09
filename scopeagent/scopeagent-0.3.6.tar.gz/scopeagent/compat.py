"""
Handles extra Python 2/3 compatibility not handled by six.
"""
try:
    from datetime import timezone

    utc = timezone.utc
except ImportError:
    # UTC tzinfo from Python 2.7 datetime documentation
    from datetime import timedelta, tzinfo

    ZERO = timedelta(0)


    class UTC(tzinfo):
        def utcoffset(self, dt):
            return ZERO

        def tzname(self, dt):
            return "UTC"

        def dst(self, dt):
            return ZERO


    utc = UTC()
