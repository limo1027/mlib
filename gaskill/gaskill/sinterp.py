from .smath import EPSILON, acos, clamp, cos, pi, sin


def lerp(a, b, t):
    """线性插值"""
    t = clamp(t, 0, 1)
    return a + (b - a) * t


def lerp_unclamped(a, b, t):
    """无限制的线性插值"""
    return a + (b - a) * t


def bilerp(v00, v10, v01, v11, x, y):
    """双线性插值"""
    t1 = lerp(v00, v10, x)
    t2 = lerp(v01, v11, x)
    return lerp(t1, t2, y)


def trilerp(v000, v100, v010, v110, v001, v101, v011, v111, x, y, z):
    """三线性插值"""
    t00 = lerp(v000, v100, x)
    t10 = lerp(v010, v110, x)
    t01 = lerp(v001, v101, x)
    t11 = lerp(v011, v111, x)

    t0 = lerp(t00, t10, y)
    t1 = lerp(t01, t11, y)

    return lerp(t0, t1, z)


def slerp(v1, v2, t):
    """球面线性插值（用于四元数或归一化向量）"""
    dot = v1.dot(v2)
    dot = clamp(dot, -1, 1)

    if dot > 0.9995:
        return lerp(v1, v2, t).normalize()

    theta = acos(dot)
    sin_theta = sin(theta)

    if sin_theta < EPSILON:
        return lerp(v1, v2, t).normalize()

    t1 = sin((1 - t) * theta) / sin_theta
    t2 = sin(t * theta) / sin_theta

    return v1 * t1 + v2 * t2


def smoothstep(edge0, edge1, x):
    """平滑步进函数"""
    t = clamp((x - edge0) / (edge1 - edge0), 0, 1)
    return t * t * (3 - 2 * t)


def smootherstep(edge0, edge1, x):
    """更平滑的步进函数"""
    t = clamp((x - edge0) / (edge1 - edge0), 0, 1)
    return t * t * t * (t * (t * 6 - 15) + 10)


def coserp(a, b, t):
    """余弦插值"""
    t = clamp(t, 0, 1)
    ft = t * pi
    f = (1 - cos(ft)) * 0.5
    return a * (1 - f) + b * f


def cubic_bezier(p0, p1, p2, p3, t):
    """三次贝塞尔曲线"""
    t = clamp(t, 0, 1)
    inv_t = 1 - t
    return (
        inv_t ** 3 * p0 +
        3 * inv_t ** 2 * t * p1 +
        3 * inv_t * t ** 2 * p2 +
        t ** 3 * p3
    )


def cubic_bezier_derivative(p0, p1, p2, p3, t):
    """三次贝塞尔曲线的导数（切线）"""
    t = clamp(t, 0, 1)
    inv_t = 1 - t
    return (
        3 * inv_t ** 2 * (p1 - p0) +
        6 * inv_t * t * (p2 - p1) +
        3 * t ** 2 * (p3 - p2)
    )


def catmull_rom(p0, p1, p2, p3, t):
    """Catmull-Rom 样条"""
    t = clamp(t, 0, 1)
    t2 = t * t
    t3 = t2 * t
    return (
        0.5 * ((2 * p1) +
               (-p0 + p2) * t +
               (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 +
               (-p0 + 3 * p1 - 3 * p2 + p3) * t3)
    )


def hermite(p0, t0, p1, t1, s):
    """Hermite 曲线"""
    s = clamp(s, 0, 1)
    s2 = s * s
    s3 = s2 * s

    h1 = 2 * s3 - 3 * s2 + 1
    h2 = -2 * s3 + 3 * s2
    h3 = s3 - 2 * s2 + s
    h4 = s3 - s2

    return p0 * h1 + p1 * h2 + t0 * h3 + t1 * h4


def inverse_lerp(a, b, value):
    """反向线性插值"""
    if abs(b - a) < EPSILON:
        return 0.0
    return clamp((value - a) / (b - a), 0, 1)


def remap(value, in_min, in_max, out_min, out_max):
    """值映射"""
    t = inverse_lerp(in_min, in_max, value)
    return lerp(out_min, out_max, t)


def pingpong(value, length):
    """乒乓值计算"""
    if length <= 0:
        return 0
    value = value % (length * 2)
    if value > length:
        return length * 2 - value
    return value


def damp(current, target, lambda_val, dt):
    """阻尼插值（平滑跟随）"""
    decay = 1.0 / (1.0 + lambda_val * dt)
    return current + (target - current) * (1.0 - decay)


def spring(current, target, velocity, frequency, damping, dt):
    """弹簧插值"""
    if dt <= 0:
        return current, velocity

    k = 4 * pi * pi * frequency * frequency
    c = 4 * pi * frequency * damping

    force = k * (target - current) - c * velocity
    acceleration = force

    new_velocity = velocity + acceleration * dt
    new_position = current + new_velocity * dt

    return new_position, new_velocity
