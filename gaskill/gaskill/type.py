from .sabc import ABC, abstractmethod  # noqa


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


class Iterable(ABC):
    """可迭代对象抽象基类"""

    @abstractmethod
    def __iter__(self):
        while False:
            yield None

    @classmethod
    def __subclasshook__(cls, C):
        # 用 hasattr 而不是 in __dict__
        if any(hasattr(B, "__iter__") for B in C.__mro__):
            return True
        return NotImplemented


class Callable(ABC):
    """可调用对象抽象基类"""

    def __init__(self):
        self.__name__ = ...
        self.__annotations__ = ...

    @abstractmethod
    def __call__(self, *args, **kwargs):
        ...

    @classmethod
    def __subclasshook__(cls, C):
        if cls is Callable:
            if any("__call__" in B.__dict__ for B in C.__mro__):
                return True
        return NotImplemented

    @classmethod
    def __class_getitem__(cls, item):
        """支持 Callable[[Args], Ret] 语法"""
        return cls


class Number(ABC):
    """数值类型抽象基类"""

    @abstractmethod
    def __add__(self, other):
        ...

    @abstractmethod
    def __sub__(self, other):
        ...

    @abstractmethod
    def __mul__(self, other):
        ...

    @abstractmethod
    def __truediv__(self, other):
        ...

    # 可选：其他常见的数值方法
    @abstractmethod
    def __neg__(self):
        ...

    @abstractmethod
    def __pos__(self):
        ...

    @abstractmethod
    def __abs__(self):
        ...

    @classmethod
    def __subclasshook__(cls, C):
        # 检查是否实现了核心算术方法
        required = {"__add__", "__sub__", "__mul__", "__truediv__"}
        for meth in required:
            if not any(meth in B.__dict__ for B in C.__mro__):
                return NotImplemented
        return True
