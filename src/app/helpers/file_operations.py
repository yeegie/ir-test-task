import logging
import os

import pandas as pd

from app.helpers.wrappers import cache_file_data


@cache_file_data
def get_file_caching_data(path: str, filename: str) -> pd.DataFrame:
    return pd.read_excel(path + filename)


def get_file_data(path: str, filename: str) -> pd.DataFrame:
    return pd.read_excel(path + filename)
