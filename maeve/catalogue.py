from pydantic import BaseModel
from typing import Any, Optional
import re


class CatalogueItem(BaseModel):
    obj: Any
    name: str
    source: str = None
    obj_type: Optional[str] = None
    description: Optional[str] = None
    metadata: Optional[dict] = None


class Catalogue:

    def __init__(self):
        self.obj = {}

    def add(self,
            obj: Any,
            name: str = None,
            source: str = None,
            obj_type: str = None,
            description: str = None,
            metadata: dict = None,
            protect: str = "block",
            return_item: bool = False
            ):

        name = self.protect(name, protect)

        metadata = metadata if metadata else {}
        self.obj[name] = CatalogueItem(
            obj=obj,
            name=name,
            source=source,
            obj_type=obj_type,
            description=description,
            metadata=metadata
        )
        if return_item:
            return self.obj[name].obj

    def protect(self, name, mode: str = "block"):
        if name in self.obj.keys():
            if mode == "overwrite":
                return name
            elif mode == "increment":
                return self.increment_name(name)
            else:
                raise AttributeError(f"Cannot add item with name {name} to catalogue "
                                     f"as already exists. Use different name or set protect "
                                     f"to 'overwrite' or 'increment'")
        else:
            return name

    def increment_name(self, name):
        try:
            n = int(re.match("_(\d+)$", name).groups()[0])
        except AttributeError:
            return name + "_1"

        return re.sub(r"\d+$", str(n + 1), name)


class Register:
    def __init__(self):
        pass
