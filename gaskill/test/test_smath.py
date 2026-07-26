from gaskill import smath
from gaskill import TestCase, TestRunner, test, skip

class MathTester(TestCase):
    
    # ========== 常量测试 ==========
    @test
    def test_constants(self):
        """测试数学常量"""
        self.assert_almost_equal(smath.pi, 3.141592653589793, places=12)
        self.assert_almost_equal(smath.e, 2.718281828459045, places=12)
        self.assert_almost_equal(smath.tau, 6.283185307179586, places=12)
        self.assert_almost_equal(smath.phi, 1.618033988749895, places=12)
    
    # ========== 复数基础 ==========
    @test
    def test_complex_creation(self):
        """测试复数创建"""
        c1 = smath.Complex(3, 4)
        self.assert_equal(c1.real, 3)
        self.assert_equal(c1.imag, 4)
        
        c2 = smath.Complex("3+4i")
        self.assert_equal(c2.real, 3)
        self.assert_equal(c2.imag, 4)
        
        c3 = smath.Complex(1j)  # 从 Python complex 转换
        self.assert_equal(c3.real, 0)
        self.assert_equal(c3.imag, 1)
    
    @test
    def test_complex_repr(self):
        """测试复数显示格式"""
        i = smath.Complex(1j)
        self.assert_equal(str(i), "i")
        self.assert_equal(str(smath.Complex(0, 1)), "i")
        self.assert_equal(str(smath.Complex(0, -1)), "-i")
        self.assert_equal(str(smath.Complex(3, 4)), "(3+4i)")
        self.assert_equal(str(smath.Complex(3, -4)), "(3-4i)")
        self.assert_equal(str(smath.Complex(3, 0)), "3")
    
    # ========== 复数运算 ==========
    @test
    def test_complex_add(self):
        """测试复数加法"""
        c1 = smath.Complex(1, 2)
        c2 = smath.Complex(3, 4)
        result = c1 + c2
        self.assert_equal(result.real, 4)
        self.assert_equal(result.imag, 6)
        
        # 复数 + 实数
        result = c1 + 5
        self.assert_equal(result.real, 6)
        self.assert_equal(result.imag, 2)
    
    @test
    def test_complex_mul(self):
        """测试复数乘法"""
        c1 = smath.Complex(1, 2)
        c2 = smath.Complex(3, 4)
        result = c1 * c2
        # (1+2i)(3+4i) = -5+10i
        self.assert_equal(result.real, -5)
        self.assert_equal(result.imag, 10)
    
    @test
    def test_complex_conjugate(self):
        """测试共轭"""
        c = smath.Complex(3, 4)
        conj = c.conjugate()
        self.assert_equal(conj.real, 3)
        self.assert_equal(conj.imag, -4)
    
    # ========== 欧拉恒等式 ==========
    @test
    def test_euler_identity(self):
        """测试欧拉恒等式 e^(iπ) = -1"""
        i = smath.Complex(1j)
        result = smath.exp(smath.pi * i)
        # 应该是 -1 + 0i
        self.assert_almost_equal(result.real, -1.0, places=10)
        self.assert_almost_equal(result.imag, 0.0, places=10)
    
    # ========== 复数幂运算 ==========
    @test
    def test_complex_power_i_i(self):
        """测试 i^i = e^(-π/2)"""
        i = smath.Complex(1j)
        result = i ** i
        expected = smath.exp(-smath.pi / 2)
        self.assert_almost_equal(result.real, expected, places=10)
        self.assert_almost_equal(result.imag, 0.0, places=10)
    
    @test
    def test_complex_power_1_plus_i(self):
        """测试 (1+i)^(1+i)"""
        z = smath.Complex(1, 1)
        result = z ** z
        # 精确值: 0.2739572538301211 + 0.5837007587586147i
        expected_real = 0.2739572538301211
        expected_imag = 0.5837007587586147
        self.assert_almost_equal(result.real, expected_real, places=8)
        self.assert_almost_equal(result.imag, expected_imag, places=8)
    
    @test
    def test_complex_power_real_base(self):
        """测试实数底数的复数幂"""
        result = 2 ** smath.Complex(0, 1)  # 2^i
        # 2^i = cos(ln2) + i*sin(ln2)
        expected_real = smath.cos(smath.ln(2))
        expected_imag = smath.sin(smath.ln(2))
        self.assert_almost_equal(result.real, expected_real, places=10)
        self.assert_almost_equal(result.imag, expected_imag, places=10)
    
    # ========== 三角函数 ==========
    @test
    def test_sin(self):
        """测试 sin"""
        self.assert_almost_equal(smath.sin(0), 0, places=12)
        self.assert_almost_equal(smath.sin(smath.pi / 2), 1, places=12)
        self.assert_almost_equal(smath.sin(smath.pi), 0, places=12)
        self.assert_almost_equal(smath.sin(smath.pi * 3 / 2), -1, places=12)
    
    @test
    def test_cos(self):
        """测试 cos"""
        self.assert_almost_equal(smath.cos(0), 1, places=12)
        self.assert_almost_equal(smath.cos(smath.pi / 2), 0, places=12)
        self.assert_almost_equal(smath.cos(smath.pi), -1, places=12)
    
    @test
    def test_tan(self):
        """测试 tan"""
        self.assert_almost_equal(smath.tan(0), 0, places=12)
        self.assert_almost_equal(smath.tan(smath.pi / 4), 1, places=12)
    
    # ========== 反三角函数 ==========
    @test
    def test_asin(self):
        """测试 asin"""
        self.assert_almost_equal(smath.asin(0), 0, places=12)
        self.assert_almost_equal(smath.asin(1), smath.pi / 2, places=12)
        self.assert_almost_equal(smath.asin(-1), -smath.pi / 2, places=12)
    
    @test
    def test_acos(self):
        """测试 acos"""
        self.assert_almost_equal(smath.acos(1), 0, places=12)
        self.assert_almost_equal(smath.acos(0), smath.pi / 2, places=12)
        self.assert_almost_equal(smath.acos(-1), smath.pi, places=12)
    
    # ========== 对数 ==========
    @test
    def test_log(self):
        """测试自然对数"""
        self.assert_almost_equal(smath.ln(1), 0, places=12)
        self.assert_almost_equal(smath.ln(smath.e), 1, places=12)
        self.assert_almost_equal(smath.ln(smath.e ** 2), 2, places=10)
    
    @test
    def test_log_base(self):
        """测试任意底数对数"""
        self.assert_almost_equal(smath.log(8, 2), 3, places=10)
        self.assert_almost_equal(smath.log(100, 10), 2, places=10)
    
    @test
    def test_log_complex(self):
        """测试复数对数"""
        # ln(-1) = iπ
        result = smath.ln(smath.Complex(-1, 0))
        self.assert_almost_equal(result.real, 0, places=10)
        self.assert_almost_equal(result.imag, smath.pi, places=10)
    
    # ========== 指数 ==========
    @test
    def test_exp(self):
        """测试 exp"""
        self.assert_almost_equal(smath.exp(0), 1, places=12)
        self.assert_almost_equal(smath.exp(1), smath.e, places=12)
        self.assert_almost_equal(smath.exp(smath.ln(2)), 2, places=10)
    
    @test
    def test_exp_complex(self):
        """测试复数 exp"""
        # e^(iπ/2) = i
        result = smath.exp(smath.Complex(0, smath.pi / 2))
        self.assert_almost_equal(result.real, 0, places=10)
        self.assert_almost_equal(result.imag, 1, places=10)
    
    # ========== 双曲函数 ==========
    @test
    def test_sinh_cosh(self):
        """测试双曲函数"""
        self.assert_almost_equal(smath.sinh(0), 0, places=12)
        self.assert_almost_equal(smath.cosh(0), 1, places=12)
        # cosh^2 - sinh^2 = 1
        x = 1.23
        ch = smath.cosh(x)
        sh = smath.sinh(x)
        self.assert_almost_equal(ch*ch - sh*sh, 1, places=10)
    
    # ========== 伽马函数 ==========
    @test
    def test_gamma(self):
        """测试 Gamma 函数"""
        self.assert_almost_equal(smath.gamma(1), 1, places=10)
        self.assert_almost_equal(smath.gamma(2), 1, places=10)
        self.assert_almost_equal(smath.gamma(3), 2, places=10)
        self.assert_almost_equal(smath.gamma(4), 6, places=10)
        # Γ(0.5) = √π
        self.assert_almost_equal(smath.gamma(0.5), smath.sqrt(smath.pi), places=8)
    
    @test
    def test_gamma_negative(self):
        """测试 Gamma 函数负整数极点"""
        # Γ(-1) 应该抛出异常
        with self.assert_raises(smath.UndeFinedError):
            smath.gamma(-1)
    
    # ========== 阶乘 ==========
    @test
    def test_factorial(self):
        """测试阶乘"""
        self.assert_equal(smath.factorial(0), 1)
        self.assert_equal(smath.factorial(1), 1)
        self.assert_equal(smath.factorial(5), 120)
        self.assert_equal(smath.factorial(10), 3628800)
    
    @test
    def test_factorial_float(self):
        """测试浮点数阶乘（通过 Gamma）"""
        # 0.5! = Γ(1.5) = √π/2
        result = smath.factorial(0.5)
        expected = smath.sqrt(smath.pi) / 2
        self.assert_almost_equal(result, expected, places=8)
    
    # ========== 组合数 ==========
    @test
    def test_comb(self):
        """测试组合数"""
        self.assert_equal(smath.comb(5, 0), 1)
        self.assert_equal(smath.comb(5, 1), 5)
        self.assert_equal(smath.comb(5, 2), 10)
        self.assert_equal(smath.comb(5, 5), 1)
    
    # ========== 素数 ==========
    @test
    def test_is_prime(self):
        """测试素数判断"""
        # 小素数
        primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]
        for p in primes:
            self.assert_true(smath.is_prime(p))
        
        # 合数
        composites = [4, 6, 8, 9, 10, 12, 14, 15, 16, 18, 20]
        for c in composites:
            self.assert_false(smath.is_prime(c))
    
    @test
    def test_prime_factors(self):
        """测试质因数分解"""
        factors = smath.prime_factors(12)
        self.assert_equal(factors, {2: 2, 3: 1})
        
        factors = smath.prime_factors(100)
        self.assert_equal(factors, {2: 2, 5: 2})
    
    # ========== 工具函数 ==========
    @test
    def test_clamp(self):
        """测试 clamp"""
        self.assert_equal(smath.clamp(5, 0, 10), 5)
        self.assert_equal(smath.clamp(-5, 0, 10), 0)
        self.assert_equal(smath.clamp(15, 0, 10), 10)
    
    @test
    def test_gcd(self):
        """测试最大公约数"""
        self.assert_equal(smath.gcd(12, 18), 6)
        self.assert_equal(smath.gcd(17, 19), 1)
        self.assert_equal(smath.gcd(0, 5), 5)
    
    @test
    def test_sqrt(self):
        """测试平方根"""
        self.assert_almost_equal(smath.sqrt(4), 2, places=12)
        self.assert_almost_equal(smath.sqrt(2) ** 2, 2, places=10)
        
        # 负数平方根 → 复数
        result = smath.sqrt(-1)
        self.assert_almost_equal(result.real, 0, places=10)
        self.assert_almost_equal(result.imag, 1, places=10)
    
    @test
    def test_rad_deg(self):
        """测试角度转换"""
        self.assert_almost_equal(smath.rad(180), smath.pi, places=12)
        self.assert_almost_equal(smath.deg(smath.pi), 180, places=12)
        self.assert_almost_equal(smath.rad(90), smath.pi / 2, places=12)
    
    @test
    def test_fibonacci(self):
        """测试斐波那契"""
        fibs = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
        for i, expected in enumerate(fibs):
            self.assert_equal(smath.fibonacci(i), expected)


# ========== 运行 ==========
if __name__ == "__main__":
    runner = TestRunner()
    runner.run_all()