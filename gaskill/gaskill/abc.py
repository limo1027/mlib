"""
gaskill.abc - 抽象基类模块（零依赖）
"""


class ABCMeta(type):
    """元类：自动收集抽象方法"""

    def __new__(cls, name, bases, dct):
        # 1. 从所有父类继承抽象方法
        abstract_methods = set()
        for base in bases:
            if hasattr(base, '_abstract_methods'):
                abstract_methods.update(base._abstract_methods)

        # 2. 处理当前类定义的方法
        for key, value in dct.items():
            # 如果当前类显式定义了抽象方法（有 _is_abstract 标记）
            if hasattr(value, '_is_abstract') and value._is_abstract:
                abstract_methods.add(key)
            else:
                # 如果当前类定义了具体实现（没有 _is_abstract 标记）
                # 并且该方法在抽象方法集合中，则移除（即实现了该抽象方法）
                if key in abstract_methods:
                    abstract_methods.remove(key)

        # 3. 存储最终的抽象方法集合
        dct['_abstract_methods'] = frozenset(abstract_methods)
        return super().__new__(cls, name, bases, dct)

    def __call__(cls, *args, **kwargs):
        """实例化时检查抽象方法是否都已实现"""
        if cls._abstract_methods:
            methods = ', '.join(cls._abstract_methods)
            raise TypeError(
                f"Can't instantiate abstract class {cls.__name__} "
                f"with abstract methods {methods}"
            )
        return super().__call__(*args, **kwargs)


class ABC(metaclass=ABCMeta):
    """抽象基类"""

    def __init__(self):

        if type(self) is ABC:
            raise TypeError(
                "Can't instantiate abstract class ABC with abstract methods")


def abstractmethod(func):
    """装饰器：标记抽象方法"""
    func._is_abstract = True
    return func


def abstractclassmethod(func):
    """装饰器：标记抽象类方法"""
    func._is_abstract = True
    return classmethod(func)


def abstractstaticmethod(func):
    """装饰器：标记抽象静态方法"""
    func._is_abstract = True
    return staticmethod(func)


def abstractproperty(func):
    """装饰器：标记抽象属性"""
    func._is_abstract = True
    return property(func)
