from .smath import cos, pi, sin

# ========== 基本缓动 ==========


def linear(t):
    """匀速"""
    return t


def quad_in(t):
    """加速 - t²"""
    return t * t


def quad_out(t):
    """减速 - t*(2-t)"""
    return t * (2 - t)


def quad_in_out(t):
    """先加速后减速"""
    if t < 0.5:
        return 2 * t * t
    else:
        return -1 + (4 - 2 * t) * t

# ========== 三次缓动 ==========


def cubic_in(t):
    """加速 - t³"""
    return t * t * t


def cubic_out(t):
    """三次缓出"""
    t -= 1
    return t * t * t + 1


def cubic_in_out(t):
    """先加速后减速(三次)"""
    if t < 0.5:
        return 4 * t * t * t
    else:
        t = 2 * t - 2
        return 0.5 * t * t * t + 1

# ========== 弹性缓动 ==========


def back_in(t):
    """先回拉再前进"""
    s = 1.70158
    return t * t * ((s + 1) * t - s)


def back_out(t):
    """回弹缓出"""
    s = 1.70158
    t -= 1
    return t * t * ((s + 1) * t + s) + 1

# ========== 弹跳缓动 ==========


def bounce_out(t):
    """落地弹跳效果"""
    if t < 1/2.75:
        return 7.5625 * t * t
    elif t < 2/2.75:
        t -= 1.5/2.75
        return 7.5625 * t * t + 0.75
    elif t < 2.5/2.75:
        t -= 2.25/2.75
        return 7.5625 * t * t + 0.9375
    else:
        t -= 2.625/2.75
        return 7.5625 * t * t + 0.984375


# ========== 工具函数 ==========

def tween(start, end, duration, elapsed, easing=linear):
    """实际补间计算"""
    if elapsed >= duration:
        return end
    if elapsed <= 0:
        return start

    t = elapsed / duration
    return start + (end - start) * easing(t)


class Tween:
    """简单的补间动画类"""

    def __init__(self, start, end, duration, easing=linear):
        self.start = start
        self.end = end
        self.duration = duration
        self.easing = easing
        self.elapsed = 0
        self.completed = False

    def update(self, dt):
        """更新补间动画"""
        if self.completed:
            return self.end

        self.elapsed += dt
        if self.elapsed >= self.duration:
            self.completed = True
            return self.end

        t = self.elapsed / self.duration
        return self.start + (self.end - self.start) * self.easing(t)

    def reset(self):
        """重置补间动画状态"""
        self.elapsed = 0
        self.completed = False

# ========== 指数缓动 ==========


def expo_in(t):
    """指数加速"""
    return 0 if t == 0 else 2 ** (10 * (t - 1))


def expo_out(t):
    """指数减速"""
    return 1 if t == 1 else 1 - 2 ** (-10 * t)


def expo_in_out(t):
    """先加速后减速（指数）"""
    if t == 0 or t == 1:
        return t
    t *= 2
    if t < 1:
        return 0.5 * 2 ** (10 * (t - 1))
    return 0.5 * (2 - 2 ** (-10 * (t - 1)))

# ========== 圆形缓动 ==========


def circ_in(t):
    """圆形加速"""
    return 1 - (1 - t * t) ** 0.5


def circ_out(t):
    """圆形减速"""
    t -= 1
    return (1 - t * t) ** 0.5


def circ_in_out(t):
    """先加速后减速（圆形）"""
    t *= 2
    if t < 1:
        return -0.5 * ((1 - t * t) ** 0.5 - 1)
    t -= 2
    return 0.5 * ((1 - t * t) ** 0.5 + 1)

# ========== 更弹的弹性 ==========


def elastic_out(t, amplitude=1, period=0.3):
    """弹性缓出（可调参数）"""
    if t == 0 or t == 1:
        return t

    s = period / 4
    return amplitude * 2 ** (-10 * t) * sin((t - s) * (2 * pi) / period) + 1


def elastic_in(t, amplitude=1, period=0.3):
    """弹性缓入"""
    if t == 0 or t == 1:
        return t

    s = period / 4
    t -= 1
    return -(amplitude * 2 ** (10 * t) * sin((t - s) * (2 * pi) / period))

# ========== 反弹（完整版） ==========


def bounce_in(t):
    """反弹缓入（落地前倒放）"""
    return 1 - bounce_out(1 - t)


def bounce_in_out(t):
    """先反弹后落地"""
    if t < 0.5:
        return bounce_in(t * 2) * 0.5
    return bounce_out(t * 2 - 1) * 0.5 + 0.5

# ========== 正弦缓动 ==========


def sine_in(t):
    """正弦加速"""
    return 1 - cos(t * pi / 2)


def sine_out(t):
    """正弦减速"""
    return sin(t * pi / 2)


def sine_in_out(t):
    """正弦缓动"""
    return -0.5 * (cos(pi * t) - 1)

# ========== 更新 EASING 字典 ==========


EASING = {
    "linear": linear,
    "quad_in": quad_in,
    "quad_out": quad_out,
    "quad_in_out": quad_in_out,
    "cubic_in": cubic_in,
    "cubic_out": cubic_out,
    "cubic_in_out": cubic_in_out,
    "back_in": back_in,
    "back_out": back_out,
    "bounce_out": bounce_out,
    # 指数
    "expo_in": expo_in,
    "expo_out": expo_out,
    "expo_in_out": expo_in_out,
    # 圆形
    "circ_in": circ_in,
    "circ_out": circ_out,
    "circ_in_out": circ_in_out,
    # 正弦
    "sine_in": sine_in,
    "sine_out": sine_out,
    "sine_in_out": sine_in_out,
    # 弹性增强版
    "elastic_out": elastic_out,
    "elastic_in": elastic_in,
    # 反弹完整版
    "bounce_in": bounce_in,
    "bounce_in_out": bounce_in_out,
}

# ========== 快捷函数 ==========


def ease(t, type_="linear"):
    """用字符串指定缓动类型"""
    return EASING.get(type_, linear)(t)
