from maeve.catalogue import CatalogueClass

class PolarsDataFrame:
    def __init__(self):
        pass

    def mangle_columns(self, df):
        df = df.rename({"track_name": "TESTING"})
        return df


class PolarsDFCatalogue(CatalogueClass):
    pass
