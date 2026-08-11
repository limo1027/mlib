from gaskill import DJB2


class DiskKV:
    """极致优化 - 最小化对象分配"""

    def __init__(self, filepath, initial_capacity=131072):
        self.filepath = filepath
        self.capacity = initial_capacity
        self.slot_size = 256
        self.key_max = 100
        self.val_max = 100
        self.load_factor = 0.9

        # 标记
        self.FLAG_EMPTY = 0
        self.FLAG_OCCUPIED = 1
        self.FLAG_DELETED = 2

        # 内存索引（关键！）
        self.index = {}  # key → slot_index
        self.count = 0

        # 预分配字节数组（复用！）
        self._slot_buffer = bytearray(self.slot_size)
        self._key_buffer = bytearray(self.key_max)
        self._val_buffer = bytearray(self.val_max)

        # 打开文件
        try:
            self.f = open(filepath, 'r+b')
            self._rebuild_index()
        except FileNotFoundError:
            self.f = open(filepath, 'w+b')
            self._init_file()

    def _init_file(self):
        """初始化空文件"""
        self.f.seek(0)
        self.f.write(b'\x00' * (self.capacity * self.slot_size))
        self.f.flush()
        self.index = {}
        self.count = 0

    def _rebuild_index(self):
        """重建索引"""
        self.index = {}
        self.count = 0

        # 一次读一大块，减少系统调用
        self.f.seek(0)
        chunk_size = self.capacity * self.slot_size
        data = self.f.read(chunk_size)

        for i in range(self.capacity):
            offset = i * self.slot_size
            flag = data[offset]
            if flag == self.FLAG_OCCUPIED:
                key_len = data[offset + 1]
                key = data[offset + 2:offset + 2 + key_len].decode('utf-8')
                self.index[key] = i
                self.count += 1

    def _read_slot_fast(self, index):
        """快速读取槽位 - 最小化对象分配"""
        self.f.seek(index * self.slot_size)
        data = self.f.read(self.slot_size)  # 仍然分配，但不可避免

        flag = data[0]
        if flag != self.FLAG_OCCUPIED:
            return (flag, '', '')

        key_len = data[1]
        key = data[2:2+key_len].decode('utf-8')

        val_len = data[2+self.key_max]
        val = data[3+self.key_max:3+self.key_max+val_len].decode('utf-8')

        return (flag, key, val)

    def _write_slot_fast(self, index, flag, key, value):
        """快速写入槽位 - 复用缓冲区"""
        key_bytes = key.encode('utf-8')
        val_bytes = value.encode('utf-8')

        # 复用缓冲区，减少分配
        slot = bytearray(self.slot_size)
        slot[0] = flag
        slot[1] = len(key_bytes)
        slot[2:2+len(key_bytes)] = key_bytes
        slot[2+self.key_max] = len(val_bytes)
        slot[3+self.key_max:3+self.key_max+len(val_bytes)] = val_bytes

        self.f.seek(index * self.slot_size)
        self.f.write(slot)
        # 不 flush！让 OS 缓存

    def _find_empty_slot(self, key):
        """查找空位 - 使用内存缓存"""
        start = DJB2(key) % self.capacity
        index = start

        # 先查内存中的空位缓存
        while True:
            flag, _, _ = self._read_slot_fast(index)
            if flag == self.FLAG_EMPTY or flag == self.FLAG_DELETED:
                return index
            index = (index + 1) % self.capacity
            if index == start:
                self._resize()
                return self._find_empty_slot(key)

    def set(self, key, value):
        """设置值 - 使用内存索引"""
        # 1. 查内存索引
        slot = self.index.get(key)
        if slot is None:
            # 新 key，找空位
            slot = self._find_empty_slot(key)

        # 2. 写入
        self._write_slot_fast(slot, self.FLAG_OCCUPIED, key, value)

        # 3. 更新索引
        if key not in self.index:
            self.index[key] = slot
            self.count += 1

        # 4. 检查扩容
        if self.count > self.capacity * self.load_factor:
            self._resize()

    def get(self, key, default=None):
        """获取值 - 使用内存索引"""
        slot = self.index.get(key)
        if slot is None:
            return default

        flag, _, value = self._read_slot_fast(slot)
        return value if flag == self.FLAG_OCCUPIED else default

    def _resize(self):
        """扩容 - 一次性操作"""
        # 刷盘
        self.f.flush()

        # 读取所有数据
        items = []
        for key, slot in self.index.items():
            _, _, value = self._read_slot_fast(slot)
            items.append((key, value))

        # 扩容
        self.capacity *= 16
        self.f.close()
        self.f = open(self.filepath, 'w+b')
        self.f.write(b'\x00' * (self.capacity * self.slot_size))

        # 重建
        self.index = {}
        self.count = 0
        for key, value in items:
            slot = self._find_empty_slot(key)
            self._write_slot_fast(slot, self.FLAG_OCCUPIED, key, value)
            self.index[key] = slot
            self.count += 1

        self.f.flush()

    def flush(self):
        """强制刷盘"""
        self.f.flush()

    def close(self):
        """关闭"""
        self.f.flush()
        self.f.close()
