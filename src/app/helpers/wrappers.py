from typing import List
import asyncio
import time
from functools import wraps

from aiogram.types import Message


def cache_file_data(func, ttl: int = 28800):  # 8 hours
    cache_data = None
    last_update_time = None

    def wrapper(*args, **kwargs):
        nonlocal cache_data, last_update_time

        now = time.time()
        if cache_data is None or (now - last_update_time) > ttl:
            cache_data = func(*args, **kwargs)
            last_update_time = now
        return cache_data

    return wrapper


def group_files(waiting_time: int = 3):
    buffer: List[Message] = []
    lock = asyncio.Lock()
    timer_running: bool = False

    def decorator(func):
        @wraps(func)
        async def wrapper(message: Message, *args, **kwargs):
            nonlocal timer_running

            if not message.document:
                return

            async with lock:
                buffer.append(message)

                if not timer_running:
                    timer_running = True
                    asyncio.create_task(process_batch())

        async def process_batch():
            nonlocal timer_running

            await asyncio.sleep(waiting_time)

            async with lock:
                batch = buffer.copy()
                buffer.clear()
                timer_running = False

            try:
                await func(batch)
            except Exception as e:
                print("ERROR IN HANDLER:", e)

        return wrapper
    return decorator
