from .scache import memoize
from .smath import EPSILON, acos, cos, pi, sin, sqrt
from .svector import vec2


class Polygon:
    """多边形"""

    def __init__(self, points):
        """初始化多边形"""
        self.vertices = [p if isinstance(
            p, vec2) else vec2(p[0], p[1]) for p in points]
        self._cached_edges = None
        self._cached_normals = None
        self._cache = None

    @property
    def edges(self):
        """获取所有边"""
        if self._cached_edges is None:
            self._cached_edges = []
            n = len(self.vertices)
            for i in range(n):
                edge = self.vertices[(i+1) % n] - self.vertices[i]
                self._cached_edges.append(edge)
        return self._cached_edges

    @property
    def normals(self):
        """获取所有边的法线"""
        if self._cached_normals is None:
            self._cached_normals = []
            center = self._center()
            for i, edge in enumerate(self.edges):
                normal = vec2(-edge.y, edge.x).normalize()
                # 确保法线向外
                mid_point = (
                    self.vertices[i] + self.vertices[(i+1) % len(self.vertices)]) * 0.5
                if (mid_point - center).dot(normal) < 0:
                    normal = -normal
                self._cached_normals.append(normal)
        return self._cached_normals

    @memoize(method=True)
    def get_rects(self, step=10):
        """将多边形转换为 AABB 矩形列表"""
        # 获取包围盒
        if self._cache:
            return self._cache
        if step == 0:
            raise ValueError("step必须大于0")
        min_x, min_y, w, h = self.get_aabb()
        max_x, max_y = min_x + w, min_y + h

        rects = []
        half_step = step / 2

        for y in range(int(min_y), int(max_y), step):
            start_x = None

            for x in range(int(min_x), int(max_x), step):
                cx, cy = x + half_step, y + half_step

                if self.contains_point(vec2(cx, cy)):
                    if start_x is None:
                        start_x = x
                else:
                    if start_x is not None:
                        rects.append(Rect(start_x, y, x - start_x, step))
                        start_x = None

            if start_x is not None:
                rects.append(Rect(start_x, y, max_x - start_x, step))
        self._cache = rects

        return rects

    def contains_point(self, point):
        """点是否在多边形内"""
        if isinstance(point, (tuple, list)):
            point = vec2(point[0], point[1])

        inside = False
        n = len(self.vertices)

        for i in range(n):
            v1 = self.vertices[i]
            v2 = self.vertices[(i+1) % n]

            # 检查射线是否穿过边
            if ((v1.y > point.y) != (v2.y > point.y)) and \
               (point.x < (v2.x - v1.x) * (point.y - v1.y) / (v2.y - v1.y) + v1.x):
                inside = not inside

        return inside

    def contains_point_accurate(self, point):
        """点是否在多边形边界上或多边形内"""
        if self._on_boundary(point):
            return True

        return self.contains_point(point)

    def get_aabb(self):
        """获取包围盒"""
        xs = [v.x for v in self.vertices]
        ys = [v.y for v in self.vertices]
        return (min(xs), min(ys), max(xs)-min(xs), max(ys)-min(ys))

    def convex_hull(self):
        """计算凸包"""
        points = sorted(self.vertices, key=lambda p: (p.x, p.y))

        if len(points) <= 1:
            return Polygon(points)

        def cross(o, a, b):
            return (a.x - o.x) * (b.y - o.y) - (a.y - o.y) * (b.x - o.x)

        lower = []
        for p in points:
            while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
                lower.pop()
            lower.append(p)

        upper = []
        for p in reversed(points):
            while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
                upper.pop()
            upper.append(p)

        # 合并，去掉重复的端点
        hull = lower[:-1] + upper[:-1]
        return Polygon(hull)

    def triangulate(self):
        """耳剪裁算法（支持凸多边形）"""
        if len(self.vertices) < 3:
            return []

        # 先转成逆时针顺序
        vertices = self.vertices.copy()
        if self._signed_area() < 0:
            vertices.reverse()

        triangles = []
        n = len(vertices)

        for _ in range(n - 2):
            for i in range(len(vertices)):
                prev = vertices[i-1]
                curr = vertices[i]
                nxt = vertices[(i+1) % len(vertices)]

                # 检查是否是凸耳
                if self._is_convex_vertex(prev, curr, nxt) and self._no_vertex_inside(prev, curr, nxt, vertices):
                    triangles.append([prev, curr, nxt])
                    vertices.pop(i)
                    break

        return triangles

    def _signed_area(self):
        """计算有向面积，正=逆时针，负=顺时针"""
        area = 0
        n = len(self.vertices)
        for i in range(n):
            v1 = self.vertices[i]
            v2 = self.vertices[(i+1) % n]
            area += v1.x * v2.y - v2.x * v1.y
        return area / 2

    def _is_convex_vertex(self, a, b, c):
        cross = (b.x - a.x) * (c.y - b.y) - (b.y - a.y) * (c.x - b.x)
        return cross <= 0  # 逆时针多边形中，凸顶点交叉积为负或零

    def collide_rect(self, rect):
        """多边形与矩形碰撞（SAT）"""
        # 矩形转多边形
        rect_poly = Polygon([
            vec2(rect.x, rect.y),
            vec2(rect.x + rect.w, rect.y),
            vec2(rect.x + rect.w, rect.y + rect.h),
            vec2(rect.x, rect.y + rect.h),
        ])
        return self.collide_polygon(rect_poly)

    def _on_boundary(self, point):
        for i in range(len(self.vertices)):
            v1 = self.vertices[i]
            v2 = self.vertices[(i+1) % len(self.vertices)]
            if self._point_on_segment(point, v1, v2):
                return True
        return False

    def _point_on_segment(self, point, a, b, tolerance=EPSILON):
        """检查点是否在线段 ab 上"""
        # 检查点是否在线段边界框内
        min_x = min(a.x, b.x) - tolerance
        max_x = max(a.x, b.x) + tolerance
        min_y = min(a.y, b.y) - tolerance
        max_y = max(a.y, b.y) + tolerance

        if not (min_x <= point.x <= max_x and min_y <= point.y <= max_y):
            return False

        # 检查共线性：叉积为 0
        cross = (b.x - a.x) * (point.y - a.y) - (b.y - a.y) * (point.x - a.x)
        if abs(cross) > tolerance:
            return False

        # 检查点是否在线段范围内（点积）
        dot = (point.x - a.x) * (b.x - a.x) + (point.y - a.y) * (b.y - a.y)
        if dot < -tolerance:
            return False

        squared_len = (b.x - a.x) ** 2 + (b.y - a.y) ** 2
        if dot > squared_len + tolerance:
            return False

        return True

    def collide_polygon(self, other):
        """多边形与多边形碰撞"""
        # 收集所有要检查的轴
        axes = self.normals + other.normals

        for axis in axes:
            proj1 = self._project(axis)
            proj2 = other._project(axis)

            if proj1[1] < proj2[0] or proj2[1] < proj1[0]:
                return False  # 找到分离轴

        return True  # 没有分离轴，碰撞

    def _project(self, axis):
        """在轴上的投影区间"""
        dots = [v.dot(axis) for v in self.vertices]
        return (min(dots), max(dots))

    def move(self, dx, dy):
        """平移"""
        return Polygon([vec2(v.x + dx, v.y + dy) for v in self.vertices])

    def rotate(self, angle, center=None):
        """旋转"""
        if center is None:
            center = self._center()

        c, s = cos(angle), sin(angle)
        new_vertices = []
        for v in self.vertices:
            dx = v.x - center.x
            dy = v.y - center.y
            new_vertices.append(vec2(
                center.x + dx * c - dy * s,
                center.y + dx * s + dy * c,
            ))
        return Polygon(new_vertices)

    def _center(self):
        """重心"""
        if not self.vertices:
            return vec2(0, 0)
        total = vec2(0, 0)
        for v in self.vertices:
            total += v
        return total / len(self.vertices)

    def scale(self, factor, center=None):
        """缩放"""
        if center is None:
            center = self._center()
        return Polygon([center + (v - center) * factor for v in self.vertices])

    def __repr__(self):
        return f"Polygon({self.vertices})"


class Rect:
    """矩形"""

    def __init__(self, x=0, y=0, w=0, h=0, angle=0):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.angle = angle  # 弧度，默认0

    @property
    def left(self):
        return self.x

    @property
    def angle(self):
        return self._angle * 180 / pi

    @angle.setter
    def angle(self, value):
        self._angle = (value % 180) / 180 * pi

    @property
    def right(self):
        return self.x + self.w

    @property
    def top(self):
        return self.y

    @property
    def bottom(self):
        return self.y + self.h

    @property
    def center(self):
        return vec2(self.x + self.w/2, self.y + self.h/2)

    @property
    def topleft(self):
        return vec2(self.x, self.y)

    @property
    def topright(self):
        return vec2(self.x + self.w, self.y)

    @property
    def bottomleft(self):
        return vec2(self.x, self.y + self.h)

    @property
    def bottomright(self):
        return vec2(self.x + self.w, self.y + self.h)

    @property
    def width(self):
        return self.w

    @property
    def height(self):
        return self.h

    @property
    def area(self):
        return self.w * self.h

    def _rotated_verts(self):
        if self._angle == 0:
            return [
                vec2(self.x, self.y),
                vec2(self.x + self.w, self.y),
                vec2(self.x + self.w, self.y + self.h),
                vec2(self.x, self.y + self.h),
            ]

        cx, cy = self.x + self.w/2, self.y + self.h/2
        half_w, half_h = self.w/2, self.h/2
        c, s = cos(self._angle), sin(self._angle)

        return [
            vec2(cx + (-half_w)*c - (-half_h)*s,
                 cy + (-half_w)*s + (-half_h)*c),
            vec2(cx + (half_w)*c - (-half_h)*s, cy + (half_w)*s + (-half_h)*c),
            vec2(cx + (half_w)*c - (half_h)*s, cy + (half_w)*s + (half_h)*c),
            vec2(cx + (-half_w)*c - (half_h)*s, cy + (-half_w)*s + (half_h)*c),
        ]

    @memoize(method=True)
    def get_rects(self, step=10):
        if self.angle == 0:
            return [Rect(self.x, self.y, self.w, self.h)]

        if step == 0:
            raise ValueError("step必须大于0")
        verts = self._rotated_verts()
        min_x = int(min(v.x for v in verts))
        max_x = int(max(v.x for v in verts))
        min_y = int(min(v.y for v in verts))
        max_y = int(max(v.y for v in verts))

        edges = []
        for i in range(4):
            v1 = verts[i]
            v2 = verts[(i+1) % 4]
            edges.append((v1, v2))

        rects = []
        half_step = step / 2

        for y in range(min_y, max_y, step):
            start_x = None
            for x in range(min_x, max_x, step):
                cx, cy = x + half_step, y + half_step

                inside = True
                for v1, v2 in edges:
                    cross = (v2.x - v1.x) * (cy - v1.y) - \
                        (v2.y - v1.y) * (cx - v1.x)
                    if cross < 0:
                        inside = False
                        break

                if inside:
                    if start_x is None:
                        start_x = x
                else:
                    if start_x is not None:
                        rects.append(Rect(start_x, y, x - start_x, step))
                        start_x = None
            if start_x is not None:
                rects.append(Rect(start_x, y, max_x - start_x, step))

        return rects

    def collide_point(self, x, y=None):
        """点是否在矩形内"""
        if y is None:
            x, y = x.x, x.y

        if self.angle == 0:
            return (self.x <= x <= self.x + self.w and
                    self.y <= y <= self.y + self.h)

        verts = self._rotated_verts()

        def cross(ox, oy, ax, ay, bx, by):
            return (ax - ox) * (by - oy) - (ay - oy) * (bx - ox)

        last = None
        for i in range(4):
            v1 = verts[i]
            v2 = verts[(i+1) % 4]
            c = cross(v1.x, v1.y, v2.x, v2.y, x, y)

            if abs(c) < EPSILON:
                continue

            if last is None:
                last = c > 0
            elif (c > 0) != last:
                return False

        return True

    def collide_rect(self, other):
        """矩形与矩形碰撞"""
        if self._angle == 0 and other._angle == 0:
            return (self.x < other.x + other.w and
                    self.x + self.w > other.x and
                    self.y < other.y + other.h and
                    self.y + self.h > other.y)

        # 分离轴定理（SAT）
        axes = self._get_axes() + other._get_axes()
        for axis in axes:
            if not self._overlap_on_axis(other, axis):
                return False
        return True

    def _get_axes(self):
        """获取分离轴"""
        if self._angle == 0:
            return [vec2(1, 0), vec2(0, 1)]

        verts = self._rotated_verts()
        axes = []
        for i in range(4):
            edge = verts[(i+1) % 4] - verts[i]
            # 垂直方向（法线）
            axis = vec2(-edge.y, edge.x).normalize()
            axes.append(axis)
        return axes

    def _overlap_on_axis(self, other, axis):
        """检查在轴上的投影是否重叠"""
        p1 = self._project(axis)
        p2 = other._project(axis)
        return not (p1[1] < p2[0] or p2[1] < p1[0])

    def _project(self, axis):
        """在轴上的投影区间"""
        verts = self._rotated_verts()
        dots = [v.x*axis.x + v.y*axis.y for v in verts]
        return (min(dots), max(dots))

    def collide_circle(self, circle):
        """矩形与圆碰撞"""
        if self._angle == 0:
            closest_x = max(self.x, min(circle.center.x, self.x + self.w))
            closest_y = max(self.y, min(circle.center.y, self.y + self.h))
            dx = circle.center.x - closest_x
            dy = circle.center.y - closest_y
            return (dx*dx + dy*dy) <= circle.radius * circle.radius

        # 旋转情况：将圆变换到矩形局部坐标系
        cx, cy = self.x + self.w/2, self.y + self.h/2
        dx, dy = circle.center.x - cx, circle.center.y - cy
        c, s = cos(-self._angle), sin(-self._angle)
        lx = dx * c - dy * s
        ly = dx * s + dy * c

        # 在局部坐标系中，矩形是轴对齐的
        closest_x = max(-self.w/2, min(lx, self.w/2))
        closest_y = max(-self.h/2, min(ly, self.h/2))
        dx = lx - closest_x
        dy = ly - closest_y
        return (dx*dx + dy*dy) <= circle.radius * circle.radius

    def inflate(self, dw, dh):
        """扩展矩形"""
        return Rect(
            self.x - dw/2,
            self.y - dh/2,
            self.w + dw,
            self.h + dh,
            self._angle,
        )

    def expand(self, *args):
        """扩展矩形以包含点或其他矩形"""
        # 获取当前矩形的四个顶点（旋转后的）
        verts = list(self._rotated_verts())

        # 添加新的点/矩形顶点
        if len(args) == 1:
            arg = args[0]
            if isinstance(arg, Rect):
                verts.extend(arg._rotated_verts())
            elif hasattr(arg, "x") and hasattr(arg, "y"):
                verts.append(vec2(arg.x, arg.y))
            else:
                verts.append(vec2(arg[0], arg[1]))
        else:
            verts.append(vec2(args[0], args[1]))

        c, s = cos(-self._angle), sin(-self._angle)
        local_verts = []
        for v in verts:
            dx = v.x - self.center.x
            dy = v.y - self.center.y
            lx = dx * c - dy * s
            ly = dx * s + dy * c
            local_verts.append(vec2(lx, ly))

        min_x = min(v.x for v in local_verts)
        max_x = max(v.x for v in local_verts)
        min_y = min(v.y for v in local_verts)
        max_y = max(v.y for v in local_verts)

        new_cx = (min_x + max_x) / 2
        new_cy = (min_y + max_y) / 2
        new_w = max_x - min_x
        new_h = max_y - min_y

        c2, s2 = cos(self._angle), sin(self._angle)
        world_cx = self.center.x + new_cx * c2 - new_cy * s2
        world_cy = self.center.y + new_cx * s2 + new_cy * c2

        return Rect(
            world_cx - new_w/2,
            world_cy - new_h/2,
            new_w,
            new_h,
            self._angle,
        )

    def move(self, dx, dy):
        """移动矩形"""
        return Rect(self.x + dx, self.y + dy, self.w, self.h, self._angle)

    def union(self, other):
        """计算两个矩形的最小包围盒"""
        x = min(self.x, other.x)
        y = min(self.y, other.y)
        w = max(self.right, other.right) - x
        h = max(self.bottom, other.bottom) - y
        return Rect(x, y, w, h, 0)

    def __repr__(self):
        if self._angle == 0:
            return f"Rect({self.x:.2f}, {self.y:.2f}, {self.w:.2f}, {self.h:.2f})"
        return f"Rect({self.x:.2f}, {self.y:.2f}, {self.w:.2f}, {self.h:.2f}, angle={self.angle:.2f}°)"


class Circle:
    """圆形"""

    def __init__(self, center, radius):
        self.center = center if isinstance(
            center, vec2) else vec2(center[0], center[1])
        self.radius = radius

    def collide_point(self, x, y=None):
        """点与圆碰撞"""
        if y is None:
            x, y = x.x, x.y
        dx = x - self.center.x
        dy = y - self.center.y
        return (dx*dx + dy*dy) <= self.radius * self.radius

    @property
    def area(self):
        """圆面积"""
        return self.radius ** 2 * pi

    def collide_circle(self, other):
        """圆与圆碰撞"""
        dx = self.center.x - other.center.x
        dy = self.center.y - other.center.y
        return (dx*dx + dy*dy) <= (self.radius + other.radius) ** 2

    def collide_rect(self, rect):
        """圆与矩形碰撞（复用Rect的碰撞）"""
        return rect.collide_circle(self)

    def __repr__(self):
        return f"Circle({self.center}, {self.radius})"

    @memoize(method=True)
    def get_rects(self, step=10):
        """将圆形转换为小矩形列表（用于轴对齐渲染器）"""
        if step <= 0:
            raise ValueError("step必须大于0")

        rects = []
        cx, cy = self.center.x, self.center.y
        r = self.radius

        # 计算包围盒
        min_x = int(cx - r)
        max_x = int(cx + r)
        min_y = int(cy - r)
        max_y = int(cy + r)

        half_step = step / 2
        r_sq = r * r

        for y in range(min_y, max_y, step):
            start_x = None
            for x in range(min_x, max_x, step):
                # 检查采样点是否在圆内
                dx = (x + half_step) - cx
                dy = (y + half_step) - cy
                if dx*dx + dy*dy <= r_sq:
                    if start_x is None:
                        start_x = x
                else:
                    if start_x is not None:
                        rects.append(Rect(start_x, y, x - start_x, step))
                        start_x = None
            if start_x is not None:
                rects.append(Rect(start_x, y, max_x - start_x, step))

        return rects


class Line2:
    """2D线段"""

    def __init__(self, p1, p2):
        self.p1 = p1 if isinstance(p1, vec2) else vec2(p1[0], p1[1])
        self.p2 = p2 if isinstance(p2, vec2) else vec2(p2[0], p2[1])

    def length(self):
        """线段长度"""
        dx = self.p2.x - self.p1.x
        dy = self.p2.y - self.p1.y
        return sqrt(dx*dx + dy*dy)

    def closest_point(self, p):
        """线段上离点p最近的点"""
        p = p if isinstance(p, vec2) else vec2(p[0], p[1])

        # 向量
        ab = vec2(self.p2.x - self.p1.x, self.p2.y - self.p1.y)
        ap = vec2(p.x - self.p1.x, p.y - self.p1.y)

        # 投影系数 t
        ab_len2 = ab.x*ab.x + ab.y*ab.y
        if ab_len2 == 0:  # 线段退化成点
            return self.p1

        t = (ap.x*ab.x + ap.y*ab.y) / ab_len2
        t = max(0, min(1, t))  # 限制在线段范围内

        return vec2(
            self.p1.x + t * ab.x,
            self.p1.y + t * ab.y,
        )

    def collide_point(self, x, y=None, tolerance=0.1):
        """点是否在线段上（在容差范围内）"""
        if y is None:
            x, y = x.x, x.y
        p = vec2(x, y)
        closest = self.closest_point(p)
        dx = p.x - closest.x
        dy = p.y - closest.y
        return (dx*dx + dy*dy) <= tolerance * tolerance

    def intersect_line(self, other):
        """线段与线段相交检测"""
        # 参数方程
        x1, y1 = self.p1.x, self.p1.y
        x2, y2 = self.p2.x, self.p2.y
        x3, y3 = other.p1.x, other.p1.y
        x4, y4 = other.p2.x, other.p2.y

        denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if denom == 0:  # 平行
            return None

        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
        u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denom

        if 0 <= t <= 1 and 0 <= u <= 1:
            x = x1 + t * (x2 - x1)
            y = y1 + t * (y2 - y1)
            return vec2(x, y)
        return None

    def __repr__(self):
        return f"Line2({self.p1}, {self.p2})"


def raycast_rect(ray_origin, ray_dir, rect):
    """射线与矩形碰撞检测（返回碰撞点、距离、法线、入射角）"""
    t_min = -float("inf")
    t_max = float("inf")
    hit_normal = None

    for i in range(2):
        if abs(ray_dir[i]) < EPSILON:
            if ray_origin[i] < rect.x or ray_origin[i] > rect.x + rect.w:
                return None, None, None, None
            continue

        t1 = (rect.x - ray_origin[i]) / ray_dir[i]
        t2 = (rect.x + rect.w - ray_origin[i]) / ray_dir[i]

        if t1 > t2:
            t1, t2 = t2, t1

        if t1 > t_min:
            t_min = t1
            if i == 0:
                hit_normal = vec2(-1 if ray_dir[i] > 0 else 1, 0)
            else:
                hit_normal = vec2(0, -1 if ray_dir[i] > 0 else 1)

        t_max = min(t_max, t2)

    if t_max >= t_min and t_max > 0:
        t = t_min if t_min > 0 else t_max
        hit_point = vec2(
            ray_origin.x + t * ray_dir.x,
            ray_origin.y + t * ray_dir.y,
        )

        ray_dir_norm = ray_dir.normalize()
        dot = ray_dir_norm.dot(hit_normal)
        angle = acos(max(-1, min(1, dot)))

        return hit_point, t, hit_normal, angle

    return None, None, None, None


def reflect(vector, normal):
    """反射向量"""
    dot = vector.x * normal.x + vector.y * normal.y
    return vec2(
        vector.x - 2 * dot * normal.x,
        vector.y - 2 * dot * normal.y,
    )


def rect(x=0, y=0, w=0, h=0, angle=0):
    """创建矩形"""
    return Rect(x, y, w, h, angle)


def circle(center, radius):
    """创建圆形"""
    return Circle(center, radius)


def line(p1, p2):
    """创建线段"""
    return Line2(p1, p2)
