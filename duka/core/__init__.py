from .fetch import fetch_day
from .csv_dumper import dump
from .utils import valid_date, Logger, set_up_signals
from .processor import decompress

__all__ = ['fetch_day', 'decompress', 'dump', 'valid_date', 'Logger', 'set_up_signals']


class TimeFrame(object):
    TICK = 0
    S_30 = 30
    M1 = 60
    M2 = 120
    M5 = 300
    M10 = 600
    M15 = 900
    M30 = 1800
    H1 = 3600
    H4 = 14400
    D1 = 86400


