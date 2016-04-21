import csv
from .utils import Logger
from . import TimeFrame
from .utils import to_utc_timestamp
from datetime import datetime

TEMPLATE_FILE_NAME = "{}_{}_{:02d}_{:02d}.csv"


class CSVFormatter(object):
    COLUMN_TIME = 0
    COLUMN_ASK = 1
    COLUMN_BID = 2
    COLUMN_ASK_VOLUME = 3
    COLUMN_BID_VOLUME = 4


class Candle:
    def __init__(self, symbol, timestamp, timeframe, sorted_values):
        self.symbol = symbol
        self.timestamp = timestamp
        self.timeframe = timeframe
        self.open_price = sorted_values[0]
        self.close_price = sorted_values[len(sorted_values) - 1]
        self.high = max(sorted_values)
        self.low = min(sorted_values)

    def __str__(self):
        return str(datetime.fromtimestamp(self.timestamp)) + " [" + str(self.timestamp) + "] " \
               + "-- " + self.symbol + " -- " \
               + "{ H:" + str(self.high) + " L:" + str(self.low) + " O: " \
               + str(self.open_price) + " C: " + str(self.close_price) + " }"

    def __eq__(self, other):
        return self.symbol == other.symbol \
               and self.timestamp == other.timestamp \
               and self.timeframe == other.timeframe \
               and self.close_price == other.close_price \
               and self.open_price == other.open_price \
               and self.high == other.high \
               and self.low == other.low

    def __repr__(self):
        return self.__str__()


def dump(symbol, day, ticks, time_frame=TimeFrame.TICK):
    file_name = TEMPLATE_FILE_NAME.format(symbol, day.year, day.month, day.day)
    Logger.info("Writing {0}".format(file_name))
    with open(file_name, 'w') as csv_file:
        fieldnames = ['time', 'ask', 'bid', 'ask_volume', 'bid_volume']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for tick in ticks:
            if time_frame == TimeFrame.TICK:
                write_tick(tick)
            else:
                ts = to_utc_timestamp(tick[0])
                key = int(ts - (ts % time_frame))
                if previous_key != key and previous_key is not None:
                    write_candle(Candle(symbol, previous_key, time_frame, current_ticks))
                    current_ticks = []
                current_ticks.append(tick[1])
                previous_key = key

        if time_frame != TimeFrame.TICK:
            write_candle(writer, Candle(symbol, previous_key, time_frame, ticks))
    Logger.info("{0} completed".format(file_name))


def get_header(time_frame):
    if time_frame == TimeFrame.TICK:
        return ['time', 'ask', 'bid', 'ask_volume', 'bid_volume']
    return ['time', 'open', 'close', 'high', 'low']


def write_tick(writer, tick):
    writer.writerow(
        {'time': tick[0],
         'ask': tick[1],
         'bid': tick[2],
         'ask_volume': tick[3],
         'bid_volume': tick[4]})


def write_candle(writer, candle):
    writer.writerow(
        {'time': candle.timestamp,
         'open': candle.open,
         'close': candle.close,
         'high': candle.high,
         'low': candle.low})
