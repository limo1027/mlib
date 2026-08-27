class ABCMeta(type):
    def __new__(cls, name, bases, dct):
        # 初始化缓存和注册表(必须有！)
        dct.setdefault("_abc_cache", set())
        dct.setdefault("_abc_negative_cache", set())
        dct.setdefault("_abc_registry", set())

        # 收集抽象方法(你已有的代码)
        abstract_methods = set()
        for base in bases:
            if hasattr(base, "_abstract_methods"):
                abstract_methods.update(base._abstract_methods)

        for key, value in dct.items():
            if hasattr(value, "__isabstractmethod__") and value.__isabstractmethod__:
                abstract_methods.add(key)
            elif key in abstract_methods:
                abstract_methods.remove(key)

        dct["_abstract_methods"] = frozenset(abstract_methods)
        return super().__new__(cls, name, bases, dct)

    def __call__(cls, *args, **kwargs):
        """实例化检查"""
        if cls._abstract_methods:
            methods = ", ".join(cls._abstract_methods)
            raise TypeError(
                f"Can't instantiate abstract class {cls.__name__} "
                f"with abstract methods {methods}",
            )
        return super().__call__(*args, **kwargs)

    # ============ 新增: 必须重写的方法 ============

    def __subclasscheck__(cls, subclass):
        """控制 issubclass(subclass, cls) 的行为"""
        # 1️⃣ 检查缓存(加速)
        if subclass in cls._abc_cache:
            return True
        if subclass in cls._abc_negative_cache:
            return False

        # 2️⃣ 检查真实继承
        if cls in subclass.__mro__:
            cls._abc_cache.add(subclass)
            return True

        # 3️⃣ 检查注册的虚拟子类
        if subclass in getattr(cls, "_abc_registry", set()):
            cls._abc_cache.add(subclass)
            return True

        # 4️⃣ 调用 __subclasshook__(这是你自定义逻辑的入口)
        hook = getattr(cls, "__subclasshook__", None)
        if hook is not None:
            try:
                result = hook(subclass)
                if result is True:
                    cls._abc_cache.add(subclass)
                    return True
                # 如果返回 NotImplemented，继续检查
            except Exception:
                # 钩子出错，视为不是子类
                pass

        # 5️⃣ 负缓存
        cls._abc_negative_cache.add(subclass)
        return False

    def __instancecheck__(cls, instance):
        """控制 isinstance(instance, cls) 的行为"""
        return cls.__subclasscheck__(type(instance))

    def register(cls, subclass):
        """注册虚拟子类"""
        cls._abc_registry.add(subclass)
        return subclass


class ABC(metaclass=ABCMeta):
    """抽象基类"""

    def __init__(self):

        if type(self) is ABC:
            raise TypeError(
                "Can't instantiate abstract class ABC with abstract methods")


def abstractmethod(func):
    """装饰器: 标记抽象方法"""
    func._is_abstract = True
    return func


def abstractclassmethod(func):
    """装饰器: 标记抽象类方法"""
    func._is_abstract = True
    return classmethod(func)


def abstractstaticmethod(func):
    """装饰器: 标记抽象静态方法"""
    func._is_abstract = True
    return staticmethod(func)


def abstractproperty(func):
    """装饰器: 标记抽象属性"""
    func._is_abstract = True
    return property(func)
