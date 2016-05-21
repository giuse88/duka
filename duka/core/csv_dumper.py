import csv
import time

from .candle import Candle
from .utils import TimeFrame, stringify, Logger

from os.path import join

TEMPLATE_FILE_NAME = "{}-{}_{:02d}_{:02d}-{}_{:02d}_{:02d}.csv"


class CSVFormatter(object):
    COLUMN_TIME = 0
    COLUMN_ASK = 1
    COLUMN_BID = 2
    COLUMN_ASK_VOLUME = 3
    COLUMN_BID_VOLUME = 4


def write_tick(writer, tick):
    writer.writerow(
        {'time': tick[0],
         'ask': tick[1],
         'bid': tick[2],
         'ask_volume': tick[3],
         'bid_volume': tick[4]})


def write_candle(writer, candle):
    writer.writerow(
        {'time': stringify(candle.timestamp),
         'open': candle.open_price,
         'close': candle.close_price,
         'high': candle.high,
         'low': candle.low})


class CSVDumper:
    def __init__(self, symbol, timeframe, start, end, folder):
        self.symbol = symbol
        self.timeframe = timeframe
        self.start = start
        self.end = end
        self.folder = folder
        self.buffer = {}

    def get_header(self):
        if self.timeframe == TimeFrame.TICK:
            return ['time', 'ask', 'bid', 'ask_volume', 'bid_volume']
        return ['time', 'open', 'close', 'high', 'low']

    def append(self, day, ticks):
        previous_key = None
        current_ticks = []
        self.buffer[day] = []
        for tick in ticks:
            if self.timeframe == TimeFrame.TICK:
                self.buffer[day].append(tick)
            else:
                ts = time.mktime(tick[0].timetuple())
                key = int(ts - (ts % self.timeframe))
                if previous_key != key and previous_key is not None:
                    self.buffer[day].append(Candle(self.symbol, previous_key, self.timeframe, current_ticks))
                    current_ticks = []
                current_ticks.append(tick[1])
                previous_key = key

        if self.timeframe != TimeFrame.TICK:
            self.buffer[day].append(Candle(self.symbol, previous_key, self.timeframe, current_ticks))

    def dump(self):
        file_name = TEMPLATE_FILE_NAME.format(self.symbol,
                                              self.start.year, self.start.month, self.start.day,
                                              self.end.year, self.end.month, self.end.day)

        Logger.info("Writing {0}".format(file_name))

        with open(join(self.folder, file_name), 'w') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=self.get_header())
            writer.writeheader()
            for day in sorted(self.buffer.keys()):
                for value in self.buffer[day]:
                    if self.timeframe == TimeFrame.TICK:
                        write_tick(writer, value)
                    else:
                        write_candle(writer, value)

        Logger.info("{0} completed".format(file_name))
