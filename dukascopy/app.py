from datetime import timedelta

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


def fetch_ticks(symbols, start, end):
    for symbol in symbols:
        for date in dates(start, end):
            dump(symbol, decompress(date, fetch_day(symbol, date)))

