from gaskill import radical
from gaskill import TestCase, TestRunner, test


class RadicalTester(TestCase):

    # ==================== 创建和化简 ====================

    @test
    def test_simplify_square(self):
        """√4 = 2"""
        r = radical.Radical(2, 4)
        self.assert_almost_equal(r.approx(), 2.0, places=10)

    @test
    def test_simplify_sqrt12(self):
        """√12 = 2√3，数值上约等于 3.464101615"""
        r = radical.Radical(2, 12)
        self.assert_almost_equal(r.approx(), 3.464101615, places=8)

    @test
    def test_simplify_cube8(self):
        """³√8 = 2"""
        r = radical.Radical(3, 8)
        self.assert_almost_equal(r.approx(), 2.0, places=10)

    @test
    def test_simplify_sqrt_frac(self):
        """√(1/4) = 1/2"""
        from gaskill import Frac
        r = radical.Radical(2, Frac(1, 4))
        self.assert_almost_equal(r.approx(), 0.5, places=10)

    @test
    def test_simplify_zero(self):
        """√0 = 0"""
        r = radical.Radical(2, 0)
        self.assert_almost_equal(r.approx(), 0.0, places=10)

    @test
    def test_simplify_one(self):
        """√1 = 1"""
        r = radical.Radical(2, 1)
        self.assert_almost_equal(r.approx(), 1.0, places=10)

    # ==================== 乘法 ====================

    @test
    def test_mul_same_index(self):
        """√2 * √3 = √6 ≈ 2.449489743"""
        r1 = radical.Radical(2, 2)
        r2 = radical.Radical(2, 3)
        result = r1 * r2
        self.assert_almost_equal(result.approx(), 2.449489743, places=8)

    @test
    def test_mul_simplify(self):
        """√8 * √2 = √16 = 4"""
        r1 = radical.Radical(2, 8)
        r2 = radical.Radical(2, 2)
        result = r1 * r2
        self.assert_almost_equal(result.approx(), 4.0, places=10)

    @test
    def test_mul_with_coeff(self):
        """(2√3) * (3√5) = 6√15 ≈ 23.23790008"""
        r1 = radical.Radical(2, 3, 2)
        r2 = radical.Radical(2, 5, 3)
        result = r1 * r2
        self.assert_almost_equal(result.approx(), 23.23790008, places=8)

    @test
    def test_mul_different_index(self):
        """√2 * ³√3 ≈ 1.56508458（数学上等于 ⁶√72）"""
        r1 = radical.Radical(2, 2)
        r2 = radical.Radical(3, 3)
        result = r1 * r2
        self.assert_almost_equal(result.approx(), 2.0396489026555056, places=8)

    @test
    def test_mul_by_int(self):
        """3 * √2 = 3√2 ≈ 4.242640687"""
        r = radical.Radical(2, 2)
        result = r * 3
        self.assert_almost_equal(result.approx(), 4.242640687, places=8)

    @test
    def test_mul_by_zero(self):
        """√2 * 0 = 0"""
        r = radical.Radical(2, 2)
        result = r * 0
        self.assert_almost_equal(result.approx(), 0.0, places=10)

    # ==================== 除法 ====================

    @test
    def test_div_same_index(self):
        """√6 / √2 = √3 ≈ 1.732050808"""
        r1 = radical.Radical(2, 6)
        r2 = radical.Radical(2, 2)
        result = r1 / r2
        self.assert_almost_equal(result.approx(), 1.732050808, places=8)

    @test
    def test_div_simplify(self):
        """√12 / √3 = √4 = 2"""
        r1 = radical.Radical(2, 12)
        r2 = radical.Radical(2, 3)
        result = r1 / r2
        self.assert_almost_equal(result.approx(), 2.0, places=10)

    @test
    def test_div_with_coeff(self):
        """(6√15) / (3√5) = 2√3 ≈ 3.464101615"""
        r1 = radical.Radical(2, 15, 6)
        r2 = radical.Radical(2, 5, 3)
        result = r1 / r2
        self.assert_almost_equal(result.approx(), 3.464101615, places=8)

    @test
    def test_div_rationalize(self):
        """1 / √2 = √2/2 ≈ 0.707106781"""
        r1 = radical.Radical(1, 1, 1)
        r2 = radical.Radical(2, 2)
        result = r1 / r2
        self.assert_almost_equal(result.approx(), 0.707106781, places=8)

    @test
    def test_div_by_zero(self):
        """√2 / 0 应该报错"""
        r = radical.Radical(2, 2)
        with self.assert_raises(ZeroDivisionError):
            r / 0

    # ==================== 加法和减法 ====================

    @test
    def test_add_like_terms(self):
        """2√3 + 3√3 = 5√3 ≈ 8.660254038"""
        r1 = radical.Radical(2, 3, 2)
        r2 = radical.Radical(2, 3, 3)
        result = r1 + r2
        self.assert_almost_equal(result.approx(), 8.660254038, places=8)

    @test
    def test_add_unlike_terms(self):
        """√2 + √3 ≈ 3.14626437（保持为和式）"""
        r1 = radical.Radical(2, 2)
        r2 = radical.Radical(2, 3)
        result = r1 + r2
        self.assert_almost_equal(result.approx(), 3.14626437, places=8)

    @test
    def test_add_with_int(self):
        """√2 + 3 ≈ 4.414213562"""
        r = radical.Radical(2, 2)
        result = r + 3
        self.assert_almost_equal(result.approx(), 4.414213562, places=8)

    @test
    def test_sub_like_terms(self):
        """5√3 - 2√3 = 3√3 ≈ 5.196152423"""
        r1 = radical.Radical(2, 3, 5)
        r2 = radical.Radical(2, 3, 2)
        result = r1 - r2
        self.assert_almost_equal(result.approx(), 5.196152423, places=8)

    @test
    def test_sub_unlike_terms(self):
        """√3 - √2 ≈ 0.317837245"""
        r1 = radical.Radical(2, 3)
        r2 = radical.Radical(2, 2)
        result = r1 - r2
        self.assert_almost_equal(result.approx(), 0.317837245, places=8)

    # ==================== 幂运算 ====================

    @test
    def test_pow_square(self):
        """(√2)² = 2"""
        r = radical.Radical(2, 2)
        result = r ** 2
        self.assert_almost_equal(result.approx(), 2.0, places=10)

    @test
    def test_pow_cube(self):
        """(√2)³ = 2√2 ≈ 2.828427125"""
        r = radical.Radical(2, 2)
        result = r ** 3
        self.assert_almost_equal(result.approx(), 2.828427125, places=8)

    @test
    def test_pow_zero(self):
        """任何数的 0 次方 = 1"""
        r = radical.Radical(2, 2)
        result = r ** 0
        self.assert_almost_equal(result.approx(), 1.0, places=10)

    # ==================== 近似值 ====================

    @test
    def test_approx_sqrt2(self):
        """√2 ≈ 1.41421356237"""
        r = radical.Radical(2, 2)
        self.assert_almost_equal(r.approx(), 1.41421356237, places=8)

    @test
    def test_approx_with_coeff(self):
        """3√2 ≈ 4.24264068712"""
        r = radical.Radical(2, 2, 3)
        self.assert_almost_equal(r.approx(), 4.24264068712, places=8)

    @test
    def test_approx_frac(self):
        """√(1/2) ≈ 0.70710678118"""
        from gaskill import Frac
        r = radical.Radical(2, Frac(1, 2))
        self.assert_almost_equal(r.approx(), 0.70710678118, places=8)

    @test
    def test_float_conversion(self):
        """float(√2) ≈ 1.41421356237"""
        r = radical.Radical(2, 2)
        self.assert_almost_equal(float(r), 1.41421356237, places=8)

    # ==================== 实际场景 ====================

    @test
    def test_pythagorean(self):
        """√(3² + 4²) = 5"""
        r = radical.Radical(2, 3*3 + 4*4)  # √25
        self.assert_almost_equal(r.approx(), 5.0, places=10)

    @test
    def test_quadratic_discriminant(self):
        """x²-5x+6 的判别式 √(25-24) = 1"""
        r = radical.Radical(2, 25 - 24)  # √1
        self.assert_almost_equal(r.approx(), 1.0, places=10)


if __name__ == "__main__":
    runner = TestRunner()
    runner.run_all()
