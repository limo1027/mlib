# spool.py - 对象池模块


class ObjectPool:
    """对象池 - 用于复用对象，减少内存分配"""

    def __init__(self, factory=None, reset_func=None, max_size=100):
        """初始化对象池"""
        self._available = []
        self._in_use = set()
        self._factory = factory
        self._reset_func = reset_func
        self._max_size = max_size
        self._created_count = 0

    def acquire(self, *args, **kwargs):
        """获取一个对象"""
        if self._available:
            obj = self._available.pop()
            self._in_use.add(id(obj))
            return obj

        if self._factory:
            if self._created_count < self._max_size:
                obj = self._factory(*args, **kwargs)
                self._created_count += 1
                self._in_use.add(id(obj))
                return obj
            else:
                raise RuntimeError(f"对象池已达最大容量 ({self._max_size})")

        raise RuntimeError("未设置工厂函数且池中无可用对象")

    def release(self, obj):
        """释放对象回池中"""
        obj_id = id(obj)
        if obj_id not in self._in_use:
            return

        self._in_use.remove(obj_id)

        if len(self._available) < self._max_size:
            if self._reset_func:
                self._reset_func(obj)
            self._available.append(obj)

    def clear(self):
        """清空池中所有对象"""
        self._available.clear()
        self._in_use.clear()
        self._created_count = 0

    @property
    def available_count(self):
        """可用对象数量"""
        return len(self._available)

    @property
    def in_use_count(self):
        """使用中对象数量"""
        return len(self._in_use)

    @property
    def total_count(self):
        """总对象数量"""
        return self._created_count

    def __len__(self):
        """返回可用对象数量"""
        return len(self._available)

    def __repr__(self):
        return f"ObjectPool(available={self.available_count}, in_use={self.in_use_count}, total={self.total_count})"


class PooledObject:
    """可池化对象基类"""

    def __init__(self):
        self._pool = None
        self._is_active = True

    def recycle(self):
        """回收对象到池中"""
        self._is_active = False
        if self._pool:
            self._pool.release(self)

    def on_acquire(self):
        """当对象被获取时调用"""
        self._is_active = True

    def on_release(self):
        """当对象被释放时调用"""
        self._is_active = False

    @property
    def is_active(self):
        """对象是否激活"""
        return self._is_active


class AutoReleasePool:
    """自动释放池 - 用于管理临时对象的生命周期"""

    def __init__(self):
        self._objects = []
        self._parent = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release_all()
        return False

    def add(self, obj, release_method="recycle"):
        """添加对象到自动释放池"""
        self._objects.append((obj, release_method))

    def release_all(self):
        """释放所有对象"""
        for obj, method_name in reversed(self._objects):
            if hasattr(obj, method_name):
                getattr(obj, method_name)()
        self._objects.clear()

    @property
    def count(self):
        """池中对象数量"""
        return len(self._objects)


class StackAllocator:
    """栈式分配器 - LIFO 对象管理"""

    def __init__(self, initial_capacity=100):
        """初始化栈分配器"""
        self._storage = [None] * initial_capacity
        self._top = 0
        self._capacity = initial_capacity

    def _grow(self):
        """扩容"""
        new_capacity = self._capacity * 2
        new_storage = [None] * new_capacity
        for i in range(self._top):
            new_storage[i] = self._storage[i]
        self._storage = new_storage
        self._capacity = new_capacity

    def push(self, obj):
        """压入对象"""
        if self._top >= self._capacity:
            self._grow()
        self._storage[self._top] = obj
        self._top += 1

    def pop(self):
        """弹出对象"""
        if self._top <= 0:
            raise IndexError("栈为空")
        self._top -= 1
        obj = self._storage[self._top]
        self._storage[self._top] = None
        return obj

    def pop_multiple(self, count):
        """弹出多个对象"""
        if count > self._top:
            raise IndexError(f"栈中只有 {self._top} 个对象，请求弹出 {count} 个")

        result = []
        for _ in range(count):
            self._top -= 1
            result.append(self._storage[self._top])
            self._storage[self._top] = None

        return result

    def clear(self):
        """清空栈"""
        for i in range(self._top):
            self._storage[i] = None
        self._top = 0

    @property
    def size(self):
        """栈中对象数量"""
        return self._top

    @property
    def capacity(self):
        """栈容量"""
        return self._capacity

    def __len__(self):
        return self._top

    def __repr__(self):
        return f"StackAllocator(size={self.size}, capacity={self.capacity})"
