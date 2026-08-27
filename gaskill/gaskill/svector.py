from .smath import EPSILON, acos, atan2, clamp, cos, sin, sqrt


class vec2:
    """二维向量"""

    def __init__(self, x=0.0, y=0.0):
        self.x = float(x)
        self.y = float(y)

    def __add__(self, other):
        if isinstance(other, vec2):
            return vec2(self.x + other.x, self.y + other.y)
        return vec2(self.x + other, self.y + other)

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if isinstance(other, vec2):
            return vec2(self.x - other.x, self.y - other.y)
        return vec2(self.x - other, self.y - other)

    def __rsub__(self, other):
        if isinstance(other, vec2):
            return vec2(other.x - self.x, other.y - self.y)
        return vec2(other - self.x, other - self.y)

    def __mul__(self, scalar):
        return vec2(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar):
        return self.__mul__(scalar)

    def __truediv__(self, scalar):
        if abs(scalar) < EPSILON:
            raise ValueError("除数不能为 0")
        return vec2(self.x / scalar, self.y / scalar)

    def __floordiv__(self, scalar):
        if abs(scalar) < EPSILON:
            raise ValueError("除数不能为 0")
        return vec2(self.x // scalar, self.y // scalar)

    def __neg__(self):
        return vec2(-self.x, -self.y)

    def __eq__(self, other):
        if not isinstance(other, vec2):
            return False
        return abs(self.x - other.x) < EPSILON and abs(self.y - other.y) < EPSILON

    def __ne__(self, other):
        return not self.__eq__(other)

    def __iter__(self):
        yield self.x
        yield self.y

    def __getitem__(self, index):
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        raise IndexError("vec2 索引超出范围")

    def __setitem__(self, index, value):
        if index == 0:
            self.x = value
        elif index == 1:
            self.y = value
        else:
            raise IndexError("vec2 索引超出范围")

    def __repr__(self):
        return f"vec2({self.x}, {self.y})"

    def __str__(self):
        return f"({self.x}, {self.y})"

    def __len__(self):
        return 2

    def copy(self):
        return vec2(self.x, self.y)

    def dot(self, other):
        """点积"""
        return self.x * other.x + self.y * other.y

    def cross(self, other):
        """二维叉积（返回标量）"""
        return self.x * other.y - self.y * other.x

    def length(self):
        """模长"""
        return sqrt(self.x ** 2 + self.y ** 2)

    def length_squared(self):
        """模长的平方"""
        return self.x ** 2 + self.y ** 2

    def normalize(self):
        """归一化"""
        length = self.length()
        if length < EPSILON:
            return vec2(0, 0)
        return vec2(self.x / length, self.y / length)

    def normalize_or_zero(self):
        """安全归一化，零向量返回零向量"""
        return self.normalize()

    def distance(self, other):
        """到另一个向量的距离"""
        return (other - self).length()

    def distance_squared(self, other):
        """到另一个向量的距离的平方"""
        return (other - self).length_squared()

    def lerp(self, other, t):
        """线性插值"""
        return vec2(
            self.x + (other.x - self.x) * t,
            self.y + (other.y - self.y) * t,
        )
    def rotate_around(self, center, angle):
        """绕某点旋转 angle 弧度"""
        dx = self.x - center.x
        dy = self.y - center.y
        c, s = cos(angle), sin(angle)
        return vec2(
            center.x + dx * c - dy * s,
            center.y + dx * s + dy * c,
        )

    def reflect(self, normal):
        """反射向量"""
        n = normal.normalize()
        d = self.dot(n)
        return self - n * (2 * d)

    def project(self, onto):
        """投影到另一个向量"""
        denom = onto.dot(onto)
        if denom < EPSILON:
            return vec2(0, 0)
        return onto * (self.dot(onto) / denom)

    def reject(self, onto):
        """拒绝投影（垂直分量）"""
        return self - self.project(onto)

    def rotate(self, angle):
        """旋转向量（弧度）"""
        c, s = cos(angle), sin(angle)
        return vec2(
            self.x * c - self.y * s,
            self.x * s + self.y * c,
        )

    def angle(self):
        """向量的角度（弧度）"""
        return atan2(self.y, self.x)

    def angle_to(self, other):
        """到另一个向量的夹角（弧度）"""
        dot = self.dot(other)
        norms = self.length() * other.length()
        if norms < EPSILON:
            return 0.0
        cos_angle = clamp(dot / norms, -1, 1)
        return acos(cos_angle)

    def perpendicular(self):
        """垂直向量（逆时针 90 度）"""
        return vec2(-self.y, self.x)

    def scale(self, sx, sy=None):
        """缩放"""
        if sy is None:
            sy = sx
        return vec2(self.x * sx, self.y * sy)

    @staticmethod
    def zero():
        return vec2(0, 0)

    @staticmethod
    def one():
        return vec2(1, 1)

    @staticmethod
    def up():
        return vec2(0, 1)

    @staticmethod
    def down():
        return vec2(0, -1)

    @staticmethod
    def left():
        return vec2(-1, 0)

    @staticmethod
    def right():
        return vec2(1, 0)

    @staticmethod
    def from_angle(angle):
        """从角度创建单位向量"""
        return vec2(cos(angle), sin(angle))

    @staticmethod
    def lerp_batch(v1, v2, t_values):
        """批量线性插值"""
        return [v1.lerp(v2, t) for t in t_values]


class vec3:
    """三维向量"""

    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def __add__(self, other):
        if isinstance(other, vec3):
            return vec3(self.x + other.x, self.y + other.y, self.z + other.z)
        return vec3(self.x + other, self.y + other, self.z + other)

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if isinstance(other, vec3):
            return vec3(self.x - other.x, self.y - other.y, self.z - other.z)
        return vec3(self.x - other, self.y - other, self.z - other)

    def __rsub__(self, other):
        if isinstance(other, vec3):
            return vec3(other.x - self.x, other.y - self.y, other.z - self.z)
        return vec3(other - self.x, other - self.y, other - self.z)

    def __mul__(self, scalar):
        return vec3(self.x * scalar, self.y * scalar, self.z * scalar)

    def __rmul__(self, scalar):
        return self.__mul__(scalar)

    def __truediv__(self, scalar):
        if abs(scalar) < EPSILON:
            raise ValueError("除数不能为 0")
        return vec3(self.x / scalar, self.y / scalar, self.z / scalar)

    def __floordiv__(self, scalar):
        if abs(scalar) < EPSILON:
            raise ValueError("除数不能为 0")
        return vec3(self.x // scalar, self.y // scalar, self.z // scalar)

    def __neg__(self):
        return vec3(-self.x, -self.y, -self.z)

    def __eq__(self, other):
        if not isinstance(other, vec3):
            return False
        return (abs(self.x - other.x) < EPSILON and
                abs(self.y - other.y) < EPSILON and
                abs(self.z - other.z) < EPSILON)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __iter__(self):
        yield self.x
        yield self.y
        yield self.z

    def __getitem__(self, index):
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        elif index == 2:
            return self.z
        else:
            raise IndexError("vec3 索引超出范围")

    def __setitem__(self, index, value):
        if index == 0:
            self.x = value
        elif index == 1:
            self.y = value
        elif index == 2:
            self.z = value
        else:
            raise IndexError("vec3 索引超出范围")

    def __repr__(self):
        return f"vec3({self.x}, {self.y}, {self.z})"

    def __str__(self):
        return f"({self.x}, {self.y}, {self.z})"

    def __len__(self):
        return 3

    def copy(self):
        return vec3(self.x, self.y, self.z)

    def rotate_around(self, center, axis, angle):
        """绕某点、绕指定轴旋转 angle 弧度"""
        # 平移到原点
        p = vec3(self.x - center.x, self.y - center.y, self.z - center.z)
        # 绕轴旋转
        rotated = p.rotate_axis(axis, angle)
        # 平移回去
        return vec3(
            center.x + rotated.x,
            center.y + rotated.y,
            center.z + rotated.z,
        )

    def dot(self, other):
        """点积"""
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other):
        """叉积"""
        return vec3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x,
        )

    def length(self):
        """模长"""
        return sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)

    def length_squared(self):
        """模长的平方"""
        return self.x ** 2 + self.y ** 2 + self.z ** 2

    def normalize(self):
        """归一化"""
        length = self.length()
        if length < EPSILON:
            return vec3(0, 0, 0)
        return vec3(self.x / length, self.y / length, self.z / length)

    def normalize_or_zero(self):
        """安全归一化"""
        return self.normalize()

    def distance(self, other):
        """到另一个向量的距离"""
        return (other - self).length()

    def distance_squared(self, other):
        """到另一个向量的距离的平方"""
        return (other - self).length_squared()

    def lerp(self, other, t):
        """线性插值"""
        return vec3(
            self.x + (other.x - self.x) * t,
            self.y + (other.y - self.y) * t,
            self.z + (other.z - self.z) * t,
        )

    def reflect(self, normal):
        """反射向量"""
        n = normal.normalize()
        d = self.dot(n)
        return self - n * (2 * d)

    def project(self, onto):
        """投影到另一个向量"""
        denom = onto.dot(onto)
        if denom < EPSILON:
            return vec3(0, 0, 0)
        return onto * (self.dot(onto) / denom)

    def reject(self, onto):
        """拒绝投影"""
        return self - self.project(onto)

    def rotate_x(self, angle):
        """绕 X 轴旋转"""
        c, s = cos(angle), sin(angle)
        return vec3(
            self.x,
            self.y * c - self.z * s,
            self.y * s + self.z * c,
        )

    def rotate_y(self, angle):
        """绕 Y 轴旋转"""
        c, s = cos(angle), sin(angle)
        return vec3(
            self.x * c + self.z * s,
            self.y,
            -self.x * s + self.z * c,
        )

    def rotate_z(self, angle):
        """绕 Z 轴旋转"""
        c, s = cos(angle), sin(angle)
        return vec3(
            self.x * c - self.y * s,
            self.x * s + self.y * c,
            self.z,
        )

    def scale(self, sx, sy=None, sz=None):
        """缩放"""
        if sy is None:
            sy = sx
        if sz is None:
            sz = sx
        return vec3(self.x * sx, self.y * sy, self.z * sz)

    def to_tuple(self):
        """转换为元组"""
        return (self.x, self.y, self.z)

    def to_list(self):
        """转换为列表"""
        return [self.x, self.y, self.z]

    @staticmethod
    def zero():
        return vec3(0, 0, 0)

    @staticmethod
    def one():
        return vec3(1, 1, 1)

    @staticmethod
    def up():
        return vec3(0, 1, 0)

    @staticmethod
    def down():
        return vec3(0, -1, 0)

    @staticmethod
    def left():
        return vec3(-1, 0, 0)

    @staticmethod
    def right():
        return vec3(1, 0, 0)

    @staticmethod
    def forward():
        return vec3(0, 0, 1)

    @staticmethod
    def back():
        return vec3(0, 0, -1)

    @staticmethod
    def from_tuple(t):
        return vec3(t[0], t[1], t[2])

    @staticmethod
    def from_list(lst):
        return vec3(lst[0], lst[1], lst[2])


class vec4:
    """四维向量"""

    def __init__(self, x=0.0, y=0.0, z=0.0, w=0.0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
        self.w = float(w)

    def __add__(self, other):
        if isinstance(other, vec4):
            return vec4(self.x + other.x, self.y + other.y, self.z + other.z, self.w + other.w)
        return vec4(self.x + other, self.y + other, self.z + other, self.w + other)

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if isinstance(other, vec4):
            return vec4(self.x - other.x, self.y - other.y, self.z - other.z, self.w - other.w)
        return vec4(self.x - other, self.y - other, self.z - other, self.w - other)

    def __rsub__(self, other):
        if isinstance(other, vec4):
            return vec4(other.x - self.x, other.y - self.y, other.z - self.z, other.w - self.w)
        return vec4(other - self.x, other - self.y, other - self.z, other - self.w)

    def __mul__(self, scalar):
        return vec4(self.x * scalar, self.y * scalar, self.z * scalar, self.w * scalar)

    def __rmul__(self, scalar):
        return self.__mul__(scalar)

    def __truediv__(self, scalar):
        if abs(scalar) < EPSILON:
            raise ValueError("除数不能为 0")
        return vec4(self.x / scalar, self.y / scalar, self.z / scalar, self.w / scalar)

    def __floordiv__(self, scalar):
        if abs(scalar) < EPSILON:
            raise ValueError("除数不能为 0")
        return vec4(self.x // scalar, self.y // scalar, self.z // scalar, self.w // scalar)

    def __neg__(self):
        return vec4(-self.x, -self.y, -self.z, -self.w)

    def __eq__(self, other):
        if not isinstance(other, vec4):
            return False
        return (abs(self.x - other.x) < EPSILON and
                abs(self.y - other.y) < EPSILON and
                abs(self.z - other.z) < EPSILON and
                abs(self.w - other.w) < EPSILON)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __iter__(self):
        yield self.x
        yield self.y
        yield self.z
        yield self.w

    def __getitem__(self, index):
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        elif index == 2:
            return self.z
        elif index == 3:
            return self.w
        else:
            raise IndexError("vec4 索引超出范围")

    def __setitem__(self, index, value):
        if index == 0:
            self.x = value
        elif index == 1:
            self.y = value
        elif index == 2:
            self.z = value
        elif index == 3:
            self.w = value
        else:
            raise IndexError("vec4 索引超出范围")

    def __repr__(self):
        return f"vec4({self.x}, {self.y}, {self.z}, {self.w})"

    def __str__(self):
        return f"({self.x}, {self.y}, {self.z}, {self.w})"

    def __len__(self):
        return 4

    def copy(self):
        return vec4(self.x, self.y, self.z, self.w)

    def dot(self, other):
        """点积"""
        return self.x * other.x + self.y * other.y + self.z * other.z + self.w * other.w

    def cross(self, other):
        """叉积（仅取前三维）"""
        return vec3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x,
        )

    def length(self):
        """模长"""
        return sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2 + self.w ** 2)

    def length_squared(self):
        """模长的平方"""
        return self.x ** 2 + self.y ** 2 + self.z ** 2 + self.w ** 2

    def normalize(self):
        """归一化"""
        length = self.length()
        if length < EPSILON:
            return vec4(0, 0, 0, 0)
        return vec4(self.x / length, self.y / length, self.z / length, self.w / length)

    def normalize_or_zero(self):
        """安全归一化"""
        return self.normalize()

    def distance(self, other):
        """到另一个向量的距离"""
        return (other - self).length()

    def distance_squared(self, other):
        """到另一个向量的距离的平方"""
        return (other - self).length_squared()

    def lerp(self, other, t):
        """线性插值"""
        return vec4(
            self.x + (other.x - self.x) * t,
            self.y + (other.y - self.y) * t,
            self.z + (other.z - self.z) * t,
            self.w + (other.w - self.w) * t,
        )

    def reflect(self, normal):
        """反射向量"""
        n = normal.normalize()
        d = self.dot(n)
        return self - n * (2 * d)

    def project(self, onto):
        """投影到另一个向量"""
        denom = onto.dot(onto)
        if denom < EPSILON:
            return vec4(0, 0, 0, 0)
        return onto * (self.dot(onto) / denom)

    def reject(self, onto):
        """拒绝投影"""
        return self - self.project(onto)

    def to_vec3(self, w_divide=True):
        """转换为 vec3（齐次坐标除法）"""
        if w_divide and abs(self.w) > EPSILON:
            return vec3(self.x / self.w, self.y / self.w, self.z / self.w)
        return vec3(self.x, self.y, self.z)

    def to_tuple(self):
        """转换为元组"""
        return (self.x, self.y, self.z, self.w)

    def to_list(self):
        """转换为列表"""
        return [self.x, self.y, self.z, self.w]

    def to_rgba(self):
        """转换为 RGBA 颜色元组 (0-255)"""
        return (
            int(clamp(self.x * 255, 0, 255)),
            int(clamp(self.y * 255, 0, 255)),
            int(clamp(self.z * 255, 0, 255)),
            int(clamp(self.w * 255, 0, 255)),
        )

    def to_rgb(self):
        """转换为 RGB 颜色元组 (0-255)"""
        return (
            int(clamp(self.x * 255, 0, 255)),
            int(clamp(self.y * 255, 0, 255)),
            int(clamp(self.z * 255, 0, 255)),
        )

    @staticmethod
    def zero():
        return vec4(0, 0, 0, 0)

    @staticmethod
    def one():
        return vec4(1, 1, 1, 1)

    @staticmethod
    def unit_x():
        return vec4(1, 0, 0, 0)

    @staticmethod
    def unit_y():
        return vec4(0, 1, 0, 0)

    @staticmethod
    def unit_z():
        return vec4(0, 0, 1, 0)

    @staticmethod
    def unit_w():
        return vec4(0, 0, 0, 1)

    @staticmethod
    def from_vec3(v, w=1.0):
        """从 vec3 创建（齐次坐标）"""
        return vec4(v.x, v.y, v.z, w)

    @staticmethod
    def from_rgba(r, g, b, a=255):
        """从 RGBA (0-255) 创建"""
        return vec4(r / 255.0, g / 255.0, b / 255.0, a / 255.0)

    @staticmethod
    def from_tuple(t):
        """从元组创建"""
        return vec4(t[0], t[1], t[2], t[3] if len(t) > 3 else 1.0)

    @staticmethod
    def from_list(lst):
        """从列表创建"""
        return vec4(lst[0], lst[1], lst[2], lst[3] if len(lst) > 3 else 1.0)


def v2(x=0, y=0):
    """创建 vec2 的快捷函数"""
    return vec2(x, y)


def v3(x=0, y=0, z=0):
    """创建 vec3 的快捷函数"""
    return vec3(x, y, z)


def v4(x=0, y=0, z=0, w=0):
    """创建 vec4 的快捷函数"""
    return vec4(x, y, z, w)


def vlerp(v1, v2, t):
    """向量线性插值"""
    return v1.lerp(v2, t)


def distance(v1, v2):
    """向量间距离"""
    return v1.distance(v2)


def dot(v1, v2):
    """点积"""
    return v1.dot(v2)


def cross(v1, v2):
    """叉积（仅 vec3）"""
    return v1.cross(v2)


def normalize(v):
    """归一化"""
    return v.normalize()


def angle_between(v1, v2):
    """向量夹角"""
    return v1.angle_to(v2)
