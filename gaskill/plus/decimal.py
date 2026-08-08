from gaskill import factorial
prec = 500


def get_e():
    # 设置计算精度（比需要的多算几位，减少舍入误差）
    precision = prec + 10

    e = Decimal(0)
    factorial = Decimal(1)  # 0! = 1

    for n in range(0, precision * 2):  # 迭代足够多的项
        if n > 0:
            factorial *= n  # 计算 n!
        e += Decimal(1) / factorial
    return e


def compute_ln2():
    """使用 arctanh 级数计算 ln(2) 到指定精度"""
    precision = prec + 1
    # 常数：1/3
    one_third = Decimal(1) / Decimal(3)

    # 级数求和
    term = one_third
    n = 1
    result = Decimal(0)

    while True:
        # 当前项 = term / (2n-1)
        current = term / Decimal(2*n - 1)

        # 如果当前项小到可以忽略，停止
        if current <= Decimal(1) / (10 ** precision):
            break

        result += current

        # 更新 term：term *= (1/3)^2 = term / 9
        term = term / Decimal(9)
        n += 1

    return result * 2


class Decimal:
    def __init__(self, value, fr_len=None):
        if fr_len is not None:
            self.value = value
            self.fr_len = fr_len
            self._simplify()
            return

        if isinstance(value, Decimal):
            self.value = value.value
            self.fr_len = value.fr_len
            return

        if isinstance(value, str):
            if '.' in value:
                if value[0] == '-':
                    int_part, frac_part = value[1:].split('.')
                    self.value = -int(int_part + frac_part)
                else:
                    int_part, frac_part = value.split('.')
                    self.value = int(int_part + frac_part)
                self.fr_len = len(frac_part)
            else:
                self.value = int(value)
                self.fr_len = 0
            self._simplify()
            return

        if isinstance(value, float):
            if value < 0:
                neg = True
            else:
                neg = False
            if value == 0:
                self.value = 0
                self.fr_len = 0
                return

            if str(value) in ('inf', '-inf', 'nan'):
                raise ValueError("Cannot convert NaN or Infinity to Decimal")

            try:
                str_val = str(value)
                if '.' in str_val:
                    int_part, frac_part = str_val.split('.')
                    frac_part = frac_part.rstrip('0')
                    if frac_part:
                        self.fr_len = len(frac_part)
                        self.value = int(
                            int_part + frac_part) if int_part else int(frac_part)
                        if value < 0:
                            self.value = -self.value
                    else:
                        self.fr_len = 0
                        self.value = int(int_part) if int_part else 0
                        if value < 0:
                            self.value = -self.value
                else:
                    self.fr_len = 0
                    self.value = int(str_val)
            except (ValueError, OverflowError):
                int_part = int(value)
                frac_part = value - int_part
                if frac_part < 0:
                    frac_part = -frac_part

                frac_value = 0
                fr_len = 0
                max_digits = prec + 5
                temp = frac_part

                while fr_len < max_digits:
                    temp *= 10
                    digit = int(temp)
                    frac_value = frac_value * 10 + digit
                    temp -= digit
                    fr_len += 1
                    if abs(temp) < 1e-12:
                        break

                while fr_len > 0 and frac_value % 10 == 0:
                    frac_value //= 10
                    fr_len -= 1

                if int_part < 0:
                    self.value = int_part * (10 ** fr_len) - frac_value
                else:
                    self.value = int_part * (10 ** fr_len) + frac_value
                self.fr_len = fr_len

            finally:
                if neg:
                    self.value = -self.value
            self._simplify()
            return

        self.value = int(value)
        self.fr_len = 0
        self._simplify()

    def _simplify(self):
        if self.fr_len > prec:
            self.value //= 10 ** (self.fr_len - prec)
            self.fr_len = prec
        if self.value == 0:
            self.fr_len = 0
            return
        while self.value % 10 == 0 and self.fr_len > 0:
            self.value //= 10
            self.fr_len -= 1

    def _to_decimal(self, value):
        if isinstance(value, Decimal):
            return value
        return Decimal(value)

    def _align(self, other):
        v1, f1 = self.value, self.fr_len
        v2, f2 = other.value, other.fr_len

        f1 = max(0, f1)
        f2 = max(0, f2)

        while f1 < f2:
            v1 *= 10
            f1 += 1
        while f2 < f1:
            v2 *= 10
            f2 += 1

        return v1, v2, f1

    def __add__(self, other):
        other = self._to_decimal(other)

        if self.value == 0:
            return other
        if other.value == 0:
            return self

        v1, v2, f = self._align(other)
        return Decimal(v1 + v2, f)

    def __radd__(self, other):
        return self + other

    def __sub__(self, other):
        other = self._to_decimal(other)
        return self + (-other)

    def __rsub__(self, other):
        return -self + other

    def __neg__(self):
        return Decimal(-self.value, self.fr_len)

    def __abs__(self):
        return Decimal(abs(self.value), self.fr_len)

    def __mul__(self, other):
        other = self._to_decimal(other)
        return Decimal(self.value * other.value, self.fr_len + other.fr_len)

    def __round__(self, value=0):
        result = Decimal(self.value, self.fr_len)
        if result.fr_len > value:
            last = int(str(result.value)[value + 1])
            result.value //= 10 ** (result.fr_len - value)
            if last >= 5:
                result.value += 1
            result.fr_len = value
        result._simplify()
        return result

    def __mod__(self, other):
        other = self._to_decimal(other)
        v1, v2, f = self._align(other)
        return Decimal(v1 % v2, f)

    def __rmul__(self, other):
        return self * other

    def __floordiv__(self, other):
        result = self / other
        if result.fr_len > 0:
            result.value //= 10 ** result.fr_len
            result.fr_len = 0
        return result

    def __truediv__(self, other):
        other = self._to_decimal(other)

        if other.value == 0:
            raise ZeroDivisionError("division by zero")

        v1, v2, _ = self._align(other)

        sign = 1
        if v1 < 0:
            sign = -sign
            v1 = -v1
        if v2 < 0:
            sign = -sign
            v2 = -v2

        int_part = v1 // v2
        remainder = v1 % v2

        frac_digits = []
        for _ in range(prec):
            remainder *= 10
            digit = remainder // v2
            remainder = remainder % v2
            frac_digits.append(str(digit))

        while frac_digits and frac_digits[-1] == '0':
            frac_digits.pop()

        if frac_digits:
            frac_str = ''.join(frac_digits)
            frac_len = len(frac_str)
            result_value = int_part * (10 ** frac_len) + int(frac_str)
            if sign < 0:
                result_value = -result_value
            return Decimal(result_value, frac_len)
        else:
            if sign < 0:
                int_part = -int_part
            return Decimal(int_part, 0)

    def __rtruediv__(self, other):
        other = self._to_decimal(other)
        return other / self

    def __eq__(self, other):
        other = self._to_decimal(other)
        v1, v2, _ = self._align(other)
        return v1 == v2

    def __ne__(self, other):
        return not self == other

    def __lt__(self, other):
        other = self._to_decimal(other)
        v1, v2, _ = self._align(other)
        return v1 < v2

    def __le__(self, other):
        return self < other or self == other

    def __gt__(self, other):
        return not (self <= other)

    def __ge__(self, other):
        return not (self < other)

    # ==================== pow 相关 ====================

    def exp(self, value):
        if value < 0:
            return 1.0 / self.exp(-value)

        int_part = int(value)
        float_part = value - int_part
        result = Decimal(1)
        term = 1.0
        i = 1
        EPS = Decimal(1) / 10 ** prec
        while abs(term) >= EPS:
            term *= float_part / i
            result += term
            i += 1

        e_pow_int = result  # 已经是 e^fractional_part
        e1 = get_e()  # e 的近似值

        for _ in range(int_part):
            e_pow_int *= e1

        return e_pow_int

    def ln(self, value):
        EPS = Decimal(1) / 10 ** prec
        if value <= 0:
            raise ValueError("ln(x) 定义域为 x > 0")
        if value < 1:
            return -self.ln(1 / value)
        exponent = 0
        while value > 2:
            value /= 2
            exponent += 1

        y = (value - 1) / (value + 1)

        result = 0
        y_pow = y
        i = 1
        while True:
            result += y_pow / i
            y_pow *= y * y
            if y_pow / (i + 2) < EPS:
                break

            i += 2

        result *= 2
        return result + exponent * compute_ln2()

    def __pow__(self, other):
        result = self

        if self == 1:
            return Decimal(1)

        elif other == 0:
            if self != 0:
                return Decimal(1)
            else:
                raise ValueError("0^0 is undefined.")

        elif self == 0:
            if other > 0:
                return 0
            else:
                raise ValueError(f"{int(other)}^0 is undefined.")

        elif isinstance(other, int):
            if other < 0:
                return 1 / self ** (-other)
            for _ in range(other-1):
                result = result * self

            return result

        if isinstance(other, (float, Decimal)):
            other = Decimal(other)
            return self.exp(other * self.ln(self))

    def __rpow__(self, other):
        return other ** self

    def __float__(self):
        return self.value / (10 ** self.fr_len)

    def __int__(self):
        return self.value // (10 ** self.fr_len)

    def __repr__(self):
        if self.value == 0:
            return 'Decimal("0")'

        if self.fr_len == 0:
            return f'Decimal("{self.value}")'

        result = list(str(abs(self.value)))
        neg = self.value < 0

        if self.fr_len >= len(result):
            result = ['0'] * (self.fr_len - len(result) + 1) + result

        result.insert(-self.fr_len, ".")

        if result[0] == ".":
            result.insert(0, "0")
        if neg:
            result.insert(0, "-")

        return f'Decimal("{"".join(result)}")'

    def __str__(self):
        return repr(self)


def pi():
    """丘德诺夫斯基算法"""
    global prec
    prec = prec + 10

    # 常数: 12 / 640320^(3/2)
    C = Decimal(640320) ** Decimal('1.5')
    constant = Decimal(12) / C

    series_sum = Decimal(0)
    n = 0

    while True:
        # 计算 (6n)!
        fact_6n = Decimal(factorial(6 * n))

        # 计算 (n!)^3
        fact_n = Decimal(factorial(n))
        fact_n_3 = fact_n ** 3

        # 计算 (3n)!
        fact_3n = Decimal(factorial(3 * n))

        # 计算分子: (-1)^n * (6n)! * (13591409 + 545140134n)
        numerator = fact_6n * Decimal(13591409 + 545140134 * n)
        if n % 2 == 1:
            numerator = -numerator

        # 计算分母: (n!)^3 * (3n)! * 640320^(3n)
        denominator = fact_n_3 * fact_3n * (Decimal(640320) ** (3 * n))

        term = numerator / denominator

        # 如果项小到可以忽略，停止
        if abs(term) <= Decimal(1) / (10 ** (prec + 5)):
            break

        series_sum += term
        n += 1

    pi = Decimal(1) / (constant * series_sum)
    pi = round(pi, prec - 10)
    return pi
