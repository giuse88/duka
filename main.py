import lzma
import csv
import struct
from datetime import datetime, timedelta
from io import BytesIO, DEFAULT_BUFFER_SIZE

import requests


URL = "https://www.dukascopy.com/datafeed/{currency}/{year}/{month:02d}/{day:02d}/{hour:02d}h_ticks.bi5"


def fetch(currency, day):
    buffer = BytesIO()
    url_info = {
        'currency': currency,
        'year': day.year,
        'month': day.month - 1,
        'day': day.day
    }
    for i in range(0, 24):
        url_info['hour'] = i
        print(URL.format(**url_info))
        res = requests.get(URL.format(**url_info), stream=True)
        if res.status_code == 200:
            for chunk in res.iter_content(DEFAULT_BUFFER_SIZE):
                buffer.write(chunk)
        else:
            print("Request failed with " + str(res.status_code))

    return buffer.getbuffer()


def decompress(compressed_buffer):
    return lzma.decompress(compressed_buffer)


def tokenize(buffer):
    token_size = 20
    size = int(len(buffer) / token_size)
    tokens = []
    for i in range(0, size):
        tokens.append(struct.unpack('!IIIff', buffer[i * token_size: (i + 1) * token_size]))
    return tokens


def normalize(day, ticks):
    def norm(time, ask, bid, volume_ask, volume_bid):
        date = day + timedelta(milliseconds=time)
        return date, ask, bid, round(volume_ask * 1000000), round(volume_bid * 1000000)

    return list(map(lambda x: norm(*x), ticks))


def dump(currency, ticks):
    date = ticks[0][0]
    file_name = "{}_{}_{}_{}.csv".format(currency, date.year, date.month, date.day)
    print(file_name)
    with open(file_name, 'w') as csvfile:
        fieldnames = ['time', 'ask', 'bid', 'ask_volume', 'bid_volume']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for tick in ticks:
            writer.writerow(
                {'time': tick[0], 'ask': tick[1], 'bid': tick[2], 'ask_volume': tick[3], 'bid_volume': tick[4]})


def main():
    day = datetime(2016, 3, 29)
    currency = 'EURUSD'
    tokens = normalize(day, tokenize(decompress(fetch(currency, day))))
    dump(currency, tokens)


if __name__ == '__main__':
    main()