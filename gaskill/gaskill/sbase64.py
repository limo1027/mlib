# ==================== 字符表 ====================

BASE16_ALPHABET = b"0123456789ABCDEF"
BASE32_ALPHABET = b"ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"
BASE64_ALPHABET = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
BASE64URL_ALPHABET = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
BASE58_ALPHABET = b"123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

# Base256使用中文符号（从4E00开始，共256个连续汉字）
_BASE256_START = 0x4E00
_BASE256_ALPHABET = ''.join(chr(_BASE256_START + i)
                            for i in range(256)).encode('utf-8')


# ==================== Base16 ====================

def b16encode(data: bytes) -> bytes:
    """Base16编码(十六进制)"""
    result = bytearray()
    for byte in data:
        result.append(BASE16_ALPHABET[byte >> 4])      # 高4位
        result.append(BASE16_ALPHABET[byte & 0x0F])    # 低4位
    return bytes(result)


def b16decode(data: bytes) -> bytes:
    """Base16解码"""
    if len(data) % 2 != 0:
        raise ValueError("Base16编码长度必须为偶数")
    # 构建反向映射表
    dec_map = {c: i for i, c in enumerate(BASE16_ALPHABET)}
    result = bytearray()
    for i in range(0, len(data), 2):
        high = dec_map.get(data[i], -1)
        low = dec_map.get(data[i+1], -1)
        if high < 0 or low < 0:
            raise ValueError("包含非法Base16字符")
        result.append((high << 4) | low)
    return bytes(result)


# ==================== Base32 ====================

def b32encode(data: bytes) -> bytes:
    """Base32编码"""
    if not data:
        return b''

    result = bytearray()
    bit_buffer = 0
    bit_count = 0

    for byte in data:
        bit_buffer = (bit_buffer << 8) | byte
        bit_count += 8

        while bit_count >= 5:
            bit_count -= 5
            index = (bit_buffer >> bit_count) & 0x1F  # 取高5位
            result.append(BASE32_ALPHABET[index])

    # 处理剩余位
    if bit_count > 0:
        # 左移补齐到5位
        index = (bit_buffer << (5 - bit_count)) & 0x1F
        result.append(BASE32_ALPHABET[index])
        # 填充等号
        pad_count = (8 - len(result) % 8) % 8
        result.extend(b'=' * pad_count)
    else:
        # 刚好对齐时也可能需要填充
        pad_count = (8 - len(result) % 8) % 8
        result.extend(b'=' * pad_count)

    return bytes(result)


def b32decode(data: bytes) -> bytes:
    """Base32解码"""
    data = data.rstrip(b'=')
    if not data:
        return b''

    dec_map = {c: i for i, c in enumerate(BASE32_ALPHABET)}

    result = bytearray()
    bit_buffer = 0
    bit_count = 0

    for ch in data:
        val = dec_map.get(ch, -1)
        if val < 0:
            raise ValueError("包含非法Base32字符")
        bit_buffer = (bit_buffer << 5) | val
        bit_count += 5

        while bit_count >= 8:
            bit_count -= 8
            result.append((bit_buffer >> bit_count) & 0xFF)

    return bytes(result)


# ==================== Base64 ====================

def b64encode(data: bytes) -> bytes:
    """Base64编码"""
    if not data:
        return b''

    result = bytearray()
    bit_buffer = 0
    bit_count = 0

    for byte in data:
        bit_buffer = (bit_buffer << 8) | byte
        bit_count += 8

        while bit_count >= 6:
            bit_count -= 6
            index = (bit_buffer >> bit_count) & 0x3F
            result.append(BASE64_ALPHABET[index])

    # 处理剩余位
    if bit_count > 0:
        index = (bit_buffer << (6 - bit_count)) & 0x3F
        result.append(BASE64_ALPHABET[index])
        # 填充等号
        pad_count = (4 - len(result) % 4) % 4
        result.extend(b'=' * pad_count)
    else:
        pad_count = (4 - len(result) % 4) % 4
        result.extend(b'=' * pad_count)

    return bytes(result)


def b64decode(data: bytes) -> bytes:
    """Base64解码"""
    data = data.rstrip(b'=')
    if not data:
        return b''

    dec_map = {c: i for i, c in enumerate(BASE64_ALPHABET)}

    result = bytearray()
    bit_buffer = 0
    bit_count = 0

    for ch in data:
        val = dec_map.get(ch, -1)
        if val < 0:
            raise ValueError("包含非法Base64字符")
        bit_buffer = (bit_buffer << 6) | val
        bit_count += 6

        while bit_count >= 8:
            bit_count -= 8
            result.append((bit_buffer >> bit_count) & 0xFF)

    return bytes(result)


# ==================== Base64URL ====================

def b64urlencode(data: bytes) -> bytes:
    """Base64URL编码(URL安全版本,用 - 和 _ 替代 + 和 /)"""
    result = b64encode(data)
    return result.replace(b'+', b'-').replace(b'/', b'_')


def b64urldecode(data: bytes) -> bytes:
    """Base64URL解码"""
    data = data.replace(b'-', b'+').replace(b'_', b'/')
    return b64decode(data)


# ==================== Base58 ====================

def b58encode(data: bytes) -> bytes:
    """Base58编码"""
    if not data:
        return b''

    # 统计前导零的数量（每个前导零字节对应一个'1'）
    leading_zeros = 0
    for byte in data:
        if byte == 0:
            leading_zeros += 1
        else:
            break

    # 将整个bytes转换为大整数
    num = 0
    for byte in data:
        num = (num << 8) | byte

    # 不断除以58取余
    result = bytearray()
    while num > 0:
        num, rem = divmod(num, 58)
        result.append(BASE58_ALPHABET[rem])

    # 反转结果（因为除法的余数是倒序的）
    result.reverse()

    # 补回前导零对应的'1'
    return b'1' * leading_zeros + bytes(result)


def b58decode(data: bytes) -> bytes:
    """Base58解码"""
    if not data:
        return b''

    # 统计前导的'1'数量（每个对应一个零字节）
    leading_ones = 0
    for ch in data:
        if ch == ord('1'):
            leading_ones += 1
        else:
            break

    # 构建反向映射
    dec_map = {c: i for i, c in enumerate(BASE58_ALPHABET)}

    # 将每个字符转换为数值，累加成一个大整数
    num = 0
    for ch in data:
        val = dec_map.get(ch, -1)
        if val < 0:
            raise ValueError("包含非法Base58字符")
        num = num * 58 + val

    # 将大整数转换为bytes
    result = bytearray()
    while num > 0:
        result.append(num & 0xFF)
        num >>= 8

    result.reverse()

    # 补回前导零字节
    return b'\x00' * leading_ones + bytes(result)


# ==================== Base256（中文版） ====================

def b256encode(data: bytes) -> bytes:
    """Base256编码（中文版）"""
    result = bytearray()
    for byte in data:
        result.extend(_BASE256_ALPHABET[byte * 3:(byte + 1) * 3])
    return bytes(result)


def b256decode(data: bytes) -> bytes:
    """Base256解码（中文版）"""
    if len(data) % 3 != 0:
        raise ValueError("Base256编码长度必须为3的倍数")

    # 构建反向映射：UTF-8字节序列 → 索引
    dec_map = {}
    for i in range(256):
        seq = _BASE256_ALPHABET[i * 3:(i + 1) * 3]
        dec_map[seq] = i

    result = bytearray()
    for i in range(0, len(data), 3):
        seq = bytes(data[i:i+3])
        val = dec_map.get(seq)
        if val is None:
            raise ValueError(f"非法Base256字符序列: {seq}")
        result.append(val)
    return bytes(result)


# ==================== 统一接口（类似base64模块风格） ====================

__all__ = [
    'b16encode', 'b16decode',
    'b32encode', 'b32decode',
    'b64encode', 'b64decode',
    'b64urlencode', 'b64urldecode',
    'b58encode', 'b58decode',
    'b256encode', 'b256decode',
]
