class Primitives:
    def __init__(self, session):
        self.s = session

    @staticmethod
    def primitive(recipe, obj=None):
        try:
            return recipe["value"]
        except KeyError:
            raise ValueError("No 'value' key in recipe")

    main = primitive

