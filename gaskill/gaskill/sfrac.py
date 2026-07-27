from .smath import gcd as _gcd, log_fast, EPSILON


def _is_int(floater):
    return abs(round(floater) - floater) < EPSILON


def _perfect_root(n, k):
    """检查 n 是否是某个整数的 k 次方，返回那个整数，否则返回 None"""
    if n < 0 and k % 2 == 0:
        return None
    if n < 0:
        n = -n
        sign = -1
    else:
        sign = 1

    # 二分查找
    low, high = 0, int(n ** (1/k)) + 2
    while low <= high:
        mid = (low + high) // 2
        power = mid ** k
        if power == n:
            return sign * mid
        elif power < n:
            low = mid + 1
        else:
            high = mid - 1
    return None


class Frac:
    """轻量分数类"""

    def __init__(self, numerator, denominator=None):
        """初始化分数"""
        if denominator is None:
            numerator, denominator = int(self._to_frac(
                numerator).n), int(self._to_frac(numerator).d)
        if denominator == 0:
            raise ValueError("分母不能为0")

        # 处理负号
        if denominator < 0:
            numerator = -numerator
            denominator = -denominator

        # 自己约分，不用 math
        g = _gcd(numerator, denominator)
        self.n = numerator // g
        self.d = denominator // g

    def __hash__(self):
        """使 Frac 可哈希"""
        return hash((self.n, self.d))

    def as_percent(self, precision=0):
        """准确的分数百分数显示"""
        # 用整数运算避免浮点误差
        percent_numerator = self.n * 100
        whole = percent_numerator // self.d
        remainder = percent_numerator % self.d

        if precision == 0:
            # 四舍五入
            if remainder * 2 >= self.d:
                whole += 1
            return f"{whole}%"

        # 小数部分
        result = f"{whole}."
        for i in range(precision):
            remainder *= 10
            digit = remainder // self.d
            result += str(digit)
            remainder = remainder % self.d

        return f"{result}%"

    def __pow__(self, other):
        other = self._to_frac(other)

        if other.d == 1:
            # 整数指数
            exp = other.n
            if exp >= 0:
                return Frac(self.n ** exp, self.d ** exp)
            else:
                return Frac(self.d ** (-exp), self.n ** (-exp))

        # 分数指数：a/b 的 p/q 次方
        # = (a^p / b^p) 开 q 次方
        p = other.n
        q = other.d

        num_pow = self.n ** p
        den_pow = self.d ** p

        # 尝试开 q 次方
        num_root = _perfect_root(num_pow, q)
        den_root = _perfect_root(den_pow, q)

        if num_root is not None and den_root is not None:
            # 能开尽，返回有理数
            return Frac(num_root, den_root)

        # 不能开尽
        raise UserWarning(
            f"({self})^{other} 不是有理数，"
            f"请使用近似值: {float(self) ** (p/q)}"
        )

    def __rpow__(self, other):
        """右幂运算：other ** self"""
        other = self._to_frac(other)
        return other.__pow__(self)

    def __round__(self, digits):
        return round(self.n / self.d, digits)

    def __mod__(self, other):
        """分数取模 self % other"""
        other = self._to_frac(other)

        # self / other = (a/b) / (c/d) = (a*d) / (b*c)
        quotient = (self.n * other.d) / (self.d * other.n)

        # 向下取整
        from .smath import floor
        k = floor(quotient)

        # self - other × k
        return self - other * k

    def __rmod__(self, other):
        """右取模 other % self"""
        return self._to_frac(other) % self

    def __add__(self, other):
        """加法：self + other"""
        other = self._to_frac(other)

        if other is NotImplemented:
            return NotImplemented
        return Frac(
            self.n * other.d + other.n * self.d,
            self.d * other.d
        )

    def __sub__(self, other):
        """减法：self - other"""
        other = self._to_frac(other)
        if other is NotImplemented:
            return NotImplemented
        return Frac(
            self.n * other.d - other.n * self.d,
            self.d * other.d
        )

    def __mul__(self, other):
        """乘法：self * other"""
        other = self._to_frac(other)
        if other is NotImplemented:
            return NotImplemented
        return Frac(self.n * other.n, self.d * other.d)

    def __truediv__(self, other):
        """除法：self / other"""
        other = self._to_frac(other)
        if other is NotImplemented:
            return NotImplemented
        if other.n == 0:
            raise ZeroDivisionError("除数不能为0")
        return Frac(self.n * other.d, self.d * other.n)

    def __eq__(self, other):
        """等于：self == other"""
        other = self._to_frac(other)
        if other is NotImplemented:
            return NotImplemented
        return self.n == other.n and self.d == other.d

    def __lt__(self, other):
        """小于：self < other"""
        other = self._to_frac(other)
        if other is NotImplemented:
            return NotImplemented
        # a/b < c/d  <=> a*d < c*b
        return self.n * other.d < other.n * self.d

    def __le__(self, other):
        """小于等于：self <= other"""
        return self == other or self < other

    def __gt__(self, other):
        """大于：self > other"""
        return not self < other

    def __ge__(self, other):
        """大于等于：self >= other"""
        return not self < other or self == other

    def __radd__(self, other):
        """右加法：other + self"""
        return self + other  # 直接复用 __add__

    def __rsub__(self, other):
        """右减法：other - self"""
        # 注意顺序：other - self
        return -self + other

    def __rmul__(self, other):
        """右乘法：other * self"""
        return self * other

    def __rtruediv__(self, other):
        """右除法：other / self"""
        # other / self = other * (1/self)
        return self._to_frac(other) * ~self

    def __neg__(self):
        """负数：-self"""
        return Frac(-self.n, self.d)

    def __pos__(self):
        """正数：+self"""
        return self

    def __abs__(self):
        """绝对值：abs(self)"""
        return Frac(abs(self.n), self.d)

    def __invert__(self):
        """~frac 返回倒数"""
        return Frac(self.d, self.n)

    def __float__(self):
        """将分数转换为浮点数"""
        return self.n / self.d

    def __int__(self):
        return self.n // self.d

    def __format__(self, spec):
        """支持格式化字符串"""
        if not spec:
            return str(self)

        spec = spec.strip()

        if spec.endswith('%'):
            length = spec[:-1].replace(".", "")
            length = int(length) if length else 0
            return self.as_percent(length)


        if spec == 'l' or spec == 'latex':
            if self.d == 1:
                return str(self.n)
            return f"\\frac{{{self.n}}}{{{self.d}}}"

        if spec == 'm' or spec == 'mixed':
            if abs(self.n) >= self.d:
                whole = self.n // self.d
                remainder = abs(self.n % self.d)
                if remainder == 0:
                    return str(whole)
                sign = '-' if self.n < 0 else ''
                return f"{sign}{abs(whole)} + {remainder}/{self.d}"
            return str(self)

        if spec == '/' or spec == 'frac':
            return f"{self.n}/{self.d}"

        if spec.endswith('f'):
            length = spec[:-1].replace(".", "")
            precision = int(length) if length else 6
            return f"{self.n / self.d:.{precision}f}"

        if spec.endswith('e') or spec.endswith('E'):
            precision = int(spec[:-1].replace(".")) if spec[:-1] else 6
            return f"{self.n / self.d:.{precision}{spec[-1]}}"

        return str(self)

    def __str__(self):
        """将分数转换为字符串"""
        # 尝试显示分数
        try:
            if self.d >= 10**1000 or self.n >= 10**1000:
                raise ValueError
            if self.d != 1:
                return f"{self.n}/{self.d}"
            return str(self.n)
        except ValueError:
            pass

        n, d = self.n, self.d

        # 计算指数（log10 返回整数）
        exp_n = log_fast(n)
        exp_d = log_fast(d)
        exp = exp_n - exp_d

        # 计算 mantissa = n / (10**exp) / d
        # 用整数运算：mantissa = n * 10**(-exp) / d
        if exp >= 0:
            # n / (10**exp) / d = n / (d * 10**exp)
            numerator = n
            denominator = d * (10 ** exp)
        else:
            # n / (10**exp) / d = n * (10**(-exp)) / d
            numerator = n * (10 ** (-exp))
            denominator = d

        # 调整到 [1, 10)
        while numerator >= denominator * 10:
            denominator *= 10
            exp += 1
        while numerator < denominator:
            numerator *= 10
            exp -= 1

        # 计算 mantissa 浮点值（此时 numerator 和 denominator 都很小）
        mantissa = Frac(numerator, denominator)
        self._mantissa = mantissa
        mantissa = f"{mantissa:1f}"
        self._exp = exp
        return f"{mantissa}e{exp}"

    def __repr__(self):
        """返回可被 eval() 重建的字符串表示"""
        try:
            # 正常情况：小数字
            if self.d == 1:
                return f"Frac({self.n})"
            return f"Frac({self.n}, {self.d})"
        except (ValueError, OverflowError, RecursionError):
            # 数字太大时的降级方案
            pass

        # 科学计数法情况：不再返回嵌套的 Frac，而是直接返回浮点数的字符串
        if not hasattr(self, '_exp'):
            # 强制计算科学计数法表示
            str(self)  # 这会设置 self._exp 和 self._mantissa

        # 关键修复：将 mantissa 转为浮点数字符串，而不是 repr
        mantissa = self._mantissa
        if isinstance(mantissa, Frac):
            # 转为浮点数或分数形式
            mantissa_str = f"{mantissa.n / mantissa.d:.10f}".rstrip(
                '0').rstrip('.')
        else:
            mantissa_str = str(mantissa)

        exp = self._exp
        if exp >= 0:
            return f'Frac("{mantissa_str}e+{exp}")'
        else:
            return f'Frac("{mantissa_str}e{exp}")'

    def _to_frac(self, other):
        """将其他类型转换为分数"""
        if isinstance(other, Frac):
            return other
        if isinstance(other, str) and "e" not in other.lower():
            other = float(other)
        if isinstance(other, float) and _is_int(other) and "e" not in str(other).lower():
            return Frac(other, 1)
        if isinstance(other, int):
            return Frac(other, 1)
        if isinstance(other, (float, int, str)):
            if isinstance(other, (float, str, int)):
                # 转成整数处理 (1.23 -> 123/100)
                s = str(other)

                if 'e' not in s.lower():  # 暂不考虑科学计数法
                    parts = s.split('.')
                    if len(parts) == 2:
                        whole, dec = parts
                        n = int(whole + dec)
                        d = 10 ** len(dec)
                        return Frac(n, d)
                else:
                    # 直接解析
                    coeff, exp = s.lower().split('e')
                    exp = int(exp)

                    # 把系数转成整数分子分母
                    if '.' in coeff:
                        whole, dec = coeff.split('.')
                        n = int(whole + dec)
                        d = 10 ** len(dec)
                    else:
                        n = int(coeff)
                        d = 1

                    # 根据指数调整
                    if exp >= 0:
                        n *= 10 ** exp
                    else:
                        d *= 10 ** (-exp)

                    return Frac(n, d)
                return Frac(other, 1)
        return NotImplemented
