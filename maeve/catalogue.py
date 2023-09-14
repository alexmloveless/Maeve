from pydantic import BaseModel
from typing import Any, Optional

class CatalogueItem(BaseModel):
    obj: Any
    name: str
    obj_type: str = None
    description: str = None
    metadata: dict = None


class Catalogue:

    def __init__(self):
        self._items = []

    def add(self,
            obj: Any,
            name: str,
            obj_type: str = None,
            description: str = None,
            metadata: dict = None,
            protect: bool = True,
            ):

        if protect and hasattr(self, name):
            raise AttributeError(f"Cannot add item with name {name} to catalogue "
                                 f"as already exists. Use different name or set protect=False")

        metadata = metadata if metadata else {}
        setattr(self, name,
                CatalogueItem(obj=obj, name=name, obj_type=obj_type, description=description, metadata=metadata)
                )

