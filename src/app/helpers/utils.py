def is_excel(filename: str) -> bool:
    return filename.lower().endswith((".xlsx", ".xls"))


def extract_article(filename: str) -> str:
    return filename.split("-")[0].strip()
