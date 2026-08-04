import timeit, time

dt_reTime = timeit.timeit(
    'time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(float("1782645154.25017")))',
    setup = 'import time',
    number = 10000
)

dt_reDatetime = timeit.timeit(
    'datetime.fromtimestamp(float("1782645154.25017")).strftime("%Y-%m-%d %H:%M:%S")',
    setup = 'from datetime import datetime',
    number = 10000
)

print(dt_reTime)
print(dt_reDatetime)

#time is about 3x faster than datetime in this application
from datetime import datetime

utc_offset = time.altzone if time.daylight else time.timezone
print(utc_offset*-1)