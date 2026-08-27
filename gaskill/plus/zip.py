# 不用任何import，纯Python实现

class BitWriter:
    """位写入器"""

    def __init__(self):
        self.bits = []

    def write_bit(self, bit):
        self.bits.append(bit)

    def write_bits(self, bits):
        for b in bits:
            self.bits.append(b)

    def to_bytes(self):
        # 补齐到8的倍数
        while len(self.bits) % 8 != 0:
            self.bits.append(0)

        result = []
        for i in range(0, len(self.bits), 8):
            byte = 0
            for j in range(8):
                byte = (byte << 1) | self.bits[i + j]
            result.append(byte)
        return bytes(result)


class BitReader:
    """位读取器"""

    def __init__(self, data):
        self.bits = []
        for byte in data:
            for i in range(7, -1, -1):
                self.bits.append((byte >> i) & 1)
        self.pos = 0
        self.total_bits = len(self.bits)

    def read_bit(self):
        if self.pos >= self.total_bits:
            return None
        bit = self.bits[self.pos]
        self.pos += 1
        return bit

    def read_bits(self, n):
        result = []
        for _ in range(n):
            bit = self.read_bit()
            if bit is None:
                break
            result.append(bit)
        return result


class HuffmanNode:
    """哈夫曼树节点"""

    def __init__(self, freq, char=None, left=None, right=None):
        self.freq = freq
        self.char = char
        self.left = left
        self.right = right


def build_huffman_tree(freq):
    """构建哈夫曼树"""
    nodes = []
    for char, f in freq.items():
        nodes.append(HuffmanNode(f, char))

    while len(nodes) > 1:
        # 找两个最小的
        min1_idx = 0
        for i in range(1, len(nodes)):
            if nodes[i].freq < nodes[min1_idx].freq:
                min1_idx = i

        min2_idx = 0
        if min1_idx == 0:
            min2_idx = 1
        else:
            min2_idx = 0
        for i in range(len(nodes)):
            if i != min1_idx and nodes[i].freq < nodes[min2_idx].freq:
                min2_idx = i

        left = nodes.pop(max(min1_idx, min2_idx))
        right = nodes.pop(min(min1_idx, min2_idx))
        parent = HuffmanNode(left.freq + right.freq, None, left, right)
        nodes.append(parent)

    return nodes[0] if nodes else None


def generate_huffman_codes(node, code="", codes=None):
    """生成哈夫曼编码"""
    if codes is None:
        codes = {}
    if node.char is not None:
        codes[node.char] = code if code else "0"
    else:
        if node.left:
            generate_huffman_codes(node.left, code + "0", codes)
        if node.right:
            generate_huffman_codes(node.right, code + "1", codes)
    return codes


def lz77_compress(data, window_size=32768, max_match=258):
    """LZ77压缩"""
    result = []
    i = 0
    n = len(data)

    while i < n:
        best_len = 0
        best_dist = 0

        start = max(0, i - window_size)

        for j in range(start, i):
            length = 0
            while (i + length < n and
                   j + length < i and
                   data[j + length] == data[i + length] and
                   length < max_match):
                length += 1

            if length > best_len and length >= 3:
                best_len = length
                best_dist = i - j

        if best_len >= 3:
            result.append(("R", best_dist, best_len))
            i += best_len
        else:
            result.append(("L", data[i]))
            i += 1

    return result


def huffman_compress(symbols):
    """哈夫曼压缩"""
    freq = {}
    for sym in symbols:
        freq[sym] = freq.get(sym, 0) + 1

    tree = build_huffman_tree(freq)
    codes = generate_huffman_codes(tree)

    writer = BitWriter()
    for sym in symbols:
        code = codes[sym]
        for bit in code:
            writer.write_bit(1 if bit == "1" else 0)

    return writer.to_bytes(), codes, len(symbols)


def huffman_decompress(data, codes, expected_count):
    """哈夫曼解压"""
    reader = BitReader(data)

    reverse_codes = {v: k for k, v in codes.items()}

    max_len = 0
    for code in codes.values():
        if len(code) > max_len:
            max_len = len(code)

    result = []
    buffer = []

    while len(result) < expected_count:
        bit = reader.read_bit()
        if bit is None:
            break
        buffer.append(bit)

        code_str = "".join(str(b) for b in buffer)
        if code_str in reverse_codes:
            result.append(reverse_codes[code_str])
            buffer = []

        if len(buffer) > max_len:
            buffer = []

    return result


def compress(data):
    tokens = lz77_compress(data)

    symbols = []
    for token in tokens:
        if token[0] == "R":
            # 把距离和长度打包成一个整数
            symbols.append(("R", token[1], token[2]))
        else:
            # 直接使用整数，不用包装成元组
            symbols.append(token[1])  # 直接是整数

    compressed, codes, count = huffman_compress(symbols)

    return compressed, codes, count


def decompress(data, codes, count):
    symbols = huffman_decompress(data, codes, count)

    result = []
    i = 0
    while i < len(symbols):
        sym = symbols[i]
        if isinstance(sym, tuple) and sym[0] == "R":
            _, dist, length = sym
            start = len(result) - dist
            for j in range(length):
                if start + j < len(result):
                    result.append(result[start + j])
            i += 1
        else:
            # sym 现在应该是整数了
            if isinstance(sym, int):
                result.append(sym)
            else:
                # 降级方案
                result.append(ord(sym) if isinstance(sym, str) else sym)
            i += 1

    return bytes(result)
