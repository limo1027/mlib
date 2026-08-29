from .abc import ABC, abstractmethod


class Iterable(ABC):
    @abstractmethod
    def __iter__(self):
        while False:
            yield None

    @classmethod
    def __subclasshook__(cls, C):
        if cls is Iterable:
            if any("__iter__" in B.__dict__ for B in C.__mro__):
                return True
        return NotImplemented


class DefaultDict:
    """带默认值的字典"""

    def __init__(self, default_factory=None, **kwargs):
        self._data = {}
        self._default_factory = default_factory
        self.update(kwargs)

    def __getitem__(self, key):
        try:
            return self._data[key]
        except KeyError:
            if self._default_factory is None:
                raise
            value = self._default_factory()
            self._data[key] = value
            return value

    def __setitem__(self, key, value):
        self._data[key] = value

    def __delitem__(self, key):
        del self._data[key]

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def __repr__(self):
        return f"DefaultDict({self._default_factory}, {self._data})"

    def update(self, other):
        self._data.update(other)

    def get(self, key, default=None):
        return self._data.get(key, default)

    def pop(self, key, default=None):
        return self._data.pop(key, default)

    def keys(self):
        return self._data.keys()

    def values(self):
        return self._data.values()

    def items(self):
        return self._data.items()

    def copy(self):
        return DefaultDict(self._default_factory, **self._data)

    def clear(self):
        self._data.clear()
