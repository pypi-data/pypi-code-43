from datetime import datetime

from whattime import whattime

# Asking for all types of time descriptors for a e.g. a monday afternoon:
now = datetime.now()
info = whattime(now)

print(info.types)
# {<TimeType.WEEKDAY: 'weekday'>, <TimeType.MONDAY: 'monday'>, ...}

print(info.is_weekday)
# True

print(info.is_weekend)
# False

print(info.is_monday)
# True

print(info.is_tuesday)
# True

print(info.is_afternoon)
# True

print(info.is_morning)
# False
