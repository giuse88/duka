import asyncio
import os
import threading
import time
from io import BytesIO, DEFAULT_BUFFER_SIZE

import requests

from ..core.utils import Logger

URL = "https://datafeed.dukascopy.com/datafeed/{currency}/{year}/{month:02d}/{day:02d}/{hour:02d}h_ticks.bi5"
ATTEMPTS = 5
REQUEST_TIMEOUT = 30
DEFAULT_HOUR_CONCURRENCY = 3
MAX_BACKOFF_SECONDS = 30


def hour_concurrency():
    try:
        return max(1, int(os.getenv('DUKA_HOUR_CONCURRENCY', DEFAULT_HOUR_CONCURRENCY)))
    except ValueError:
        return DEFAULT_HOUR_CONCURRENCY


def backoff_seconds(attempt):
    return min(MAX_BACKOFF_SECONDS, 2 ** attempt)


async def get(url):
    loop = asyncio.get_event_loop()
    id = url.split("/datafeed/", 1)[-1].replace('/', " ")
    start = time.time()
    Logger.info("Fetching {0}".format(id))
    for i in range(ATTEMPTS):
        try:
            res = await loop.run_in_executor(
                None,
                lambda: requests.get(url, stream=True, timeout=REQUEST_TIMEOUT)
            )
            if res.status_code == 200:
                buffer = BytesIO()
                for chunk in res.iter_content(DEFAULT_BUFFER_SIZE):
                    buffer.write(chunk)
                Logger.info("Fetched {0} completed in {1}s".format(id, time.time() - start))
                if len(buffer.getbuffer()) <= 0:
                    Logger.info("Buffer for {0} is empty ".format(id))
                return buffer.getbuffer()
            else:
                Logger.warn("Request to {0} failed with error code : {1} ".format(url, str(res.status_code)))
        except Exception as e:
            Logger.warn("Request {0} failed with exception : {1}".format(id, str(e)))

        if i < ATTEMPTS - 1:
            await asyncio.sleep(backoff_seconds(i))

    raise Exception("Request failed for {0} after ATTEMPTS attempts".format(url))


async def fetch_hours(symbol, day):
    url_info = {
        'currency': symbol,
        'year': day.year,
        'month': day.month - 1,
        'day': day.day
    }
    semaphore = asyncio.Semaphore(hour_concurrency())

    async def fetch_hour(hour):
        await semaphore.acquire()
        try:
            return await get(URL.format(**url_info, hour=hour))
        finally:
            semaphore.release()

    tasks = [asyncio.ensure_future(fetch_hour(i)) for i in range(0, 24)]

    # if is_dst(day):
    #     next_day = day + datetime.timedelta(days=1)
    #     url_info = {
    #         'currency': symbol,
    #         'year': next_day.year,
    #         'month': next_day.month - 1,
    #         'day': next_day.day
    #     }
    #     tasks.append(asyncio.ensure_future(get(URL.format(**url_info, hour=0))))
    return await asyncio.gather(*tasks)


def fetch_day(symbol, day):
    local_data = threading.local()
    loop = getattr(local_data, 'loop', asyncio.new_event_loop())
    asyncio.set_event_loop(loop)
    loop = asyncio.get_event_loop()
    buffers = loop.run_until_complete(fetch_hours(symbol, day))

    output = BytesIO()
    for buffer in buffers:
        output.write(buffer)
    return output.getbuffer()
