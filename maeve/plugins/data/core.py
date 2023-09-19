from pydantic import BaseModel

class Loader(BaseModel):
    pass

class Data:
    def __init__(self, session=None):
        self.s = session

    def main(self, recipe: dict):
        loader = recipe.get("load", {})


class Loaders:

    def loader(self):
        # loader decorator that parses the model etc.
        pass

    @staticmethod
    def file(recipe):
        pass