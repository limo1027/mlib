from gaskill.gaskill.smath import ceil


def pack_float(num):
    """将浮点数转换为二进制表示"""

    if num == 0:
        if str(num) == "0.0":
            return '0' * 64
        else:
            return '1' + '0' * 63

    if num == float("inf") or num == float("-inf"):
        return '0' + '1'*11 + '0'*52 if num > 0 else '1' + '1'*11 + '0'*52

    if str(num) == 'nan':
        return '0' + '1'*11 + '1' + '0'*51

    sign = '0' if num > 0 else '1'
    num = abs(num)

    int_part = int(num)
    frac_part = num - int_part

    int_bits = []
    if int_part == 0:
        int_bits = ['0']
    else:
        temp = int_part
        while temp > 0:
            int_bits.append(str(temp % 2))
            temp //= 2
        int_bits.reverse()

    frac_bits = []
    temp = frac_part
    count = 0
    while temp > 0 and count < 60:
        temp *= 2
        if temp >= 1:
            frac_bits.append('1')
            temp -= 1
        else:
            frac_bits.append('0')
        count += 1
    binary = int_bits + frac_bits

    first_one = -1
    for i, bit in enumerate(binary):
        if bit == '1':
            first_one = i
            break

    if first_one == -1:  # 全是0
        return '0' * 64

    if first_one < len(int_bits):
        exponent = len(int_bits) - first_one - 1
    else:
        exponent = - (first_one - len(int_bits) + 1)

    biased_exponent = exponent + 1023
    exp_bits = bin(biased_exponent)[2:].zfill(11)

    mantissa_start = first_one + 1
    mantissa_bits = binary[mantissa_start:mantissa_start + 52]

    mantissa_bits = mantissa_bits + ['0'] * (52 - len(mantissa_bits))
    mantissa_bits = ''.join(mantissa_bits[:52])

    result = sign + exp_bits + mantissa_bits

    return result


def unpack_float(byte_data):
    """从 8 字节解析 IEEE 754 双精度浮点数（不用 struct）"""
    # 修复：如果传入的是字符串，先转换为字节
    if isinstance(byte_data, str):
        # 将二进制字符串转换为字节
        if len(byte_data) == 64:
            # 每 8 位转一个字节
            byte_list = []
            for i in range(0, 64, 8):
                byte_list.append(int(byte_data[i:i+8], 2))
            byte_data = bytes(byte_list)
        else:
            raise ValueError("二进制字符串长度必须是64")

    # 1. 转成 64 位二进制字符串
    bits = ''.join(format(b, '08b') for b in byte_data)

    # 2. 解析符号、指数、尾数
    sign = int(bits[0])
    exponent = int(bits[1:12], 2)
    mantissa = int(bits[12:], 2)

    # 3. 特殊值
    if exponent == 2047:
        if mantissa == 0:
            return float('-inf') if sign else float('inf')
        return float('nan')

    # 4. 零
    if exponent == 0 and mantissa == 0:
        return -0.0 if sign else 0.0

    # 5. 非规格化数
    if exponent == 0:
        value = (mantissa / (2**52)) * (2 ** -1022)
        return -value if sign else value

    # 6. 规格化数
    value = (1 + mantissa / (2**52)) * (2 ** (exponent - 1023))
    return -value if sign else value


def pack_int(n, bits=None):
    if bits is None:
        # 自动计算所需位数（包括符号位）
        if n >= 0:
            bits = max(1, n.bit_length() + 1)
        else:
            bits = max(1, (-n).bit_length() + 1)

    if n < 0:
        n = (1 << bits) + n

    return bin(n)[2:].zfill(bits)[-bits:]


def pack_str(n):
    result = bin(int.from_bytes(n.encode(), "big"))[2:]
    return result.rjust(ceil(len(result) / 8) * 8, "0")


def bits_to_bytes(bits):
    """二进制字符串 → bytes"""
    # 补齐到 8 的倍数
    if len(bits) % 8 != 0:
        bits = bits.rjust((len(bits) + 7) // 8 * 8, "0")

    # 每 8 位转一个字节
    result = []
    for i in range(0, len(bits), 8):
        result.append(int(bits[i:i+8], 2))
    return bytes(result)


def bytes_to_bits(data):
    """bytes → 二进制字符串"""
    return ''.join(format(b, '08b') for b in data)


def pack_to_file(obj, filename):
    """打包对象并写入文件"""
    # 1. 打包对象
    packed = pack(obj)  # 返回 b'类型标记 + 二进制字符串 + \x00'

    # 2. 写入文件
    with open(filename, 'wb') as f:
        f.write(packed)


# ============ 辅助函数 ============

def pack_varint(n):
    """变长整数编码（无符号）"""
    if n == 0:
        return b'\x00'
    result = []
    while n > 0:
        byte = n & 0x7F
        n >>= 7
        if n > 0:
            byte |= 0x80
        result.append(byte)
    return bytes(result)


def unpack_varint(data, pos):
    """解包变长整数"""
    result = 0
    shift = 0
    while pos < len(data):
        byte = data[pos]
        pos += 1
        result |= (byte & 0x7F) << shift
        if not (byte & 0x80):
            return result, pos
        shift += 7
    raise ValueError("不完整的变长整数")


# ============ pack ============

def pack(obj):
    """打包任意对象为二进制"""
    if isinstance(obj, str):
        # 字符串：S + 变长长度 + UTF-8 数据
        data = obj.encode('utf-8')
        return b'S' + pack_varint(len(data)) + data

    elif isinstance(obj, int):
        # 整数：I + 变长编码
        if obj >= 0:
            return b'I' + pack_varint(obj)
        else:
            # 负数用补码
            return b'i' + pack_varint(-obj)

    elif isinstance(obj, float):
        # 浮点数：F + 8字节 IEEE 754
        bits = pack_float(obj)  # 您的函数，返回二进制字符串
        return b'F' + bits_to_bytes(bits)

    elif isinstance(obj, bool):
        # 布尔值：B + 1字节 (0 或 1)
        return b'B' + (b'\x01' if obj else b'\x00')

    elif isinstance(obj, (list, tuple)):
        # 列表：L + 每个元素递归 + E
        result = b'L'
        for item in obj:
            result += pack(item)
        return result + b'E'

    elif isinstance(obj, dict):
        # 字典：D + 每个键值对递归 + E
        result = b'D'
        for key, value in obj.items():
            result += pack(key) + pack(value)
        return result + b'E'

    elif obj is None:
        # None：N
        return b'N'

    else:
        raise TypeError(f"不支持的类型: {type(obj)}")


# ============ unpack ============

def unpack(data, pos=0):
    """从二进制解包"""
    if pos >= len(data):
        return None, pos

    type_code = data[pos:pos+1]
    pos += 1

    if type_code == b'S':
        # 字符串
        length, pos = unpack_varint(data, pos)
        value = data[pos:pos+length].decode('utf-8')
        return value, pos + length

    elif type_code == b'I':
        # 无符号整数
        value, pos = unpack_varint(data, pos)
        return value, pos

    elif type_code == b'i':
        # 负整数
        value, pos = unpack_varint(data, pos)
        return -value, pos

    elif type_code == b'F':
        # 浮点数 - 直接传入字节数据
        value = unpack_float(data[pos:pos+8])
        return value, pos + 8

    elif type_code == b'B':
        # 布尔值
        value = data[pos] == 1
        return value, pos + 1

    elif type_code == b'L':
        # 列表
        result = []
        while pos < len(data):
            if data[pos:pos+1] == b'E':
                pos += 1
                break
            item, pos = unpack(data, pos)
            result.append(item)
        return result, pos

    elif type_code == b'D':
        # 字典
        result = {}
        while pos < len(data):
            if data[pos:pos+1] == b'E':
                pos += 1
                break
            key, pos = unpack(data, pos)
            value, pos = unpack(data, pos)
            result[key] = value
        return result, pos

    elif type_code == b'N':
        # None
        return None, pos

    else:
        raise TypeError(f"未知类型码: {type_code}")


def dump(obj, filename):
    """保存对象到文件"""
    with open(filename, 'wb') as f:
        f.write(pack(obj))


def load(filename):
    """从文件加载对象"""
    with open(filename, 'rb') as f:
        data = f.read()
    return unpack(data)[0]
