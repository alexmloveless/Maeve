from maeve.util import FuncUtils



class Pipeline:
    def __init__(self, session):
        self.s = session

    def main(self, recipe, obj=None):
        return FuncUtils.run_pipeline(recipe, obj=obj)