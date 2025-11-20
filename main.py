import time
import pandas as pd

from helpers.file_operations import get_file_data, get_directory_files
from helpers.table_exporter import export_table


def main():
    referense_data = get_file_data("data/справочник.xlsx")
    input_files = get_directory_files("data/input/")

    print(f"Referense data loaded. len: {len(referense_data)}")
    print(f"Loaded {len(input_files)} input files.\n{'\n'.join([code for code, _ in input_files])}")

    start = time.time()
    export_table(input_files[0][0], input_files[0][1])
    print(f"Processing time: {time.time() - start} seconds")

if __name__ == "__main__":
    main()
