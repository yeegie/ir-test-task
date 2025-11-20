import logging
import os

import pandas as pd

from helpers.wrappers import cache_file_data, validate_file

@validate_file
@cache_file_data
def get_file_data(file_path: str) -> pd.DataFrame:
    return pd.read_excel(file_path)

@validate_file
def get_directory_files(directory_path: str) -> list[tuple[str, pd.DataFrame]]:
    files = [f for f in os.listdir(directory_path) if f.endswith(('.xlsx', '.xls'))]
    dataframes: list[pd.DataFrame] = []

    for file in files:
        file_path = os.path.join(directory_path, file)
        df = get_file_data(file_path)

        code = (file.split("-")[0]).strip()
        dataframes.append((code, df))

    return dataframes