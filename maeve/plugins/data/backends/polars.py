import polars as pl

class PolarsDataFrame:
    def __init__(self):
        pass

    @staticmethod
    def is_polars_df(df):
        if isinstance(df, pl.dataframe.frame.DataFrame):
            return True
        return False

class PolarsSeries:
    def __init__(self):
        pass

    @staticmethod
    def is_polars_series(df):
        if isinstance(df, pl.series.series.Series):
            return True
        return False
