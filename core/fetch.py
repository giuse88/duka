import requests
from io import BytesIO, DEFAULT_BUFFER_SIZE

URL = "https://www.dukascopy.com/datafeed/{currency}/{year}/{month:02d}/{day:02d}/{hour:02d}h_ticks.bi5"


def fetch_day(symbol, day):
    """
    :param symbol: symbol to be downloaded
    :param day: the day which we downloading data for
    :return: binary buffer containing the data fetched
    """
    buffer = BytesIO()
    url_info = {
        'currency': symbol,
        'year': day.year,
        'month': day.month - 1,
        'day': day.day
    }
    for i in range(0, 24):
        url_info['hour'] = i
        url = URL.format(**url_info)
        res = requests.get(url, stream=True)
        if res.status_code == 200:
            for chunk in res.iter_content(DEFAULT_BUFFER_SIZE):
                buffer.write(chunk)
        else:
            print("Request to {0} failed with error code : {1} ".format(url, str(res.status_code)))

    return buffer.getbuffer()
