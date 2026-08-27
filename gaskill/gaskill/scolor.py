# scolor.py - 颜色处理模块

from .sinterp import lerp
from .smath import clamp
from .type import Color


def rgb(r: int, g: int, b: int) -> Color:
    """RGB 颜色 (0-255)"""
    return (int(r), int(g), int(b))


def rgba(r: int, g: int, b: int, a: int = 255) -> "tuple[int, int, int, int]":
    """RGBA 颜色"""
    return (int(r), int(g), int(b), int(a))


def hex_to_rgb(hex_str: str) -> Color:
    """16 进制转 RGB，如 #FF0000 转 (255,0,0)"""
    hex_str = hex_str.lstrip("#")
    r = int(hex_str[0:2], 16)
    g = int(hex_str[2:4], 16)
    b = int(hex_str[4:6], 16)
    return (r, g, b)


def rgb_to_hex(r: int, g: int, b: int):
    """RGB 转 16 进制"""
    return f"#{int(r):02x}{int(g):02x}{int(b):02x}"


def complementary(color: Color, mode="rgb") -> Color:
    """返回互补色"""
    if mode == "rgb":
        return tuple(255 - c for c in color[:3])

    elif mode == "hsv":
        h, s, v = color
        return ((h + 180) % 360, s, v)

    else:
        raise ValueError("mode 必须是 'rgb' 或 'hsv'")


def color_lerp(c1: Color, c2: Color, t: float):
    """颜色线性插值"""
    t = clamp(t, 0, 1)
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2, strict=False))


def rgb_to_hsv(r: int, g: int, b: int) -> "tuple[float, float, float]":
    """RGB 转 HSV"""

    _r, _g, _b = r / 255.0, g / 255.0, b / 255.0
    cmax = max(_r, _g, _b)
    cmin = min(_r, _g, _b)
    delta = cmax - cmin

    if delta == 0:
        h = 0
    elif cmax == _r:
        h = 60 * (((_g - _b) / delta) % 6)
    elif cmax == _g:
        h = 60 * (((_b - _r) / delta) + 2)
    else:
        h = 60 * (((_r - _g) / delta) + 4)

    if h < 0:
        h += 360

    if cmax == 0:
        s = 0
    else:
        s = delta / cmax

    v = cmax

    return (h, s, v)


def hsv_to_rgb(h: float, s: float, v: float) -> Color:
    """HSV 转 RGB，返回 (0-255) 的 RGB 值"""
    h = h % 360
    s = clamp(s, 0, 1)
    v = clamp(v, 0, 1)

    c = v * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = v - c

    if h < 60:
        r, g, b = c, x, 0
    elif h < 120:
        r, g, b = x, c, 0
    elif h < 180:
        r, g, b = 0, c, x
    elif h < 240:
        r, g, b = 0, x, c
    elif h < 300:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x

    return (int((r + m) * 255), int((g + m) * 255), int((b + m) * 255))


def blend(c1: Color, c2: Color, mode: str = "normal", alpha: float = 0.5):
    """颜色混合模式"""
    alpha = clamp(alpha, 0, 1)

    if mode == "normal":
        result = []
        for a, b in zip(c1[:3], c2[:3], strict=False):
            result.append(int(a + (b - a) * alpha))
        if len(c1) > 3:
            result.append(c1[3])
        return tuple(result)

    elif mode == "multiply":
        return tuple(int(a * b / 255) for a, b in zip(c1[:3], c2[:3], strict=False))

    elif mode == "screen":
        return tuple(255 - int((255 - a) * (255 - b) / 255) for a, b in zip(c1[:3], c2[:3], strict=False))

    elif mode == "overlay":
        result = []
        for a, b in zip(c1[:3], c2[:3], strict=False):
            if a < 128:
                result.append(int(2 * a * b / 255))
            else:
                result.append(int(255 - 2 * (255 - a) * (255 - b) / 255))
        return tuple(result)

    elif mode == "add":
        return tuple(min(255, a + b) for a, b in zip(c1[:3], c2[:3], strict=False))

    elif mode == "subtract":
        return tuple(max(0, a - b) for a, b in zip(c1[:3], c2[:3], strict=False))

    elif mode == "difference":
        return tuple(abs(a - b) for a, b in zip(c1[:3], c2[:3], strict=False))

    elif mode == "average":
        return tuple((a + b) // 2 for a, b in zip(c1[:3], c2[:3], strict=False))

    else:
        raise ValueError(f"不支持的混合模式：{mode}")


def gradient_at(color_dict: "dict[tuple[int, int, int]: float]", t: float):
    """根据位置获取渐变色"""
    t = clamp(t, 0, 1)

    items = sorted(color_dict.items(), key=lambda x: x[1])
    colors, positions = zip(*items, strict=False)

    if not colors:
        return (0, 0, 0)

    if len(colors) == 1:
        return colors[0]

    if t <= positions[0]:
        return colors[0]
    if t >= positions[-1]:
        return colors[-1]

    for i in range(len(positions) - 1):
        if positions[i] <= t <= positions[i + 1]:
            t0, t1 = positions[i], positions[i + 1]
            ratio = (t - t0) / (t1 - t0) if (t1 - t0) > 0 else 0

            c1, c2 = colors[i], colors[i + 1]
            return tuple(
                int(c1[j] + (c2[j] - c1[j]) * ratio)
                for j in range(3)
            )

    return colors[-1]


def gradient_range(color_dict: "dict[tuple[int, int, int]: float]", steps=256):
    """生成渐变色列表"""
    return [gradient_at(color_dict, i / steps) for i in range(steps + 1)]


def grayscale(color: Color) -> int:
    """转灰度"""
    r, g, b = color[:3]
    gray = int(0.299 * r + 0.587 * g + 0.114 * b)
    return gray


def invert(color: Color) -> Color:
    """反色"""
    return tuple(255 - c for c in color[:3])


def adjust_brightness(color: Color, factor: int) -> Color:
    """调整亮度"""
    return tuple(clamp(int(c * factor), 0, 255) for c in color[:3])


def adjust_saturation(color: Color, factor: int) -> Color:
    """调整饱和度"""
    h, s, v = rgb_to_hsv(*color[:3])
    s = clamp(s * factor, 0, 1)
    return hsv_to_rgb(h, s, v)


def adjust_hue(color: Color, degrees: int) -> Color:
    """调整色相"""
    h, s, v = rgb_to_hsv(*color[:3])
    h = (h + degrees) % 360
    return hsv_to_rgb(h, s, v)


def set_alpha(color: Color, alpha: int) -> "tuple[int, int, int, int]":
    """设置 alpha 通道"""
    if len(color) == 3:
        return (*color, int(alpha))
    return (color[0], color[1], color[2], int(alpha))


def premultiply_alpha(color: "tuple[int, int, int, int]") -> "tuple[int, int, int, int]":
    """预乘 alpha"""
    if len(color) < 4:
        return color
    r, g, b, a = color
    a_norm = a / 255.0
    return (int(r * a_norm), int(g * a_norm), int(b * a_norm), a)


def delta_e(c1: Color, c2: Color) -> float:
    """ΔE 色差 (CIE 1976)"""
    # RGB → XYZ (D65)
    def _gamma(c):
        c = c / 255.0
        return ((c + 0.055) / 1.055) ** 2.4 if c > 0.04045 else c / 12.92

    def _rgb_to_xyz(r, g, b):
        r, g, b = _gamma(r), _gamma(g), _gamma(b)
        return (
            r * 0.4124564 + g * 0.3575761 + b * 0.1804375,
            r * 0.2126729 + g * 0.7151522 + b * 0.0721750,
            r * 0.0193339 + g * 0.1191920 + b * 0.9503041,
        )

    # XYZ → Lab (D65 白点)
    def _xyz_to_lab(x, y, z):
        xr, yr, zr = 0.95047, 1.00000, 1.08883

        def f(t):
            return t ** (1/3) if t > 0.008856 else 7.787 * t + 16/116
        x, y, z = f(x / xr), f(y / yr), f(z / zr)
        return (116 * y - 16, 500 * (x - y), 200 * (y - z))

    L1, a1, b1 = _xyz_to_lab(*_rgb_to_xyz(*c1))
    L2, a2, b2 = _xyz_to_lab(*_rgb_to_xyz(*c2))
    return ((L1 - L2) ** 2 + (a1 - a2) ** 2 + (b1 - b2) ** 2) ** 0.5


def distance(c1: Color, c2: Color) -> float:
    """颜色欧几里得距离"""
    return sum((a - b) ** 2 for a, b in zip(c1[:3], c2[:3], strict=False)) ** 0.5


def luminance(color: Color) -> float:
    """亮度"""
    r, g, b = color[:3]
    r, g, b = r / 255.0, g / 255.0, b / 255.0

    if r <= 0.03928:
        r = r / 12.92
    else:
        r = ((r + 0.055) / 1.055) ** 2.4

    if g <= 0.03928:
        g = g / 12.92
    else:
        g = ((g + 0.055) / 1.055) ** 2.4

    if b <= 0.03928:
        b = b / 12.92
    else:
        b = ((b + 0.055) / 1.055) ** 2.4

    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(c1: Color, c2: Color) -> float:
    """对比度比率（WCAG）"""
    l1 = luminance(c1)
    l2 = luminance(c2)

    lighter = max(l1, l2)
    darker = min(l1, l2)

    return (lighter + 0.05) / (darker + 0.05)


def is_dark(color: Color, threshold: float = 0.5) -> bool:
    """判断颜色是否为暗色"""
    return luminance(color) < threshold


def is_light(color: Color, threshold: float = 0.5) -> bool:
    """判断颜色是否为亮色"""
    return luminance(color) > threshold


def mix(c1: Color, c2: Color, amount: float = 0.5) -> Color:
    """混合两种颜色(lerp别名)"""
    return lerp(c1, c2, clamp(amount, 0, 1))


def rgb_to_cymb(r: int, g: int, b: int) -> Color:
    """RGB 转 CYMB（青色、洋红色、黄色、黑色）"""
    r, g, b = r / 255.0, g / 255.0, b / 255.0
    c = 1 - r
    y = 1 - g
    m = 1 - b
    k = min(c, y, m)

    if k == 1:
        return (0, 0, 0, 255)

    c = (c - k) / (1 - k)
    y = (y - k) / (1 - k)
    m = (m - k) / (1 - k)
    c *= 255
    y *= 255
    m *= 255
    k *= 255
    return (c, y, m, k)


def cymb_to_rgb(c, y, m, k):
    """CYMB 转 RGB"""
    c /= 255
    y /= 255
    m /= 255
    k /= 255

    r = 255 * (1 - min(1, c + k))
    g = 255 * (1 - min(1, y + k))
    b = 255 * (1 - min(1, m + k))

    return (int(r), int(g), int(b))


def random_color(rng=None):
    """生成随机颜色"""
    if rng is None:
        from .srandom import Random
        rng = Random()

    return (
        rng.randint(0, 255),
        rng.randint(0, 255),
        rng.randint(0, 255),
    )


WHITE = (255, 255, 255)
BLACK = (20, 20, 30)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (147, 112, 219)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)
GRAY = (128, 128, 128)
BROWN = (139, 69, 19)
PINK = (255, 67, 170)
GOLD = (255, 215, 0)
MAGENTA = (255, 0, 255)
BACKGROUND = (5, 5, 15)
LIGHT_BLUE = (173, 216, 230)
LIGHT_GRAY = (150, 150, 150)
LIGHT_ORANGE = (255, 215, 0)
LIGHT_GREEN = (144, 238, 144)
LIGHT_BROWN = (205, 133, 63)
LIGHT_PINK = (255, 182, 193)
LIGHT_PURPLE = (200, 162, 200)
LIGHT_CYAN = (224, 255, 255)
LIGHT_YELLOW = (255, 255, 224)
LIGHT_CORAL = (240, 128, 128)
DARK_GREEN = (0, 100, 0)
DARK_BLUE = (0, 0, 139)
DARK_RED = (100, 0, 0)
DARK_GOLD = (184, 134, 11)
DARK_PURPLE = (75, 0, 130)
DARK_BROWN = (101, 67, 33)
DARK_CYAN = (0, 139, 139)
DARK_ORANGE = (255, 140, 0)
DARK_GRAY = (64, 64, 64)
DARK_PINK = (231, 84, 128)
AQUA = (0, 255, 255)
LAVENDER = (230, 230, 250)
CORAL = (255, 127, 80)
TEAL = (0, 128, 128)
INDIGO = (75, 0, 130)
VIOLET = (238, 130, 238)
MAROON = (128, 0, 0)
OLIVE = (128, 128, 0)
NAVY = (0, 0, 128)
LIME = (0, 255, 0)
FUCHSIA = (255, 0, 255)
SILVER = (192, 192, 192)
PRIMARY = (97, 168, 255)
SECONDARY = (60, 60, 100)
SUCCESS = (100, 255, 100)
WARNING = (255, 255, 100)
ERROR = (255, 100, 100)
INFO = (173, 216, 230)
TRANSPARENT = (0, 0, 0, 0)
