import asyncio
import datetime
import threading
import time
from functools import reduce
from io import BytesIO, DEFAULT_BUFFER_SIZE

import requests

from ..core.utils import Logger, is_dst


URL = "https://datafeed.dukascopy.com/datafeed/{currency}/{year}/{month:02d}/{day:02d}/{hour:02d}h_ticks.bi5"
ATTEMPTS = 5


async def get(url, session=None):
    """
    Async download function that uses either a provided requests.Session (for proxy)
    or falls back to the global requests module.
    """
    loop = asyncio.get_event_loop()
    buffer = BytesIO()
    id_str = url[35:].replace('/', " ")  # for logging
    start = time.time()
    Logger.info(f"Fetching {id_str}")

    # Use session if provided, otherwise use plain requests
    req = session if session is not None else requests

    for attempt in range(ATTEMPTS):
        try:
            res = await loop.run_in_executor(
                None, lambda: req.get(url, stream=True, timeout=30)
            )

            if res.status_code == 200:
                for chunk in res.iter_content(DEFAULT_BUFFER_SIZE):
                    if chunk:
                        buffer.write(chunk)
                elapsed = time.time() - start
                size = len(buffer.getbuffer())
                Logger.info(f"Fetched {id_str} completed in {elapsed:.1f}s ({size} bytes)")
                if size == 0:
                    Logger.info(f"Buffer for {id_str} is empty")
                return buffer.getbuffer()

            else:
                Logger.warn(f"Request to {id_str} failed with status {res.status_code}")

        except Exception as e:
            Logger.warn(f"Attempt {attempt + 1}/{ATTEMPTS} failed for {id_str}: {e}")
            if attempt < ATTEMPTS - 1:
                time.sleep(0.5 * (attempt + 1))

    raise Exception(f"Request failed for {id_str} after {ATTEMPTS} attempts")


def create_tasks(symbol, day, session=None):
    """
    Create list of tasks for all 24 hours (handles DST by skipping or adjusting as needed)
    """
    # Dukascopy uses 0-based month in URL
    url_info = {
        'currency': symbol,
        'year': day.year,
        'month': day.month - 1,
        'day': day.day
    }

    # Standard 24 hours
    tasks = [
        asyncio.ensure_future(get(URL.format(**url_info, hour=hour), session=session))
        for hour in range(24)
    ]

    # Optional: handle DST transition (uncomment if you want to fetch extra hour)
    # if is_dst(day):
    #     next_day = day + datetime.timedelta(days=1)
    #     next_url_info = {
    #         'currency': symbol,
    #         'year': next_day.year,
    #         'month': next_day.month - 1,
    #         'day': next_day.day
    #     }
    #     tasks.append(asyncio.ensure_future(get(URL.format(**next_url_info, hour=0), session=session)))

    return tasks


def fetch_day(symbol, day, session=None):
    """
    Main function: fetch all hourly data for a symbol and day.
    Now accepts optional session for proxy support.
    """
    local_data = threading.local()
    loop = getattr(local_data, 'loop', None)

    if loop is None or loop.is_closed():
        loop = asyncio.new_event_loop()
        local_data.loop = loop

    asyncio.set_event_loop(loop)

    tasks = create_tasks(symbol, day, session=session)

    # Run all tasks concurrently
    loop.run_until_complete(asyncio.wait(tasks))

    # Combine all results
    def add(acc, task):
        try:
            data = task.result()
            if data:
                acc.write(data)
        except Exception as e:
            Logger.error(f"Task failed: {e}")
        return acc

    result = reduce(add, tasks, BytesIO())
    return result.getbuffer()