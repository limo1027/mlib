from .smath import comb, exp, factorial, pi, sqrt


def erf(x):
    """误差函数 - 混合实现"""
    sign = 1 if x >= 0 else -1
    x = abs(x)

    if x < 1.5:  # 小 x 用泰勒，收敛快
        result = 0.0
        term = x
        n = 0
        while term != 0:
            result += term / (2*n + 1) / (n or 1)  # 0! = 1
            term *= -x * x
            n += 1
            if n > 50:
                break
        return sign * 2 * result / 1.772453850905516

    # 大 x 用近似
    a1, a2, a3, a4, a5 = 0.254829592, - \
        0.284496736, 1.421413741, -1.453152027, 1.061405429
    p = 0.3275911

    t = 1.0 / (1.0 + p * x)
    y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2)
               * t + a1) * t * exp(-x * x)

    return sign * y


def _sum(arr):
    """求和"""
    s = 0
    for x in arr:
        s += x
    return s


def _validate(data, name="data"):
    """验证数据"""
    if not data:
        raise ValueError(f"{name} 不能为空")


# ========== 集中趋势 ==========

def mean(data):
    """算术平均数"""
    _validate(data)
    return _sum(data) / len(data)


def geometric_mean(data):
    """几何平均数"""
    _validate(data)
    if any(x <= 0 for x in data):
        raise ValueError("几何平均数要求所有数据为正数")
    product = 1
    for x in data:
        product *= x
    return product ** (1 / len(data))


def harmonic_mean(data):
    """调和平均数"""
    _validate(data)
    if any(x <= 0 for x in data):
        raise ValueError("调和平均数要求所有数据为正数")
    reciprocal_sum = 0
    for x in data:
        reciprocal_sum += 1 / x
    return len(data) / reciprocal_sum


def median(data):
    """中位数"""
    _validate(data)
    sorted_data = sorted(data)
    n = len(sorted_data)
    mid = n // 2
    if n % 2 == 1:
        return sorted_data[mid]
    return (sorted_data[mid - 1] + sorted_data[mid]) / 2


def mode(data):
    """众数（返回所有众数）"""
    _validate(data)
    freq = {}
    for x in data:
        freq[x] = freq.get(x, 0) + 1

    if not freq:
        return []

    max_freq = max(freq.values())

    if max_freq == 1:
        return []  # 所有值出现一次，无众数

    return [x for x, f in freq.items() if f == max_freq]


def quantile(data, p):
    """分位数, p: 0-1 之间，如 0.25 为 Q1，0.5 为中位数"""
    _validate(data)
    if not 0 <= p <= 1:
        raise ValueError("p 必须在 0-1 之间")

    sorted_data = sorted(data)
    n = len(sorted_data)
    pos = p * (n - 1)
    idx = int(pos)
    frac = pos - idx

    if frac == 0 or idx == n - 1:
        return sorted_data[idx]
    return sorted_data[idx] * (1 - frac) + sorted_data[idx + 1] * frac


def quartiles(data):
    """四分位数 (Q1, Q2, Q3)"""
    return (quantile(data, 0.25), quantile(data, 0.5), quantile(data, 0.75))


def iqr(data):
    """四分位距"""
    q1, _, q3 = quartiles(data)
    return q3 - q1


# ========== 离散程度 ==========

def variance(data, ddof=0):
    """方差（ddof=0 总体方差，ddof=1 样本方差）"""
    _validate(data)
    if len(data) <= ddof:
        raise ValueError("数据长度不足以计算方差")
    m = mean(data)
    s = 0
    for x in data:
        s += (x - m) ** 2
    return s / (len(data) - ddof)


def stdev(data, ddof=0):
    """标准差"""
    return sqrt(variance(data, ddof))


def mad(data):
    """平均绝对偏差"""
    _validate(data)
    m = mean(data)
    s = 0
    for x in data:
        s += abs(x - m)
    return s / len(data)


def range_stat(data):
    """极差"""
    _validate(data)
    return max(data) - min(data)


def cv(data, ddof=0):
    """变异系数"""
    m = mean(data)
    if m == 0:
        raise ValueError("均值为0，无法计算变异系数")
    return stdev(data, ddof) / m


# ========== 分布形态 ==========

def skewness(data, ddof=0):
    """偏度（衡量分布不对称程度）"""
    _validate(data)
    if len(data) < 3:
        return 0.0
    m = mean(data)
    n = len(data)
    s = stdev(data, ddof=ddof)
    if s == 0:
        return 0.0
    third = 0
    for x in data:
        third += ((x - m) / s) ** 3
    return third * n / ((n - 1) * (n - 2))


def kurtosis(data, ddof=0):
    """峰度（衡量分布陡峭程度）"""
    _validate(data)
    if len(data) < 4:
        return 0.0
    m = mean(data)
    n = len(data)
    s = stdev(data, ddof=ddof)
    if s == 0:
        return 0.0
    fourth = 0
    for x in data:
        fourth += ((x - m) / s) ** 4
    return fourth * n * (n + 1) / ((n - 1) * (n - 2) * (n - 3)) - 3 * (n - 1) ** 2 / ((n - 2) * (n - 3))


def covariance(x, y):
    """协方差"""
    if len(x) != len(y):
        raise ValueError("两个数据长度必须相同")
    _validate(x)
    _validate(y)
    if len(x) < 2:
        return 0.0
    mx = mean(x)
    my = mean(y)
    s = 0
    for i in range(len(x)):
        s += (x[i] - mx) * (y[i] - my)
    return s / (len(x) - 1)


def correlation(x, y):
    """皮尔逊相关系数"""
    cov = covariance(x, y)
    sx = stdev(x, ddof=1)
    sy = stdev(y, ddof=1)
    if sx == 0 or sy == 0:
        return 0.0
    return cov / (sx * sy)


def spearman(x, y):
    """斯皮尔曼秩相关系数"""
    if len(x) != len(y):
        raise ValueError("两个数据长度必须相同")
    n = len(x)
    if n < 2:
        return 0.0

    def rank(arr):
        sorted_arr = sorted(arr)
        ranks = {}
        for i, val in enumerate(sorted_arr):
            if val not in ranks:
                ranks[val] = i + 1
        return [ranks[v] for v in arr]

    rx = rank(x)
    ry = rank(y)
    d_sq = [(rx[i] - ry[i]) ** 2 for i in range(n)]
    return 1 - 6 * _sum(d_sq) / (n * (n * n - 1))


def linear_regression(x, y):
    """线性回归 y = a + b*x"""
    if len(x) != len(y):
        raise ValueError("两个数据长度必须相同")
    _validate(x)
    _validate(y)
    if len(x) < 2:
        raise ValueError("至少需要2个数据点")

    mx = mean(x)
    my = mean(y)

    numerator = 0
    denominator = 0
    for i in range(len(x)):
        dx = x[i] - mx
        numerator += dx * (y[i] - my)
        denominator += dx * dx

    if denominator == 0:
        raise ValueError("x 的方差为0")

    slope = numerator / denominator
    intercept = my - slope * mx

    # R²
    ss_res = 0
    ss_tot = 0
    for i in range(len(x)):
        pred = intercept + slope * x[i]
        ss_res += (y[i] - pred) ** 2
        ss_tot += (y[i] - my) ** 2

    r2 = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0

    return (slope, intercept, r2)


# ========== 概率分布函数 ==========

def normal_pdf(x, mu=0, sigma=1):
    """正态分布概率密度函数"""
    if sigma <= 0:
        raise ValueError("sigma 必须大于0")
    return exp(-((x - mu) ** 2) / (2 * sigma ** 2)) / (sigma * (2 * pi) ** 0.5)


def normal_cdf(x, mu=0, sigma=1):
    """正态分布累积分布函数（近似）"""
    return (1 + erf((x - mu) / (sigma * 2 ** 0.5))) / 2


def binomial_pmf(k, n, p):
    """二项分布概率质量函数"""
    if not 0 <= k <= n:
        return 0.0
    if not 0 <= p <= 1:
        raise ValueError("p 必须在 0-1 之间")
    return comb(n, k) * (p ** k) * ((1 - p) ** (n - k))


def poisson_pmf(k, lam):
    """泊松分布概率质量函数"""
    if lam <= 0:
        raise ValueError("lam 必须大于0")
    if k < 0 or k != int(k):
        return 0.0
    k = int(k)
    return exp(-lam) * (lam ** k) / factorial(k)


# ========== 假设检验 ==========

def z_score(x, mu, sigma):
    """Z 分数"""
    if sigma <= 0:
        raise ValueError("sigma 必须大于0")
    return (x - mu) / sigma


def t_test(data, mu0):
    """单样本 t 检验"""
    _validate(data)
    n = len(data)
    if n < 2:
        raise ValueError("至少需要2个数据点")

    x_bar = mean(data)
    s = stdev(data, ddof=1)
    t = (x_bar - mu0) / (s / sqrt(n))

    # p 值（双侧）
    p = 2 * (1 - erf(abs(t) / sqrt(2)))  # 近似
    return (t, p)


def chi_square(observed, expected):
    """卡方检验"""
    if len(observed) != len(expected):
        raise ValueError("观察值和期望值长度必须相同")
    chi2 = 0
    for obs, _exp in zip(observed, expected, strict=False):
        if _exp == 0:
            raise ValueError("期望值不能为0")
        chi2 += (obs - _exp) ** 2 / _exp
    return chi2


def f_test(a, b):
    """F 检验（方差齐性检验）"""
    _validate(a)
    _validate(b)
    if len(a) < 2 or len(b) < 2:
        raise ValueError("每组至少需要2个数据点")

    var_a = variance(a, ddof=1)
    var_b = variance(b, ddof=1)

    if var_a < var_b:
        var_a, var_b = var_b, var_a

    return var_a / var_b


def normalize(data, new_min=0, new_max=1):
    """归一化到 [new_min, new_max]"""
    _validate(data)
    min_val = min(data)
    max_val = max(data)
    if min_val == max_val:
        return [new_min] * len(data)

    result = []
    for x in data:
        t = (x - min_val) / (max_val - min_val)
        result.append(new_min + t * (new_max - new_min))
    return result


def standardize(data):
    """标准化（均值为0，标准差为1）"""
    _validate(data)
    m = mean(data)
    s = stdev(data, ddof=0)
    if s == 0:
        return [0] * len(data)
    return [(x - m) / s for x in data]


# ========== 时间序列 ==========

def rolling_mean(data, window):
    """移动平均"""
    _validate(data)
    if window <= 0 or window > len(data):
        raise ValueError("窗口大小无效")
    result = []
    for i in range(len(data) - window + 1):
        result.append(mean(data[i:i+window]))
    return result


def ewma(data, alpha):
    """指数加权移动平均"""
    _validate(data)
    if not 0 < alpha <= 1:
        raise ValueError("alpha 必须在 (0,1] 之间")

    result = [data[0]]
    for i in range(1, len(data)):
        result.append(alpha * data[i] + (1 - alpha) * result[-1])
    return result


# ========== 统计摘要 ==========

def summary(data):
    """返回完整统计摘要"""
    _validate(data)
    return {
        "count": len(data),
        "mean": mean(data),
        "median": median(data),
        "mode": mode(data),
        "variance": variance(data, ddof=0),
        "stdev": stdev(data, ddof=0),
        "min": min(data),
        "max": max(data),
        "range": max(data) - min(data),
        "q1": quantile(data, 0.25),
        "q3": quantile(data, 0.75),
        "iqr": iqr(data),
        "skewness": skewness(data),
        "kurtosis": kurtosis(data),
    }


def probability_distribution(data):
    """概率分布"""
    _validate(data)
    freq = {}
    for x in data:
        freq[x] = freq.get(x, 0) + 1
    total = len(data)
    return {k: v / total for k, v in freq.items()}
