import os
import pandas as pd


def is_excel(filename: str) -> bool:
    return filename.lower().endswith((".xlsx", ".xls"))


def extract_article(filename: str) -> str:
    """Extract article code from filename"""
    return filename.split("-")[0].strip()


def validate_reference_file(filepath: str) -> None:
    """Validate reference file exists and not empty"""
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"Reference file '{filepath}' not found")

    if pd.read_excel(filepath).empty:
        raise ValueError(f"Reference file '{filepath}' is empty")


def extract_barcode(reference_data: pd.DataFrame, article_code: str) -> str | None:
    """Get barcode by article code"""
    matches = reference_data.loc[
        reference_data["Артикул"].astype(str) == str(article_code),
        "Штрихкод"
    ]

    return None if matches.empty else str(matches.iloc[0])
