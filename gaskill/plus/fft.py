from gaskill import Complex, exp, pi

# ============================================================
# 辅助函数
# ============================================================

def _next_power_of_2(n):
    """计算大于等于 n 的最小 2 的幂次"""
    if n <= 0:
        return 1
    power = 1
    while power < n:
        power <<= 1
    return power


def _fft_recursive(x):
    """
    递归 FFT 实现（要求长度为 2 的幂次）
    """
    N = len(x)

    if N == 1:
        return x

    # 奇偶拆分
    even = _fft_recursive(x[0::2])
    odd = _fft_recursive(x[1::2])

    # 蝶形合并
    X = [Complex(0, 0)] * N
    half = N // 2

    for k in range(half):
        angle = -2 * pi * k / N
        twiddle = exp(Complex(0, angle))
        X[k] = even[k] + twiddle * odd[k]
        X[k + half] = even[k] - twiddle * odd[k]

    return X


# ============================================================
# 核心变换
# ============================================================

def fft(x):
    """快速傅里叶变换（支持任意长度）"""
    N = len(x)

    # 边界情况
    if N == 0:
        return [], 0
    if N == 1:
        return x[:], 1

    # 计算补零后的长度（2 的幂次）
    N_padded = _next_power_of_2(N)

    # 如果已经是 2 的幂次，不需要补零
    if N == N_padded:
        return _fft_recursive(x), N

    # 补零到 2 的幂次
    x_padded = x + [Complex(0, 0)] * (N_padded - N)
    X = _fft_recursive(x_padded)

    return X, N


def ifft(X, original_length=None):
    """快速傅里叶逆变换"""
    N = len(X)

    if N == 0:
        return []
    if N == 1:
        if original_length is not None and original_length == 0:
            return []
        return X[:]

    # 共轭 → FFT → 共轭 → 除以 N
    X_conj = [Complex(c.real, -c.imag) for c in X]
    x_conj = _fft_recursive(X_conj)
    x = [Complex(c.real / N, -c.imag / N) for c in x_conj]

    # 如果指定了原始长度，截断
    if original_length is not None:
        return x[:original_length]

    return x


# ============================================================
# 频率工具
# ============================================================

def fftfreq(N, d=1.0):
    """生成 FFT 的频率坐标"""
    if N <= 0:
        return []

    result = []
    for k in range(N):
        if k < (N + 1) // 2:
            result.append(k / (N * d))
        else:
            result.append((k - N) / (N * d))

    return result


def fftshift(x):
    """将零频分量移到数组中心"""
    N = len(x)
    if N <= 1:
        return x[:]

    half = N // 2
    if N % 2 == 0:
        return x[half:] + x[:half]
    else:
        return x[half+1:] + x[:half+1]


def ifftshift(x):
    """fftshift 的逆操作"""
    N = len(x)
    if N <= 1:
        return x[:]

    half = N - N // 2
    return x[half:] + x[:half]


# ============================================================
# 频谱分析
# ============================================================

def magnitude_spectrum(x, shift=False):
    """计算幅值谱"""
    X, _ = fft(x)
    magnitude = [((c.real ** 2 + c.imag ** 2) ** 0.5) for c in X]

    if shift:
        magnitude = fftshift(magnitude)

    return magnitude


def power_spectrum(x, shift=False):
    """计算功率谱 |X|^2"""
    X, _ = fft(x)
    power = [(c.real ** 2 + c.imag ** 2) for c in X]

    if shift:
        power = fftshift(power)

    return power


def phase_spectrum(x, shift=False):
    """计算相位谱 angle(X)"""
    from math import atan2
    X, _ = fft(x)
    phase = [atan2(c.imag, c.real) for c in X]

    if shift:
        phase = fftshift(phase)

    return phase
