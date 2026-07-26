prec = 50


class Decimal:
    def __init__(self, value, fr_len=None):
        if fr_len is not None:
            self.value = value
            self.fr_len = fr_len
            self._simplify()
            return
        self.value = float(value)
        self.fr_len = len(str(self.value).split(".")[-1])
        self.value = int(self.value * (10 ** self.fr_len))
        self._simplify()

    def _simplify(self):
        while self.value % 10 == 0 and self.value != 0:
            self.value //= 10
            self.fr_len -= 1

    def _to_decimal(self, value):
        if isinstance(value, Decimal):
            return value
        return Decimal(value)

    def __add__(self, other):
        other = self._to_decimal(other)

        if self.value == 0:
            return other
        if other.value == 0:
            return self

        v1, f1 = self.value, self.fr_len
        v2, f2 = other.value, other.fr_len

        while f1 != f2:
            if f1 > f2:
                v2 *= 10
                f2 += 1
            else:
                v1 *= 10
                f1 += 1

        return Decimal(v1 + v2, f1)

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
        result = ""
        mod = self.value
        for _ in range(prec):
            quo, mod = divmod(mod, other.value)
            result += str(int(quo))
            mod *= 10
        return Decimal(int(result), prec)

    def __rtruediv__(self, other):
        return self / other

    def __eq__(self, other):
        other = self._to_decimal(other)
        return self.value == other.value and self.fr_len == other.fr_len

    def __ne__(self, other):
        return not self == other

    def __lt__(self, other):
        if self.fr_len != other.fr_len and len(str(self.value)) == len(str(other.value)):
            return self.fr_len > other.fr_len
        for i, j in zip(str(self.value), str(other.value)):
            if i < j:
                return True
            elif i > j:
                return False

    def __le__(self, other):
        return self < other or self == other

    def __gt__(self, other):
        return not (self == other or self < other)

    def __ge__(self, other):
        return self == other or self > other

    def __float__(self):
        return self.value / (10 ** self.fr_len)

    def __repr__(self):
        result = list(str(int(abs(self.value))))
        neg = self.value < 0
        if self.fr_len >= len(result):
            for _ in range(self.fr_len - len(result) - 1):
                result.insert(0, "0")
        result.insert(-self.fr_len + 1, ".")
        if result[0] == ".":
            result.insert(0, "0")
        if neg:
            result.insert(0, "-")
        return f'Decimal("{''.join(result)}")'

    def __str__(self):
        return repr(self)
