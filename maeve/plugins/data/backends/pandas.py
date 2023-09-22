import pandas as pd


class PandasDataFrame:
    def __init__(self):
        pass

    def mangle_columns(self, df):
        df = df.rename(columns={"track_name": "TESTING"})
        return df


class PandasLoaders:
    def load_csv(*args, **kwargs):
        return pd.read_csv(*args, **kwargs)
