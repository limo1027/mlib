# smath.py - 数学工具模块

pi = 3.141592653589793
e = 2.718281828459045
tau = 2 * pi
phi = 1.618033988749895

EPSILON = 1e-18
INF = float('inf')


class MathError(BaseException):
    pass


class UndeFinedError(MathError):
    pass


class Complex:
    def __init__(self, real, imag=None):
        if imag is None:
            result = self._to_Complex(real)
            self._real = result._real
            self._imag = result._imag
            self._update_polar()
            return
        self._real = real
        self._imag = imag
        self._update_polar()

    @property
    def imag(self):
        return self._imag

    @imag.setter
    def imag(self, value):
        self._imag = value
        self._update_polar()

    @property
    def r(self):
        return self._r

    @r.setter
    def r(self, value):
        self._r = value
        self._update_xy()

    @property
    def theta(self):
        return self._theta

    @theta.setter
    def theta(self, value):
        self._theta = value
        self._update_xy()

    @property
    def real(self):
        return self._real

    @real.setter
    def real(self, value):
        self._real = value
        self._update_polar()

    def _update_polar(self):
        self._r = hypot(self._real, self._imag)
        self._theta = atan2(self._imag, self._real)

    def _update_xy(self):
        self._real = self._r * cos(self._theta)
        self._imag = self._r * sin(self._theta)

    def __add__(self, other):
        other = self._to_Complex(other)
        return Complex(self.real + other.real, self.imag + other.imag)

    def __radd__(self, other):
        return self + other

    def __sub__(self, other):
        return self + -other

    def __rsub__(self, other):
        return -self + other

    def __mul__(self, other):
        other = self._to_Complex(other)
        return Complex(self.real * other.real - self.imag * other.imag,
                       self.imag * other.real + self.real * other.imag)

    def __rmul__(self, other):
        return self * other

    def __neg__(self):
        return Complex(-self.real, -self.imag)

    def __mod__(self, other):
        if isinstance(other, (Complex, complex)):
            raise TypeError(
                "unsupported operand type(s) for %: 'complex' and 'complex'")

        return Complex(self.real % other, self.imag % other)

    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            return Complex(self.real / other, self.imag / other)

        other = self._to_Complex(other)
        return self * other.conjugate() / (other.real ** 2 + other.imag ** 2)

    def __rtruediv__(self, other):
        other = self._to_Complex(other)
        return other / self

    def __pow__(self, other):
        other = self._to_Complex(other)
        if self.real == 0 and self.imag == 0:
            if other.real == 0 and other.imag == 0:
                raise UndeFinedError("0^0 is undefined")
            elif other.real < 0:
                raise UndeFinedError("0^negative is undefined")
            else:
                return Complex(0, 0)

        log_z = log(self)
        return exp(other * log_z)

    def __rpow__(self, other):
        other = self._to_Complex(other)
        return other ** self

    def __abs__(self):
        return (self.real ** 2 + self.imag ** 2) ** 0.5

    def __hash__(self):
        return hash(repr(self))

    def __eq__(self, other):
        try:
            other = self._to_Complex(other)
        except TypeError:
            return False
        return abs(self.real - other.real) < EPSILON and abs(self.imag - other.imag) < EPSILON

    def __repr__(self):
        imag = round(self.imag, 12)
        real = round(self.real, 12)

        # 消除 -0.0 和接近 0 的值
        if abs(real) < EPSILON:
            real = 0.0
        if abs(imag) < EPSILON:
            imag = 0.0

        if real == 0:
            if imag == 1:
                return "i"
            elif imag == -1:
                return "-i"
            return f"{imag}i"
        if imag < 0:
            if imag == -1:
                return f"({real}-i)"
            return f"({real}{imag}i)"
        elif imag == 0:
            return f"{real}"
        else:
            if imag == 1:
                return f"({real}+i)"
            return f"({real}+{imag}i)"

    def __str__(self):
        return repr(self)

    def conjugate(self):
        """获取复数的共轭"""
        return Complex(self.real, -self.imag)

    def _to_Complex(self, number):
        if isinstance(number, Complex):
            return number

        elif isinstance(number, complex):
            return Complex(number.real, number.imag)

        elif isinstance(number, (int, float)):
            return Complex(number, 0)

        elif isinstance(number, tuple):
            return Complex(number[0], number[1])

        elif isinstance(number, str):
            try:
                real, imag = self._parse_complex_str(number)
                return Complex(real, imag)
            except ValueError as e:
                raise TypeError(f"无法从字符串创建复数: {e}")
        raise TypeError(f"Unknown type: {type(number)}")

    def _parse_complex_str(self, s):
        """解析复数字符串"""
        s = s.strip().replace(' ', '')

        if not s:
            raise ValueError("空字符串不能解析为复数")

        # 特殊值
        if s in ('i', 'j', '+i', '+j'):
            return (0, 1)
        if s in ('-i', '-j'):
            return (0, -1)

        # 找到虚部标记
        imag_pos = -1
        for i, char in enumerate(s):
            if char in 'ij':
                imag_pos = i
                break

        if imag_pos == -1:
            try:
                return (float(s), 0)
            except ValueError:
                raise ValueError(f"无法解析复数字符串: {s}")

        # 🔥 修复：找到最后一个运算符的位置
        # 从 imag_pos 往前找 '+' 或 '-'
        op_pos = -1
        for i in range(imag_pos - 1, -1, -1):
            if s[i] in '+-':
                op_pos = i
                break

        if op_pos == -1:
            # 没有运算符，整个字符串就是虚部
            real = 0.0
            imag_str = s[:imag_pos]
        else:
            real_str = s[:op_pos]
            imag_str = s[op_pos:imag_pos]

            # 处理实部
            if real_str == '' or real_str == '+':
                real = 0.0
            elif real_str == '-':
                real = 0.0
            else:
                try:
                    real = float(real_str)
                except ValueError:
                    raise ValueError(f"无法解析实数部分: {real_str}")

        # 处理虚部系数
        if imag_str == '' or imag_str == '+':
            imag = 1.0
        elif imag_str == '-':
            imag = -1.0
        else:
            try:
                imag = float(imag_str)
            except ValueError:
                raise ValueError(f"无法解析虚数部分: {imag_str}")

        return (real, imag)


def triangle_wave(t, period=1.0, amplitude=1.0, phase=0.0):
    """三角波"""
    t = (t + phase) % period
    normalized = t / period
    value = 2 * abs(normalized - 0.5)
    return amplitude * (2 * value - 1)


def gcd(a, b):
    """最大公约数"""
    a, b = abs(a), abs(b)
    while b:
        a, b = b, a % b
    return a


def log_fast(n, base=10):
    if n <= 0:
        return -float('inf')
    k = 1
    while True:
        try:
            if base ** k > n:
                break
            k *= 2
        except OverflowError:
            break

    low, high = k // 2, k
    while low <= high:
        mid = (low + high) // 2
        if base ** mid <= n:
            low = mid + 1
        else:
            high = mid - 1

    return high


def lcm(a, b):
    """最小公倍数"""
    return abs(a * b) // gcd(a, b)


def factorial(n):
    """阶乘 n!"""
    if isinstance(n, int) or abs(n - int(n)) <= EPSILON:

        if n < 0:
            raise UndeFinedError("阶乘不支持负整数")
        if n <= 1:
            return 1
        result = 1
        for i in range(2, n + 1):
            result *= i
        return result
    return gamma(n + 1)


def comb(n, k):
    """组合数 C(n,k)"""
    if k < 0 or k > n:
        return 0
    k = min(k, n - k)
    result = 1
    for i in range(1, k + 1):
        result = result * (n - k + i) // i
    return result


def perm(n, k):
    """排列数 P(n,k)"""
    return comb(n, k) * factorial(k)


def _exp(x, terms=20):
    """e^x 泰勒展开 - 快速收敛"""
    # 负数转正数（利用 e^-x = 1/e^x）
    if x < 0:
        return 1.0 / _exp(-x, terms)

    # 小数优化：e^(a+b) = e^a * e^b，让 x 在 [0, 1] 范围内
    integer_part = int(x)
    fractional_part = x - integer_part

    # 泰勒展开小数部分
    result = 1.0
    term = 1.0
    for i in range(1, terms + 1):
        term *= fractional_part / i
        result += term
        if abs(term) < EPSILON:
            break

    # 整数部分用乘法（e^整数 = e^1 累乘）
    e_pow_int = result  # 已经是 e^fractional_part
    e1 = e  # e 的近似值

    for _ in range(integer_part):
        e_pow_int *= e1

    return float(e_pow_int)


def _ln(x):
    """自然对数 ln(x)，使用 arctanh 展开，支持范围缩小"""
    if x <= 0:
        raise UndeFinedError("ln(x) 定义域为 x > 0")

    if x < 1:
        return -_ln(1/x)
    exponent = 0
    while x > 2:
        x /= 2
        exponent += 1

    y = (x - 1) / (x + 1)

    result = 0
    y_pow = y
    for i in range(1, 40, 2):
        result += y_pow / i
        y_pow *= y * y
        if y_pow / (i + 2) < EPSILON:
            break

    result *= 2
    return result + exponent * 0.6931471805599453


def _lanczos_coefficients(g=7):
    """Lanczos 近似系数（g=7，精度约 1e-7）"""
    # 参考：Numerical Recipes
    return [
        0.99999999999980993,
        676.5203681218851,
        -1259.1392167224028,
        771.32342877765313,
        -176.61502916214059,
        12.507343278686905,
        -0.13857109526572012,
        9.9843695780195716e-6,
        1.5056327351493116e-7
    ]


def gamma(z):
    """ Gamma 函数 Γ(z)"""
    mul = 1
    # 检查负整数（极点）
    if isinstance(z, (int, float)) and not isinstance(z, Complex):
        if z <= 0 and z == int(z):
            raise UndeFinedError(f"Gamma({z}) 无定义（负整数极点）")

    if z < 0.5:
        return pi / (sin(pi * z) * gamma(1 - z))

    while z > 1:
        z -= 1
        mul *= z
    coeffs = _lanczos_coefficients()
    g = 7

    sum_p = coeffs[0]
    for i in range(1, g + 2):
        sum_p += coeffs[i] / (z + i - 1)

    t = z + g - 0.5
    try:
        return sqrt(2 * pi) * (t ** (z - 0.5)) * exp(-t) * sum_p * mul
    except OverflowError:
        return float('inf')


def log_gamma(z):
    """对数 Gamma 函数 ln(|Γ(z)|)"""
    return ln(abs(gamma(z)))


def digamma(z):
    """近似公式，适用于实数 z > 0"""
    if z <= 0:
        # 用反射公式：ψ(1-z) = ψ(z) + π cot(πz)
        return digamma(1 - z) - pi / tan(pi * z)

    # 渐近展开（z 较大时）
    if z > 8:
        inv_z = 1 / z
        inv_z2 = inv_z * inv_z
        inv_z4 = inv_z2 * inv_z2
        return ln(z) - 0.5 / z - inv_z2 / 12 + inv_z4 / 120 - inv_z4 * inv_z2 / 252

    return digamma(z + 1) - 1 / z


def beta(a, b):
    """Beta 函数 B(a,b) = Γ(a)Γ(b)/Γ(a+b)"""
    return gamma(a) * gamma(b) / gamma(a + b)


def _log_complex(z):
    """复数自然对数 ln(z)"""
    if not isinstance(z, Complex):
        if z == float('inf'):
            return float('inf')
        if z == float('-inf'):
            return float('-inf')
        if z > 0:
            result = 0
            while z > e:
                z /= e
                result += 1
            return _ln(z) + result

    # 模长
    r = (z.real**2 + z.imag**2) ** 0.5
    if r == 0:
        return float("-inf")

    # 辐角 atan2(y, x)
    theta = _atan2(z.imag, z.real)
    result = Complex(_ln(r), theta)
    if abs(result.imag) < EPSILON:  # 浮点数精度阈值
        return result.real
    return result


def _atan2(y, x):
    """辐角函数 atan2(y, x)"""
    if x > 0:
        return _atan(y / x)
    elif x < 0:
        if y >= 0:
            return _atan(y / x) + pi
        else:
            return _atan(y / x) - pi
    else:
        if y > 0:
            return pi / 2
        elif y < 0:
            return -pi / 2
        else:
            return 0.0


def _atan(x, terms=40):
    sign = 1 if x >= 0 else -1
    x = abs(x)

    # 大 x 时用互补角公式
    if x > 1:
        return sign * (pi / 2 - _atan(1 / x, terms))

    t = x / (1 + (1 + x * x) ** 0.5)
    t2 = t * t
    term = t
    result = 0
    n = 1

    for _ in range(terms):
        result += term / n
        term *= -t2
        n += 2
        if abs(term / n) < EPSILON:
            break

    return sign * 2 * result


def log(z, base=None):
    """任意底数的对数"""
    if base is None:
        return _log_complex(z)
    ln_z = _log_complex(z)
    ln_base = _log_complex(base)
    if isinstance(ln_z, Complex) or isinstance(ln_base, Complex):
        return ln_z / ln_base
    return ln_z / ln_base


def exp(z):
    """e^x"""
    if isinstance(z, Complex):
        return Complex(
            exp(z.real) * cos(z.imag),   # 实部
            exp(z.real) * sin(z.imag)    # 虚部
        )
    return _exp(z)


def log10(z):
    """以 10 为底的对数"""
    return log(z, 10)


def log2(z):
    """以 2 为底的对数"""
    return log(z, 2)


def ln(z):
    """自然对数"""
    return _log_complex(z)


def cos(x, fast=True):
    from . import Frac
    """余弦函数"""
    if isinstance(x, Complex):
        ix = Complex(-x.imag, x.real)
        return (exp(ix) + exp(-ix)) / 2

    x = Frac(x)
    pi_frac = Frac(314159265358979323846264,
                   100000000000000000000000)
    return sin(x + pi_frac/2, fast)


def sin(x, fast=True):
    from . import Frac

    if isinstance(x, (Complex, complex)):
        result = 0
        term = x
        for i in range(20):  # 到 x^27，双精度够
            result += term
            term = term * (-x * x / ((2*i + 2) * (2*i + 3)))

        return result
    if isinstance(x, (int, float)) and x > 1000 and (not fast):
        pi_frac = Frac(31415926535897932384626433832795028841971,
                       10000000000000000000000000000000000000000)
        x_frac = Frac(x)
        result = Frac(0, 1)
    else:
        pi_frac = pi
        x_frac = x
        result = 0
    two_pi = pi_frac * 2
    # 周期规约到 [-pi, pi]
    x_frac = x_frac % two_pi
    if x_frac > pi_frac:
        x_frac -= two_pi
    elif x_frac < -pi_frac:
        x_frac += two_pi

    # 进一步规约到 [-pi/2, pi/2]
    if x_frac > pi_frac / 2:
        x_frac = pi_frac - x_frac
    elif x_frac < -pi_frac / 2:
        x_frac = -pi_frac - x_frac

    # 现在 x_frac 在 [-pi/2, pi/2]，泰勒展开（14项，到 x^27）
    term = x_frac
    x_frac = float(x_frac)
    for i in range(14):  # 到 x^27，双精度够
        result += term
        term *= -x_frac * x_frac / ((2*i + 2) * (2*i + 3))

    return float(result)


def tan(x):
    """正切函数"""
    from . import Frac
    pi_frac = Frac(314159265358979323846264,
                   100000000000000000000000)
    x = Frac(x)
    x = x % pi_frac
    x = float(x)
    c = cos(x)
    if abs(c) < EPSILON:
        raise UndeFinedError("tan(x) 在 x = {:.6f} 处无定义".format(x))
    return float(Frac(sin(x)) / Frac(c))


def cot(x):
    """余切函数"""
    s = sin(x)
    if abs(s) < EPSILON:
        raise UndeFinedError("cot(x) 在 x = {:.6f} 处无定义".format(x))
    return cos(x) / s


def sec(x):
    """正割函数"""
    c = cos(x)
    if abs(c) < EPSILON:
        raise UndeFinedError("sec(x) 在 x = {:.6f} 处无定义".format(x))
    return 1.0 / c


def csc(x):
    """余割函数"""
    s = sin(x)
    if abs(s) < EPSILON:
        raise UndeFinedError("csc(x) 在 x = {:.6f} 处无定义".format(x))
    return 1.0 / s


def asin(x):
    """反正弦函数"""
    if isinstance(x, Complex):
        return Complex(0, -1) * _log_complex(Complex(0, 1) * x + (1 - x * x) ** 0.5)
    if abs(x) > 1:
        return Complex(0, -1) * _log_complex(Complex(0, 1) * x + (1 - x * x) ** 0.5)
    if x == 1:
        return pi / 2
    if x == -1:
        return -pi / 2
    return _atan(x / (1 - x * x) ** 0.5)


def acos(x):
    """反余弦函数"""
    if isinstance(x, Complex):
        return Complex(0, -1) * _log_complex(x + Complex(0, 1) * (1 - x * x) ** 0.5)
    if abs(x) > 1:
        return Complex(0, -1) * _log_complex(x + Complex(0, 1) * (1 - x * x) ** 0.5)
    return pi / 2 - asin(x)


def atan(x):
    """反正切函数"""
    if isinstance(x, Complex):
        return (Complex(0, 1) / 2) * _log_complex((Complex(0, 1) + x) / (Complex(0, 1) - x))
    return _atan(x)


def atan2(y, x):
    """双参数反正切"""
    if isinstance(y, Complex) or isinstance(x, Complex):
        raise UndeFinedError("atan2 不支持复数")
    return _atan2(y, x)


def cosh(x):
    """双曲余弦"""
    return (_exp(x) + _exp(-x)) / 2


def sinh(x):
    """双曲正弦"""
    return (_exp(x) - _exp(-x)) / 2


def tanh(x):
    """双曲正切"""
    return sinh(x) / cosh(x)


def coth(x):
    """双曲余切"""
    return cosh(x) / sinh(x)


def acosh(x):
    """反双曲余弦"""
    if x < 1:
        raise UndeFinedError("acosh(x) 定义域为 x >= 1")
    return _ln(x + (x * x - 1) ** 0.5)


def asinh(x):
    """反双曲正弦"""
    return _ln(x + (x * x + 1) ** 0.5)


def atanh(x):
    """反双曲正切"""
    if abs(x) >= 1:
        raise UndeFinedError("atanh(x) 定义域为 |x| < 1")
    return 0.5 * _ln((1 + x) / (1 - x))


def sinc(x):
    """辛格函数 sin(x)/x，信号处理常用"""
    if abs(x) < EPSILON:
        return 1.0
    return sin(x) / x


def versin(x):
    """正矢函数 1 - cos(x)"""
    return 1 - cos(x)


def coversin(x):
    """余矢函数 1 - sin(x)"""
    return 1 - sin(x)


def exsec(x):
    """外正割函数 sec(x) - 1"""
    return sec(x) - 1


def excsc(x):
    """外余割函数 csc(x) - 1"""
    return csc(x) - 1


def hav(x):
    """半正矢函数 (1 - cos(x)) / 2"""
    return (1 - cos(x)) / 2


def archav(x):
    """反半正矢函数"""
    return 2 * asin(sqrt(x))


def gudermannian(x):
    """古德曼函数 gd(x) = 2*atan(tanh(x/2))"""
    return 2 * atan(tanh(x / 2))


def inv_gudermannian(x):
    """反古德曼函数"""
    return log(tan(pi/4 + x/2))


def sech(x):
    """双曲正割 1/cosh(x)"""
    return 1 / cosh(x)


def csch(x):
    """双曲余割 1/sinh(x)"""
    if abs(x) < EPSILON:
        raise UndeFinedError("csch(x) 在 x=0 处无定义")
    return 1 / sinh(x)


def acoth(x):
    """反双曲余切"""
    if abs(x) <= 1:
        raise UndeFinedError("acoth(x) 定义域为 |x| > 1")
    return 0.5 * log((x + 1) / (x - 1))


def asech(x):
    """反双曲正割"""
    if not 0 < x <= 1:
        raise UndeFinedError("asech(x) 定义域为 0 < x <= 1")
    return log((1 + sqrt(1 - x*x)) / x)


def acsch(x):
    """反双曲余割"""
    if x == 0:
        raise UndeFinedError("acsch(x) 在 x=0 处无定义")
    return log((1 + sqrt(1 + x*x)) / abs(x)) * (1 if x > 0 else -1)


def floor(x):
    """向下取整"""
    i = int(x)
    return i - 1 if x < 0 and x != i else i


def ceil(x):
    """向上取整"""
    i = int(x)
    return i + 1 if x > 0 and x != i else i


def trunc(x):
    """截断取整"""
    return int(x)


def root(x, n=2):
    """n 次方根"""
    if n == 0:
        raise UndeFinedError("0 次方根无定义")

    # 负数的奇数根
    if isinstance(x, (int, float)) and x < 0 and n % 2 == 1:
        return -((-x) ** (1.0 / n))

    elif isinstance(x, (complex, Complex)) or n % 2 == 0:
        x = Complex(x)  # 就这么简单！

    return x ** (1.0 / n)


def sqrt(x):
    """平方根"""
    if isinstance(x, complex):
        x = Complex(x.real, x.imag)
    elif isinstance(x, (float, int)):
        if x < 0:
            x = Complex(x, 0)
    return x ** 0.5


def cbrt(x):
    """立方根"""
    if x < 0:
        return -((-x) ** (1.0 / 3))
    return x ** (1.0 / 3)


def hypot(*args):
    """欧几里得范数（距离）"""
    if not args:
        return 0.0
    return sum(x * x for x in args) ** 0.5


def sign(x): return 1 if x > 0 else (-1 if x < 0 else 0)
def rad(x): return x * pi / 180
def deg(x): return x * 180 / pi
def fract(x): return x - floor(x) if x >= 0 else fract(-x)


def wrap(x, a, b):
    """将 x 限制在 [a, b) 范围内循环"""
    if a >= b:
        raise UndeFinedError("a 必须小于 b")
    range_len = b - a
    return a + (x - a) % range_len


def clamp(x, min_val, max_val):
    """将 x 限制在 [min_val, max_val] 范围内"""
    if min_val > max_val:
        min_val, max_val = max_val, min_val
    if x < min_val:
        return min_val
    if x > max_val:
        return max_val
    return x


def lerp(a, b, t):
    """线性插值"""
    return a + (b - a) * t


def inv_lerp(a, b, v):
    """反向线性插值"""
    if a == b:
        return 0.0
    return (v - a) / (b - a)


def map(x, in_min, in_max, out_min, out_max, clamp_result=False):
    """将 x 从 [in_min, in_max] 映射到 [out_min, out_max]"""
    if in_max == in_min:
        raise UndeFinedError("in_max 不能等于 in_min")
    value = (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
    if clamp_result:
        return clamp(value, out_min, out_max)
    return value


def is_prime(n):
    """判断素数"""
    if n < 2:
        return False
    if n == 2:
        return True
    if n < 2**64:
        return is_prime_fast(n)
    if n % 2 == 0:
        return False
    i = 3
    while i * i <= n:
        if n % i == 0:
            return False
        i += 2
    return True


def is_prime_fast(n):
    """Miller-Rabin 素性检测 - 确定性版本（n < 2^64）"""
    if n < 2:
        return False
    # 小素数快速判断
    small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
    for p in small_primes:
        if n == p:
            return True
        if n % p == 0:
            return False

    # 写 n-1 = d * 2^s
    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1

    # 对于 n < 2^64，这些底数足够
    test_bases = [2, 325, 9375, 28178, 450775, 9780504, 1795265022]

    for a in test_bases:
        if a >= n:
            continue
        x = pow(a, d, n)  # a^d mod n
        if x == 1 or x == n - 1:
            continue
        for _ in range(s - 1):
            x = (x * x) % n
            if x == n - 1:
                break
        else:
            return False
    return True


def prime_factors(n):
    """质因数分解"""
    if n < 2:
        return {}

    factors = {}

    # 处理 2 和 3
    for p in (2, 3):
        count = 0
        while n % p == 0:
            count += 1
            n //= p
        if count:
            factors[p] = count

    d = 5
    step = 2
    limit = int(n ** 0.5) + 1

    while d <= limit and n > 1:
        if n % d == 0:
            count = 0
            while n % d == 0:
                count += 1
                n //= d
            factors[d] = count
            limit = int(n ** 0.5) + 1
        d += step
        step = 6 - step

    if n > 1:
        factors[n] = factors.get(n, 0) + 1

    return factors


def fibonacci(n):
    """第 n 个斐波那契数"""
    if n < 0:
        raise UndeFinedError("n 必须是非负整数")
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


def product(arr):
    """求积"""
    if not arr:
        return 1
    result = 1
    for x in arr:
        result *= x
    return result


def normalize_angle(angle):
    """将角度归一化到 [-pi, pi]"""
    angle = angle % (2 * pi)
    if angle > pi:
        angle -= 2 * pi
    return angle


def distance(p1, p2):
    """两点间距离"""
    if len(p1) != len(p2):
        raise UndeFinedError("点的维度必须相同")
    return sum((a - b) ** 2 for a, b in zip(p1, p2)) ** 0.5


def nearest(value, candidates):
    """返回 candidates 中离 value 最近的一项"""
    if not candidates:
        return None

    best = candidates[0]
    best_dist = abs(value - best)

    for p in candidates[1:]:
        dist = abs(value - p)
        if dist < best_dist:
            best_dist = dist
            best = p

    return best


def angle_between(v1, v2):
    """两向量间夹角（弧度）"""
    dot = sum(a * b for a, b in zip(v1, v2))
    norm1 = sum(a * a for a in v1) ** 0.5
    norm2 = sum(b * b for b in v2) ** 0.5
    if norm1 < EPSILON or norm2 < EPSILON:
        return 0.0
    cos_angle = clamp(dot / (norm1 * norm2), -1, 1)
    return acos(cos_angle)


def egcd(a, m):
    """计算 a 在模 m 下的乘法逆元"""
    if gcd(a, m) != 1:
        raise UndeFinedError
    m0 = m
    y = 0
    x = 1
    if m == 1:
        return 0
    while a > 1:
        q = a // m
        t = m
        m = a % m
        a = t
        t = y
        y = x - q * y
        x = t
    if x < 0:
        x = x % m0
    return x


def relative_error(self_val, real_val):
    """计算相对误差：|self - real| / |real|"""
    if abs(real_val) < EPSILON:
        return float('inf')  # 避免除以零
    return abs(self_val - real_val) / abs(real_val)
