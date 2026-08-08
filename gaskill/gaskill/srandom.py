from ._roll import parse_dice, roll_dice
from .smath import ln


class Random:
    """简单随机数生成器"""

    def __init__(self, seed=None):
        """初始化随机数生成器"""
        if seed is None:
            if not hasattr(Random, '_seed_counter'):
                Random._seed_counter = 0
            else:
                Random._seed_counter = Random._seed_counter + 1
            seed = id(object()) ^ id([]) ^ id(
                {}) ^ id(()) ^ Random._seed_counter

        self.a, self.b, self.c, self.d, self.e, self.f, self.g, self.h, self.i = \
            self.hash(seed)
        self.i = self.i / 1000
        for _ in range(20):
            self.next()

    def hash_digit(self, n):
        """数字哈希：数根 x 原数 的后三位"""
        m = n
        while n >= 10:
            n = sum(int(d) for d in str(n))
        return (n * m) % 1000

    def hash(self, seed):
        """自定义哈希函数"""
        moduli = [5, 7, 11, 13, 89, 97, 997, 991, 9971]

        s = str(seed) + type(seed).__name__
        parts = [str(ord(c) * place) for place, c in enumerate(s, start=1)]
        big_str = ''.join(parts)

        result = []
        for m in moduli:
            k = len(str(m))
            remainders = []
            for i in range(0, len(big_str), k):
                group = big_str[i:i+k]
                group_num = int(group)
                r = group_num % m ^ 0x3FF9E3779B97F4A8
                remainders.append(r)
            total = sum(remainders)
            digit = self.hash_digit(total)
            result.append(digit)

        return tuple(int(d) for d in result)

    def seed(self, seed):
        """重新设置种子"""
        self.a, self.b, self.c, self.d, self.e, self.f, self.g, self.h, self.i = self.hash(
            seed)
        self.i = self.i / 1000
        for _ in range(20):
            self.next()

    def next(self, a=0, b=9):
        """生成下一个随机数"""
        self.a ^= self.a >> 3
        self.a = (self.a + self.h * round(self.i * 10**5)) % 10**16
        self.b ^= self.b >> 1
        self.b = (self.b + self.a) % 10**16
        self.c ^= self.c >> 4
        self.c = (self.c + self.b) % 10**16
        self.d ^= self.d >> 1
        self.d = (self.d + self.c) % 10**16
        self.e ^= self.e >> 5
        self.e = (self.e + self.d) % 10**16
        self.f ^= self.f >> 9
        self.f = (self.f + self.e) % 10**16
        self.g ^= self.g >> 2
        self.g = (self.g + self.f) % 10**16
        self.h ^= self.h >> 6
        self.h = (self.h + self.g) % 10**16
        self.i = 3.75 * self.i * (1 - self.i)
        return a + self.h % (b - a + 1)

    def roll(self, expr):
        """掷骰子表达式"""
        parsed = parse_dice(expr)
        total = 0

        for part in parsed['parts']:
            if part['type'] == 'dice':
                total += roll_dice(part, self.randint)
            else:
                total += part['value']

        return total

    def randint(self, a, b):
        """生成 a-b 之间的随机整数"""
        if a > b:
            a, b = b, a
        range_len = b - a + 1

        if range_len <= 10**16:
            return a + self.next(0, range_len - 1)

        result = 0
        multiplier = 1
        while range_len > 0:
            result += self.next(0, 10**16 - 1) * multiplier
            multiplier *= 10**16
            range_len //= 10**16
        return a + result % (b - a + 1)

    def random(self):
        """生成 0-1 之间的随机浮点数"""
        self.next()
        return round(self.h / 10 ** 16, 15)

    def random_float(self, start, end):
        """生成指定范围内的随机浮点数"""
        return self.random() * (end - start) + start

    def choice(self, candidates):
        """从列表中随机选择一个元素"""
        if not candidates:
            raise ValueError("候选列表不能为空")
        return candidates[int(self.random() * len(candidates))]

    def shuffle(self, items):
        """打乱列表（原地修改）"""
        for i in range(len(items) - 1, 0, -1):
            j = self.randint(0, i)
            items[i], items[j] = items[j], items[i]
        return items

    def shuffle_copy(self, items):
        """返回打乱后的新列表（不修改原列表）"""
        items_copy = items.copy()
        return self.shuffle(items_copy)

    def sample(self, items, k):
        """从列表中随机抽取 k 个不重复的元素"""
        if k > len(items):
            raise ValueError("k 不能大于列表长度")

        items_copy = items.copy()
        self.shuffle(items_copy)

        return items_copy[:k]

    def choices(self, arr, weight=None):
        """加权随机选择"""
        if weight is None:
            return self.choice(arr)

        if len(arr) != len(weight):
            raise ValueError("arr 和 weight 长度不一致")

        _sum = sum(weight)
        weight = [i / _sum for i in weight]

        su = 0
        num = self.random()
        for i, w in enumerate(weight):
            su += w
            if num < su:
                return arr[i]

        return arr[-1]

    def gauss(self, mu=0.0, sigma=1.0):
        """高斯分布（正态分布）随机数"""
        while True:
            u1 = self.random() * 2 - 1
            u2 = self.random() * 2 - 1
            r2 = u1 * u1 + u2 * u2
            if 0 < r2 < 1:
                break

        log_r2 = ln(r2)
        z = u1 * (-2 * log_r2) ** 0.5 / r2 ** 0.5
        return mu + sigma * z

    def random_from_func(self, func, x_min, x_max, step=0.01, y_max=None):
        """按函数分布采样"""
        if y_max is None:
            y_max = max(func(x_min + i * step)
                        for i in range(int((x_max - x_min) / step) + 1))
            y_min = min(func(x_min + i * step)
                        for i in range(int((x_max - x_min) / step) + 1))
        else:
            y_min = min(func(x_min + i * step)
                        for i in range(int((x_max - x_min) / step) + 1))

        while True:
            y = self.random() * (y_max - y_min) + y_min

            candidates = []
            x = x_min
            while x <= x_max:
                if func(x) >= y:
                    candidates.append(x)
                x += step

            if candidates:
                return round(candidates[int(self.random() * len(candidates))], 10)

    def uuid(self):
        """生成UUID4格式的随机uuid"""
        strings = "abcdef1234567890"
        length = len(strings) - 1

        parts = [
            ''.join(strings[self.randint(0, length)] for _ in range(8)),
            ''.join(strings[self.randint(0, length)] for _ in range(4)),
            '4' + ''.join(strings[self.randint(0, length)] for _ in range(3)),
            self.choice(('8', '9', 'a', 'b')) +
            ''.join(strings[self.randint(0, length)] for _ in range(3)),
            ''.join(strings[self.randint(0, length)] for _ in range(12))
        ]

        return '-'.join(parts)

    def uniform(self, a, b):
        """均匀分布随机浮点数"""
        return self.random_float(a, b)

    def random_ascii(self, length=16, charset='ascii'):
        """生成随机 ASCII 字符串"""
        charsets = {
            'ascii': "".join(chr(i) for i in range(33, 127)),
            'alnum': "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",
            'alpha': "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
            'digit': "0123456789",
            'hex': "0123456789abcdef",
            'base64': "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/",
            'all': "".join(chr(i) for i in range(256))
        }
        chars = charsets.get(charset, charsets['ascii'])
        return ''.join(self.choice(chars) for _ in range(length))


def random(rng=None):
    """生成 0-1 随机数"""
    if rng is None:
        rng = Random()
    return rng.random()


def randint(a, b, rng=None):
    """生成随机整数"""
    if rng is None:
        rng = Random()
    return rng.randint(a, b)


def choice(seq, rng=None):
    """随机选择"""
    if rng is None:
        rng = Random()
    return rng.choice(seq)


def shuffle(seq, rng=None):
    """打乱列表"""
    if rng is None:
        rng = Random()
    return rng.shuffle(seq)


def sample(seq, k, rng=None):
    """随机抽样"""
    if rng is None:
        rng = Random()
    return rng.sample(seq, k)


def random_ascii(length=16, charset='ascii', rng=None):
    if rng is None:
        rng = Random()
    return rng.random_ascii(length, charset)
