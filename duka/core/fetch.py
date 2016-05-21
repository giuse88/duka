import asyncio
import threading
import time
from functools import reduce
from io import BytesIO, DEFAULT_BUFFER_SIZE

import requests

from ..core.utils import Logger

URL = "https://www.dukascopy.com/datafeed/{currency}/{year}/{month:02d}/{day:02d}/{hour:02d}h_ticks.bi5"
ATTEMPTS = 5

async def get(url):
    loop = asyncio.get_event_loop()
    buffer = BytesIO()
    id = url[35:].replace('/', " ")
    start = time.time()
    Logger.info("Fetching {0}".format(id))
    for i in range(ATTEMPTS):
        try:
            res = await loop.run_in_executor(None, lambda: requests.get(url, stream=True))
            if res.status_code == 200:
                for chunk in res.iter_content(DEFAULT_BUFFER_SIZE):
                    buffer.write(chunk)
                Logger.info("Fetched {0} completed in {1}s".format(id, time.time() - start))
                return buffer.getbuffer()
            else:
                Logger.warn("Request to {0} failed with error code : {1} ".format(url, str(res.status_code)))
        except Exception as e:
            Logger.warn("Request {0} failed with exception : {1}".format(id, str(e)))
            time.sleep(0.5*i)

    raise Exception("Request failed for {0} after ATTEMPTS attempts".format(url))


def fetch_day(symbol, day):
    local_data = threading.local()
    loop = getattr(local_data, 'loop', asyncio.new_event_loop())
    asyncio.set_event_loop(loop)

    url_info = {
        'currency': symbol,
        'year': day.year,
        'month': day.month - 1,
        'day': day.day
    }

    loop = asyncio.get_event_loop()
    tasks = [asyncio.ensure_future(get(URL.format(**url_info, hour=i))) for i in range(24)]
    loop.run_until_complete(asyncio.wait(tasks))

    def add(acc, task):
        acc.write(task.result())
        return acc

    return reduce(add, tasks, BytesIO()).getbuffer()
