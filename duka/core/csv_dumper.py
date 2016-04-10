import csv

from .utils import Logger

TEMPLATE_FILE_NAME = "{}_{}_{:02d}_{:02d}.csv"


def dump(currency, day, ticks):
    file_name = TEMPLATE_FILE_NAME.format(currency, day.year, day.month, day.day)
    Logger.info("Writing {0}".format(file_name))
    with open(file_name, 'w') as csv_file:
        fieldnames = ['time', 'ask', 'bid', 'ask_volume', 'bid_volume']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for tick in ticks:
            writer.writerow(
                {'time': tick[0],
                 'ask': tick[1],
                 'bid': tick[2],
                 'ask_volume': tick[3],
                 'bid_volume': tick[4]})
    Logger.info("{0} completed".format(file_name))
