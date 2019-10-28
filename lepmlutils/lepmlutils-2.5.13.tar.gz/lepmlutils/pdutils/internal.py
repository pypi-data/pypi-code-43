import pandas as pd

def contains(df: pd.DataFrame, col: str) -> bool:
    return col in list(df.columns)