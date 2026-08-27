from .smath import EPSILON, cos, pi, sin, sqrt, tan
from .svector import vec3


class AABB:
    """轴对齐边界盒 (Axis-Aligned Bounding Box)"""

    def __init__(self, min_point=None, max_point=None):
        """初始化 AABB"""
        if min_point:
            self.min = vec3(min_point.x, min_point.y, min_point.z)
        else:
            self.min = vec3(0, 0, 0)

        if max_point:
            self.max = vec3(max_point.x, max_point.y, max_point.z)
        else:
            self.max = vec3(0, 0, 0)

    @classmethod
    def from_center_size(cls, center, size):
        """从中心和大小创建 AABB"""
        half_size = size * 0.5
        return cls(center - half_size, center + half_size)

    @classmethod
    def from_points(cls, points):
        """从点集创建 AABB"""
        if not points:
            return cls()

        min_x = min_y = min_z = float("inf")
        max_x = max_y = max_z = float("-inf")

        for p in points:
            min_x = min(min_x, p.x)
            min_y = min(min_y, p.y)
            min_z = min(min_z, p.z)
            max_x = max(max_x, p.x)
            max_y = max(max_y, p.y)
            max_z = max(max_z, p.z)

        return cls(vec3(min_x, min_y, min_z), vec3(max_x, max_y, max_z))

    @property
    def center(self):
        """中心点"""
        return (self.min + self.max) * 0.5

    @property
    def size(self):
        """尺寸"""
        return self.max - self.min

    @property
    def extents(self):
        """半长（从中心到边界的距离）"""
        return self.size * 0.5

    def expand(self, point):
        """扩展 AABB 以包含点"""
        self.min = vec3(min(self.min.x, point.x),
                        min(self.min.y, point.y),
                        min(self.min.z, point.z))
        self.max = vec3(max(self.max.x, point.x),
                        max(self.max.y, point.y),
                        max(self.max.z, point.z))

    def inflate(self, amount):
        """均匀扩展 AABB"""
        self.min -= vec3(amount, amount, amount)
        self.max += vec3(amount, amount, amount)

    def contains_point(self, point):
        """检查点是否在盒内"""
        return (self.min.x <= point.x <= self.max.x and
                self.min.y <= point.y <= self.max.y and
                self.min.z <= point.z <= self.max.z)

    def intersects_aabb(self, other):
        """检查与另一个 AABB 是否相交"""
        return (self.min.x <= other.max.x and self.max.x >= other.min.x and
                self.min.y <= other.max.y and self.max.y >= other.min.y and
                self.min.z <= other.max.z and self.max.z >= other.min.z)

    def intersects_sphere(self, center, radius):
        """检查与球体是否相交"""
        closest = vec3(
            max(self.min.x, min(center.x, self.max.x)),
            max(self.min.y, min(center.y, self.max.y)),
            max(self.min.z, min(center.z, self.max.z)),
        )

        dx = center.x - closest.x
        dy = center.y - closest.y
        dz = center.z - closest.z

        return (dx * dx + dy * dy + dz * dz) <= (radius * radius)

    def surface_area(self):
        """表面积"""
        d = self.size
        return 2 * (d.x * d.y + d.y * d.z + d.z * d.x)

    def volume(self):
        """体积"""
        d = self.size
        return d.x * d.y * d.z

    def merge(self, other):
        """合并另一个 AABB"""
        return AABB(
            vec3(min(self.min.x, other.min.x),
                 min(self.min.y, other.min.y),
                 min(self.min.z, other.min.z)),
            vec3(max(self.max.x, other.max.x),
                 max(self.max.y, other.max.y),
                 max(self.max.z, other.max.z)),
        )

    def __repr__(self):
        return f"AABB(min={self.min}, max={self.max})"


class Ray:
    """射线 - 用于射线检测"""

    def __init__(self, origin=None, direction=None):
        """初始化射线"""
        self.origin = origin if origin else vec3(0, 0, 0)
        self.direction = direction if direction else vec3(0, 0, 1)

    def point_at(self, t):
        """获取射线上参数 t 处的点"""
        return self.origin + self.direction * t

    def intersect_sphere(self, center, radius):
        """与球体相交检测"""
        oc = self.origin - center

        b = oc.dot(self.direction)
        c = oc.dot(oc) - radius * radius

        discriminant = b * b - c

        if discriminant < 0:
            return (False, None, None)

        sqrt_disc = sqrt(discriminant)
        t1 = -b - sqrt_disc
        t2 = -b + sqrt_disc

        if t1 < 0:
            t1 = t2
            if t2 < 0:
                return (False, None, None)

        return (True, t1, t2)

    def intersect_plane(self, point, normal):
        """与平面相交检测"""
        denom = normal.dot(self.direction)

        if abs(denom) < EPSILON:
            return (False, None)

        diff = point - self.origin
        t = diff.dot(normal) / denom

        if t < 0:
            return (False, None)

        return (True, t)

    def intersect_triangle(self, v0, v1, v2):
        """与三角形相交检测（Möller-Trumbore 算法）"""
        edge1 = v1 - v0
        edge2 = v2 - v0

        h = self.direction.cross(edge2)
        a = edge1.dot(h)

        if abs(a) < EPSILON:
            return (False, None, None, None)

        f = 1.0 / a
        s = self.origin - v0
        u = f * s.dot(h)

        if u < 0 or u > 1:
            return (False, None, None, None)

        q = s.cross(edge1)
        v = f * self.direction.dot(q)

        if v < 0 or u + v > 1:
            return (False, None, None, None)

        t = f * edge2.dot(q)

        if t < 0:
            return (False, None, None, None)

        return (True, t, u, v)

    def intersect_aabb(self, aabb):
        """与 AABB 相交检测（slab 方法）"""
        tmin = 0.0
        tmax = float("inf")

        for i in range(3):
            origin_i = self.origin[i]
            dir_i = self.direction[i]
            min_i = aabb.min[i]
            max_i = aabb.max[i]

            if abs(dir_i) < EPSILON:
                if origin_i < min_i or origin_i > max_i:
                    return (False, None, None)
            else:
                t1 = (min_i - origin_i) / dir_i
                t2 = (max_i - origin_i) / dir_i

                if t1 > t2:
                    t1, t2 = t2, t1

                tmin = max(tmin, t1)
                tmax = min(tmax, t2)

                if tmin > tmax:
                    return (False, None, None)

        return (True, tmin, tmax)

    def closest_point_to(self, point):
        """射线上离给定点最近的点"""
        op = point - self.origin
        t = op.dot(self.direction)
        t = max(0, t)
        return self.point_at(t)

    def distance_to_point(self, point):
        """射线到点的距离"""
        closest = self.closest_point_to(point)
        return closest.distance(point)

    def __repr__(self):
        return f"Ray(origin={self.origin}, direction={self.direction})"


class Sphere:
    """球体"""

    def __init__(self, center=None, radius=1.0):
        """初始化球体"""
        self.center = center if center else vec3(0, 0, 0)
        self.radius = float(radius)

    def contains_point(self, point):
        """检查点是否在球内"""
        return point.distance_squared(self.center) <= self.radius * self.radius

    def intersects_sphere(self, other):
        """检查与另一个球体是否相交"""
        dist_sq = self.center.distance_squared(other.center)
        radius_sum = self.radius + other.radius
        return dist_sq <= radius_sum * radius_sum

    def intersects_aabb(self, aabb):
        """检查与 AABB 是否相交"""
        return aabb.intersects_sphere(self.center, self.radius)

    def surface_area(self):
        """表面积"""
        return 4 * pi * self.radius * self.radius

    def volume(self):
        """体积"""
        return (4.0 / 3.0) * pi * self.radius ** 3

    def __repr__(self):
        return f"Sphere(center={self.center}, radius={self.radius})"


class Plane:
    """平面"""

    def __init__(self, normal=None, point=None, d=None):
        """初始化平面"""
        if normal and point:
            self.normal = normal.normalize()
            self.d = -self.normal.dot(point)
        elif normal and d is not None:
            self.normal = normal.normalize()
            self.d = d
        else:
            self.normal = vec3(0, 1, 0)
            self.d = 0

    @classmethod
    def from_three_points(cls, p1, p2, p3):
        """从三个点创建平面"""
        edge1 = p2 - p1
        edge2 = p3 - p1
        normal = edge1.cross(edge2).normalize()
        return cls(normal, p1)

    def distance_to_point(self, point):
        """点到平面的有符号距离"""
        return self.normal.dot(point) + self.d

    def project_point(self, point):
        """将点投影到平面上"""
        dist = self.distance_to_point(point)
        return point - self.normal * dist

    def is_on_plane(self, point, tolerance=EPSILON):
        """检查点是否在平面上"""
        return abs(self.distance_to_point(point)) < tolerance

    def __repr__(self):
        return f"Plane(normal={self.normal}, d={self.d})"


def project_3d_to_2d(point, camera_pos, camera_angle, fov=60, width=800, height=600):
    """将 3D 点投影到 2D 屏幕坐标"""

    # 1. 计算相对位置
    local = vec3(
        point.x - camera_pos.x,
        point.y - camera_pos.y,
        point.z - camera_pos.z,
    )

    pitch, yaw, roll = camera_angle.x, camera_angle.y, camera_angle.z

    cy, sy = cos(yaw), sin(yaw)
    cp, sp = cos(pitch), sin(pitch)
    cr, sr = cos(roll), sin(roll)

    x = local.x
    y = local.y
    z = local.z

    x1 = x * cy - z * sy
    z1 = x * sy + z * cy
    y1 = y

    y2 = y1 * cp - z1 * sp
    z2 = y1 * sp + z1 * cp
    x2 = x1

    cam_x = x2 * cr - y2 * sr
    cam_y = x2 * sr + y2 * cr
    cam_z = z2

    if cam_z <= 0:
        return None

    # 4. 透视投影
    fov_rad = fov * pi / 180
    scale = 1 / tan(fov_rad / 2)

    ndc_x = (cam_x / cam_z) * scale
    ndc_y = (cam_y / cam_z) * scale

    # 5. 映射到屏幕像素
    screen_x = (ndc_x + 1) * width / 2
    screen_y = (1 - ndc_y) * height / 2

    return (screen_x, screen_y)
