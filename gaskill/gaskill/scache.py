from .type import Callable


def _to_hashble(key: object) -> str:
    return str(key)+":"+type(key).__name__


class LFUCache:
    """最少使用缓存(Least Frequently Used Cache)"""

    def __init__(self, max_size: int = 100) -> None:
        self._max_size = max_size
        self._cache: dict = {}

    def get(self, key: object, default: object = None) -> object:
        """获取缓存值"""
        if key not in self:
            return default

        self._cache[_to_hashble(key)][1] += 1
        return self._cache[_to_hashble(key)][0]

    def set(self, key: object, value: object) -> None:
        """设置缓存"""
        if key in self:
            self._cache[_to_hashble(key)][1] += 1

        elif len(self._cache) >= self._max_size:
            oldest = sorted(self._cache.values(), key=lambda x: x[1])[0][-1]
            del self._cache[oldest]

        self._cache[_to_hashble(key)] = [value, 1, _to_hashble(key)]

    def __setitem__(self, key: object, value: object) -> None:
        self.set(key, value)

    def __getitem__(self, key: object) -> object:
        value = self.get(key)
        if value is None:
            raise KeyError(key)
        return value

    def __contains__(self, key: object) -> bool:
        return _to_hashble(key) in self._cache

    def pop(self, key: object, default: object = None) -> object:
        """移除并返回缓存"""
        if key not in self._cache:
            return default

        value = self._cache.pop(key)
        return value

    def clear(self) -> None:
        """清空缓存"""
        self._cache.clear()

    def keys(self) -> list:
        """所有键"""
        return list(self._cache.keys())

    def values(self) -> list:
        """所有值"""
        return list(self._cache.values())

    def items(self) -> object:
        """所有键值对"""
        return list(self._cache.items())

    @property
    def size(self) -> int:
        """当前缓存数量"""
        return len(self._cache)

    @property
    def max_size(self) -> int:
        """最大缓存数量"""
        return self._max_size

    def __len__(self) -> int:
        return len(self._cache)

    def __repr__(self) -> str:
        return f"LFUCache(size={len(self._cache)}, max_size={self._max_size})"


class LRUCache:
    """最近最少使用缓存 (Least Recently Used Cache)"""

    def __init__(self, max_size: int = 100) -> None:
        """初始化 LRU 缓存"""
        self._max_size = max_size
        self._cache: dict[str, object] = {}
        self._order: list[object] = []

    def get(self, key: object, default: object = None) -> object:
        """获取缓存值"""
        if key not in self:
            return default

        self._order.remove(key)
        self._order.append(key)
        return self._cache[_to_hashble(key)]

    def set(self, key: object, value: object) -> None:
        """设置缓存"""
        if key in self:
            self._order.remove(_to_hashble(key))
        elif len(self._cache) >= self._max_size:
            oldest = self._order.pop(0)
            del self._cache[_to_hashble(oldest)]

        self._cache[_to_hashble(key)] = value
        self._order.append(key)

    def __setitem__(self, key: object, value: object) -> None:
        self.set(key, value)

    def __getitem__(self, key: object) -> object:
        value = self.get(key)
        if value is None:
            raise KeyError(key)
        return value

    def __contains__(self, key: object) -> bool:
        return _to_hashble(key) in self._cache

    def pop(self, key: object, default: object = None) -> object:
        """移除并返回缓存"""
        if key not in self._cache:
            return default

        self._order.remove(_to_hashble(key))
        value = self._cache.pop(_to_hashble(key))
        return value

    def clear(self) -> None:
        """清空缓存"""
        self._cache.clear()
        self._order.clear()

    def keys(self) -> list:
        """所有键"""
        return list(self._cache.keys())

    def values(self) -> list:
        """所有值"""
        return list(self._cache.values())

    def items(self) -> list:
        """所有键值对"""
        return list(self._cache.items())

    @property
    def size(self) -> int:
        """当前缓存数量"""
        return len(self._cache)

    @property
    def max_size(self) -> int:
        """最大缓存数量"""
        return self._max_size

    def __len__(self) -> int:
        return len(self._cache)

    def __repr__(self) -> str:
        return f"LRUCache(size={len(self._cache)}, max_size={self._max_size})"


class CacheEntry:
    """缓存条目（带过期时间）"""

    def __init__(self, key: object, value: object, ttl: int = 0) -> None:
        """初始化缓存条目"""
        self.key = key
        self.value = value
        self.ttl = ttl
        self.access_count = 0
        self.last_access = 0

    def is_expired(self, current_time: int) -> bool:
        """检查是否过期"""
        if self.ttl is None:
            return False
        return current_time > self.ttl


class TTLCache:
    """带过期时间的缓存"""

    def __init__(self, max_size: int = 100, default_ttl: "int | None" = None) -> None:
        """初始化 TTL 缓存"""
        self._max_size = max_size
        self._default_ttl = default_ttl
        self._cache: dict[str, CacheEntry] = {}

    def get(self, key: object, default: object = None, current_time: int = 0) -> object:
        """获取缓存值"""
        if key not in self._cache:
            return default

        entry = self._cache[_to_hashble(key)]

        if entry.ttl is not None and current_time > entry.ttl:
            del self._cache[_to_hashble(key)]
            return default

        entry.access_count += 1
        entry.last_access = current_time

        return entry.value

    def set(self, key: object, value: object, ttl: int = 0, current_time: int = 0) -> None:
        """设置缓存"""
        if ttl is None:
            ttl = self._default_ttl

        if ttl is not None:
            ttl = current_time + ttl

        if key not in self._cache and len(self._cache) >= self._max_size:
            self._evict_lru()

        self._cache[_to_hashble(key)] = CacheEntry(key, value, ttl)

    def _evict_lru(self) -> None:
        """驱逐最少使用的条目"""
        if not self._cache:
            return

        lru_key = min(self._cache.keys(),
                      key=lambda k: self._cache[k].last_access)
        del self._cache[lru_key]

    def clear(self) -> None:
        """清空缓存"""
        self._cache.clear()

    def remove_expired(self, current_time: int) -> int:
        """移除所有过期条目"""
        expired_keys = [
            key for key, entry in self._cache.items()
            if entry.ttl is not None and current_time > entry.ttl
        ]

        for key in expired_keys:
            del self._cache[_to_hashble(key)]

        return len(expired_keys)

    @property
    def size(self) -> int:
        """当前缓存数量"""
        return len(self._cache)

    def __len__(self) -> int:
        return len(self._cache)

    def __repr__(self) -> str:
        return f"TTLCache(size={len(self._cache)}, max_size={self._max_size})"


class _MemoizeFunc:
    """记忆化装饰器（内部类）"""

    def __init__(self, func: Callable, max_size: int = 128) -> None:
        self._func = func
        self._cache = LRUCache(max_size)

    def __call__(self, *args: "tuple[object, ...]", **kwargs: "dict[object, object]"):
        key = (args, tuple(sorted(kwargs.items())))

        if key in self._cache:
            return self._cache.get(key)

        result = self._func(*args, **kwargs)
        self._cache.set(key, result)
        return result

    def clear(self) -> None:
        """清空缓存"""
        self._cache.clear()

    def __repr__(self) -> str:
        return f"<memoized function: {self._func.__name__}>"


class _MemoizeMethod:
    """方法专用记忆化装饰器（自动忽略 self）"""

    def __init__(self, func: Callable, max_size: int = 128) -> None:
        self._func = func
        self._cache = LRUCache(max_size)

    def _get_state(self, obj):
        """获取对象的状态快照，兼容 __slots__"""
        # 1. 尝试 __dict__
        try:
            return tuple(sorted(obj.__dict__.items()))
        except AttributeError:
            pass

        # 2. 尝试 __slots__
        result = []
        for cls in type(obj).__mro__:
            slots = getattr(cls, "__slots__", ())
            if slots:
                for slot in slots:
                    if hasattr(obj, slot):
                        result.append((slot, getattr(obj, slot)))
        return tuple(sorted(result))

    def __get__(self, obj: object, _=None):
        if obj is None:
            return self
        # 预计算状态快照
        state = self._get_state(obj)
        return lambda *args, **kwargs: self._call(obj, state, *args, **kwargs)

    def _call(self, obj: object, state, *args, **kwargs):
        key = (state, args, tuple(sorted(kwargs.items())))
        if key in self._cache:
            return self._cache.get(key)
        result = self._func(obj, *args, **kwargs)
        self._cache.set(key, result)
        return result


def memoize(max_size: int = 128, method: bool = False) -> Callable[[Callable], "_MemoizeMethod | _MemoizeFunc"]:
    """记忆化装饰器"""
    def decorator(func: Callable) -> "_MemoizeMethod | _MemoizeFunc":
        if method:
            return _MemoizeMethod(func, max_size)
        return _MemoizeFunc(func, max_size)
    return decorator


class RingBuffer:
    """环形缓冲区 - 固定大小的 FIFO 缓冲区"""

    def __init__(self, capacity: int) -> None:
        """初始化环形缓冲区"""
        self._capacity = capacity
        self._buffer: list[object] = [None] * capacity
        self._head = 0
        self._tail = 0
        self._size = 0

    def push(self, item: object) -> None:
        """添加元素"""
        self._buffer[self._tail] = item
        self._tail = (self._tail + 1) % self._capacity

        if self._size < self._capacity:
            self._size += 1
        else:
            self._head = (self._head + 1) % self._capacity

    def pop(self) -> object:
        """弹出元素"""
        if self._size == 0:
            raise IndexError("Buffer is empty")

        item = self._buffer[self._head]
        self._buffer[self._head] = None
        self._head = (self._head + 1) % self._capacity
        self._size -= 1

        return item

    def peek(self) -> object:
        """查看队首元素"""
        if self._size == 0:
            raise IndexError("Buffer is empty")
        return self._buffer[self._head]

    def clear(self) -> None:
        """清空缓冲区"""
        self._buffer = [None] * self._capacity
        self._head = 0
        self._tail = 0
        self._size = 0

    def __len__(self) -> int:
        return self._size

    @property
    def capacity(self) -> int:
        """容量"""
        return self._capacity

    def is_empty(self) -> bool:
        """是否为空"""
        return self._size == 0

    def is_full(self) -> bool:
        """是否已满"""
        return self._size == self._capacity

    def __repr__(self) -> str:
        return f"RingBuffer(size={self._size}, capacity={self._capacity})"


class CacheStats:
    """缓存统计"""

    def __init__(self) -> None:
        self._hits = 0
        self._misses = 0
        self._evictions = 0

    def record_hit(self) -> None:
        """记录命中"""
        self._hits += 1

    def record_miss(self) -> None:
        """记录未命中"""
        self._misses += 1

    def record_eviction(self) -> None:
        """记录驱逐"""
        self._evictions += 1

    @property
    def hits(self) -> int:
        """命中次数"""
        return self._hits

    @property
    def misses(self) -> int:
        """未命中次数"""
        return self._misses

    @property
    def evictions(self) -> int:
        """驱逐次数"""
        return self._evictions

    @property
    def total_requests(self) -> int:
        """总请求数"""
        return self._hits + self._misses

    @property
    def hit_rate(self) -> float:
        """命中率"""
        total = self.total_requests
        if total == 0:
            return 0.0
        return self._hits / total

    def reset(self) -> None:
        """重置统计"""
        self._hits = 0
        self._misses = 0
        self._evictions = 0

    def __repr__(self) -> str:
        return f"CacheStats(hits={self._hits}, misses={self._misses}, hit_rate={self.hit_rate:.2%})"
