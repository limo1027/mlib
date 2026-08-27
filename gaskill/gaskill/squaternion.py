from .smath import EPSILON, acos, cos, pi, sin, sqrt
from .smatrix import Matrix
from .srandom import Random
from .svector import vec3


class Quaternion:
    """四元数类 - 用于 3D 旋转"""

    def __init__(self, w=1.0, x=0.0, y=0.0, z=0.0):
        """初始化四元数"""
        self.w = float(w)
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def __repr__(self):
        """返回四元数的字符串表示"""
        return f"Quaternion({self.w:.4f}, {self.x:.4f}, {self.y:.4f}, {self.z:.4f})"

    def __str__(self):
        """返回四元数的可读形式"""
        return f"({self.w} + {self.x}i + {self.y}j + {self.z}k)"

    def __eq__(self, other):
        """四元数相等比较"""
        if not isinstance(other, Quaternion):
            return False
        return (abs(self.w - other.w) < EPSILON and
                abs(self.x - other.x) < EPSILON and
                abs(self.y - other.y) < EPSILON and
                abs(self.z - other.z) < EPSILON)

    def __ne__(self, other):
        """四元数不相等比较"""
        return not self.__eq__(other)

    def __add__(self, other):
        """四元数加法"""
        if isinstance(other, (int, float)):
            return Quaternion(self.w + other, self.x, self.y, self.z)
        return Quaternion(
            self.w + other.w,
            self.x + other.x,
            self.y + other.y,
            self.z + other.z,
        )

    def __radd__(self, other):
        """四元数右加法"""
        return self.__add__(other)

    def __sub__(self, other):
        """四元数减法"""
        if isinstance(other, (int, float)):
            return Quaternion(self.w - other, self.x, self.y, self.z)
        return Quaternion(
            self.w - other.w,
            self.x - other.x,
            self.y - other.y,
            self.z - other.z,
        )

    def __rsub__(self, other):
        """四元数右减法"""
        if isinstance(other, (int, float)):
            return Quaternion(other - self.w, -self.x, -self.y, -self.z)
        return other.__sub__(self)

    def __mul__(self, other):
        """四元数乘法或标量乘法"""
        if isinstance(other, (int, float)):
            return Quaternion(
                self.w * other,
                self.x * other,
                self.y * other,
                self.z * other,
            )

        if isinstance(other, Quaternion):
            w = self.w * other.w - self.x * other.x - self.y * other.y - self.z * other.z
            x = self.w * other.x + self.x * other.w + self.y * other.z - self.z * other.y
            y = self.w * other.y - self.x * other.z + self.y * other.w + self.z * other.x
            z = self.w * other.z + self.x * other.y - self.y * other.x + self.z * other.w
            return Quaternion(w, x, y, z)

        return NotImplemented

    def __rmul__(self, other):
        """四元数右乘法"""
        if isinstance(other, (int, float)):
            return self.__mul__(other)
        return NotImplemented

    def __truediv__(self, scalar):
        """四元数除法"""
        if abs(scalar) < EPSILON:
            raise ValueError("除数不能为 0")
        return self * (1.0 / scalar)

    def __neg__(self):
        """四元数取负"""
        return Quaternion(-self.w, -self.x, -self.y, -self.z)

    def __iter__(self):
        """迭代器支持"""
        yield self.w
        yield self.x
        yield self.y
        yield self.z

    def __getitem__(self, index):
        """索引访问"""
        if index == 0:
            return self.w
        elif index == 1:
            return self.x
        elif index == 2:
            return self.y
        elif index == 3:
            return self.z
        raise IndexError("Quaternion 索引超出范围")

    def copy(self):
        """复制四元数"""
        return Quaternion(self.w, self.x, self.y, self.z)

    def conjugate(self):
        """共轭四元数"""
        return Quaternion(self.w, -self.x, -self.y, -self.z)

    def norm(self):
        """四元数的范数"""
        return sqrt(self.w**2 + self.x**2 + self.y**2 + self.z**2)

    def norm_squared(self):
        """四元数范数的平方"""
        return self.w**2 + self.x**2 + self.y**2 + self.z**2

    def normalize(self):
        """归一化四元数"""
        n = self.norm()
        if n < EPSILON:
            return Quaternion(1, 0, 0, 0)
        return self / n

    def inverse(self):
        """逆四元数"""
        n_sq = self.norm_squared()
        if n_sq < EPSILON:
            raise ValueError("四元数不可逆（范数为 0）")
        return self.conjugate() / n_sq

    def dot(self, other):
        """四元数点积"""
        return (self.w * other.w +
                self.x * other.x +
                self.y * other.y +
                self.z * other.z)

    def to_axis_angle(self):
        """四元数转轴的角表示"""
        if self.w > 1:
            q = self.normalize()
        else:
            q = self

        angle = 2 * acos(q.w)

        if angle < EPSILON:
            return vec3(1, 0, 0), 0

        sin_half_angle = sin(angle / 2)
        if abs(sin_half_angle) < EPSILON:
            return vec3(1, 0, 0), angle

        axis = vec3(
            q.x / sin_half_angle,
            q.y / sin_half_angle,
            q.z / sin_half_angle,
        ).normalize()

        return axis, angle

    def to_matrix(self):
        """四元数转旋转矩阵（3x3）"""

        q = self.normalize()
        w, x, y, z = q.w, q.x, q.y, q.z

        return Matrix([
            [1 - 2*y*y - 2*z*z,     2*x*y - 2*z*w,     2*x*z + 2*y*w],
            [2*x*y + 2*z*w,     1 - 2*x*x - 2*z*z,     2*y*z - 2*x*w],
            [2*x*z - 2*y*w,     2*y*z + 2*x*w,     1 - 2*x*x - 2*y*y],
        ])

    def rotate_vector(self, v):
        """使用四元数旋转向量"""
        if isinstance(v, (tuple, list)):
            v = vec3(v[0], v[1], v[2])

        q = self.normalize()
        q_inv = q.inverse()

        v_quat = Quaternion(0, v.x, v.y, v.z)
        rotated = q * v_quat * q_inv

        return vec3(rotated.x, rotated.y, rotated.z)

    @staticmethod
    def from_axis_angle(axis, angle):
        """从轴角创建四元数"""
        if isinstance(axis, (tuple, list)):
            axis = vec3(axis[0], axis[1], axis[2])

        axis = axis.normalize()
        half_angle = angle / 2
        sin_half = sin(half_angle)

        return Quaternion(
            cos(half_angle),
            axis.x * sin_half,
            axis.y * sin_half,
            axis.z * sin_half,
        )

    @staticmethod
    def from_euler(roll, pitch, yaw):
        """从欧拉角创建四元数（Z-Y-X 顺序）"""
        cr, sr = cos(roll / 2), sin(roll / 2)
        cp, sp = cos(pitch / 2), sin(pitch / 2)
        cy, sy = cos(yaw / 2), sin(yaw / 2)

        w = cr * cp * cy + sr * sp * sy
        x = sr * cp * cy - cr * sp * sy
        y = cr * sp * cy + sr * cp * sy
        z = cr * cp * sy - sr * sp * cy

        return Quaternion(w, x, y, z)

    @staticmethod
    def from_two_vectors(v1, v2):
        """创建从一个向量到另一个向量的旋转四元数"""
        if isinstance(v1, (tuple, list)):
            v1 = vec3(v1[0], v1[1], v1[2])
        if isinstance(v2, (tuple, list)):
            v2 = vec3(v2[0], v2[1], v2[2])

        v1 = v1.normalize()
        v2 = v2.normalize()

        dot = v1.dot(v2)

        if dot > 0.999999:
            return Quaternion(1, 0, 0, 0)

        if dot < -0.999999:
            perpendicular = vec3(1, 0, 0)
            if abs(v1.x) > 0.9:
                perpendicular = vec3(0, 1, 0)
            axis = v1.cross(perpendicular).normalize()
            return Quaternion.from_axis_angle(axis, pi)

        cross = v1.cross(v2)
        w = sqrt((v1.length() ** 2) * (v2.length() ** 2)) + dot

        q = Quaternion(w, cross.x, cross.y, cross.z)
        return q.normalize()


def slerp(q1, q2, t):
    """球面线性插值（Spherical Linear Interpolation）"""
    if t <= 0:
        return q1
    if t >= 1:
        return q2

    q1 = q1.normalize()
    q2 = q2.normalize()

    dot = q1.dot(q2)

    # 确保走最短路径
    if dot < 0:
        q2 = -q2
        dot = -dot

    # 防止浮点误差
    dot = max(-1.0, min(1.0, dot))

    # 夹角太小，用线性插值
    if dot > 0.9995:
        result = q1 * (1 - t) + q2 * t
        return result.normalize()

    theta_0 = acos(dot)
    sin_theta_0 = sin(theta_0)

    theta = theta_0 * t
    sin_theta = sin(theta)

    s1 = cos(theta) - dot * sin_theta / sin_theta_0
    s2 = sin_theta / sin_theta_0

    result = q1 * s1 + q2 * s2
    return result.normalize()


def nlerp(q1, q2, t):
    """归一化线性插值（Normalized Linear Interpolation）"""
    result = q1 * (1 - t) + q2 * t
    return result.normalize()


def squad(q0, q1, q2, q3, t):
    """四元数球面二次插值（Spherical Quadrangle Interpolation）"""
    q1_q2 = slerp(q1, q2, t)
    q0_q3 = slerp(q0, q3, t)

    return slerp(q1_q2, q0_q3, 2 * t * (1 - t))


def angular_velocity(q1, q2, dt):
    """计算两个四元数之间的角速度"""
    if dt < EPSILON:
        return vec3(0, 0, 0)

    q_diff = q2 * q1.inverse()
    q_diff = q_diff.normalize()

    if q_diff.w < 0:
        q_diff = -q_diff

    angle = 2 * acos(q_diff.w)

    if angle < EPSILON:
        return vec3(0, 0, 0)

    sin_half = sin(acos(q_diff.w))
    if abs(sin_half) < EPSILON:
        return vec3(0, 0, 0)

    axis = vec3(q_diff.x, q_diff.y, q_diff.z) / sin_half
    return axis * (angle / dt)


def integrate_angular_velocity(q, omega, dt):
    """使用角速度积分四元数"""
    if isinstance(omega, (tuple, list)):
        omega = vec3(omega[0], omega[1], omega[2])

    omega_norm = omega.length()

    if omega_norm < EPSILON:
        return q

    half_omega_dt = omega_norm * dt / 2
    dq = Quaternion(
        cos(half_omega_dt),
        omega.x / omega_norm * sin(half_omega_dt),
        omega.y / omega_norm * sin(half_omega_dt),
        omega.z / omega_norm * sin(half_omega_dt),
    )

    return (dq * q).normalize()


def look_at(eye, target, up=None):
    """创建朝向目标的四元数"""
    if isinstance(eye, (tuple, list)):
        eye = vec3(eye[0], eye[1], eye[2])
    if isinstance(target, (tuple, list)):
        target = vec3(target[0], target[1], target[2])
    if up is None:
        up = vec3(0, 1, 0)
    if isinstance(up, (tuple, list)):
        up = vec3(up[0], up[1], up[2])

    forward = (target - eye).normalize()
    right = forward.cross(up).normalize()
    up = right.cross(forward).normalize()

    m00, m01, m02 = right.x, right.y, right.z
    m10, m11, m12 = up.x, up.y, up.z
    m20, m21, m22 = forward.x, forward.y, forward.z

    trace = m00 + m11 + m22

    if trace > 0:
        s = sqrt(trace + 1.0)
        w = s * 0.5
        s = 0.5 / s
        x = (m21 - m12) * s
        y = (m02 - m20) * s
        z = (m10 - m01) * s
    else:
        if m00 > m11 and m00 > m22:
            s = sqrt(1.0 + m00 - m11 - m22)
            inv_s = 0.5 / s
            x = 0.5 * s
            y = (m01 + m10) * inv_s
            z = (m02 + m20) * inv_s
            w = (m21 - m12) * inv_s
        elif m11 > m22:
            s = sqrt(1.0 + m11 - m00 - m22)
            inv_s = 0.5 / s
            x = (m01 + m10) * inv_s
            y = 0.5 * s
            z = (m12 + m21) * inv_s
            w = (m02 - m20) * inv_s
        else:
            s = sqrt(1.0 + m22 - m00 - m11)
            inv_s = 0.5 / s
            x = (m02 + m20) * inv_s
            y = (m12 + m21) * inv_s
            z = 0.5 * s
            w = (m10 - m01) * inv_s

    return Quaternion(w, x, y, z)


def random_quaternion(rng=None):
    """生成随机单位四元数"""
    if rng is None:
        rng = Random()

    u1 = rng.random()
    u2 = rng.random()
    u3 = rng.random()

    w = sqrt(1 - u1) * sin(2 * pi * u2)
    x = sqrt(1 - u1) * cos(2 * pi * u2)
    y = sqrt(u1) * sin(2 * pi * u3)
    z = sqrt(u1) * cos(2 * pi * u3)

    return Quaternion(w, x, y, z)


IDENTITY = Quaternion(1, 0, 0, 0)
ZERO = Quaternion(0, 0, 0, 0)
