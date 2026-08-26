from .srandom import Random
from .sformat import encode, decode
from .sfrac import Frac
from .smath import gcd, is_prime_fast, egcd as _modinv
from .type import Iterable


def rsa_generate_keys(bits: int = 512):
    """生成 RSA 密钥对"""
    rng = Random()

    p = _generate_prime(bits // 2, rng)
    q = _generate_prime(bits // 2, rng)
    while q == p:
        q = _generate_prime(bits // 2, rng)

    n = p * q
    phi = (p - 1) * (q - 1)

    e = 65537
    while gcd(e, phi) != 1:
        e = rng.randint(3, phi - 1)

    d = _modinv(e, phi)

    return {
        'e': e, 'd': d, 'n': n,
        'p': p, 'q': q, 'phi': phi
    }


def rsa_encrypt(message: str, public_key: "dict[str, int]") -> int:
    """RSA 加密"""
    m = int(encode(message))
    n = public_key['n']
    e = public_key['e']
    return pow(m, e, n)


def rsa_decrypt(cipher: int, private_key: "dict[str, int]") -> str:
    """RSA 解密"""
    n = private_key['n']
    d = private_key['d']
    m = pow(cipher, d, n)
    return decode(str(m))


def _generate_prime(bits: int, rng: Random) -> int:
    """生成指定位数的素数"""
    while True:
        candidate = rng.randint(2**(bits-1), 2**bits - 1)
        if candidate % 2 == 0:
            candidate += 1

        if is_prime_fast(candidate):
            return candidate


def simple_encrypt(value: str, key: str = None, second: "list[int] | None" = None) -> "tuple[int, str]":
    """加密"""
    random_key = False
    if key is None:
        key = Random().uuid()[:8]
        random_key = True
    IV = Random().uuid().replace("-", "")
    real_key = int(encode(key+IV))
    moduli = second
    if (not hasattr(moduli, "__iter__")) or (not all(isinstance(i, int) for i in moduli)) or len(moduli) == 0:
        moduli = Random().hash(str(moduli))
    value = int(encode(value)) * real_key * 0x9e3779b97f4a7c15
    hash_list = moduli
    keys = []
    hash_value = real_key

    for i in range(4):
        hash_value = Random().hash(hash_value, hash_list)
        hash_list = [i for i in hash_value if not i == 0]
        hash_value = int(''.join(str(h) for h in hash_value))
        keys.append(real_key ^ (hash_value << 1))

    for i in range(10000):
        keys[i % 4] = (keys[(i-1) % 4] ^ (keys[(i-2) %
                       4] + keys[(i-3) % 4])) % 2**256

    if random_key:
        return (keys[0] * (value+1)) ^ keys[1] ^ keys[2] ^ keys[3], key, IV
    else:
        return (keys[0] * (value+1)) ^ keys[1] ^ keys[2] ^ keys[3], IV


def simple_decrypt(cipher: int, key: str, IV: str, second: "list[int] | None" = None):
    """解密"""
    moduli = second
    if (not hasattr(moduli, "__iter__")) or (not all(isinstance(i, int) for i in moduli)) or len(moduli) == 0:
        moduli = Random().hash(str(moduli))
    hash_list = moduli

    real_key = int(encode(key+IV))
    keys = []
    hash_value = real_key

    for i in range(4):
        hash_value = Random().hash(hash_value, hash_list)
        hash_list = [i for i in hash_value if not i == 0]
        hash_value = int(''.join(str(h) for h in hash_value))
        keys.append(real_key ^ (hash_value << 1))

    for i in range(10000):
        keys[i % 4] = (keys[(i-1) % 4] ^ (keys[(i-2) %
                       4] + keys[(i-3) % 4])) % 2**256

    temp = cipher ^ keys[1] ^ keys[2] ^ keys[3]
    if temp % keys[0] != 0:
        raise ValueError("密文被篡改或密钥错误")

    value_int = temp // keys[0] - 1
    value_int //= real_key
    value_int //= 0x9e3779b97f4a7c15

    return decode(str(value_int))


def share_secret(plaintext: str, keys: "list[object]", threshold: int):
    """秘密共享 - 加密"""

    encoded = encode(plaintext)

    coeffs = []
    group_size = max(1, len(encoded) // threshold + 1)
    for i in range(0, len(encoded), group_size):
        group = encoded[i:i+group_size]
        coeffs.append(int("1"+group) if group else 71114112)

    while len(coeffs) < threshold:
        coeffs.append(71114112)
    coeffs = coeffs[:threshold]

    shares = {}
    rng = Random()

    for key in keys:
        x = int(''.join(str(h) for h in rng.hash(key)))
        y = 0
        for i, coeff in enumerate(coeffs):
            y += coeff * (x ** i)
        shares[key] = y

    return shares


def recover_secret(shares_dict: "dict[object, int]", threshold):
    """秘密共享 - 解密"""

    if len(shares_dict) < threshold:
        raise ValueError(f"至少需要 {threshold} 个密钥")

    points = []
    rng = Random()
    for key, y in list(shares_dict.items())[:threshold]:
        x = int(''.join(str(h) for h in rng.hash(key)))
        points.append((x, y))

    A = []
    for x, y in points:
        row = [x**i for i in range(threshold)]
        A.append(row)

    coeffs = gaussian_elimination(A, [y for x, y in points])

    while coeffs and coeffs[-1] == 71114112:
        coeffs.pop()

    encoded = ''.join(str(c)[1:] for c in coeffs)
    return decode(encoded)


def gaussian_elimination(A, b):
    """解整数线性方程组（模大素数或直接用分数）"""
    n = len(A)
    A = [[Frac(x) for x in row] for row in A]
    b = [Frac(x) for x in b]
    for i in range(n):
        A[i].append(b[i])

    for i in range(n):
        max_row = i
        for j in range(i+1, n):
            if abs(A[j][i]) > abs(A[max_row][i]):
                max_row = j
        A[i], A[max_row] = A[max_row], A[i]

        pivot = A[i][i]
        for j in range(i, n+1):
            A[i][j] /= pivot

        for j in range(n):
            if j != i:
                factor = A[j][i]
                for k in range(i, n+1):
                    A[j][k] -= factor * A[i][k]

    result = []
    for i in range(n):
        val = A[i][n]
        if val.d != 1:
            raise ValueError("线性方程组解不是整数，秘密共享恢复失败（可能是模数或阈值问题）")
        result.append(abs(val.n))

    return result
