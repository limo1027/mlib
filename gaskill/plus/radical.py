# -*- coding: utf-8 -*-
from gaskill import Frac
from gaskill import comb, prime_factors as factorize
from gaskill import superscript


class Radical:
    """
    表示 coeff * (radicand)^(1/index)
    radicand 可以是：
      - int / float               （数字）
      - Radical                    （嵌套根式）
      - tuple                      （和式）
    """

    def __init__(self, index, radicand, coeff=1):
        self.index = index
        self.radicand = radicand
        self.coeff = coeff
        self._simplify()

    # ---------- 化简 ----------
    def _simplify(self):
        if self.coeff == 0:
            self.index = 1
            self.radicand = 0
            return

        if self.radicand == 1:
            self.index = 1
            self.radicand = 1
            return

        # 数字
        if isinstance(self.radicand, (int, float)):
            if self.index == 1:
                if self.radicand < 0:
                    self.coeff *= -1
                    self.radicand = -self.radicand
                return

            if isinstance(self.radicand, int) and self.radicand > 0:
                n = self.radicand
                factors = {}
                d = 2
                while d * d <= n:
                    while n % d == 0:
                        factors[d] = factors.get(d, 0) + 1
                        n //= d
                    d += 1
                if n > 1:
                    factors[n] = factors.get(n, 0) + 1

                outside = 1
                inside = 1
                for p, e in factors.items():
                    q, r = divmod(e, self.index)
                    if q:
                        outside *= p ** q
                    if r:
                        inside *= p ** r

                self.coeff *= outside
                self.radicand = inside
                if self.radicand == 1:
                    self.index = 1
            return

        # Frac
        if isinstance(self.radicand, Frac):
            if self.index == 1:
                return

            num_factors = factorize(self.radicand.n)
            den_factors = factorize(self.radicand.d)

            outside_num = 1
            inside_num = 1
            for p, e in num_factors.items():
                q, r = divmod(e, self.index)
                if q:
                    outside_num *= p ** q
                if r:
                    inside_num *= p ** r

            outside_den = 1
            inside_den = 1
            for p, e in den_factors.items():
                q, r = divmod(e, self.index)
                if q:
                    outside_den *= p ** q
                if r:
                    inside_den *= p ** r

            self.coeff *= outside_num / outside_den
            if inside_num == 1 and inside_den == 1:
                self.radicand = 1
                self.index = 1
            elif inside_den == 1:
                self.radicand = inside_num
            else:
                self.radicand = Frac(inside_num, inside_den)
            return

        # 嵌套根式
        if isinstance(self.radicand, Radical):
            self.index = self.index * self.radicand.index
            self.radicand = self.radicand.radicand
            self._simplify()
            return

        # 和式 (tuple)
        if isinstance(self.radicand, tuple):
            if self.index == 1:
                flat_terms = []
                for item in self.radicand:
                    if isinstance(item, Radical):
                        if item.coeff == 0:
                            continue
                        item = Radical(item.index, item.radicand,
                                       item.coeff * self.coeff)
                        if item.index == 1 and isinstance(item.radicand, tuple):
                            for sub in item.radicand:
                                flat_terms.append(
                                    Radical(sub.index, sub.radicand, sub.coeff * self.coeff))
                            continue
                        flat_terms.append(item)
                    else:
                        flat_terms.append(item * self.coeff)

                groups = {}
                for term in flat_terms:
                    if isinstance(term, Radical):
                        key = (term.index, term.radicand)
                        if key in groups:
                            groups[key] = groups[key] + term
                        else:
                            groups[key] = term
                    else:
                        if 0 in groups:
                            groups[0] = groups[0] + term
                        else:
                            groups[0] = term

                new_terms = [v for v in groups.values() if v != 0 and (
                    isinstance(v, Radical) and v.radicand != 0)]

                if not new_terms:
                    self.index = 1
                    self.radicand = 0
                    self.coeff = 1
                    return
                if len(new_terms) == 1:
                    t = new_terms[0]
                    if isinstance(t, Radical):
                        self.index = t.index
                        self.radicand = t.radicand
                        self.coeff = t.coeff
                    else:
                        self.index = 1
                        self.radicand = t
                        self.coeff = 1
                    return
                self.radicand = tuple(new_terms)
                self.coeff = 1
                return

            # index > 1，尝试化简
            temp = Radical(1, self.radicand, 1)
            if temp.index == 1 and isinstance(temp.radicand, (int, float)):
                self.radicand = temp.radicand
                self._simplify()

    # ---------- 乘法辅助 ----------
    def _mul_radicand(self, a, b):
        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
            return a * b

        if isinstance(a, (int, float)):
            if a == 1:
                return b
            if isinstance(b, tuple):
                return tuple(self._mul_radicand(a, x) for x in b)
            if isinstance(b, Radical):
                return Radical(b.index, b.radicand, a * b.coeff)
            return a * b

        if isinstance(b, (int, float)):
            return self._mul_radicand(b, a)

        if isinstance(a, tuple) and isinstance(b, tuple):
            if len(a) == 1:
                a = a[0]
            if len(b) == 1:
                b = b[0]
            if not isinstance(a, tuple) or not isinstance(b, tuple):
                return self._mul_radicand(a, b)

            terms = []
            for x in a:
                for y in b:
                    terms.append(self._mul_radicand(x, y))
            return self._merge_terms(terms)

        if isinstance(a, tuple):
            if len(a) == 1:
                return self._mul_radicand(a[0], b)
            return tuple(self._mul_radicand(x, b) for x in a)

        if isinstance(b, tuple):
            if len(b) == 1:
                return self._mul_radicand(a, b[0])
            return tuple(self._mul_radicand(a, x) for x in b)

        if isinstance(a, Radical) and isinstance(b, Radical):
            new_coeff = a.coeff * b.coeff
            if a.index == b.index:
                new_rad = self._mul_radicand(a.radicand, b.radicand)
                return Radical(a.index, new_rad, new_coeff)
            common_idx = a.index * b.index
            r1 = self._pow_radicand(a.radicand, b.index)
            r2 = self._pow_radicand(b.radicand, a.index)
            new_rad = self._mul_radicand(r1, r2)
            return Radical(common_idx, new_rad, new_coeff)

        return (a, b)

    # ---------- 幂运算 ----------
    def _pow_radicand(self, radicand, exp):
        if exp == 0:
            return 1
        if exp == 1:
            return radicand

        if isinstance(radicand, (int, float)):
            return radicand ** exp

        if isinstance(radicand, Radical):
            new_coeff = radicand.coeff ** exp
            inner = radicand.radicand
            idx = radicand.index

            inner_pow = self._pow_radicand(inner, exp)

            if exp % idx == 0:
                k = exp // idx
                inner_k = self._pow_radicand(inner, k)
                if new_coeff != 1:
                    if isinstance(inner_k, (int, float)):
                        return inner_k * new_coeff
                    return Radical(1, inner_k, new_coeff)
                return inner_k
            else:
                return Radical(idx, inner_pow, new_coeff)

        if isinstance(radicand, tuple):
            return self._pow_tuple(radicand, exp)

        return radicand

    def _pow_tuple(self, terms, exp):
        if not terms:
            return 0
        if len(terms) == 1:
            return self._pow_radicand(terms[0], exp)
        if exp == 0:
            return 1
        if exp == 1:
            return terms if len(terms) > 1 else terms[0]

        if len(terms) == 2:
            a, b = terms[0], terms[1]
            result = []
            for k in range(exp + 1):
                coeff = comb(exp, k)
                term_a = self._pow_radicand(a, k)
                term_b = self._pow_radicand(b, exp - k)
                product = self._mul_radicand(term_a, term_b)
                if coeff != 1:
                    product = self._mul_radicand(coeff, product)
                result.append(product)
            return self._merge_terms(result)

        first = terms[0]
        rest = terms[1:]
        result = []
        for k in range(exp + 1):
            coeff = self._comb(exp, k)
            term_a = self._pow_radicand(first, k)
            term_b = self._pow_radicand(rest, exp - k)
            product = self._mul_radicand(term_a, term_b)
            if coeff != 1:
                product = self._mul_radicand(coeff, product)
            result.append(product)
        return self._merge_terms(result)

    def _merge_terms(self, terms):
        if not terms:
            return 0
        if len(terms) == 1:
            return terms[0]

        groups = {}
        for term in terms:
            if isinstance(term, Radical):
                key = (term.index, term.radicand)
                if key in groups:
                    groups[key] = groups[key] + term
                else:
                    groups[key] = term
            else:
                if 0 in groups:
                    groups[0] = groups[0] + term
                else:
                    groups[0] = term

        merged = [v for v in groups.values() if v != 0]
        if not merged:
            return 0
        if len(merged) == 1:
            return merged[0]
        return tuple(merged)

    # ---------- 共轭 ----------
    def conjugate(self):
        if self.index == 1 and isinstance(self.radicand, tuple) and len(self.radicand) == 2:
            a, b = self.radicand[0], self.radicand[1]
            if isinstance(b, Radical):
                return Radical(1, (a, Radical(b.index, b.radicand, -b.coeff)), self.coeff)
            if isinstance(b, (int, float)):
                return Radical(1, (a, -b), self.coeff)
        return None

    # ---------- 运算符 ----------
    def __add__(self, other):
        if not isinstance(other, Radical):
            other = Radical(1, other, 1)
        if self.coeff == 0:
            return other
        if other.coeff == 0:
            return self

        def to_frac(val):
            if isinstance(val, Frac):
                return val
            if isinstance(val, (int, float)):
                return Frac(val)
            return val

        if self.index == other.index and self.radicand == other.radicand:
            return Radical(self.index, self.radicand, to_frac(self.coeff) + to_frac(other.coeff))

        if self.index == 1 and isinstance(self.radicand, tuple):
            return Radical(1, self.radicand + (other,), 1)

        if other.index == 1 and isinstance(other.radicand, tuple):
            return other + self

        return Radical(1, (self, other), 1)

    def __radd__(self, other):
        return self + other

    def __sub__(self, other):
        if not isinstance(other, Radical):
            other = Radical(1, other, 1)
        return self + Radical(other.index, other.radicand, -other.coeff)

    def __rsub__(self, other):
        return Radical(1, other, 1) - self

    def __mul__(self, other):
        if not isinstance(other, Radical):
            other = Radical(1, other, 1)
        if self.coeff == 0 or other.coeff == 0:
            return Radical(1, 0, 0)

        def to_frac(val):
            if isinstance(val, Frac):
                return val
            if isinstance(val, (int, float)):
                return Frac(val)
            return val

        new_coeff = to_frac(self.coeff) * to_frac(other.coeff)

        if self.index == 1 and isinstance(self.radicand, (int, float)) and other.index == 1 and isinstance(other.radicand, (int, float)):
            return Radical(1, self.radicand * other.radicand, new_coeff)

        if self.index == other.index:
            new_rad = self._mul_radicand(self.radicand, other.radicand)
            if isinstance(new_rad, tuple):
                new_rad = Radical(1, new_rad, 1)
            return Radical(self.index, new_rad, new_coeff)

        common_idx = self.index * other.index
        r1 = self._pow_radicand(self.radicand, other.index)
        r2 = self._pow_radicand(other.radicand, self.index)
        new_rad = self._mul_radicand(r1, r2)
        return Radical(common_idx, new_rad, new_coeff)

    def __rmul__(self, other):
        return self * other

    def __truediv__(self, other):
        if not isinstance(other, Radical):
            other = Radical(1, other, 1)
        if other.coeff == 0:
            raise ZeroDivisionError("Division by zero")

        def to_frac(val):
            if isinstance(val, Frac):
                return val
            if isinstance(val, (int, float)):
                return Frac(val)
            return val

        # 分母是数字
        if other.index == 1 and isinstance(other.radicand, (int, float, Frac)):
            if self.index == 1 and isinstance(self.radicand, tuple):
                terms = list(self.radicand)
                new_terms = []
                for term in terms:
                    if isinstance(term, Radical):
                        new_terms.append(Radical(term.index, term.radicand, to_frac(
                            term.coeff) / to_frac(other.radicand)))
                    else:
                        new_terms.append(term / other.radicand)
                return Radical(1, tuple(new_terms), 1)
            return Radical(self.index, self.radicand, to_frac(self.coeff) / to_frac(other.radicand))

        # 分母是二项式 → 共轭有理化
        if other.index == 1 and isinstance(other.radicand, tuple) and len(other.radicand) == 2:
            conj = other.conjugate()
            if conj:
                return (self * conj) / (other * conj)

        # 同类根式
        if self.index == other.index and self.radicand == other.radicand:
            return Radical(1, 1, to_frac(self.coeff) / to_frac(other.coeff))

        # 分子是单项式
        if not (isinstance(other.radicand, (tuple)) and isinstance(self.radicand, tuple)):
            n = other ** (other.index - 1) * self
            d = other.coeff ** other.index * other.radicand
            return n / d

        # 一般情况
        common_idx = self.index * other.index
        r1 = self._pow_radicand(self.radicand, other.index)
        r2 = self._pow_radicand(other.radicand, self.index)
        new_rad = self._mul_radicand(r1, r2)
        return Radical(common_idx, new_rad, to_frac(self.coeff) / to_frac(other.coeff))

    def __rtruediv__(self, other):
        return Radical(1, other, 1) / self

    def __neg__(self):
        return Radical(self.index, self.radicand, -self.coeff)

    def __pos__(self):
        return self

    def __pow__(self, exp):
        if not isinstance(exp, int) or exp < 0:
            raise ValueError("Exponent must be a non-negative integer")
        if exp == 0:
            return Radical(1, 1, 1)
        if exp == 1:
            return self

        result = self
        for i in range(exp-1):
            result *= self

        return result

    # ---------- 显示 ----------
    def __eq__(self, other):
        if not isinstance(other, Radical):
            return False
        if self.index != other.index:
            return False
        if self.coeff != other.coeff:
            return False

        def is_simple(val):
            return isinstance(val, (int, float, str, Frac))

        if is_simple(self.radicand) and is_simple(other.radicand):
            return self.radicand == other.radicand
        return repr(self.radicand) == repr(other.radicand)

    def __hash__(self):
        return hash((self.index, self.radicand, self.coeff))

    def _to_str(self, radicand):
        if isinstance(radicand, Frac):
            if radicand.d == 1:
                return str(radicand.n)
            return f"({radicand.n}/{radicand.d})"
        if isinstance(radicand, (int, float)):
            return str(radicand)
        if isinstance(radicand, Radical):
            return str(radicand)

        if isinstance(radicand, tuple):
            parts = []
            for i, x in enumerate(radicand):
                s = self._to_str(x)
                if i == 0:
                    parts.append(s)
                elif s.startswith('-'):
                    parts.append(" - " + s[1:])
                else:
                    parts.append(" + " + s)
            return "(" + "".join(parts) + ")"

        return str(radicand)

    def __str__(self):
        if self.coeff == 0:
            return "0"

        def fmt(c):
            if isinstance(c, Frac):
                return str(c.n) if c.d == 1 else f"({c.n}/{c.d})"
            if isinstance(c, float) and c == int(c):
                return str(int(c))
            return str(c)

        def is_one(c):
            return (isinstance(c, Frac) and c.n == 1 and c.d == 1) or c == 1

        def is_neg_one(c):
            return (isinstance(c, Frac) and c.n == -1 and c.d == 1) or c == -1

        if self.index == 1:
            if self.radicand == 1:
                return fmt(self.coeff)
            rad_str = self._to_str(self.radicand)
            if is_one(self.coeff):
                return rad_str
            if is_neg_one(self.coeff):
                return "-" + rad_str
            return fmt(self.coeff) + "*" + rad_str

        rad_str = self._to_str(self.radicand)
        root = "√" if self.index == 2 else f"{superscript(self.index)}√"
        if is_one(self.coeff):
            return f"{root}({rad_str})"
        if is_neg_one(self.coeff):
            return f"-{root}({rad_str})"
        return fmt(self.coeff) + "*" + f"{root}({rad_str})"

    def __repr__(self):
        return str(self)

    def approx(self):
        """返回浮点数近似值"""
        if self.coeff == 0:
            return 0.0

        coeff_val = float(self.coeff) if isinstance(
            self.coeff, (int, float, Frac)) else float(self.coeff)

        # 计算 radicand 的近似值
        if isinstance(self.radicand, (int, float)):
            rad_val = float(self.radicand)
        elif isinstance(self.radicand, Frac):
            rad_val = self.radicand.n / self.radicand.d
        elif isinstance(self.radicand, Radical):
            rad_val = self.radicand.approx()
        elif isinstance(self.radicand, tuple):
            # 和式：逐项相加
            rad_val = 0
            for term in self.radicand:
                if isinstance(term, Radical):
                    rad_val += term.approx()
                else:
                    rad_val += float(term)
        else:
            rad_val = float(self.radicand)

        # 处理负数
        if rad_val < 0 and self.index % 2 == 0:
            raise ValueError(
                f"Cannot take even root of negative number: {rad_val}")

        # 开根号
        if rad_val >= 0:
            result = rad_val ** (1.0 / self.index)
        else:
            result = -((-rad_val) ** (1.0 / self.index))

        return coeff_val * result

    def __float__(self):
        """支持 float() 转换"""
        return self.approx()


def real_sqrt(n):
    return Radical(2, n)


def real_root(n, x):
    return Radical(x, n)
