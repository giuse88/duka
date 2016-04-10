import csv


def dump(currency, ticks):
    date = ticks[0][0]
    file_name = "{}_{}_{}_{}.csv".format(currency, date.year, date.month, date.day)
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
