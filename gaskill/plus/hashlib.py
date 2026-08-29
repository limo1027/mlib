
H0 = 0x6a09e667
H1 = 0xbb67ae85
H2 = 0x3c6ef372
H3 = 0xa54ff53a
H4 = 0x510e527f
H5 = 0x9b05688c
H6 = 0x1f83d9ab
H7 = 0x5be0cd19

K = [
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2,
]


def rotr(x, n):
    """循环右移 n 位（32-bit）"""
    return (x >> n) | ((x & ((1 << n) - 1)) << (32 - n))


def shr(x, n):
    """逻辑右移 n 位（高位补 0）"""
    return x >> n


def xor3(a, b, c):
    """三个数的异或"""
    return a ^ b ^ c


def add_mod32(a, b):
    """32-bit 加法（自动截断）"""
    return (a + b) & 0xffffffff


def ch(x, y, z):
    """Choose: 根据 x 的位选择 y 或 z"""
    return (x & y) ^ ((~x) & z)


def maj(x, y, z):
    """Majority: 按位多数投票"""
    return (x & y) ^ (x & z) ^ (y & z)


def sigma0(x):
    """Σ0：用于压缩函数"""
    return xor3(rotr(x, 2), rotr(x, 13), rotr(x, 22))


def sigma1(x):
    """Σ1：用于压缩函数"""
    return xor3(rotr(x, 6), rotr(x, 11), rotr(x, 25))


def gamma0(x):
    """σ0：用于消息调度"""
    return xor3(rotr(x, 7), rotr(x, 18), shr(x, 3))


def gamma1(x):
    """σ1：用于消息调度"""
    return xor3(rotr(x, 17), rotr(x, 19), shr(x, 10))


def pad_message(msg_bytes):
    """
    将字节消息填充为 512-bit 整数倍
    返回：填充后的字节数组（每个元素 0-255）
    """
    msg_len = len(msg_bytes)
    bit_len = msg_len * 8

    padded = list(msg_bytes)

    padded.append(0x80)

    while len(padded) % 64 != 56:
        padded.append(0x00)

    for i in range(7, -1, -1):
        padded.append((bit_len >> (8 * i)) & 0xff)

    return padded


def bytes_to_words(block):
    """block: 64 字节的 list，返回 16 个 32-bit 整数"""
    words = []
    for i in range(0, 64, 4):
        w = (block[i] << 24) | (block[i+1] <<
                                16) | (block[i+2] << 8) | block[i+3]
        words.append(w)
    return words


def compress_block(block_bytes, h_vals):
    w = bytes_to_words(block_bytes)

    for t in range(16, 64):
        w.append(
            add_mod32(
                add_mod32(gamma1(w[t-2]), w[t-7]),
                add_mod32(gamma0(w[t-15]), w[t-16])
            )
        )

    a, b, c, d = h_vals[0], h_vals[1], h_vals[2], h_vals[3]
    e, f, g, h = h_vals[4], h_vals[5], h_vals[6], h_vals[7]

    for t in range(64):
        t1 = add_mod32(
            add_mod32(
                add_mod32(
                    add_mod32(h, sigma1(e)),
                    ch(e, f, g)
                ),
                K[t]
            ),
            w[t]
        )
        t2 = add_mod32(sigma0(a), maj(a, b, c))

        h = g
        g = f
        f = e
        e = add_mod32(d, t1)
        d = c
        c = b
        b = a
        a = add_mod32(t1, t2)

    return [
        add_mod32(h_vals[0], a),
        add_mod32(h_vals[1], b),
        add_mod32(h_vals[2], c),
        add_mod32(h_vals[3], d),
        add_mod32(h_vals[4], e),
        add_mod32(h_vals[5], f),
        add_mod32(h_vals[6], g),
        add_mod32(h_vals[7], h),
    ]


def sha256(message):
    # 统一转为字节
    if isinstance(message, str):
        msg_bytes = [ord(c) for c in message]
    else:
        msg_bytes = list(message)

    # 填充
    padded = pad_message(msg_bytes)

    # 初始哈希值（拷贝一份，避免修改全局）
    h_vals = [H0, H1, H2, H3, H4, H5, H6, H7]

    # 逐块处理（每 64 字节一块）
    for i in range(0, len(padded), 64):
        block = padded[i:i+64]
        h_vals = compress_block(block, h_vals)

    # 拼接最终摘要
    result = ''
    for val in h_vals:
        # 转 8 位十六进制（补零）
        hex_str = hex(val)[2:]  # 去掉 '0x'
        if len(hex_str) < 8:
            hex_str = '0' * (8 - len(hex_str)) + hex_str
        result += hex_str

    return result

def DJB2(s, capacity):
    h = 5381
    for byte in s.encode('utf-8'):
        h = ((h * 33) + byte) & 0x7fffffff
    return h % capacity
