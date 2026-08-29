class DiskKV:
    def __init__(self, filepath, initial_capacity=1024):
        self.filepath = filepath
        self.capacity = initial_capacity
        self.slot_size = 256
        self.key_max = 100
        self.val_max = 100
        self.FLAG_EMPTY = 0
        self.FLAG_OCCUPIED = 1
        self.FLAG_DELETED = 2
        self.count = 0          # 当前有效键值对数
        self.load_factor = 0.7

        # 打开或创建文件
        try:
            self.f = open(filepath, 'r+b')
        except FileNotFoundError:
            self.f = open(filepath, 'w+b')
            self._init_file()
        else:
            # 文件存在，扫描统计现有键值对数量
            self._rebuild_count()

    # ---------- 哈希函数 ----------
    @staticmethod
    def _hash_str(s, capacity):
        h = 5381
        for byte in s.encode('utf-8'):
            h = ((h * 33) + byte) & 0x7fffffff
        return h % capacity

    # ---------- 文件初始化 ----------
    def _init_file(self):
        self.f.seek(0)
        self.f.write(b'\x00' * (self.capacity * self.slot_size))
        self.f.flush()
        self.count = 0

    # ---------- 重新统计键值对数量 ----------
    def _rebuild_count(self):
        self.f.seek(0, 2)
        file_size = self.f.tell()
        # 如果文件大小不符合当前容量，重新初始化（兼容旧版本）
        expected_size = self.capacity * self.slot_size
        if file_size != expected_size:
            self._init_file()
            return
        cnt = 0
        for i in range(self.capacity):
            flag = self._read_flag(i)
            if flag == self.FLAG_OCCUPIED:
                cnt += 1
        self.count = cnt

    def _read_flag(self, index):
        self.f.seek(index * self.slot_size)
        return self.f.read(1)[0]

    # ---------- 槽读写 ----------
    def _read_slot(self, index):
        self.f.seek(index * self.slot_size)
        data = self.f.read(self.slot_size)
        flag = data[0]
        key_len = data[1]
        key_bytes = data[2:2+self.key_max]
        val_len = data[2+self.key_max]
        val_bytes = data[3+self.key_max:3+self.key_max+self.val_max]
        key = key_bytes[:key_len].decode('utf-8') if flag == self.FLAG_OCCUPIED else ''
        val = val_bytes[:val_len].decode('utf-8') if flag == self.FLAG_OCCUPIED else ''
        return (flag, key, val)

    def _write_slot(self, index, flag, key, value):
        key_bytes = key.encode('utf-8')
        val_bytes = value.encode('utf-8')
        slot = bytearray(self.slot_size)
        slot[0] = flag
        slot[1] = len(key_bytes)
        slot[2:2+self.key_max] = key_bytes.ljust(self.key_max, b'\x00')
        slot[2+self.key_max] = len(val_bytes)
        slot[3+self.key_max:3+self.key_max+self.val_max] = val_bytes.ljust(self.val_max, b'\x00')
        self.f.seek(index * self.slot_size)
        self.f.write(slot)
        self.f.flush()

    # ---------- 查找键（返回索引或 -1） ----------
    def _find_key(self, key):
        start = self._hash_str(key, self.capacity)
        index = start
        while True:
            flag, k, _ = self._read_slot(index)
            if flag == self.FLAG_EMPTY:
                return -1
            if flag == self.FLAG_OCCUPIED and k == key:
                return index
            index = (index + 1) % self.capacity
            if index == start:
                return -1

    # ---------- 查找空槽或可复用槽 ----------
    def _find_slot_for_write(self, key):
        start = self._hash_str(key, self.capacity)
        index = start
        first_deleted = -1
        while True:
            flag, k, _ = self._read_slot(index)
            if flag == self.FLAG_EMPTY:
                return index if first_deleted == -1 else first_deleted
            if flag == self.FLAG_DELETED and first_deleted == -1:
                first_deleted = index
            if flag == self.FLAG_OCCUPIED and k == key:
                return index   # 已存在，直接覆盖
            index = (index + 1) % self.capacity
            if index == start:
                # 转了一圈，如果有删除标记，返回；否则表满
                if first_deleted != -1:
                    return first_deleted
                return -1

    # ---------- 扩容 ----------
    def _resize(self):
        # 收集所有有效键值对
        items = []
        for i in range(self.capacity):
            flag, k, v = self._read_slot(i)
            if flag == self.FLAG_OCCUPIED:
                items.append((k, v))
        # 关闭当前文件，以 w+b 重新打开（清空）
        self.f.close()
        new_capacity = self.capacity * 2
        self.capacity = new_capacity
        self.f = open(self.filepath, 'w+b')
        self._init_file()      # 写入扩容后的空文件
        # 重新插入所有数据（这里直接调用内部写入，不触发扩容）
        for k, v in items:
            idx = self._find_slot_for_write(k)
            if idx == -1:
                # 理论上不会，因为新容量很大
                raise Exception('扩容后仍无法插入')
            self._write_slot(idx, self.FLAG_OCCUPIED, k, v)
            self.count += 1     # 重新计数
        # 再次校验计数
        # 注意：_rebuild_count 已经不需要，因为我们手动增加

    # ---------- 对外接口 ----------
    def get(self, key):
        idx = self._find_key(key)
        if idx == -1:
            return None
        _, _, val = self._read_slot(idx)
        return val

    def set(self, key, value):
        # 先检查是否需要扩容（在插入前检查，若需要则先扩容再插入）
        if self.count >= int(self.capacity * self.load_factor):
            self._resize()
        idx = self._find_slot_for_write(key)
        if idx == -1:
            # 正常扩容后不会出现，但以防万一
            self._resize()
            idx = self._find_slot_for_write(key)
        flag, k, _ = self._read_slot(idx)
        # 判断是新增还是更新
        if flag != self.FLAG_OCCUPIED or k != key:
            # 新键
            self.count += 1
        self._write_slot(idx, self.FLAG_OCCUPIED, key, value)

    def delete(self, key):
        idx = self._find_key(key)
        if idx != -1:
            self._write_slot(idx, self.FLAG_DELETED, '', '')
            self.count -= 1

    def close(self):
        if self.f:
            self.f.close()
            self.f = None

    def __del__(self):
        self.close()