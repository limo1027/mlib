# ==================== 装饰器定义 ====================

def test(func):
    """标记测试方法，并自动注入当前测试名"""
    def wrapper(self, *args, **kwargs):
        # 保存当前测试名到实例
        self._current_test = func.__name__
        # 执行原始测试方法
        return func(self, *args, **kwargs)
    wrapper._is_test = True
    wrapper.__name__ = func.__name__
    return wrapper


def skip(reason="跳过"):
    """跳过测试"""
    def decorator(func):
        func._skip = True
        func._skip_reason = reason
        return func
    return decorator


# ==================== assert_raises 上下文管理器 ====================

class _AssertRaisesContext:
    """assert_raises 的上下文管理器，支持 with 风格"""
    
    def __init__(self, test_name, exc_class):
        self.test_name = test_name
        self.exc_class = exc_class
        self.exception = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            # 没有抛出异常
            raise AssertionError(
                f"AssertionError in {self.test_name}: 期望 {self.exc_class.__name__}, 但没有抛出异常"
            )
        if issubclass(exc_type, self.exc_class):
            # 抛出了期望的异常（或其子类），吞噬它
            self.exception = exc_val
            return True  # 表示已处理
        # 抛出了其他异常，不吞噬
        return False


# ==================== TestCase 基类 ====================

class TestCase:
    def __init__(self):
        self._current_test = None
    
    def get_test_methods(self):
        """获取所有被 @test 标记的方法"""
        methods = []
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if callable(attr) and hasattr(attr, "_is_test"):
                methods.append(attr)
        return methods
    
    def _get_test_name(self):
        """获取当前测试名称"""
        return self._current_test or "未知测试"
    
    # ==================== 断言方法 ====================
    
    # ---- 相等性断言 ----
    
    def assert_equal(self, a, b):
        """断言 a == b"""
        if not (a == b):
            test_name = self._get_test_name()
            raise AssertionError(
                f"AssertionError in {test_name}: {repr(a)} != {repr(b)}"
            )
    
    def assert_not_equal(self, a, b):
        """断言 a != b"""
        if not (a != b):
            test_name = self._get_test_name()
            raise AssertionError(
                f"AssertionError in {test_name}: {repr(a)} == {repr(b)}"
            )
    
    # ---- 近似相等断言 ----
    
    def assert_almost_equal(self, a, b, places=7):
        """断言 round(a-b, places) == 0（浮点数近似相等）"""
        test_name = self._get_test_name()
        if round(a - b, places) != 0:
            raise AssertionError(
                f"AssertionError in {test_name}: {repr(a)} 与 {repr(b)} 在小数点后 {places} 位不相等"
            )
    
    def assert_not_almost_equal(self, a, b, places=7):
        """断言 round(a-b, places) != 0（浮点数不近似相等）"""
        test_name = self._get_test_name()
        if round(a - b, places) == 0:
            raise AssertionError(
                f"AssertionError in {test_name}: {repr(a)} 与 {repr(b)} 在小数点后 {places} 位相等"
            )
    
    # ---- 比较断言 ----
    
    def assert_greater(self, a, b):
        """断言 a > b"""
        if not (a > b):
            test_name = self._get_test_name()
            raise AssertionError(
                f"AssertionError in {test_name}: {repr(a)} 不大于 {repr(b)}"
            )
    
    def assert_greater_equal(self, a, b):
        """断言 a >= b"""
        if not (a >= b):
            test_name = self._get_test_name()
            raise AssertionError(
                f"AssertionError in {test_name}: {repr(a)} 不大于等于 {repr(b)}"
            )
    
    def assert_less(self, a, b):
        """断言 a < b"""
        if not (a < b):
            test_name = self._get_test_name()
            raise AssertionError(
                f"AssertionError in {test_name}: {repr(a)} 不小于 {repr(b)}"
            )
    
    def assert_less_equal(self, a, b):
        """断言 a <= b"""
        if not (a <= b):
            test_name = self._get_test_name()
            raise AssertionError(
                f"AssertionError in {test_name}: {repr(a)} 不小于等于 {repr(b)}"
            )
    
    # ---- 布尔值断言 ----
    
    def assert_true(self, x):
        """断言 bool(x) is True（真值检查）"""
        if not bool(x):
            test_name = self._get_test_name()
            raise AssertionError(
                f"AssertionError in {test_name}: {repr(x)} 不是真值"
            )
    
    def assert_false(self, x):
        """断言 bool(x) is False（假值检查）"""
        if bool(x):
            test_name = self._get_test_name()
            raise AssertionError(
                f"AssertionError in {test_name}: {repr(x)} 不是假值"
            )
    
    # ---- 身份断言（对象引用） ----
    
    def assert_is(self, a, b):
        """断言 a is b（同一个对象）"""
        if a is not b:
            test_name = self._get_test_name()
            raise AssertionError(
                f"AssertionError in {test_name}: {repr(a)} is not {repr(b)}"
            )
    
    def assert_is_not(self, a, b):
        """断言 a is not b（不是同一个对象）"""
        if not (a is not b):
            test_name = self._get_test_name()
            raise AssertionError(
                f"AssertionError in {test_name}: {repr(a)} is {repr(b)}"
            )
    
    # ---- None 断言 ----
    
    def assert_is_none(self, x):
        """断言 x is None"""
        if x is not None:
            test_name = self._get_test_name()
            raise AssertionError(
                f"AssertionError in {test_name}: 期望 None，实际是 {repr(x)} ({type(x).__name__})"
            )
    
    def assert_is_not_none(self, x):
        """断言 x is not None"""
        if not (x is not None):
            test_name = self._get_test_name()
            raise AssertionError(
                f"AssertionError in {test_name}: 期望不是 None，实际是 None"
            )
    
    # ---- 成员关系断言 ----
    
    def assert_in(self, a, b):
        """断言 a in b"""
        if a not in b:
            test_name = self._get_test_name()
            raise AssertionError(
                f"AssertionError in {test_name}: {repr(a)} 不在 {repr(b)} 中"
            )
    
    def assert_not_in(self, a, b):
        """断言 a not in b"""
        if not (a not in b):
            test_name = self._get_test_name()
            raise AssertionError(
                f"AssertionError in {test_name}: {repr(a)} 在 {repr(b)} 中"
            )
    
    # ---- 类型断言 ----
    
    def assert_isinstance(self, a, b):
        """断言 isinstance(a, b)"""
        if not isinstance(a, b):
            test_name = self._get_test_name()
            if isinstance(b, tuple):
                expected = f"({', '.join(c.__name__ for c in b)})"
            else:
                expected = b.__name__
            actual = type(a).__name__
            raise AssertionError(
                f"AssertionError in {test_name}: 期望 {repr(a)} 是 {expected} 的实例，实际是 {actual}"
            )
    
    def assert_not_isinstance(self, a, b):
        """断言 not isinstance(a, b)"""
        if isinstance(a, b):
            test_name = self._get_test_name()
            if isinstance(b, tuple):
                expected = f"({', '.join(c.__name__ for c in b)})"
            else:
                expected = b.__name__
            actual = type(a).__name__
            raise AssertionError(
                f"AssertionError in {test_name}: 期望 {repr(a)} 不是 {expected} 的实例，实际是 {actual}"
            )
    
    # ---- 子类断言 ----
    
    def assert_issubclass(self, a, b):
        """断言 issubclass(a, b)（a 是 b 的子类）"""
        if not issubclass(a, b):
            test_name = self._get_test_name()
            if isinstance(b, tuple):
                expected = f"({', '.join(c.__name__ for c in b)})"
            else:
                expected = b.__name__
            if isinstance(a, type):
                actual = a.__name__
            else:
                actual = type(a).__name__
            raise AssertionError(
                f"AssertionError in {test_name}: 期望 {actual} 是 {expected} 的子类"
            )
    
    def assert_not_issubclass(self, a, b):
        """断言 not issubclass(a, b)（a 不是 b 的子类）"""
        if issubclass(a, b):
            test_name = self._get_test_name()
            if isinstance(b, tuple):
                expected = f"({', '.join(c.__name__ for c in b)})"
            else:
                expected = b.__name__
            if isinstance(a, type):
                actual = a.__name__
            else:
                actual = type(a).__name__
            raise AssertionError(
                f"AssertionError in {test_name}: 期望 {actual} 不是 {expected} 的子类"
            )
    
    # ---- 计数断言（比较两个容器的元素，忽略顺序） ----
    
    def assert_count_equal(self, a, b):
        """断言 a 和 b 包含相同的元素，忽略顺序"""
        test_name = self._get_test_name()
        
        # 先比较长度
        if len(a) != len(b):
            raise AssertionError(
                f"AssertionError in {test_name}: 长度不同，{repr(a)} (len={len(a)}) vs {repr(b)} (len={len(b)})"
            )
        
        # 转换为列表并排序比较（适用于可哈希元素）
        try:
            sorted_a = sorted(a)
            sorted_b = sorted(b)
            if sorted_a != sorted_b:
                raise AssertionError(
                    f"AssertionError in {test_name}: 元素不同\n  {repr(a)}\n  vs\n  {repr(b)}"
                )
        except TypeError:
            # 如果元素不可排序（如包含字典），用计数方式
            remaining = list(b)
            for item in a:
                found = False
                for i, other in enumerate(remaining):
                    if item == other:
                        remaining.pop(i)
                        found = True
                        break
                if not found:
                    raise AssertionError(
                        f"AssertionError in {test_name}: {repr(item)} 在 a 中但不在 b 中"
                    )
            if remaining:
                raise AssertionError(
                    f"AssertionError in {test_name}: {repr(remaining[0])} 在 b 中但不在 a 中"
                )
    
    # ---- 字符串前缀/后缀断言 ----
    
    def assert_starts_with(self, a, b):
        """断言 a.startswith(b)（字符串以 b 开头）"""
        if not a.startswith(b):
            test_name = self._get_test_name()
            raise AssertionError(
                f"AssertionError in {test_name}: {repr(a)} 不以 {repr(b)} 开头"
            )
    
    def assert_not_starts_with(self, a, b):
        """断言 not a.startswith(b)（字符串不以 b 开头）"""
        if a.startswith(b):
            test_name = self._get_test_name()
            raise AssertionError(
                f"AssertionError in {test_name}: {repr(a)} 以 {repr(b)} 开头"
            )
    
    def assert_ends_with(self, a, b):
        """断言 a.endswith(b)（字符串以 b 结尾）"""
        if not a.endswith(b):
            test_name = self._get_test_name()
            raise AssertionError(
                f"AssertionError in {test_name}: {repr(a)} 不以 {repr(b)} 结尾"
            )
    
    def assert_not_ends_with(self, a, b):
        """断言 not a.endswith(b)（字符串不以 b 结尾）"""
        if a.endswith(b):
            test_name = self._get_test_name()
            raise AssertionError(
                f"AssertionError in {test_name}: {repr(a)} 以 {repr(b)} 结尾"
            )
    
    # ---- 属性断言 ----
    
    def assert_has_attr(self, a, b):
        """断言 hasattr(a, b)（对象有指定属性）"""
        if not hasattr(a, b):
            test_name = self._get_test_name()
            raise AssertionError(
                f"AssertionError in {test_name}: {repr(a)} 没有属性 {repr(b)}"
            )
    
    def assert_not_has_attr(self, a, b):
        """断言 not hasattr(a, b)（对象没有指定属性）"""
        if hasattr(a, b):
            test_name = self._get_test_name()
            raise AssertionError(
                f"AssertionError in {test_name}: {repr(a)} 有属性 {repr(b)}"
            )
    
    # ---- 异常断言（支持 with 风格和函数风格） ----
    
    def assert_raises(self, exc_class, func=None, *args, **kwargs):
        """断言抛出指定异常"""
        test_name = self._get_test_name()
        return _AssertRaisesContext(test_name, exc_class)
    
    
    # ====== 生命周期钩子 ======
    
    def setup(self):
        """每个测试方法执行前调用"""
        pass
    
    def teardown(self):
        """每个测试方法执行后调用"""
        pass
    
    @classmethod
    def setup_class(cls):
        """整个测试类执行前调用"""
        pass
    
    @classmethod
    def teardown_class(cls):
        """整个测试类执行后调用"""
        pass


# ==================== 测试运行器 ====================

class TestRunner:
    def run_single_test(self, test_instance, method):
        """执行单个测试方法，method 是绑定方法"""
        
        # 检查是否需要跳过
        if hasattr(method, "_skip"):
            return "skipped", method._skip_reason
        
        try:
            # 执行 setup
            test_instance.setup()
            
            # 执行测试方法（绑定方法直接调用，无需传参）
            method()
            
            # 执行 teardown
            test_instance.teardown()
            
            return "passed", None
            
        except AssertionError as e:
            return "failed", str(e)
        except Exception as e:
            return "error", f"{type(e).__name__}: {e}"
    
    def run_class(self, test_class):
        """运行一个测试类"""
        print(f"\n▶️ 测试类: {test_class.__name__}")
        
        test_instance = test_class()
        
        # 类级 setup
        test_class.setup_class()
        
        # 获取所有测试方法（绑定方法列表）
        test_methods = test_instance.get_test_methods()
        
        if not test_methods:
            print("   ⚠️ 没有测试方法")
            return {"passed": 0, "failed": 0, "error": 0, "skipped": 0}
        
        # 执行每个测试
        stats = {"passed": 0, "failed": 0, "error": 0, "skipped": 0}
        
        for method in test_methods:
            status, detail = self.run_single_test(test_instance, method)
            
            if status == "passed":
                stats["passed"] += 1
                print(f"   ✅ {method.__name__}")
            elif status == "skipped":
                stats["skipped"] += 1
                print(f"   ⏭️ {method.__name__} (跳过: {detail})")
            elif status == "failed":
                stats["failed"] += 1
                print(f"   ❌ {detail}")
            else:  # error
                stats["error"] += 1
                print(f"   💥 {method.__name__} (错误: {detail})")
        
        # 类级 teardown
        test_class.teardown_class()
        
        return stats
    
    def run_all(self):
        """发现并运行所有测试"""
        # 利用 __subclasses__ 发现所有 TestCase 子类
        test_classes = []
        for cls in TestCase.__subclasses__():
            test_classes.append(cls)
            # 递归获取子类的子类
            for subcls in cls.__subclasses__():
                test_classes.append(subcls)
        
        if not test_classes:
            print("⚠️ 没有找到测试类")
            return
        
        print(f"发现 {len(test_classes)} 个测试类")
        
        total = {"passed": 0, "failed": 0, "error": 0, "skipped": 0}
        
        for test_class in test_classes:
            stats = self.run_class(test_class)
            total["passed"] += stats["passed"]
            total["failed"] += stats["failed"]
            total["error"] += stats["error"]
            total["skipped"] += stats["skipped"]
        
        # 输出汇总
        print("\n" + "=" * 50)
        print("测试结果汇总")
        print("=" * 50)
        print(f"  通过: {total['passed']}")
        print(f"  失败: {total['failed']}")
        print(f"  错误: {total['error']}")
        print(f"  跳过: {total['skipped']}")
        print(f"  总计: {sum(total.values())}")
        print("=" * 50)
        
        # 返回是否有失败
        return total["failed"] == 0 and total["error"] == 0