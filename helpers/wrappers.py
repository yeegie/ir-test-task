from typing import Callable
import os
import time
import logging


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

def validate_file(func):
    def wrapper(file_path: str, *args, **kwargs):
        # Existence check
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file at {file_path} does not exist.")
        
        df = func(file_path, *args, **kwargs)
        
        # Not null check
        if len(df) == 0:
            logging.warning(f"The file at {file_path} is empty.")
        
        return df
    return wrapper