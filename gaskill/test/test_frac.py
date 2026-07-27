from gaskill import Frac
from gaskill import TestCase, TestRunner, test


class FracTester(TestCase):
    
    # ==================== 创建和表示 ====================
    
    @test
    def test_creation_from_ints(self):
        """测试从两个整数创建"""
        f = Frac(1, 2)
        self.assert_equal(f.n, 1)
        self.assert_equal(f.d, 2)
        self.assert_equal(str(f), "1/2")
    
    @test
    def test_creation_from_single_int(self):
        """测试从单个整数创建（分母为 1）"""
        f = Frac(5)
        self.assert_equal(f.n, 5)
        self.assert_equal(f.d, 1)
        self.assert_equal(str(f), "5")
    
    @test
    def test_creation_from_float(self):
        """测试从浮点数创建"""
        f = Frac(0.5)
        self.assert_equal(f.n, 1)
        self.assert_equal(f.d, 2)
    
    @test
    def test_creation_from_string(self):
        """测试从字符串创建"""
        f = Frac("0.75")
        self.assert_equal(f.n, 3)
        self.assert_equal(f.d, 4)
    
    @test
    def test_creation_from_scientific_notation(self):
        """测试从科学计数法字符串创建"""
        f = Frac("1.5e-1")
        self.assert_equal(f.n, 3)
        self.assert_equal(f.d, 20)
    
    @test
    def test_auto_simplify(self):
        """测试自动约分"""
        f = Frac(2, 4)
        self.assert_equal(f.n, 1)
        self.assert_equal(f.d, 2)
    
    @test
    def test_negative_denominator(self):
        """测试负分母自动归一化"""
        f = Frac(1, -2)
        self.assert_equal(f.n, -1)
        self.assert_equal(f.d, 2)
    
    @test
    def test_creation_from_frac(self):
        """测试从 Frac 创建 Frac"""
        f1 = Frac(1, 2)
        f2 = Frac(f1)
        self.assert_equal(f2.n, 1)
        self.assert_equal(f2.d, 2)
    
    @test
    def test_repr(self):
        """测试 repr 可 eval"""
        f = Frac(1, 3)
        r = repr(f)
        # 应该能被 eval 还原
        f2 = eval(r)
        self.assert_equal(f2.n, 1)
        self.assert_equal(f2.d, 3)
    
    # ==================== 加法 ====================
    
    @test
    def test_add_two_fracs(self):
        """测试两个分数相加"""
        f1 = Frac(1, 3)
        f2 = Frac(1, 6)
        result = f1 + f2
        self.assert_equal(result.n, 1)
        self.assert_equal(result.d, 2)
    
    @test
    def test_add_with_int(self):
        """测试分数 + 整数"""
        f = Frac(1, 2)
        result = f + 3
        self.assert_equal(result.n, 7)
        self.assert_equal(result.d, 2)
    
    @test
    def test_add_with_float(self):
        """测试分数 + 浮点数"""
        f = Frac(1, 2)
        result = f + 0.25
        self.assert_equal(result.n, 3)
        self.assert_equal(result.d, 4)
    
    @test
    def test_radd(self):
        """测试右加法：int + Frac"""
        f = Frac(1, 2)
        result = 3 + f
        self.assert_equal(result.n, 7)
        self.assert_equal(result.d, 2)
    
    @test
    def test_add_zero(self):
        """测试加零"""
        f = Frac(1, 2)
        result = f + 0
        self.assert_equal(result.n, 1)
        self.assert_equal(result.d, 2)
    
    # ==================== 减法 ====================
    
    @test
    def test_sub_two_fracs(self):
        """测试两个分数相减"""
        f1 = Frac(1, 2)
        f2 = Frac(1, 3)
        result = f1 - f2
        self.assert_equal(result.n, 1)
        self.assert_equal(result.d, 6)
    
    @test
    def test_sub_with_int(self):
        """测试分数 - 整数"""
        f = Frac(7, 2)
        result = f - 3
        self.assert_equal(result.n, 1)
        self.assert_equal(result.d, 2)
    
    @test
    def test_rsub(self):
        """测试右减法：int - Frac"""
        f = Frac(1, 2)
        result = 3 - f
        self.assert_equal(result.n, 5)
        self.assert_equal(result.d, 2)
    
    @test
    def test_sub_negative_result(self):
        """测试结果为负数"""
        f1 = Frac(1, 3)
        f2 = Frac(1, 2)
        result = f1 - f2
        self.assert_equal(result.n, -1)
        self.assert_equal(result.d, 6)
    
    # ==================== 乘法 ====================
    
    @test
    def test_mul_two_fracs(self):
        """测试两个分数相乘"""
        f1 = Frac(2, 3)
        f2 = Frac(3, 4)
        result = f1 * f2
        self.assert_equal(result.n, 1)
        self.assert_equal(result.d, 2)
    
    @test
    def test_mul_with_int(self):
        """测试分数 * 整数"""
        f = Frac(1, 3)
        result = f * 6
        self.assert_equal(result.n, 2)
        self.assert_equal(result.d, 1)
    
    @test
    def test_rmul(self):
        """测试右乘法：int * Frac"""
        f = Frac(1, 3)
        result = 6 * f
        self.assert_equal(result.n, 2)
        self.assert_equal(result.d, 1)
    
    @test
    def test_mul_zero(self):
        """测试乘零"""
        f = Frac(3, 4)
        result = f * 0
        self.assert_equal(result.n, 0)
        self.assert_equal(result.d, 1)
    
    # ==================== 除法 ====================
    
    @test
    def test_div_two_fracs(self):
        """测试两个分数相除"""
        f1 = Frac(1, 2)
        f2 = Frac(3, 4)
        result = f1 / f2
        self.assert_equal(result.n, 2)
        self.assert_equal(result.d, 3)
    
    @test
    def test_div_with_int(self):
        """测试分数 / 整数"""
        f = Frac(1, 2)
        result = f / 3
        self.assert_equal(result.n, 1)
        self.assert_equal(result.d, 6)
    
    @test
    def test_rdiv(self):
        """测试右除法：int / Frac"""
        f = Frac(1, 2)
        result = 3 / f
        self.assert_equal(result.n, 6)
        self.assert_equal(result.d, 1)
    
    @test
    def test_div_zero(self):
        """测试除以零"""
        f = Frac(1, 2)
        with self.assert_raises(ZeroDivisionError):
            f / 0
    
    @test
    def test_invert(self):
        """测试倒数 ~f"""
        f = Frac(2, 3)
        result = ~f
        self.assert_equal(result.n, 3)
        self.assert_equal(result.d, 2)
    
    # ==================== 幂运算 ====================
    
    @test
    def test_pow_positive_int(self):
        """测试正整数指数"""
        f = Frac(2, 3)
        result = f ** 2
        self.assert_equal(result.n, 4)
        self.assert_equal(result.d, 9)
    
    @test
    def test_pow_negative_int(self):
        """测试负整数指数"""
        f = Frac(2, 3)
        result = f ** (-2)
        self.assert_equal(result.n, 9)
        self.assert_equal(result.d, 4)
    
    @test
    def test_pow_zero(self):
        """测试指数为 0"""
        f = Frac(2, 3)
        result = f ** 0
        self.assert_equal(result.n, 1)
        self.assert_equal(result.d, 1)
    
    @test
    def test_pow_fractional_raises_warning(self):
        """测试分数指数（无理数）应抛出警告或返回近似"""
        f = Frac(4, 9)
        # 4/9 的 1/2 次方 = 2/3（有理数）
        result = f ** Frac(1, 2)
        self.assert_equal(result.n, 2)
        self.assert_equal(result.d, 3)
    
    @test
    def test_rpow(self):
        """测试右幂：int ** Frac"""
        # 8^(1/3) = 2
        result = 8 ** Frac(1, 3)
        self.assert_equal(result.n, 2)
        self.assert_equal(result.d, 1)
    
    # ==================== 比较 ====================
    
    @test
    def test_eq(self):
        """测试相等"""
        f1 = Frac(1, 2)
        f2 = Frac(2, 4)
        self.assert_true(f1 == f2)
        self.assert_false(f1 == Frac(1, 3))
    
    @test
    def test_eq_with_int(self):
        """测试 Frac == int"""
        f = Frac(4, 2)
        self.assert_true(f == 2)
        self.assert_false(f == 3)
    
    @test
    def test_lt(self):
        """测试小于"""
        f1 = Frac(1, 3)
        f2 = Frac(1, 2)
        self.assert_true(f1 < f2)
        self.assert_false(f2 < f1)
    
    @test
    def test_lt_with_int(self):
        """测试 Frac < int"""
        f = Frac(3, 2)
        self.assert_true(f < 2)
        self.assert_false(f < 1)
    
    @test
    def test_le(self):
        """测试小于等于"""
        f1 = Frac(1, 2)
        f2 = Frac(2, 4)
        self.assert_true(f1 <= f2)
        self.assert_true(f1 <= Frac(3, 4))
    
    @test
    def test_gt(self):
        """测试大于"""
        f1 = Frac(1, 2)
        f2 = Frac(1, 3)
        self.assert_true(f1 > f2)
        self.assert_false(f2 > f1)
    
    @test
    def test_ge(self):
        """测试大于等于"""
        f1 = Frac(1, 2)
        f2 = Frac(2, 4)
        self.assert_true(f1 >= f2)
        self.assert_true(f1 >= Frac(1, 3))
    
    # ==================== 取负和绝对值 ====================
    
    @test
    def test_neg(self):
        """测试取负"""
        f = Frac(1, 2)
        result = -f
        self.assert_equal(result.n, -1)
        self.assert_equal(result.d, 2)
    
    @test
    def test_pos(self):
        """测试取正"""
        f = Frac(1, 2)
        result = +f
        self.assert_equal(result.n, 1)
        self.assert_equal(result.d, 2)
    
    @test
    def test_abs(self):
        """测试绝对值"""
        f = Frac(-1, 2)
        result = abs(f)
        self.assert_equal(result.n, 1)
        self.assert_equal(result.d, 2)
    
    # ==================== 类型转换 ====================
    
    @test
    def test_float_conversion(self):
        """测试转 float"""
        f = Frac(1, 2)
        self.assert_almost_equal(float(f), 0.5, places=10)
    
    @test
    def test_int_conversion(self):
        """测试转 int（向下取整）"""
        f = Frac(5, 2)
        self.assert_equal(int(f), 2)
        f = Frac(-5, 2)
        self.assert_equal(int(f), -3)  # Python 的 int 向下取整
    
    # ==================== 格式化 ====================
    
    @test
    def test_format_percent(self):
        """测试百分数格式"""
        f = Frac(1, 4)
        self.assert_equal(format(f, '%'), "25%")
        self.assert_equal(format(f, '.1%'), "25.0%")
    
    @test
    def test_format_latex(self):
        """测试 LaTeX 格式"""
        f = Frac(1, 2)
        self.assert_equal(format(f, 'l'), "\\frac{1}{2}")
        f = Frac(5)
        self.assert_equal(format(f, 'l'), "5")
    
    @test
    def test_format_mixed(self):
        """测试带分数格式"""
        f = Frac(7, 2)
        self.assert_equal(format(f, 'm'), "3 + 1/2")
        f = Frac(-7, 2)
        self.assert_equal(format(f, 'm'), "-4 + 1/2")
    
    @test
    def test_format_frac(self):
        """测试分数格式"""
        f = Frac(1, 2)
        self.assert_equal(format(f, '/'), "1/2")
    
    @test
    def test_format_float(self):
        """测试浮点数格式"""
        f = Frac(1, 3)
        self.assert_equal(format(f, '.3f'), "0.333")
    
    # ==================== 哈希 ====================
    
    @test
    def test_hash(self):
        """测试 Frac 可哈希"""
        f = Frac(1, 2)
        d = {f: "half"}
        self.assert_equal(d[f], "half")
        # 相等的分数应该有相同的哈希
        f2 = Frac(2, 4)
        self.assert_equal(hash(f), hash(f2))
    
    # ==================== 取模 ====================
    
    @test
    def test_mod(self):
        """测试取模"""
        f1 = Frac(7, 2)
        f2 = Frac(3, 2)
        result = f1 % f2
        # 7/2 % 3/2 = 1/2（因为 3/2 * 2 = 3，余 1/2）
        self.assert_equal(result.n, 1)
        self.assert_equal(result.d, 2)
    
    @test
    def test_mod_with_int(self):
        """测试 Frac % int"""
        f = Frac(7, 2)
        result = f % 2
        self.assert_equal(result.n, 3)
        self.assert_equal(result.d, 2)  # 7/2 % 2 = 3/2
    
    @test
    def test_rmod(self):
        """测试右取模：int % Frac"""
        f = Frac(3, 2)
        result = 4 % f
        # 4 % 3/2 = 1/2（因为 3/2 * 2 = 3，余 1/2）
        self.assert_equal(result.n, 1)
        self.assert_equal(result.d, 1)
    
    # ==================== 大数处理 ====================
    
    @test
    def test_large_numbers(self):
        """测试大整数分数"""
        f = Frac(10**100, 10**50)
        # 应该能化简
        self.assert_equal(f.n, 10**50)
        self.assert_equal(f.d, 1)
    
    @test
    def test_scientific_notation_str(self):
        """测试超大数字自动转科学计数法"""
        f = Frac(10**1000, 1)
        s = str(f)
        # 应该包含 'e'
        self.assert_true('e' in s or 'E' in s)
    
    # ==================== 实际场景 ====================
    
    @test
    def test_fraction_calculation(self):
        """测试混合运算：1/2 + 1/3 * 1/4"""
        f1 = Frac(1, 2)
        f2 = Frac(1, 3)
        f3 = Frac(1, 4)
        result = f1 + f2 * f3
        # 1/2 + 1/12 = 6/12 + 1/12 = 7/12
        self.assert_equal(result.n, 7)
        self.assert_equal(result.d, 12)


if __name__ == "__main__":
    runner = TestRunner()
    runner.run_all()