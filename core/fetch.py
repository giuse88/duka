import asyncio
import requests
from functools import reduce
from io import BytesIO, DEFAULT_BUFFER_SIZE

URL = "https://www.dukascopy.com/datafeed/{currency}/{year}/{month:02d}/{day:02d}/{hour:02d}h_ticks.bi5"

async def get(url):
    loop = asyncio.get_event_loop()
    buffer = BytesIO()
    print(url)
    res = await loop.run_in_executor(None, lambda: requests.get(url, stream=True))
    if res.status_code == 200:
        for chunk in res.iter_content(DEFAULT_BUFFER_SIZE):
            buffer.write(chunk)
    else:
        print("Request to {0} failed with error code : {1} ".format(url, str(res.status_code)))
    return buffer.getbuffer()


def fetch_day(symbol, day):

    url_info = {
        'currency': symbol,
        'year': day.year,
        'month': day.month - 1,
        'day': day.day
    }

    loop = asyncio.get_event_loop()
    tasks = []
    for i in range(0, 24):
        url_info['hour'] = i
        tasks.append(asyncio.ensure_future(get(URL.format(**url_info))))

    loop.run_until_complete(asyncio.wait(tasks))

    def add(acc, task):
        acc.write(task.result())
        return acc

    return reduce(add, tasks, BytesIO()).getbuffer()
