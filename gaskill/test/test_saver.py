from gaskill import ssaver
from gaskill import TestCase, TestRunner, test
from gaskill import vec2, vec3

class MockFile:
    """模拟文件对象，存内存里，不依赖任何标准库"""
    
    def __init__(self):
        self.content = ""
    
    def write(self, data):
        self.content += data
    
    def read(self):
        return self.content
    
    def readlines(self):
        return self.content.split("\n")
    
    def __repr__(self):
        return f"MockFile({repr(self.content)})"


class MockFile:
    def __init__(self):
        self.content = ""
    
    def write(self, data):
        self.content += data
    
    def read(self):
        return self.content
    
    def readlines(self):
        return self.content.split("\n")
    
    def seek(self, pos):
        pass  # 如果你不需要，直接忽略
    
    def tell(self):
        return len(self.content)


class SsaverTester(TestCase):
    
    @test
    def test_set_and_get(self):
        """测试设置和获取值"""
        s = ssaver.SGTsaver()
        s.set_value(name="mlib", version="1.0", score=100)
        
        self.assert_equal(s.get("name"), "mlib")
        self.assert_equal(s.get("version"), "1.0")
        self.assert_equal(s.get("score"), 100)
        self.assert_is_none(s.get("not_exist"))
        self.assert_equal(s.get("not_exist", "default"), "default")
    
    @test
    def test_add_method(self):
        """测试 add 方法（链式调用）"""
        s = ssaver.SGTsaver()
        s.add("a", 1).add("b", 2).add("c", 3)
        
        self.assert_equal(s.get("a"), 1)
        self.assert_equal(s.get("b"), 2)
        self.assert_equal(s.get("c"), 3)
    
    @test
    def test_dict_access(self):
        """测试 [] 访问和赋值"""
        s = ssaver.SGTsaver()
        s["name"] = "mlib"
        s["version"] = 42
        
        self.assert_equal(s["name"], "mlib")
        self.assert_equal(s["version"], 42)
    
    @test
    def test_value_types(self):
        """测试各种类型的存储"""
        s = ssaver.SGTsaver()
        s.set_value(
            str_val="hello",
            int_val=123,
            float_val=3.14,
            bool_true=True,
            bool_false=False,
            list_val=[1, 2, 3],
            vec2_val=vec2(1, 2),
            vec3_val=vec3(3, 4, 5)
        )
        
        self.assert_equal(s.get("str_val"), "hello")
        self.assert_equal(s.get("int_val"), 123)
        self.assert_almost_equal(s.get("float_val"), 3.14, places=5)
        self.assert_true(s.get("bool_true"))
        self.assert_false(s.get("bool_false"))
        self.assert_equal(s.get("list_val"), [1, 2, 3])
        self.assert_equal(s.get("vec2_val"), vec2(1, 2))
        self.assert_equal(s.get("vec3_val"), vec3(3, 4, 5))
    
    @test
    def test_save_load_mock(self):
        """测试保存到 MockFile 并加载回来"""
        s1 = ssaver.SGTsaver()
        s1.set_value(name="mlib", version="1.0", score=100)
        s1.add("tags", ["math", "geometry", "crypto"])
        s1["data"] = {'server': '127.0.0.1, 3000', 'port': 3306, "users": {"Alice": "password123", "Bob": "password12"}}
        
        # 保存到模拟文件
        mock = MockFile()
        s1.save(mock, use_hash=True)
        # 加载回来
        s2 = ssaver.SGTsaver()
        s2.load(mock, require_hash=True)
        
        self.assert_equal(s2.get("name"), "mlib")
        self.assert_equal(s2.get("version"), "1.0")
        self.assert_equal(s2.get("score"), 100)
        self.assert_equal(s2.get("tags"), ["math", "geometry", "crypto"])
        self.assert_equal(s2["data"], {'server': '127.0.0.1, 3000', 'port': 3306, "users": {"Alice": "password123", "Bob": "password12"}})

    
    @test
    def test_hash_validation(self):
        """测试校验和验证 - 篡改数据应该报错"""
        s = ssaver.SGTsaver()
        s.set_value(name="mlib", version="1.0")
        
        mock = MockFile()
        s.save(mock, use_hash=True)
        
        # 篡改内容（手动改字符串）
        mock.content = mock.content.replace("mlib", "hacked")
        
        s2 = ssaver.SGTsaver()
        with self.assert_raises(ValueError):
            s2.load(mock, require_hash=True)
    
    @test
    def test_no_hash(self):
        """测试不生成校验和"""
        s = ssaver.SGTsaver()
        s.set_value(name="mlib")
        
        mock = MockFile()
        s.save(mock, use_hash=False)
        
        # 没有 hash 行
        self.assert_false("hash=" in mock.content)
        
        # 但应该能正常加载（require_hash=False）
        s2 = ssaver.SGTsaver()
        s2.load(mock, require_hash=False)
        self.assert_equal(s2.get("name"), "mlib")
    
    @test
    def test_overwrite(self):
        """测试覆盖已有键"""
        s = ssaver.SGTsaver()
        s.set_value(name="old", version=1)
        s.set_value(name="new")  # 覆盖 name
        
        self.assert_equal(s.get("name"), "new")
        self.assert_equal(s.get("version"), 1)  # version 还在
    


if __name__ == "__main__":
    runner = TestRunner()
    runner.run_all()