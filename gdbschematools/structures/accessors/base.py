"""
Base classes used by the various specific element accessors.

Author: David Blanchard
"""

from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from ..geodatabase import Geodatabase


class Accessor():
    """Base class for all accessors providing sequence methods."""

    _elements_container:list[object] = None
    _iter_list:list[object] = None


    def __init__(self) -> None:
        self._elements_container = []


    @property
    def _elements(self):
        return self._elements_container


    def _append(self, value):
        self._elements_container.append(value)
        self._elements_container.sort()


    def _remove(self, value):
        self._elements_container.remove(value)


    # for element in accessor / list(accessor)
    def __iter__(self):
        self._iter_list = list(self._elements)
        return self


    def __next__(self):
        if self._iter_list:
            return self._iter_list.pop(0)
        raise StopIteration


    # accessor[0] or accessor['name']
    def __getitem__(self, key:Union[int, str]) -> object:
        if isinstance(key, int):
            return self._elements[key]

        return self._get(key)


    # len(accessor)
    def __len__(self) -> int:
        return len(self._elements)


    # 'name' in accessor or <dataset> in accessor
    def __contains__(self, item:Union[object, str]) -> bool:
        if isinstance(item, str):
            try:
                self._get(item)
                return True
            except LookupError:
                return False

        return item in self._elements


    # print(accessor)
    def __repr__(self) -> str:
        return f"<structures.{self.__class__.__name__}'>"


    # str(accessor)
    def __str__(self) -> str:
        return f"<structures.{self.__class__.__name__}'>"


    @property
    def _label(self) -> str:
        cname = self.__class__.__name__
        if cname == "_Accessor":
            return "accessor"
        return cname.lower().split("accessor", maxsplit=1)[0]


    def _get(self, name:str) -> object:
        """Get an element by its name.

        Args:
            name (str): Name of the element to find.

        Returns:
            object: Element matching the name.
        """

        items = [e for e in self._elements if e.name == name]

        if len(items) == 0:
            raise LookupError(f"No {self._label} with the name of '{name}' found.")

        if len(items) > 1:
            raise SystemError(f"Multiple {self._label} with the name of '{name}' were found.")

        return items[0]


#pylint: disable=too-few-public-methods
class AccessorWithGDB(Accessor):
    """Base class for all accessors providing sequence methods, with a geodatabase as a parent.

    Args:
        geodatabase (Geodatabase): Instance of a Geodatabase instance.
    """

    _geodatabase:"Geodatabase" = None

    def __init__(self, geodatabase:"Geodatabase") -> None:
        super().__init__()
        self._geodatabase = geodatabase


#pylint: disable=too-few-public-methods
class SubAccessor(AccessorWithGDB):
    """Main base class for access to a specific subset of datasets within a main accessor.

    Args:
        geodatabase (Geodatabase): Instance of a Geodatabase instance.
        elements_container (list): Sequence that contains the total set of elements.
    """

    _dataset_type:str = None
    _accessor:AccessorWithGDB = None


    def __init__(self, geodatabase:"Geodatabase", accessor:AccessorWithGDB, dataset_type:str) -> None:
        super().__init__(geodatabase)
        self._elements_container = accessor._elements_container
        self._dataset_type = dataset_type
        self._accessor = accessor


    @property
    def _elements(self):
        return [el for el in self._elements_container if el.dataset_type == self._dataset_type]


class DictAccessor():
    """Read-only dictionary like accessor."""

    _lookup:dict[any, any] = None
    _iter_keys:list[any] = None


    def __init__(self):
        self._lookup = {}


    def __getitem__(self, key):
        return self._lookup[key]


    def __repr__(self):
        return "<structures.DictAccessor>"


    def __len__(self):
        return len(self._lookup)


    def keys(self):
        """A set-like object providing a view on dictionary's keys"""
        return self._lookup.keys()


    def values(self):
        """An object providing a view on dictionary's values."""
        return self._lookup.values()


    def items(self):
        """A set-like object providing a view on dictionary's items"""
        return self._lookup.items()


    def __contains__(self, item):
        return item in self._lookup


    def __iter__(self):
        self._iter_keys = list(self.keys())
        return self


    def __next__(self):
        if self._iter_keys:
            return self._iter_keys.pop(0)
        raise StopIteration