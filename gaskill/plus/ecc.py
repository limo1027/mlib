"""
ECDSA 签名 - 用户自定义临时私钥 k
用户提供：私钥、消息、临时私钥 k
"""

from gaskill import egcd as mod_inv
from gaskill import sha256


class Point:
    def __init__(self, x, y, a, b, p):
        self.x = x
        self.y = y
        self.a = a
        self.b = b
        self.p = p

    def __repr__(self):
        if self.is_infinity():
            return "O"
        if self.p > 2**100:
            return f"({hex(self.x)}, {hex(self.y)})"
        return f"({self.x}, {self.y})"

    def is_infinity(self):
        return self.x is None or self.y is None

    def is_on_curve(self):
        if self.is_infinity():
            return True
        left = (self.y * self.y) % self.p
        right = (self.x * self.x * self.x + self.a * self.x + self.b) % self.p
        return left == right

    def __add__(self, other):
        if self.is_infinity():
            return other
        if other.is_infinity():
            return self
        if self.x == other.x and (self.y + other.y) % self.p == 0:
            return Point(None, None, self.a, self.b, self.p)
        if self.x != other.x:
            lam = (other.y - self.y) * \
                mod_inv(other.x - self.x, self.p) % self.p
        else:
            lam = (3 * self.x * self.x + self.a) * \
                mod_inv(2 * self.y, self.p) % self.p
        x3 = (lam * lam - self.x - other.x) % self.p
        y3 = (lam * (self.x - x3) - self.y) % self.p
        return Point(x3, y3, self.a, self.b, self.p)

    def __mul__(self, k):
        result = Point(None, None, self.a, self.b, self.p)
        base = self
        while k > 0:
            if k & 1:
                result = result + base
            base = base + base
            k >>= 1
        return result


p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
a = 0
b = 7
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

G = Point(
    0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
    0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8,
    a, b, p,
)


def sha256_int(message):
    """计算消息的 SHA256 哈希，返回整数"""
    if isinstance(message, str):
        message = message.encode("utf-8")
    return int(sha256(message), 16)


def is_valid_private_key(k):
    """检查私钥是否合法：1 <= k < n"""
    return isinstance(k, int) and 1 <= k < n


def is_valid_k(k):
    """检查临时私钥是否合法：1 <= k < n"""
    return isinstance(k, int) and 1 <= k < n


# ============================================================
# 核心签名函数
# ============================================================
def ecdsa_sign_with_k(private_key: int, message: str, k: int) -> "tuple[int, int]":
    """
    ECDSA 签名。

    Args:
        private_key: 用户私钥 (1 ~ n-1)
        message:     待签名消息
        k:           临时私钥 (1 ~ n-1)

    Returns:
        (r, s): 签名对

    Raises:
        ValueError: 私钥或临时私钥无效，或 r/s 为零
    """
    if not is_valid_private_key(private_key):
        raise ValueError(f"私钥必须在 1 到 n-1 之间，n={n}")
    if not is_valid_k(k):
        raise ValueError(f"临时私钥 k 必须在 1 到 n-1 之间，n={n}")

    z = sha256_int(message) % n

    R = G * k
    r = R.x % n
    if r == 0:
        raise ValueError("r = 0，请换一个 k 值")

    k_inv = mod_inv(k, n)
    s = (z + r * private_key) * k_inv % n
    if s == 0:
        raise ValueError("s = 0，请换一个 k 值")

    return (r, s)


def ecdsa_verify(public_key: Point, message: str, signature: "tuple[int, int]") -> bool:
    """
    ECDSA 验签。

    Args:
        public_key: 公钥 (Point 对象)
        message:    消息
        signature:  (r, s)

    Returns:
        True 有效，False 无效
    """
    r, s = signature
    if not (1 <= r < n and 1 <= s < n):
        return False

    z = sha256_int(message) % n

    s_inv = mod_inv(s, n)
    u1 = z * s_inv % n
    u2 = r * s_inv % n

    P = G * u1 + public_key * u2
    return P.x % n == r
