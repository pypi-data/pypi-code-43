from IPython.display import display
import pandas as pd


def disp(df: pd.DataFrame, max_rows: int = 1000, max_cols: int = 1000):
    """Display the full DataFrame table

    Notes: Saw this function in the fast.ai ML course as 'display_all'.
    """
    # force jupyter to display many rows
    with pd.option_context("display.max_rows", max_rows):
        # force jupyter to display many columns
        with pd.option_context("display.max_columns", max_cols):
            # display in notebook
            display(df)
