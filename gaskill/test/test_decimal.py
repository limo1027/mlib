from gaskill import decimal
from gaskill import TestCase, TestRunner, test


class DecimalTester(TestCase):

    # ==================== 创建和表示 ====================

    @test
    def test_creation_from_int(self):
        """测试从整数创建"""
        d = decimal.Decimal(42)
        self.assert_equal(d.value, 42)
        self.assert_equal(d.fr_len, 0)
        self.assert_equal(str(d), 'Decimal("42")')

    @test
    def test_creation_from_float(self):
        """测试从浮点数创建"""
        d = decimal.Decimal(3.14)
        self.assert_almost_equal(float(d), 3.14, places=10)
        self.assert_equal(d.value, 314)
        self.assert_equal(d.fr_len, 2)

    @test
    def test_creation_from_string(self):
        """测试从字符串创建"""
        d = decimal.Decimal("0.00123")
        self.assert_equal(d.value, 123)
        self.assert_equal(d.fr_len, 5)
        self.assert_almost_equal(float(d), 0.00123, places=10)

    @test
    def test_creation_from_decimal(self):
        """测试从 Decimal 创建 Decimal"""
        d1 = decimal.Decimal(3.14)
        d2 = decimal.Decimal(d1)
        self.assert_equal(d1.value, d2.value)
        self.assert_equal(d1.fr_len, d2.fr_len)

    @test
    def test_simplify_removes_trailing_zeros(self):
        """测试化简：去掉末尾的零"""
        d = decimal.Decimal(1.50)
        self.assert_equal(d.value, 15)
        self.assert_equal(d.fr_len, 1)
        self.assert_equal(str(d), 'Decimal("1.5")')

    @test
    def test_simplify_does_not_change_value(self):
        """测试化简不改变数值"""
        d1 = decimal.Decimal(1.50)
        d2 = decimal.Decimal(1.5)
        self.assert_true(d1 == d2)

    @test
    def test_repr_zero(self):
        """测试零的表示"""
        d = decimal.Decimal(0)
        self.assert_equal(str(d), 'Decimal("0")')
        self.assert_equal(d.value, 0)
        self.assert_equal(d.fr_len, 0)

    @test
    def test_repr_small_number(self):
        """测试小数的表示（小于 1）"""
        d = decimal.Decimal(0.00123)
        self.assert_equal(str(d), 'Decimal("0.00123")')

    @test
    def test_repr_large_number(self):
        """测试大数的表示"""
        d = decimal.Decimal(12345.6789)
        self.assert_equal(str(d), 'Decimal("12345.6789")')

    # ==================== 加法 ====================

    @test
    def test_add_two_decimals(self):
        """测试两个 Decimal 相加"""
        d1 = decimal.Decimal(1.23)
        d2 = decimal.Decimal(4.56)
        result = d1 + d2
        self.assert_almost_equal(float(result), 5.79, places=10)

    @test
    def test_add_with_int(self):
        """测试 Decimal + int"""
        d = decimal.Decimal(1.23)
        result = d + 5
        self.assert_almost_equal(float(result), 6.23, places=10)

    @test
    def test_add_with_float(self):
        """测试 Decimal + float"""
        d = decimal.Decimal(1.23)
        result = d + 4.56
        self.assert_almost_equal(float(result), 5.79, places=10)

    @test
    def test_add_zero(self):
        """测试加零"""
        d1 = decimal.Decimal(1.23)
        d2 = decimal.Decimal(0)
        result = d1 + d2
        self.assert_equal(result.value, d1.value)
        self.assert_equal(result.fr_len, d1.fr_len)

    @test
    def test_add_different_precision(self):
        """测试不同精度的小数相加"""
        d1 = decimal.Decimal(1.2)
        d2 = decimal.Decimal(3.456)
        result = d1 + d2
        self.assert_almost_equal(float(result), 4.656, places=10)
        self.assert_equal(result.fr_len, 3)

    # ==================== 减法 ====================

    @test
    def test_sub_two_decimals(self):
        """测试两个 Decimal 相减"""
        d1 = decimal.Decimal(5.67)
        d2 = decimal.Decimal(1.23)
        result = d1 - d2
        self.assert_almost_equal(float(result), 4.44, places=10)

    @test
    def test_sub_negative_result(self):
        """测试结果为负数"""
        d1 = decimal.Decimal(1.23)
        d2 = decimal.Decimal(5.67)
        result = d1 - d2
        self.assert_almost_equal(float(result), -4.44, places=10)
        self.assert_true(result.value < 0)

    @test
    def test_rsub(self):
        """测试右减法：int - Decimal"""
        d = decimal.Decimal(1.23)
        result = 5 - d
        self.assert_almost_equal(float(result), 3.77, places=10)

    # ==================== 乘法 ====================

    @test
    def test_mul_two_decimals(self):
        """测试两个 Decimal 相乘"""
        d1 = decimal.Decimal(1.23)
        d2 = decimal.Decimal(4.56)
        result = d1 * d2
        self.assert_almost_equal(float(result), 5.6088, places=10)
        self.assert_equal(result.fr_len, 4)

    @test
    def test_mul_with_int(self):
        """测试 Decimal * int"""
        d = decimal.Decimal(1.23)
        result = d * 3
        self.assert_almost_equal(float(result), 3.69, places=10)

    @test
    def test_mul_with_float(self):
        """测试 Decimal * float"""
        d = decimal.Decimal(1.23)
        result = d * 4.56
        self.assert_almost_equal(float(result), 5.6088, places=10)

    @test
    def test_mul_zero(self):
        """测试乘零"""
        d = decimal.Decimal(3.14)
        result = d * 0
        self.assert_almost_equal(float(result), 0.0, places=10)
        self.assert_equal(result.value, 0)

    @test
    def test_rmul(self):
        """测试右乘法：int * Decimal"""
        d = decimal.Decimal(1.23)
        result = 3 * d
        self.assert_almost_equal(float(result), 3.69, places=10)

    # ==================== 除法 ====================

    @test
    def test_div_two_decimals(self):
        """测试两个 Decimal 相除"""
        d1 = decimal.Decimal(1)
        d2 = decimal.Decimal(3)
        result = d1 / d2
        self.assert_almost_equal(float(result), 1/3, places=10)

    @test
    def test_div_precision(self):
        """测试除法的精度（prec=50）"""
        d1 = decimal.Decimal(1)
        d2 = decimal.Decimal(7)
        result = d1 / d2
        self.assert_almost_equal(float(result), 1/7, places=10)
        self.assert_equal(result.fr_len, 50)

    @test
    def test_div_returns_decimal(self):
        """测试除法返回 Decimal"""
        d1 = decimal.Decimal(1)
        d2 = decimal.Decimal(3)
        result = d1 / d2
        self.assert_isinstance(result, decimal.Decimal)

    @test
    def test_rdiv(self):
        """测试右除法：int / Decimal"""
        d = decimal.Decimal(2)
        result = 1 / d
        self.assert_almost_equal(float(result), 0.5, places=10)

    # ==================== 比较 ====================

    @test
    def test_eq_same_value(self):
        """测试相等：相同值"""
        d1 = decimal.Decimal(1.23)
        d2 = decimal.Decimal(1.23)
        self.assert_true(d1 == d2)

    @test
    def test_eq_different_precision(self):
        """测试相等：不同精度但相同数值"""
        d1 = decimal.Decimal(1.5)
        d2 = decimal.Decimal(1.50)
        self.assert_true(d1 == d2)

    @test
    def test_eq_different_value(self):
        """测试相等：不同值"""
        d1 = decimal.Decimal(1.23)
        d2 = decimal.Decimal(4.56)
        self.assert_false(d1 == d2)

    @test
    def test_eq_with_int(self):
        """测试 Decimal == int"""
        d = decimal.Decimal(5)
        self.assert_true(d == 5)
        self.assert_false(d == 6)

    @test
    def test_lt(self):
        """测试小于"""
        d1 = decimal.Decimal(1.23)
        d2 = decimal.Decimal(4.56)
        self.assert_true(d1 < d2)
        self.assert_false(d2 < d1)

    @test
    def test_lt_different_precision(self):
        """测试小于：不同精度"""
        d1 = decimal.Decimal(1.2)
        d2 = decimal.Decimal(1.23)
        self.assert_true(d1 < d2)

    @test
    def test_lt_cross_integer_boundary(self):
        """测试小于：跨整数边界（之前 bug 的测试）"""
        d1 = decimal.Decimal(0.9)
        d2 = decimal.Decimal(1.0)
        self.assert_true(d1 < d2)
        self.assert_false(d2 < d1)

    @test
    def test_le(self):
        """测试小于等于"""
        d1 = decimal.Decimal(1.23)
        d2 = decimal.Decimal(1.23)
        self.assert_true(d1 <= d2)
        self.assert_true(d1 <= decimal.Decimal(4.56))

    @test
    def test_gt(self):
        """测试大于"""
        d1 = decimal.Decimal(4.56)
        d2 = decimal.Decimal(1.23)
        self.assert_true(d1 > d2)
        self.assert_false(d2 > d1)

    @test
    def test_gt_cross_integer_boundary(self):
        """测试大于：跨整数边界"""
        d1 = decimal.Decimal(1.0)
        d2 = decimal.Decimal(0.9)
        self.assert_true(d1 > d2)

    @test
    def test_compare_with_int(self):
        """测试与 int 比较"""
        d = decimal.Decimal(3.14)
        self.assert_true(d < 4)
        self.assert_true(d > 3)
        self.assert_false(d == 3)

    # ==================== 取负 ====================

    @test
    def test_neg(self):
        """测试取负"""
        d = decimal.Decimal(3.14)
        neg = -d
        self.assert_almost_equal(float(neg), -3.14, places=10)
        self.assert_true(neg.value < 0)

    @test
    def test_neg_zero(self):
        """测试负零"""
        d = decimal.Decimal(0)
        neg = -d
        self.assert_almost_equal(float(neg), 0.0, places=10)
        self.assert_equal(neg.value, 0)

    # ==================== 类型转换 ====================

    @test
    def test_float_conversion(self):
        """测试转 float"""
        d = decimal.Decimal(3.14)
        self.assert_almost_equal(float(d), 3.14, places=10)

    @test
    def test_float_conversion_high_precision(self):
        """测试高精度转 float"""
        d = decimal.Decimal(1) / decimal.Decimal(3)
        self.assert_almost_equal(float(d), 1/3, places=10)

    # ==================== 幂运算 ====================

    @test
    def test_pow_zero_exponent(self):
        """测试指数为 0：任何数的 0 次方 = 1"""
        d = decimal.Decimal(3.14)
        result = d ** 0
        self.assert_equal(result.value, 1)
        self.assert_equal(result.fr_len, 0)

        result = d ** decimal.Decimal(0)
        self.assert_equal(result.value, 1)
        self.assert_equal(result.fr_len, 0)

    @test
    def test_pow_integer_exponent_positive(self):
        """测试正整数指数"""
        d = decimal.Decimal(2)
        result = d ** 3
        self.assert_almost_equal(float(result), 8.0, places=10)

        d = decimal.Decimal(1.5)
        result = d ** 3
        self.assert_almost_equal(float(result), 3.375, places=10)

    @test
    def test_pow_integer_exponent_negative(self):
        """测试负整数指数"""
        d = decimal.Decimal(2)
        result = d ** (-3)
        self.assert_almost_equal(float(result), 0.125, places=10)

        d = decimal.Decimal(1.5)
        result = d ** (-2)
        self.assert_almost_equal(float(result), 1/2.25, places=10)

    @test
    def test_pow_large_integer_exponent(self):
        """测试大整数指数（快速幂验证）"""
        d = decimal.Decimal(2)
        result = d ** 10
        self.assert_equal(result.value, 1024)
        self.assert_equal(result.fr_len, 0)

    @test
    def test_pow_fractional_exponent_square(self):
        """测试分数指数：开平方"""
        d = decimal.Decimal(4)
        result = d ** decimal.Decimal(0.5)
        self.assert_almost_equal(float(result), 2.0, places=10)

    @test
    def test_pow_fractional_exponent_cube(self):
        """测试分数指数：开立方"""
        d = decimal.Decimal(8)
        result = d ** decimal.Decimal(1/3)
        self.assert_almost_equal(float(result), 2.0, places=8)

    @test
    def test_pow_fractional_exponent_complex(self):
        """测试分数指数：2^(3/4)"""
        d = decimal.Decimal(2)
        result = d ** decimal.Decimal(0.75)
        # 2^(3/4) = (2^3)^(1/4) = 8^(1/4) ≈ 1.68179
        self.assert_almost_equal(float(result), 1.681792830507429, places=8)

    @test
    def test_pow_negative_fractional_exponent(self):
        """测试负分数指数：2^(-0.5) = 1/√2"""
        d = decimal.Decimal(2)
        result = d ** decimal.Decimal(-0.5)
        self.assert_almost_equal(float(result), 1 / 2**0.5, places=8)

    @test
    def test_pow_chain(self):
        """测试连续幂运算"""
        d = decimal.Decimal(2)
        result = (d ** 2) ** 3  # (2^2)^3 = 4^3 = 64
        self.assert_almost_equal(float(result), 64.0, places=10)

    @test
    def test_pow_large_base(self):
        """测试大底数"""
        d = decimal.Decimal(100)
        result = d ** decimal.Decimal(0.5)
        self.assert_almost_equal(float(result), 10.0, places=10)

    # ==================== 实际场景 ====================

    @test
    def test_interest_calculation(self):
        """测试复利计算"""
        principal = decimal.Decimal(1000)
        rate = decimal.Decimal(0.05)
        years = 3
        result = principal * ((decimal.Decimal(1) + rate) ** years)
        self.assert_almost_equal(float(result), 1157.625, places=6)

    @test
    def test_division_chain(self):
        """测试连续除法"""
        d = decimal.Decimal(1)
        for _ in range(3):
            d = d / decimal.Decimal(2)
        self.assert_almost_equal(float(d), 0.125, places=10)

    @test
    def test_pow_real_world(self):
        """测试实际场景：1.05^10"""
        d = decimal.Decimal(1.05)
        result = d ** 10
        # 1.05^10 = 1.628894626777442...
        self.assert_almost_equal(float(result), 1.628894626777442, places=8)

        # ==================== 取模运算 ====================

    @test
    def test_mod_int_basic(self):
        """测试基本整数取模：10 % 3 = 1"""
        d1 = decimal.Decimal(10)
        d2 = decimal.Decimal(3)
        result = d1 % d2
        self.assert_equal(result.value, 1)
        self.assert_equal(result.fr_len, 0)
        self.assert_almost_equal(float(result), 1.0, places=10)

    @test
    def test_mod_int_20_mod_6(self):
        """测试 20 % 6 = 2"""
        d1 = decimal.Decimal(20)
        d2 = decimal.Decimal(6)
        result = d1 % d2
        self.assert_equal(result.value, 2)
        self.assert_equal(result.fr_len, 0)

    @test
    def test_mod_int_100_mod_10(self):
        """测试 100 % 10 = 0（整除）"""
        d1 = decimal.Decimal(100)
        d2 = decimal.Decimal(10)
        result = d1 % d2
        self.assert_equal(result.value, 0)
        self.assert_equal(result.fr_len, 0)

    @test
    def test_mod_int_1_mod_10(self):
        """测试被除数小于除数：1 % 10 = 1"""
        d1 = decimal.Decimal(1)
        d2 = decimal.Decimal(10)
        result = d1 % d2
        self.assert_equal(result.value, 1)
        self.assert_equal(result.fr_len, 0)

    @test
    def test_mod_int_zero_dividend(self):
        """测试被除数为 0：0 % 5 = 0"""
        d1 = decimal.Decimal(0)
        d2 = decimal.Decimal(5)
        result = d1 % d2
        self.assert_equal(result.value, 0)
        self.assert_equal(result.fr_len, 0)

    @test
    def test_mod_negative_10_mod_3(self):
        """测试负数取模：-10 % 3 = 2"""
        d1 = decimal.Decimal(-10)
        d2 = decimal.Decimal(3)
        result = d1 % d2
        self.assert_equal(result.value, 2)
        self.assert_equal(result.fr_len, 0)
        self.assert_true(result.value >= 0)

    @test
    def test_mod_negative_10_mod_minus_3(self):
        """测试 10 % -3 = -2"""
        d1 = decimal.Decimal(10)
        d2 = decimal.Decimal(-3)
        result = d1 % d2
        self.assert_equal(result.value, -2)
        self.assert_equal(result.fr_len, 0)
        self.assert_true(result.value <= 0)

    @test
    def test_mod_negative_both_negative(self):
        """测试 -10 % -3 = -1"""
        d1 = decimal.Decimal(-10)
        d2 = decimal.Decimal(-3)
        result = d1 % d2
        self.assert_equal(result.value, -1)
        self.assert_equal(result.fr_len, 0)

    @test
    def test_mod_float_7_mod_0_3(self):
        """测试 7 % 0.3 = 0.1（精确）"""
        d1 = decimal.Decimal(7)
        d2 = decimal.Decimal(0.3)
        result = d1 % d2
        self.assert_equal(result.value, 1)
        self.assert_equal(result.fr_len, 1)
        self.assert_almost_equal(float(result), 0.1, places=10)

    @test
    def test_mod_float_5_mod_1_2(self):
        """测试 5 % 1.2 = 0.2"""
        d1 = decimal.Decimal(5)
        d2 = decimal.Decimal(1.2)
        result = d1 % d2
        self.assert_equal(result.value, 2)
        self.assert_equal(result.fr_len, 1)
        self.assert_almost_equal(float(result), 0.2, places=10)

    @test
    def test_mod_float_3_5_mod_1_5(self):
        """测试 3.5 % 1.5 = 0.5"""
        d1 = decimal.Decimal(3.5)
        d2 = decimal.Decimal(1.5)
        result = d1 % d2
        self.assert_equal(result.value, 5)
        self.assert_equal(result.fr_len, 1)
        self.assert_almost_equal(float(result), 0.5, places=10)

    @test
    def test_mod_float_2_0_mod_0_5(self):
        """测试 2.0 % 0.5 = 0"""
        d1 = decimal.Decimal(2.0)
        d2 = decimal.Decimal(0.5)
        result = d1 % d2
        self.assert_equal(result.value, 0)
        self.assert_equal(result.fr_len, 0)

    @test
    def test_mod_float_10_123_mod_3_456(self):
        """测试 10.123 % 3.456 = 3.211"""
        d1 = decimal.Decimal(10.123)
        d2 = decimal.Decimal(3.456)
        result = d1 % d2
        self.assert_equal(result.value, 3211)
        self.assert_equal(result.fr_len, 3)
        self.assert_almost_equal(float(result), 3.211, places=10)

    @test
    def test_mod_float_negative_7_mod_0_3(self):
        """测试 -7 % 0.3 = 0.2"""
        d1 = decimal.Decimal(-7)
        d2 = decimal.Decimal(0.3)
        result = d1 % d2
        self.assert_equal(result.value, 2)
        self.assert_equal(result.fr_len, 1)
        self.assert_almost_equal(float(result), 0.2, places=10)

    @test
    def test_mod_float_7_mod_negative_0_3(self):
        """测试 7 % -0.3 = -0.2"""
        d1 = decimal.Decimal(7)
        d2 = decimal.Decimal(-0.3)
        result = d1 % d2
        self.assert_equal(result.value, -2)
        self.assert_equal(result.fr_len, 1)
        self.assert_almost_equal(float(result), -0.2, places=10)

    @test
    def test_mod_float_both_negative_float(self):
        """测试 -7 % -0.3 = -0.1"""
        d1 = decimal.Decimal(-7)
        d2 = decimal.Decimal(-0.3)
        result = d1 % d2
        self.assert_equal(result.value, -1)
        self.assert_equal(result.fr_len, 1)
        self.assert_almost_equal(float(result), -0.1, places=10)

    @test
    def test_mod_verify_formula(self):
        """验证取模公式：a = (a//b)*b + (a%b)"""
        test_cases = [
            (10, 3),
            (-10, 3),
            (10, -3),
            (-10, -3),
            (7, 0.3),
            (-7, 0.3),
            (3.14159, 1.414),
        ]
        for a, b in test_cases:
            d1 = decimal.Decimal(a)
            d2 = decimal.Decimal(b)
            quotient = d1 // d2
            remainder = d1 % d2
            check = quotient * d2 + remainder
            self.assert_equal(d1, check)

    @test
    def test_mod_compare_float_vs_decimal(self):
        """对比浮点数和 Decimal 的取模精度"""
        decimal_result = decimal.Decimal(7) % decimal.Decimal(0.3)
        float_result = 7 % 0.3

        self.assert_almost_equal(float(decimal_result), 0.1, places=10)
        self.assert_not_equal(float(decimal_result), float_result)
        self.assert_almost_equal(float_result, 0.1, places=1)

    @test
    def test_mod_batch(self):
        """批量取模测试"""
        test_cases = [
            ("10", "3", 1, 0),
            ("7", "0.3", 1, 1),
            ("-7", "0.3", 2, 1),
            ("7", "-0.3", -2, 1),
            ("-7", "-0.3", -1, 1),
            ("3.14159", "1.414", 31359, 5),
            ("100.123456", "0.0001", 56, 6),
        ]
        for a_str, b_str, expected_value, expected_fr_len in test_cases:
            d1 = decimal.Decimal(a_str)
            d2 = decimal.Decimal(b_str)
            result = d1 % d2
            self.assert_equal(result.value, expected_value)
            self.assert_equal(result.fr_len, expected_fr_len)

    @test
    def test_sin_precision(self):
        """验证 sin 在关键点上的 Decimal 精度"""
        decimal.prec = 60
        pi = decimal.dec_pi()

        # sin(pi/2) = 1: 直接用 Decimal 比较
        self.assert_almost_equal(
            decimal.dec_sin(pi / 2), decimal.Decimal(1), places=40)

        # sin(pi) ≈ 0: 比较与 0 的差值
        self.assert_almost_equal(
            decimal.dec_sin(pi), decimal.Decimal(0), places=40)

    @test
    def test_sin_symmetry(self):
        """验证 sin 的对称性：比较两个 Decimal 的差值"""
        x = decimal.Decimal("1.23456789")
        two_pi = 2 * decimal.dec_pi()
        diff = decimal.dec_sin(x) - decimal.dec_sin(x + two_pi)
        self.assert_true(abs(diff) < decimal.Decimal(10) ** (-45))


if __name__ == "__main__":
    runner = TestRunner()
    runner.run_all()
