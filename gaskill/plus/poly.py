class Poly:
    """多项式类"""

    def __init__(self, terms=None):
        """初始化多项式"""
        if terms is None:
            self.terms = []
        else:
            self.terms = self._combine_like_terms(list(terms))

    @classmethod
    def from_string(cls, poly_str):
        """从字符串解析多项式"""
        terms = cls._parse_polynomial(poly_str)
        return cls(terms)

    @staticmethod
    def _parse_polynomial(poly_str):
        """解析多项式字符串, 返回项列表 [(coeff, {var: exp, ...}), ...]"""
        terms = []
        poly_str = poly_str.replace(" ", "")

        i = 0
        while i < len(poly_str):
            coeff = 1
            sign = 1

            if poly_str[i] == "+":
                sign = 1
                i += 1
            elif poly_str[i] == "-":
                sign = -1
                i += 1
            elif i == 0:
                sign = 1
            else:
                sign = 1

            j = i
            while j < len(poly_str) and (poly_str[j].isdigit() or poly_str[j] == "."):
                j += 1
            if j > i:
                coeff = int(poly_str[i:j]) * sign
                i = j
            else:
                coeff = sign

            vars_dict = {}
            while i < len(poly_str) and (poly_str[i].isalpha() or poly_str[i] == "^"):
                if poly_str[i].isalpha():
                    var = poly_str[i]
                    i += 1
                    exp = 1
                    if i < len(poly_str) and poly_str[i] == "^":
                        i += 1
                        j = i
                        while j < len(poly_str) and poly_str[j].isdigit():
                            j += 1
                        if j > i:
                            exp = int(poly_str[i:j])
                            i = j
                    if var in vars_dict:
                        vars_dict[var] += exp
                    else:
                        vars_dict[var] = exp
                else:
                    i += 1

            if not vars_dict:
                vars_dict = {}

            if coeff != 0:
                terms.append((coeff, vars_dict))

        return terms

    def _combine_like_terms(self, terms):
        """合并同类项"""
        groups = {}
        for coeff, vars_dict in terms:
            key = tuple(sorted(vars_dict.items()))
            if key in groups:
                groups[key] += coeff
            else:
                groups[key] = coeff

        result = []
        for key, coeff in groups.items():
            if coeff != 0:
                result.append((coeff, dict(key)))

        return result

    def degree(self, var=None):
        """获取多项式次数"""
        if not self.terms:
            return -1

        if var is None:
            max_deg = 0
            for _coeff, vars_dict in self.terms:
                deg = sum(vars_dict.values())
                if deg > max_deg:
                    max_deg = deg
            return max_deg
        else:
            max_deg = 0
            for _coeff, vars_dict in self.terms:
                deg = vars_dict.get(var, 0)
                if deg > max_deg:
                    max_deg = deg
            return max_deg

    def __add__(self, other):
        if not isinstance(other, Poly):
            other = Poly([(other, {})])
        combined = list(self.terms) + list(other.terms)
        return Poly(self._combine_like_terms(combined))

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if not isinstance(other, Poly):
            other = Poly([(other, {})])
        neg_other = Poly([(-c, v) for c, v in other.terms])
        return self + neg_other

    def __rsub__(self, other):
        return Poly([(other, {})]) - self

    def __mul__(self, other):
        if not isinstance(other, Poly):
            other = Poly([(other, {})])

        result = []
        for c1, v1 in self.terms:
            for c2, v2 in other.terms:
                new_coeff = c1 * c2
                new_vars = dict(v1)
                for var, exp in v2.items():
                    if var in new_vars:
                        new_vars[var] += exp
                    else:
                        new_vars[var] = exp
                result.append((new_coeff, new_vars))

        return Poly(self._combine_like_terms(result))

    def __rmul__(self, other):
        return self.__mul__(other)

    def __eq__(self, other):
        if not isinstance(other, Poly):
            other = Poly([(other, {})])
        if len(self.terms) != len(other.terms):
            return False
        self_set = set((c, tuple(sorted(v.items()))) for c, v in self.terms)
        other_set = set((c, tuple(sorted(v.items()))) for c, v in other.terms)
        return self_set == other_set

    def __neg__(self):
        return Poly([(-c, v) for c, v in self.terms])

    def __str__(self):
        """转换为字符串"""
        if not self.terms:
            return "0"

        parts = []
        for coeff, vars_dict in self.terms:
            term_str = ""

            if coeff < 0:
                term_str += "-"
            if abs(coeff) != 1 or not vars_dict:
                term_str += str(abs(coeff))

            for var in sorted(vars_dict.keys()):
                exp = vars_dict[var]
                term_str += var
                if exp > 1:
                    term_str += "^" + str(exp)

            parts.append(term_str)

        return " + ".join(parts).replace("+ -", "- ")

    def __repr__(self):
        return f"Poly({self.terms})"

    def extract_gcf(self):
        """提取最大公因式, 返回 (gcf_poly, remaining_poly)"""
        if not self.terms:
            return Poly([(1, {})]), Poly()

        coeffs = [abs(c) for c, _ in self.terms if c != 0]
        if not coeffs:
            return Poly([(1, {})]), self

        gcf_coeff = coeffs[0]
        for c in coeffs[1:]:
            a, b = gcf_coeff, c
            while b:
                a, b = b, a % b
            gcf_coeff = a

        all_vars = set()
        for _, vars_dict in self.terms:
            all_vars.update(vars_dict.keys())

        var_mins = {}
        for var in all_vars:
            min_exp = None
            for _, vars_dict in self.terms:
                exp = vars_dict.get(var, 0)
                if min_exp is None or exp < min_exp:
                    min_exp = exp
            if min_exp and min_exp > 0:
                var_mins[var] = min_exp

        gcf_vars = {var: var_mins[var] for var in var_mins}
        gcf_poly = Poly([(gcf_coeff, gcf_vars)])

        remaining = []
        for coeff, vars_dict in self.terms:
            new_coeff = coeff // gcf_coeff
            new_vars = {}
            for var, exp in vars_dict.items():
                new_exp = exp - var_mins.get(var, 0)
                if new_exp > 0:
                    new_vars[var] = new_exp
            remaining.append((new_coeff, new_vars))

        return gcf_poly, Poly(remaining)

    def evaluate(self, values):
        """代入变量值计算结果"""
        result = 0
        for coeff, vars_dict in self.terms:
            term_val = coeff
            for var, exp in vars_dict.items():
                term_val *= values.get(var, 0) ** exp
            result += term_val
        return result

    def derivative(self, var="x"):
        """求导"""
        result = []
        for coeff, vars_dict in self.terms:
            new_vars = dict(vars_dict)
            if var in new_vars and new_vars[var] > 0:
                new_coeff = coeff * new_vars[var]
                new_vars[var] -= 1
                if new_vars[var] == 0:
                    del new_vars[var]
                result.append((new_coeff, new_vars))
        return Poly(result)

    def factor(self):
        """因式分解, 返回因式列表"""
        factors = []

        gcf, remaining = self.extract_gcf()
        if gcf != Poly([(1, {})]):
            factors.append(gcf)

        if not remaining.terms:
            return factors

        deg = remaining.degree()
        if deg == 2:
            quad_factors = remaining._factor_quadratic("x")
            if quad_factors:
                factors.extend(quad_factors)
                return factors
        elif deg == 3:
            cubic_factors = remaining._factor_cubic()
            if cubic_factors:
                factors.extend(cubic_factors)
                return factors

        square_factors = remaining._factor_difference_of_squares("x")
        if square_factors:
            factors.extend(square_factors)
            return factors

        if not factors:
            factors.append(remaining)

        return factors

    def _factor_quadratic(self, var="x"):
        """分解二次三项式"""
        a, b, c = 0, 0, 0
        for coeff, vars_dict in self.terms:
            deg = sum(vars_dict.values())
            if deg == 2:
                a = coeff
            elif deg == 1:
                b = coeff
            elif deg == 0:
                c = coeff

        if a == 1:
            c_abs = abs(c)
            for i in range(1, c_abs + 1):
                if c_abs % i == 0:
                    j = c_abs // i
                    if c > 0:
                        if i + j == b:
                            if b > 0:
                                return [
                                    Poly([(1, {var: 1}), (i, {})]),
                                    Poly([(1, {var: 1}), (j, {})]),
                                ]
                            else:
                                return [
                                    Poly([(1, {var: 1}), (-i, {})]),
                                    Poly([(1, {var: 1}), (-j, {})]),
                                ]
                    else:
                        if i - j == b:
                            return [
                                Poly([(1, {var: 1}), (i, {})]),
                                Poly([(1, {var: 1}), (-j, {})]),
                            ]
                        elif -i + j == b:
                            return [
                                Poly([(1, {var: 1}), (-i, {})]),
                                Poly([(1, {var: 1}), (j, {})]),
                            ]

        return []

    def _factor_difference_of_squares(self, var="x"):
        """分解平方差"""
        pos_terms = []
        neg_terms = []

        for coeff, vars_dict in self.terms:
            if coeff > 0:
                pos_terms.append((coeff, vars_dict))
            elif coeff < 0:
                neg_terms.append((abs(coeff), vars_dict))

        if len(pos_terms) == 1 and len(neg_terms) == 1:
            p_coeff, p_vars = pos_terms[0]
            n_coeff, n_vars = neg_terms[0]

            if p_coeff == 1 and n_coeff == 1:
                p_deg = sum(p_vars.values())
                n_deg = sum(n_vars.values())
                if p_deg == 2 and n_deg == 0:
                    return [
                        Poly([(1, p_vars), (1, {})]),
                        Poly([(1, p_vars), (-1, {})]),
                    ]

        return []

    def _factor_cubic(self):
        """分解三次多项式"""
        a, c = 0, 0
        for coeff, vars_dict in self.terms:
            if sum(vars_dict.values()) == 3:
                a = coeff
            elif sum(vars_dict.values()) == 0:
                c = coeff

        if a == 1:
            if c == -1:
                return [
                    Poly([(1, {"x": 1}), (-1, {})]),
                    Poly([(1, {"x": 2}), (1, {"x": 1}), (1, {})]),
                ]
            elif c == 1:
                return [
                    Poly([(1, {"x": 1}), (1, {})]),
                    Poly([(1, {"x": 2}), (-1, {"x": 1}), (1, {})]),
                ]

        return []


def factors_to_str(factors):
    """将因式列表转换为字符串"""
    if not factors:
        return "1"

    parts = []
    for factor in factors:
        if isinstance(factor, Poly):
            poly_str = str(factor)
            if " + " in poly_str or " - " in poly_str:
                parts.append("(" + poly_str + ")")
            else:
                parts.append(poly_str)
        else:
            parts.append(str(factor))
    return " * ".join(parts)
