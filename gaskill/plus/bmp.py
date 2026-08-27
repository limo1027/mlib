# 纯 Python BMP 读写器


class BMPError(Exception):
    """BMP 操作异常"""
    pass


# ============ 字节转换工具 ============

def int16_to_bytes(n: int) -> bytes:
    """16位整数 → 小端字节 (2字节)"""
    return bytes([n & 0xFF, (n >> 8) & 0xFF])


def int32_to_bytes(n: int) -> bytes:
    """32位整数 → 小端字节 (4字节)"""
    return bytes([
        n & 0xFF,
        (n >> 8) & 0xFF,
        (n >> 16) & 0xFF,
        (n >> 24) & 0xFF,
    ])


def bytes_to_uint16(data: bytes, offset: int) -> int:
    """小端字节 → 无符号16位整数"""
    if offset + 1 >= len(data):
        return 0
    return data[offset] | (data[offset + 1] << 8)


def bytes_to_int16(data: bytes, offset: int) -> int:
    """小端字节 → 有符号16位整数"""
    val = bytes_to_uint16(data, offset)
    if val & 0x8000:
        val -= 0x10000
    return val


def bytes_to_uint32(data: bytes, offset: int) -> int:
    """小端字节 → 无符号32位整数"""
    if offset + 3 >= len(data):
        return 0
    return (data[offset] |
            (data[offset + 1] << 8) |
            (data[offset + 2] << 16) |
            (data[offset + 3] << 24))


def bytes_to_int32(data: bytes, offset: int) -> int:
    """小端字节 → 有符号32位整数"""
    val = bytes_to_uint32(data, offset)
    if val & 0x80000000:
        val -= 0x100000000
    return val


# ============ BMP 常量 ============

BI_RGB = 0
BI_RLE8 = 1
BI_RLE4 = 2
BI_BITFIELDS = 3


# ============ BMP 头结构 ============

class BMPHeader:
    """BMP 文件头 + 信息头"""

    def __init__(self):
        # 文件头 (14字节)
        self.bfType = 0              # 2字节: 'BM'
        self.bfSize = 0              # 4字节: 文件大小
        self.bfReserved1 = 0         # 2字节: 保留
        self.bfReserved2 = 0         # 2字节: 保留
        self.bfOffBits = 0           # 4字节: 像素数据偏移

        # 信息头 (通常40字节)
        self.biSize = 40             # 4字节: 信息头大小
        self.biWidth = 0             # 4字节: 宽度
        self.biHeight = 0            # 4字节: 高度 (正=从下到上, 负=从上到下)
        self.biPlanes = 1            # 2字节: 颜色平面数
        self.biBitCount = 24         # 2字节: 每像素位数
        self.biCompression = 0       # 4字节: 压缩方式
        self.biSizeImage = 0         # 4字节: 图像数据大小
        self.biXPelsPerMeter = 0     # 4字节: 水平分辨率
        self.biYPelsPerMeter = 0     # 4字节: 垂直分辨率
        self.biClrUsed = 0           # 4字节: 使用的颜色数
        self.biClrImportant = 0      # 4字节: 重要颜色数


class BMPImage:
    """BMP 图像"""

    def __init__(self, width: int = 0, height: int = 0):
        self.width = width
        self.height = height
        # [row][col] = (R, G, B, A) 或 (R, G, B)
        self.pixels: list[list[tuple[int, int, int | int, int, int, int]]] = []
        self.header = BMPHeader()
        self.palette: list[tuple[int, int, int]] = []  # 调色板 [(R, G, B), ...]
        self.bit_count = 24
        self.has_alpha = False

    def set_pixel(self, x: int, y: int, color: "tuple[int, int, int] | tuple[int, int, int, int]"):
        """设置像素颜色 (R, G, B) 或 (R, G, B, A)"""
        if not (0 <= x < self.width and 0 <= y < self.height):
            raise BMPError(f"像素坐标 ({x}, {y}) 超出范围 {self.width}x{self.height}")
        self.pixels[y][x] = tuple(color)

    def get_pixel(self, x: int, y: int) -> tuple:
        """获取像素颜色"""
        if not (0 <= x < self.width and 0 <= y < self.height):
            raise BMPError(f"像素坐标 ({x}, {y}) 超出范围 {self.width}x{self.height}")
        return self.pixels[y][x]

    # ============ 加载 ============

    @classmethod
    def load(cls, filename: str):
        """从文件加载 BMP"""
        with open(filename, "rb") as f:
            data = f.read()
        return cls.load_from_bytes(data)

    @classmethod
    def load_from_bytes(cls, data: bytes):
        """从字节数据加载 BMP"""
        if len(data) < 14:
            raise BMPError("文件太小，不是有效的BMP")

        # 检查签名
        if data[0:2] != b"BM":
            raise BMPError(f"不是BMP文件 (签名: {data[0:2].decode('ascii')})")

        # 解析文件头
        header = BMPHeader()
        header.bfType = data[0] | (data[1] << 8)
        header.bfSize = bytes_to_uint32(data, 2)
        header.bfReserved1 = bytes_to_uint16(data, 6)
        header.bfReserved2 = bytes_to_uint16(data, 8)
        header.bfOffBits = bytes_to_uint32(data, 10)

        # 解析信息头
        header.biSize = bytes_to_uint32(data, 14)

        # 根据信息头大小决定如何解析
        if header.biSize == 40:  # BITMAPINFOHEADER
            header.biWidth = bytes_to_uint32(data, 18)
            header.biHeight = bytes_to_int32(data, 22)
            header.biPlanes = bytes_to_uint16(data, 26)
            header.biBitCount = bytes_to_uint16(data, 28)
            header.biCompression = bytes_to_uint32(data, 30)
            header.biSizeImage = bytes_to_uint32(data, 34)
            header.biXPelsPerMeter = bytes_to_uint32(data, 38)
            header.biYPelsPerMeter = bytes_to_uint32(data, 42)
            header.biClrUsed = bytes_to_uint32(data, 46)
            header.biClrImportant = bytes_to_uint32(data, 50)
        else:
            raise BMPError(f"不支持的信息头大小: {header.biSize}")

        # 验证关键字段
        if header.biBitCount not in (1, 4, 8, 16, 24, 32):
            raise BMPError(f"不支持的位深度: {header.biBitCount}位")

        # 使用全局常量
        if header.biCompression not in (BI_RGB, BI_RLE8, BI_RLE4, BI_BITFIELDS):
            raise BMPError(f"不支持的压缩方式: {header.biCompression}")

        # 创建图像对象
        width = header.biWidth
        height = abs(header.biHeight)
        top_down = header.biHeight < 0

        img = cls(width, height)
        img.header = header
        img.bit_count = header.biBitCount

        # 读取调色板 (如果有)
        palette_size = 0
        if header.biBitCount <= 8:
            if header.biClrUsed > 0:
                palette_size = header.biClrUsed
            else:
                palette_size = 1 << header.biBitCount
            palette_size = min(palette_size, 256)

            palette_offset = 14 + header.biSize
            img.palette = []
            for i in range(palette_size):
                b = data[palette_offset + i*4]
                g = data[palette_offset + i*4 + 1]
                r = data[palette_offset + i*4 + 2]
                img.palette.append((r, g, b))

        # 计算行字节数
        if header.biBitCount <= 8:
            bits_per_pixel = header.biBitCount
        else:
            bits_per_pixel = header.biBitCount

        # 计算每行字节数 (4字节对齐)
        row_bytes = ((width * bits_per_pixel + 31) // 32) * 4

        # 如果有压缩，使用 biSizeImage
        if header.biCompression != BI_RGB and header.biSizeImage > 0:
            # 对于压缩图像，使用指定的大小
            pixel_data = data[header.bfOffBits:header.bfOffBits +
                              header.biSizeImage]
        else:
            pixel_data = data[header.bfOffBits:]

        # 解析像素
        img.pixels = []

        if header.biBitCount == 24:
            img._parse_24bit(pixel_data, width, height, row_bytes, top_down)
        elif header.biBitCount == 32:
            img._parse_32bit(pixel_data, width, height, row_bytes, top_down)
        elif header.biBitCount == 8:
            img._parse_8bit(pixel_data, width, height, row_bytes, top_down)
        elif header.biBitCount == 4:
            img._parse_4bit(pixel_data, width, height, row_bytes, top_down)
        elif header.biBitCount == 1:
            img._parse_1bit(pixel_data, width, height, row_bytes, top_down)
        elif header.biBitCount == 16:
            img._parse_16bit(pixel_data, width, height, row_bytes, top_down)
        else:
            raise BMPError(f"不支持的位深度: {header.biBitCount}")

        return img

    def _parse_24bit(self, data: bytes, width: int, height: int, row_bytes: int, top_down: bool):
        """解析 24 位像素"""
        for y in range(height):
            row = []
            src_y = y if top_down else (height - 1 - y)
            offset = src_y * row_bytes

            for x in range(width):
                b = data[offset + x*3]
                g = data[offset + x*3 + 1]
                r = data[offset + x*3 + 2]
                row.append((r, g, b))
            self.pixels.append(row)

    def _parse_32bit(self, data: bytes, width: int, height: int, row_bytes: int, top_down: bool):
        """解析 32 位像素 (带 Alpha)"""
        self.has_alpha = True
        for y in range(height):
            row = []
            src_y = y if top_down else (height - 1 - y)
            offset = src_y * row_bytes

            for x in range(width):
                b = data[offset + x*4]
                g = data[offset + x*4 + 1]
                r = data[offset + x*4 + 2]
                a = data[offset + x*4 + 3]
                row.append((r, g, b, a))
            self.pixels.append(row)

    def _parse_8bit(self, data: bytes, width: int, height: int, row_bytes: int, top_down: bool):
        """解析 8 位索引像素"""
        palette = self.palette
        for y in range(height):
            row = []
            src_y = y if top_down else (height - 1 - y)
            offset = src_y * row_bytes

            for x in range(width):
                idx = data[offset + x]
                if idx < len(palette):
                    row.append(palette[idx])
                else:
                    row.append((0, 0, 0))
            self.pixels.append(row)

    def _parse_4bit(self, data: bytes, width: int, height: int, row_bytes: int, top_down: bool):
        """解析 4 位索引像素"""
        palette = self.palette
        for y in range(height):
            row = []
            src_y = y if top_down else (height - 1 - y)
            offset = src_y * row_bytes

            for x in range(width):
                byte_idx = offset + (x // 2)
                if x % 2 == 0:
                    idx = (data[byte_idx] >> 4) & 0x0F
                else:
                    idx = data[byte_idx] & 0x0F
                if idx < len(palette):
                    row.append(palette[idx])
                else:
                    row.append((0, 0, 0))
            self.pixels.append(row)

    def _parse_1bit(self, data: bytes, width: int, height: int, row_bytes: int, top_down: bool):
        """解析 1 位索引像素"""
        palette = self.palette
        if len(palette) < 2:
            palette = [(0, 0, 0), (255, 255, 255)]

        for y in range(height):
            row = []
            src_y = y if top_down else (height - 1 - y)
            offset = src_y * row_bytes

            for x in range(width):
                byte_idx = offset + (x // 8)
                bit = 7 - (x % 8)
                idx = (data[byte_idx] >> bit) & 1
                row.append(palette[idx])
            self.pixels.append(row)

    def _parse_16bit(self, data: bytes, width: int, height: int, row_bytes: int, top_down: bool):
        """解析 16 位像素 (5-6-5 或 5-5-5)"""
        # 默认 5-6-5 格式
        for y in range(height):
            row = []
            src_y = y if top_down else (height - 1 - y)
            offset = src_y * row_bytes

            for x in range(width):
                val = data[offset + x*2] | (data[offset + x*2 + 1] << 8)
                r = ((val >> 11) & 0x1F) * 255 // 31
                g = ((val >> 5) & 0x3F) * 255 // 63
                b = (val & 0x1F) * 255 // 31
                row.append((r, g, b))
            self.pixels.append(row)

    # ============ 保存 ============

    def save(self, filename: str):
        """保存为 BMP 文件 (24位或32位)"""
        if not self.pixels:
            raise BMPError("没有像素数据")

        width = self.width
        height = self.height

        # 检查像素格式
        has_alpha = len(self.pixels[0][0]) == 4 if self.pixels else False
        bit_count = 32 if has_alpha else 24
        bytes_per_pixel = 4 if has_alpha else 3

        # 计算行字节数 (4字节对齐)
        row_bytes = ((width * bytes_per_pixel + 3) // 4) * 4
        image_size = row_bytes * height

        # 构建文件头
        file_size = 14 + 40 + image_size
        bfOffBits = 14 + 40

        # 构建像素数据
        pixel_data = bytearray(image_size)

        for y in range(height):
            row = self.pixels[height - 1 - y]  # BMP 从下到上
            for x in range(width):
                color = row[x]
                offset = y * row_bytes + x * bytes_per_pixel
                pixel_data[offset] = color[2] & 0xFF      # B
                pixel_data[offset + 1] = color[1] & 0xFF  # G
                pixel_data[offset + 2] = color[0] & 0xFF  # R
                if has_alpha and len(color) >= 4:
                    pixel_data[offset + 3] = color[3] & 0xFF  # A

        # 写入文件
        with open(filename, "wb") as f:
            # 文件头
            f.write(b"BM")
            f.write(int32_to_bytes(file_size))
            f.write(int16_to_bytes(0))
            f.write(int16_to_bytes(0))
            f.write(int32_to_bytes(bfOffBits))

            # 信息头
            f.write(int32_to_bytes(40))
            f.write(int32_to_bytes(width))
            f.write(int32_to_bytes(height))
            f.write(int16_to_bytes(1))
            f.write(int16_to_bytes(bit_count))
            f.write(int32_to_bytes(0))  # 无压缩
            f.write(int32_to_bytes(image_size))
            f.write(int32_to_bytes(0))  # 水平分辨率
            f.write(int32_to_bytes(0))  # 垂直分辨率
            f.write(int32_to_bytes(0))  # 使用的颜色数
            f.write(int32_to_bytes(0))  # 重要颜色数

            # 像素数据
            f.write(pixel_data)

    # ============ 工具方法 ============

    @classmethod
    def create_checkerboard(cls, width: int, height: int, size: int = 10):
        """创建棋盘格"""
        img = cls(width, height)
        img.pixels = []
        for y in range(height):
            row = []
            for x in range(width):
                if ((x // size) + (y // size)) % 2 == 0:
                    row.append((255, 255, 255))
                else:
                    row.append((0, 0, 0))
            img.pixels.append(row)
        return img

    @classmethod
    def create_gradient(cls, width: int, height: int):
        """创建渐变色"""
        img = cls(width, height)
        img.pixels = []
        for y in range(height):
            row = []
            for x in range(width):
                r = (x * 255) // width
                g = (y * 255) // height
                b = ((x + y) * 255) // (width + height)
                row.append((r, g, b))
            img.pixels.append(row)
        return img

    def to_rgb(self):
        """转换为 RGB 格式 (移除 Alpha)"""
        if not self.pixels:
            return
        if len(self.pixels[0][0]) == 4:
            for y in range(self.height):
                self.pixels[y] = [(r, g, b) for r, g, b, _ in self.pixels[y]]
            self.has_alpha = False
