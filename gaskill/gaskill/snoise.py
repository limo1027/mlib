from .sinterp import lerp
from .smath import cos, floor, pi, sin, sqrt
from .srandom import Random


class PerlinNoise:
    """Perlin 噪声 - 平滑连续的梯度噪声，适合地形"""

    def __init__(self, seed=None, octaves=4, persistence=0.5, lacunarity=2.0):
        self.rng = Random(seed)
        self.octaves = octaves
        self.persistence = persistence
        self.lacunarity = lacunarity

        self._init_gradients()

    def _init_gradients(self, size=256):
        """初始化梯度向量表和置换表"""
        self._size = size
        self._mask = size - 1

        # 随机梯度向量（8个方向或更多）
        self._gradients = []
        for _ in range(size):
            angle = self.rng.random() * 2 * pi
            self._gradients.append((cos(angle), sin(angle)))

        # 置换表（0..size-1 的随机排列）
        self._perm = list(range(size))
        self.rng.shuffle(self._perm)

        # 重复一次防止越界（重要！）
        self._perm = self._perm * 2

    def _gradient(self, ix, iy, x, y):
        """计算梯度值：gradient · (dx, dy)"""
        # 使用双重置换，确保索引在范围内
        perm = self._perm
        idx = perm[ix & self._mask] + iy
        grad_idx = perm[idx & self._mask] & self._mask
        gx, gy = self._gradients[grad_idx]

        dx = x - ix
        dy = y - iy
        return gx * dx + gy * dy

    def _fade(self, t):
        """缓和曲线 6t^5 - 15t^4 + 10t^3"""
        return t * t * t * (t * (t * 6 - 15) + 10)

    def noise2d(self, x, y):
        """2D Perlin 噪声，返回值 [-1, 1]"""
        # 整数坐标
        xi = floor(x)
        yi = floor(y)

        # 局部坐标 [0, 1)
        fx = x - xi
        fy = y - yi

        # 缓和曲线
        u = self._fade(fx)
        v = self._fade(fy)

        # 四个角的梯度值
        n00 = self._gradient(xi, yi, x, y)
        n10 = self._gradient(xi + 1, yi, x, y)
        n01 = self._gradient(xi, yi + 1, x, y)
        n11 = self._gradient(xi + 1, yi + 1, x, y)

        # 双线性插值
        nx0 = lerp(n00, n10, u)
        nx1 = lerp(n01, n11, u)

        return lerp(nx0, nx1, v)

    def fbm2d(self, x, y):
        """分形布朗运动 - 多层叠加，产生自然地形"""
        value = 0.0
        amplitude = 1.0
        frequency = 1.0
        max_value = 0.0

        for _ in range(self.octaves):
            value += amplitude * self.noise2d(x * frequency, y * frequency)
            max_value += amplitude
            amplitude *= self.persistence
            frequency *= self.lacunarity

        # 归一化到 [-1, 1]
        if max_value > 0:
            return value / max_value
        return 0.0

    def terrain_height(self, x, y):
        """地形高度 [-1, 1] -> 更自然"""
        h = self.fbm2d(x, y)

        # 山脊效果
        ridge = 1 - abs(h)
        ridge = ridge ** 2

        # 混合
        return h * 0.8 + ridge * 0.2


class SimplexNoise(PerlinNoise):
    """Simplex 噪声 - 正确实现，无方块痕迹"""

    def __init__(self, seed=None, octaves=4, persistence=0.5, lacunarity=2.0):
        super().__init__(seed, octaves, persistence, lacunarity)

        # 预计算 Skew 和 Unskew 因子
        self._skew_factor_2d = (sqrt(3) - 1) / 2
        self._unskew_factor_2d = (3 - sqrt(3)) / 6

    def _gradient(self, ix, iy, x, y):
        """重写梯度计算，避免越界"""
        perm = self._perm
        # 确保索引在有效范围内
        idx = perm[ix & self._mask] + iy
        grad_idx = perm[idx & self._mask] & self._mask
        gx, gy = self._gradients[grad_idx]

        dx = x - ix
        dy = y - iy
        return gx * dx + gy * dy

    def noise2d(self, x, y):
        """2D Simplex 噪声 - 正确实现"""
        # Skew 变换到三角形网格
        s = (x + y) * self._skew_factor_2d
        i = floor(x + s)
        j = floor(y + s)

        # Unskew 回到原始空间
        t = (i + j) * self._unskew_factor_2d
        x0 = x - (i - t)
        y0 = y - (j - t)

        # 确定 simplex 形状
        if x0 > y0:
            i1, j1 = 1, 0
        else:
            i1, j1 = 0, 1


        # 三个顶点
        # 顶点 0
        n0 = self._gradient(i, j, x, y)

        # 顶点 1
        x1 = x0 - i1 + self._unskew_factor_2d
        y1 = y0 - j1 + self._unskew_factor_2d
        n1 = self._gradient(i + i1, j + j1, x1 + i, y1 + j)

        # 顶点 2
        x2 = x0 - 1 + 2 * self._unskew_factor_2d
        y2 = y0 - 1 + 2 * self._unskew_factor_2d
        n2 = self._gradient(i + 1, j + 1, x2 + i, y2 + j)

        # 贡献计算
        t0 = 0.5 - x0*x0 - y0*y0
        if t0 < 0:
            t0 = 0
        t0 = t0 * t0 * t0 * t0

        t1 = 0.5 - x1*x1 - y1*y1
        if t1 < 0:
            t1 = 0
        t1 = t1 * t1 * t1 * t1

        t2 = 0.5 - x2*x2 - y2*y2
        if t2 < 0:
            t2 = 0
        t2 = t2 * t2 * t2 * t2

        # 结果缩放（使范围大致在 [-1, 1]）
        return 32.0 * (t0 * n0 + t1 * n1 + t2 * n2)

    def fbm2d(self, x, y):
        """分形布朗运动"""
        value = 0.0
        amplitude = 1.0
        frequency = 1.0
        max_value = 0.0

        for _ in range(self.octaves):
            value += amplitude * self.noise2d(x * frequency, y * frequency)
            max_value += amplitude
            amplitude *= self.persistence
            frequency *= self.lacunarity

        if max_value > 0:
            return value / max_value
        return 0.0

class Snoise:
    """简单噪声场 - 由控制点定义的平滑插值。不适用于地形, 适用于热力图"""

    def __init__(self, falloff=1.0):
        """初始化噪声场"""
        self.points = []  # [(x, y, value), ...]
        self.falloff = falloff
        self._cache = {}

    def add_point(self, x, y, value):
        """添加控制点"""
        self.points.append((float(x), float(y), float(value), self.falloff))
        self._cache.clear()  # 清空缓存
        return self

    def add_points(self, *points):
        """批量添加控制点"""
        for p in points:
            if len(p) == 3:
                self.add_point(*p)
        return self

    def clear(self):
        """清空所有控制点"""
        self.points.clear()
        self._cache.clear()
        return self

    def set_falloff(self, falloff):
        """设置衰减系数"""
        self.falloff = falloff
        self._cache.clear()
        return self

    def _compute(self, x, y):
        """计算 (x,y) 处的噪声值"""
        if not self.points:
            return 0.0

        total_weight = 0.0
        total_value = 0.0

        for px, py, pv, pf in self.points:
            dx = x - px
            dy = y - py
            dist_sq = dx*dx + dy*dy

            if dist_sq == 0:
                return pv  # 正好在控制点上

            # 距离平方反比权重
            weight = 1.0 / (dist_sq ** (1/pf))
            total_weight += weight
            total_value += pv * weight

        return total_value / total_weight if total_weight != 0 else 0.0

    def __call__(self, x, y, use_cache=True):
        """获取 (x,y) 处的噪声值"""
        if not use_cache:
            return self._compute(x, y)

        key = (float(x), float(y))
        if key not in self._cache:
            self._cache[key] = self._compute(x, y)
        return self._cache[key]

    def sample_rect(self, x1, y1, x2, y2, step=1.0):
        """采样矩形区域，返回二维数组"""
        width = int((x2 - x1) / step) + 1
        height = int((y2 - y1) / step) + 1

        result = []
        for iy in range(height):
            y = y1 + iy * step
            row = []
            for ix in range(width):
                x = x1 + ix * step
                row.append(self(x, y))
            result.append(row)
        return result

    def heatmap(self, x1, y1, x2, y2, step=1.0):
        """生成热力图数据（0-255整数）"""
        samples = self.sample_rect(x1, y1, x2, y2, step)

        # 找最小最大值
        flat = [v for row in samples for v in row]
        min_val = min(flat)
        max_val = max(flat)
        range_val = max_val - min_val or 1

        # 映射到0-255
        return [
            [int((v - min_val) / range_val * 255) for v in row]
            for row in samples
        ]

    def __repr__(self):
        return f"Snoise(points={len(self.points)}, falloff={self.falloff})"


# ========== 快捷函数 ==========

def snoise_from_points(points, falloff=1.0):
    """从点列表创建噪声场"""
    n = Snoise(falloff)
    n.add_points(*points)
    return n
