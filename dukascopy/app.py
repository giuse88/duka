import time
from datetime import timedelta
from collections import deque

from core import fetch_day, decompress, dump


SATURDAY = 5


def dates(start, end):
    if start > end:
        return
    end = end + timedelta(days=1)
    while start != end:
        if start.weekday() is not SATURDAY:
            yield start
        start = start + timedelta(days=1)


def format_left_time(seconds):
    if seconds < 0:
        return "--:--:--"
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return "%d:%02d:%02d" % (h, m, s)


def update_progress(done, total, avg_time_per_job):
    progress = done / total
    progress = int((1.0 if progress > 1.0 else progress) * 100)
    remainder = 100 - progress
    estimation = avg_time_per_job * (total - done)
    print('\r[{0}] {1}%  Left : {2}  '.format('#' * progress + '-' * remainder, progress, format_left_time(estimation)),
          end='')


def how_many_days(start, end):
    if start == end:
        return 1
    delta_days = (end - start).days
    saturday_counter = delta_days / 7
    return delta_days - saturday_counter


def fetch_ticks(symbols, start, end):
    if start > end:
        return

    fetched_days = 0
    days = how_many_days(start, end)

    last_fetch = deque([], maxlen=3)
    update_progress(fetched_days, days, -1)

    for symbol in symbols:
        for date in dates(start, end):
            star_time = time.time()
            dump(symbol, decompress(date, fetch_day(symbol, date)))
            last_fetch.append(time.time() - star_time)
            fetched_days += 1
            update_progress(fetched_days, days, sum(last_fetch) / len(last_fetch))

