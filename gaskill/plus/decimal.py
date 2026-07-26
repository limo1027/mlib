from gaskill import gcd

prec = 50


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
                        self.value = int(int_part + frac_part) if int_part else int(frac_part)
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

    def __mul__(self, other):
        other = self._to_decimal(other)
        return Decimal(self.value * other.value, self.fr_len + other.fr_len)

    def __rmul__(self, other):
        return self * other

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

    def _ln_series(self, x, eps):
        """级数计算 ln(x)，x > 0"""
        if x.value <= 0:
            raise ValueError("x 必须 > 0")

        # 转成 float 计算，只用于 ln 内部
        xf = float(x)
        z = (xf - 1) / (xf + 1)
        z2 = z * z
        term = z
        result = 0.0
        n = 1

        while abs(term) > eps:
            result += term
            n += 2
            term = term * z2 * (n - 2) / n

        return 2 * result


    def _ln_float(self, x, eps):
        """ln 的 float 版本"""
        if x <= 0:
            raise ValueError("x 必须 > 0")
        z = (x - 1) / (x + 1)
        z2 = z * z
        term = z
        result = 0.0
        n = 1
        while abs(term) > eps:
            result += term
            n += 2
            term = term * z2 * (n - 2) / n
        return 2 * result


    def _exp_newton(self, x_float, eps):
        """牛顿法计算 e^x"""
        # 处理负数
        if x_float < 0:
            return 1.0 / self._exp_newton(-x_float, eps)

        # 缩放，让 x 在 [-0.5, 0.5] 区间
        n = 1
        x = x_float
        while abs(x) > 0.5:
            x /= 2
            n *= 2

        # 初值：泰勒二阶近似
        y = 1.0 + x + x * x / 2

        for _ in range(50):
            ln_y = self._ln_float(y, eps / 10)
            y_new = y * (1 - ln_y + x)
            if abs(y_new - y) < eps:
                break
            y = y_new

        # 还原缩放：y = y^n（用快速幂）
        result = y
        exp = n
        while exp > 1:
            result *= result
            exp >>= 1
        return result


    def __pow__(self, other):
        other = self._to_decimal(other)
        # 指数为 0
        if other.value == 0:
            return Decimal(1)

        # 指数为整数：快速幂
        if other.fr_len == 0:
            result = Decimal(1)
            base = self
            exp = other.value

            if exp < 0:
                base = Decimal(1) / base
                exp = -exp

            if base.value < 0 and exp % 2 == 1:
                result = Decimal(-1)
                base = Decimal(abs(base.value), base.fr_len)
            elif base.value < 0:
                base = Decimal(abs(base.value), base.fr_len)

            while exp > 0:
                if exp & 1:
                    result = result * base
                base = base * base
                exp >>= 1
            return result

        # 小数指数：负底数检查
        if self.value < 0:
            m = other.value
            n = 10 ** other.fr_len
            g = gcd(abs(m), n)
            m //= g
            n //= g

            if n % 2 == 0:
                raise ValueError("negative base with fractional exponent has no real solution")

            abs_self = Decimal(abs(self.value), self.fr_len)
            result = abs_self ** other
            return -result

        # 正底数：a^b = exp(b * ln(a))
        a = float(self)
        b = float(other)
        neg = False
        if b < 0:
            b = -b
            neg = True

        eps = 10 ** (-prec - 2)
        
        # 先算 ln(a)
        ln_a = self._ln_float(a, eps)
        
        # 再算 exp(b * ln_a)
        result_float = self._exp_newton(b * ln_a, eps)
        if neg:
            result_float = 1 / result_float
        # 转回 Decimal，四舍五入到 prec 位
        result_str = f"{result_float:.{prec + 5}f}"
        # 去掉末尾的 0
        result_str = result_str.rstrip('0').rstrip('.')
        
        if '.' in result_str:
            int_part, frac_part = result_str.split('.')
            # 如果 frac_part 全是 0，转成整数
            if frac_part and all(c == '0' for c in frac_part):
                return Decimal(int(int_part), 0)
            # 否则保留小数
            value_str = int_part + frac_part
            if result_float < 0:
                value = -int(value_str)
            else:
                value = int(value_str)
            return Decimal(value, len(frac_part))
        else:
            return Decimal(int(result_str), 0)
        
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

        return f'Decimal("{''.join(result)}")'

    def __str__(self):
        return repr(self)