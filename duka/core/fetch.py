import asyncio
import aiohttp
import threading
import time
from functools import reduce
from io import BytesIO, DEFAULT_BUFFER_SIZE
from ..core.utils import Logger

URL = "https://www.dukascopy.com/datafeed/{currency}/{year}/{month:02d}/{day:02d}/{hour:02d}h_ticks.bi5"

async def get(url):
    buffer = BytesIO()
    id = url[36:].replace('/', " ")
    with aiohttp.ClientSession(loop=asyncio.get_event_loop()) as session:
        start = time.time()
        Logger.info("Fetching {0}".format(id))
        async with session.get(url) as resp:
            while True:
                chunk = await resp.content.read(DEFAULT_BUFFER_SIZE)
                if not chunk:
                    break
                buffer.write(chunk)
    Logger.info("Fetched {0} completed in {1}s".format(id, time.time() - start))
    return buffer.getbuffer()


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
