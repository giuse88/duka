import concurrent
import time
from collections import deque
from datetime import timedelta, date
from threading import Lock

from core import dump, decompress, fetch_day

SATURDAY = 5
day_counter = 0


def days(start, end):
    if start > end:
        return
    end = end + timedelta(days=1)
    today = date.today()
    while start != end:
        if start.weekday() != SATURDAY and start != today:
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
    return sum(1 for _ in days(start, end))


def fetch_ticks(symbols, start, end, threads):
    if start > end:
        return
    lock = Lock()
    global day_counter
    total_days = how_many_days(start, end)

    last_fetch = deque([], maxlen=5)
    update_progress(day_counter, total_days, -1)

    def do_work():
        global day_counter
        star_time = time.time()
        dump(symbol, decompress(day, fetch_day(symbol, day)))
        last_fetch.append(time.time() - star_time)
        with lock:
            day_counter += 1

    futures = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        for symbol in symbols:
            for day in days(start, end):
                futures.append(executor.submit(do_work))

        for future in concurrent.futures.as_completed(futures):
            if future.exception() is None:
                update_progress(day_counter, total_days, sum(last_fetch) / len(last_fetch))
            else:
                print("An error happen when fetching data : ", future.exception())

    update_progress(day_counter, total_days, sum(last_fetch) / len(last_fetch))
