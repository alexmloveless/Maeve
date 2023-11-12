import re
from typing import Union

from maeve.util.dict import DictUtils
from maeve.models.core import AnchorConst, LocationRecipe, GlobalConst
from maeve.plugins.primitives import Primitives

ac = AnchorConst()
g = GlobalConst()


class AnchorUtils:

    @classmethod
    def resolve_anchors(cls,
                        cnf,  # Should be a confscade obj but a dict will actually work, but with limited recursion
                        obj: Union[list, dict],
                        env_conf,
                        anchors: dict = None) -> dict:

        # handle both dicts and lists
        try:
            iterator = obj.items()
        except AttributeError:
            iterator = enumerate(obj)

        anchors = anchors if anchors else {}

        for k, v in iterator:
            if type(v) in [dict, list]:
                cls.resolve_anchors(cnf, v, env_conf)
            elif type(v) is str:
                if re.match(ac.match_regex, v):
                    identifier, keys = cls.parse_anchor(v)

                    if identifier in anchors.keys():
                        new_val = anchors[identifier]
                    else:
                        # grab a nested object
                        sub_conf = cnf.get(identifier)  # fully resolves the anchor incl. inheritance and nested anchors
                        if keys:
                            new_val = DictUtils.deep_dict(sub_conf, keys)
                        else:
                            new_val = sub_conf
                    if type(new_val) is dict:
                        new_val = cls.resolve_recipe(new_val, env_conf)
                    obj[k] = new_val
            else:
                continue
        return obj

    @classmethod
    def parse_anchor(cls, a):
        if not re.match(ac.match_regex, a):
            raise ValueError("Not an anchor")
        anchor = re.sub(ac.sub_regex, "", a)
        matches = re.split(r"\.", anchor)
        try:
            return matches[0], matches[1:]
        except KeyError:
            return matches[0], None

    @classmethod
    def resolve_recipe(cls, recipe, env_conf):
        if "recipe_type" not in recipe.keys():
            return recipe
        if recipe["recipe_type"] == "location":
            return LocationRecipe(paths=env_conf.paths, **recipe).model_dump()
        # if recipe["recipe_type"] == "pipeline":
        #     return PipelineRecipe(**recipe).model_dump()
        if recipe["recipe_type"] in ["dict", "list"]:
            return Primitives.primitive(recipe)

        return recipe


class RecipeUtils:
    @classmethod
    def add_package_recipes(cls,
                            loc: Union[list, dict, str],
                            load_package_recipes: list
                            ):
        if len(load_package_recipes) == 0:
            return loc

        if type(loc) in [str, list]:
            d_root = [g.package_paths[r] for r in load_package_recipes]
            if type(loc) is list:
                loc.extend(d_root)
                return loc
            else:
                return [loc] + d_root
        elif type(loc) is dict:
            for r in load_package_recipes:
                loc[r] = g.package_paths[r]
            return loc
        else:
            return loc
