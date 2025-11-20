import pandas as pd


def export_table(article: str, table_data: pd.DataFrame) -> None:
    filename = f"code_{article}.xlsx"
    table_header = pd.DataFrame()

    # df = pd.concat([table_header, table_data], ignore_index=True)

    # df.to_excel(f"data/output/{filename}", index=False)