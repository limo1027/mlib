from .smath import EPSILON
from .svector import vec2, vec3

# ========== 辅助函数 ==========

def _is_vec(p):
    """检查是否是向量类型"""
    return hasattr(p, "x") and hasattr(p, "y")


def _lerp(p0, p1, t):
    """线性插值"""
    if _is_vec(p0):
        if hasattr(p0, "z"):  # vec3
            return vec3(
                (1-t) * p0.x + t * p1.x,
                (1-t) * p0.y + t * p1.y,
                (1-t) * p0.z + t * p1.z,
            )
        else:  # vec2
            return vec2(
                (1-t) * p0.x + t * p1.x,
                (1-t) * p0.y + t * p1.y,
            )
    else:  # 元组
        if len(p0) == 3:
            return (
                (1-t) * p0[0] + t * p1[0],
                (1-t) * p0[1] + t * p1[1],
                (1-t) * p0[2] + t * p1[2],
            )
        else:
            return (
                (1-t) * p0[0] + t * p1[0],
                (1-t) * p0[1] + t * p1[1],
            )


# ========== 贝塞尔曲线 ==========
def quadratic_bezier(p0: "vec2|vec3|tuple[float, float, float|None]", p1, p2, t):
    """二次贝塞尔曲线"""
    if _is_vec(p0):
        if isinstance(p0, vec3):  # vec3
            return vec3(
                (1-t)**2 * p0.x + 2*(1-t)*t * p1.x + t**2 * p2.x,
                (1-t)**2 * p0.y + 2*(1-t)*t * p1.y + t**2 * p2.y,
                (1-t)**2 * p0.z + 2*(1-t)*t * p1.z + t**2 * p2.z,
            )
        else:  # vec2
            return vec2(
                (1-t)**2 * p0.x + 2*(1-t)*t * p1.x + t**2 * p2.x,
                (1-t)**2 * p0.y + 2*(1-t)*t * p1.y + t**2 * p2.y,
            )
    else:  # 元组
        return tuple(
            (1-t)**2 * p0[i] + 2*(1-t)*t * p1[i] + t**2 * p2[i]
            for i in range(len(p0))
        )


def cubic_bezier(p0, p1, p2, p3, t):
    """三次贝塞尔曲线"""
    if _is_vec(p0):
        if hasattr(p0, "z"):  # vec3
            return vec3(
                (1-t)**3 * p0.x + 3*(1-t)**2*t * p1.x +
                3*(1-t)*t**2 * p2.x + t**3 * p3.x,
                (1-t)**3 * p0.y + 3*(1-t)**2*t * p1.y +
                3*(1-t)*t**2 * p2.y + t**3 * p3.y,
                (1-t)**3 * p0.z + 3*(1-t)**2*t *
                p1.z + 3*(1-t)*t**2 * p2.z + t**3 * p3.z,
            )
        else:  # vec2
            return vec2(
                (1-t)**3 * p0.x + 3*(1-t)**2*t * p1.x +
                3*(1-t)*t**2 * p2.x + t**3 * p3.x,
                (1-t)**3 * p0.y + 3*(1-t)**2*t *
                p1.y + 3*(1-t)*t**2 * p2.y + t**3 * p3.y,
            )
    else:  # 元组
        return tuple(
            (1-t)**3 * p0[i] + 3*(1-t)**2*t * p1[i] +
            3*(1-t)*t**2 * p2[i] + t**3 * p3[i]
            for i in range(len(p0))
        )


def bezier(points, t):
    """任意阶贝塞尔曲线（德卡斯特里奥算法）"""
    if len(points) == 1:
        return points[0]

    if len(points) == 2:
        return _lerp(points[0], points[1], t)

    if len(points) == 3:
        return quadratic_bezier(points[0], points[1], points[2], t)

    if len(points) == 4:
        return cubic_bezier(points[0], points[1], points[2], points[3], t)

    new_points = [_lerp(points[i], points[i+1], t)
                  for i in range(len(points)-1)]
    return bezier(new_points, t)


def bezier_derivative(points, t, order=1):
    """贝塞尔曲线的导数（切向量）"""
    n = len(points) - 1

    if order == 0:
        return bezier(points, t)

    if n == 0:
        if _is_vec(points[0]):
            return type(points[0])(0, 0, 0) if hasattr(points[0], "z") else type(points[0])(0, 0)
        return tuple(0 for _ in points[0])

    new_points = []
    for i in range(n):
        if _is_vec(points[i]):
            if hasattr(points[i], "z"):
                new_points.append(vec3(
                    n * (points[i+1].x - points[i].x),
                    n * (points[i+1].y - points[i].y),
                    n * (points[i+1].z - points[i].z),
                ))
            else:
                new_points.append(vec2(
                    n * (points[i+1].x - points[i].x),
                    n * (points[i+1].y - points[i].y),
                ))
        else:
            new_points.append(tuple(
                n * (points[i+1][j] - points[i][j])
                for j in range(len(points[i]))
            ))

    if order == 1:
        return bezier(new_points, t)
    else:
        return bezier_derivative(new_points, t, order - 1)


# ========== B 样条曲线 ==========

def _cox_de_boor(knots, i, k, t):
    """Cox-de Boor 递归算法计算 B 样条基函数"""
    if k == 0:
        return 1.0 if knots[i] <= t < knots[i+1] else 0.0

    denom1 = knots[i+k] - knots[i]
    c1 = (t - knots[i]) / denom1 * \
        _cox_de_boor(knots, i, k-1, t) if denom1 > 0 else 0.0

    denom2 = knots[i+k+1] - knots[i+1]
    c2 = (knots[i+k+1] - t) / denom2 * \
        _cox_de_boor(knots, i+1, k-1, t) if denom2 > 0 else 0.0

    return c1 + c2


def b_spline(control_points, knots, degree, t):
    """B 样条曲线求值"""
    n = len(control_points) - 1

    if _is_vec(control_points[0]):
        if hasattr(control_points[0], "z"):
            result = vec3(0, 0, 0)
        else:
            result = vec2(0, 0)
    else:
        result = tuple(0.0 for _ in control_points[0])

    for i in range(n + 1):
        basis = _cox_de_boor(knots, i, degree, t)

        if _is_vec(result):
            if hasattr(result, "z"):
                result = vec3(
                    result.x + control_points[i].x * basis,
                    result.y + control_points[i].y * basis,
                    result.z + control_points[i].z * basis,
                )
            else:
                result = vec2(
                    result.x + control_points[i].x * basis,
                    result.y + control_points[i].y * basis,
                )
        else:
            result = tuple(
                result[j] + control_points[i][j] * basis
                for j in range(len(result))
            )

    return result


def uniform_knots(n, degree):
    """
    生成均匀节点向量"""
    m = n + degree + 1
    return list(range(m + 1))


def clamped_knots(n, degree):
    """生成钳制节点向量（曲线通过首尾控制点）"""
    m = n + degree + 1
    knots = [0] * (degree + 1)

    for i in range(degree + 1, m - degree):
        knots.append(i - degree)

    knots.extend([m - degree] * (degree + 1))

    return knots


def b_spline_curve(control_points, degree=3, steps=100):
    """生成 B 样条曲线上的点序列"""
    n = len(control_points) - 1
    knots = clamped_knots(n, degree)

    t_min = knots[degree]
    t_max = knots[len(knots) - degree - 1]

    if t_max <= t_min:
        return control_points[:1]

    points = []
    for i in range(steps + 1):
        t = t_min + (t_max - t_min) * i / steps
        points.append(b_spline(control_points, knots, degree, t))

    return points


# ========== NURBS 曲线 ==========

def nurbs(control_points, weights, knots, degree, t):
    """NURBS（非均匀有理 B 样条）曲线"""
    numerator = None
    denominator = 0.0

    n = len(control_points) - 1

    for i in range(n + 1):
        basis = _cox_de_boor(knots, i, degree, t)
        w = weights[i]

        if _is_vec(control_points[0]):
            weighted_point = None
            if hasattr(control_points[0], "z"):
                weighted_point = vec3(
                    control_points[i].x * w * basis,
                    control_points[i].y * w * basis,
                    control_points[i].z * w * basis,
                )
            else:
                weighted_point = vec2(
                    control_points[i].x * w * basis,
                    control_points[i].y * w * basis,
                )

            if numerator is None:
                numerator = weighted_point
            else:
                if hasattr(numerator, "z"):
                    numerator = vec3(
                        numerator.x + weighted_point.x,
                        numerator.y + weighted_point.y,
                        numerator.z + weighted_point.z,
                    )
                else:
                    numerator = vec2(
                        numerator.x + weighted_point.x,
                        numerator.y + weighted_point.y,
                    )
        else:
            if numerator is None:
                numerator = tuple(
                    control_points[i][j] * w * basis
                    for j in range(len(control_points[i]))
                )
            else:
                numerator = tuple(
                    numerator[j] + control_points[i][j] * w * basis
                    for j in range(len(control_points[i]))
                )

        denominator += w * basis

    if abs(denominator) < EPSILON:
        return control_points[0] if control_points else None

    if _is_vec(numerator):
        if hasattr(numerator, "z"):
            return vec3(
                numerator.x / denominator,
                numerator.y / denominator,
                numerator.z / denominator,
            )
        else:
            return vec2(
                numerator.x / denominator,
                numerator.y / denominator,
            )
    else:
        return tuple(
            numerator[j] / denominator
            for j in range(len(numerator))
        )


def bezier_path(points, steps=100):
    """生成贝塞尔曲线上的点序列"""
    return [bezier(points, i/steps) for i in range(steps+1)]


def bezier_length(points, steps=100):
    """估算贝塞尔曲线长度"""
    path = bezier_path(points, steps)
    length = 0

    for i in range(len(path)-1):
        p0, p1 = path[i], path[i+1]
        if _is_vec(p0):
            if hasattr(p0, "z"):
                dx = p1.x - p0.x
                dy = p1.y - p0.y
                dz = p1.z - p0.z
                length += (dx*dx + dy*dy + dz*dz) ** 0.5
            else:
                dx = p1.x - p0.x
                dy = p1.y - p0.y
                length += (dx*dx + dy*dy) ** 0.5
        else:
            if len(p0) == 3:
                length += sum((p1[j] - p0[j])**2 for j in range(3)) ** 0.5
            else:
                length += sum((p1[j] - p0[j])**2 for j in range(2)) ** 0.5

    return length


def curve_length(points_func, steps=100):
    """通用曲线长度计算"""
    path = [points_func(i/steps) for i in range(steps+1)]
    length = 0

    for i in range(len(path)-1):
        p0, p1 = path[i], path[i+1]
        if _is_vec(p0):
            if hasattr(p0, "z"):
                dx = p1.x - p0.x
                dy = p1.y - p0.y
                dz = p1.z - p0.z
                length += (dx*dx + dy*dy + dz*dz) ** 0.5
            else:
                dx = p1.x - p0.x
                dy = p1.y - p0.y
                length += (dx*dx + dy*dy) ** 0.5
        else:
            length += sum((p1[j] - p0[j])**2 for j in range(len(p0))) ** 0.5

    return length


def de_casteljau_subdivide(points, t):
    """使用德卡斯特里奥算法细分贝塞尔曲线"""
    if len(points) == 1:
        return points[:], points[:]

    left = [points[0]]
    right = [points[-1]]

    current = points[:]
    while len(current) > 1:
        next_level = [_lerp(current[i], current[i+1], t)
                      for i in range(len(current)-1)]
        left.append(next_level[0])
        right.insert(0, next_level[-1])
        current = next_level

    return left, right
