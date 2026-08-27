# readingsql.py - 读多写少的矩阵数据库
# 纯 Python，零依赖，有序索引支持范围查询


# ============================================================
# 有序索引（排序列表 + 二分查找）
# ============================================================

class _OrderedIndex:
    """有序索引：基于排序列表 + 二分查找"""

    def __init__(self):
        self._data = []          # [(value, row, col), ...] 始终保持有序

    def _insert_sorted(self, value, row, col):
        """直接插入到正确位置 — O(n)"""
        item = (value, row, col)
        low, high = 0, len(self._data)
        while low < high:
            mid = (low + high) // 2
            if self._data[mid][0] < value:
                low = mid + 1
            else:
                high = mid
        self._data.insert(low, item)

    def insert(self, value, row, col):
        """插入 — O(n)"""
        self._insert_sorted(value, row, col)

    def remove(self, value, row, col):
        """移除 (value, row, col) — O(n)"""
        idx = self._binary_search(value)
        while idx < len(self._data) and self._data[idx][0] == value:
            if self._data[idx][1] == row and self._data[idx][2] == col:
                self._data.pop(idx)
                return True
            idx += 1
        return False

    def rebuild(self, data):
        """从原始数据重建索引 — O(n log n)"""
        self._data = []
        for i in range(len(data)):
            for j in range(len(data[i])):
                self._data.append((data[i][j], i, j))
        self._data.sort(key=lambda x: x[0])

    def _binary_search(self, value):
        """二分查找第一个 >= value 的位置"""
        low, high = 0, len(self._data)
        while low < high:
            mid = (low + high) // 2
            if self._data[mid][0] < value:
                low = mid + 1
            else:
                high = mid
        return low

    def search_equal(self, value):
        """等值查询 O(log n + k)，返回 [(row, col), ...]"""
        idx = self._binary_search(value)
        result = []
        while idx < len(self._data) and self._data[idx][0] == value:
            result.append((self._data[idx][1], self._data[idx][2]))
            idx += 1
        return result

    def search_range(self, low, high):
        """范围查询 [low, high] O(log n + k)"""
        left = self._binary_search(low)
        right = self._binary_search(high + 1)
        result = []
        for i in range(left, right):
            result.append((self._data[i][1], self._data[i][2]))
        return result

    def search_less(self, value):
        """查询 < value"""
        idx = self._binary_search(value)
        result = []
        for i in range(idx):
            result.append((self._data[i][1], self._data[i][2]))
        return result

    def search_greater(self, value):
        """查询 > value"""
        idx = self._binary_search(value + 1)
        result = []
        for i in range(idx, len(self._data)):
            result.append((self._data[i][1], self._data[i][2]))
        return result

    def search_condition(self, condition):
        """条件查询（遍历所有值）"""
        result = []
        for val, row, col in self._data:
            if condition(val):
                result.append((row, col))
        return result

    def __len__(self):
        return len(self._data)


# ============================================================
# 惰性查询结果
# ============================================================

class SearchResult:
    """搜索结果包装类 — 惰性求值"""

    def __init__(self, matrix=None, positions=None, condition=None, col=None, place_condition=None):
        self._matrix = matrix
        self._positions = positions          # 预计算的位置列表
        self._condition = condition          # 值条件函数 (val) → bool
        self._col = col                      # 搜索的列（用于列搜索）
        self._place_condition = place_condition  # 位置条件函数 (row, col) → bool
        self._cache = None

    def _compute(self):
        """执行搜索"""
        if self._cache is not None:
            return self._cache

        # 情况1：已有预计算位置
        if self._positions is not None:
            self._cache = self._positions
            return self._cache

        # 情况2：位置条件搜索 (按坐标)
        if self._place_condition is not None and self._matrix is not None:
            result = []
            for i in range(self._matrix.rows):
                for j in range(self._matrix.cols):
                    if self._place_condition(i, j):
                        result.append((i, j))
            self._cache = result
            return self._cache

        # 情况3：值条件搜索 (按值)
        if self._condition is not None and self._matrix is not None:
            result = []
            if self._col is not None:
                # 只搜索指定列
                for i in range(self._matrix.rows):
                    val = self._matrix.get(i, self._col)
                    if self._condition(val):
                        result.append((i, self._col))
            else:
                # 全表搜索
                for i in range(self._matrix.rows):
                    for j in range(self._matrix.cols):
                        if self._condition(self._matrix.get(i, j)):
                            result.append((i, j))
            self._cache = result
            return self._cache

        self._cache = []
        return self._cache

    def list(self):
        """转为完整列表"""
        return self._compute()

    def first(self, n=1):
        """取前 n 个（提前终止）"""
        if self._positions is not None:
            return self._positions[:n]

        if self._matrix is None:
            return []

        result = []
        count = 0

        # 位置条件搜索
        if self._place_condition is not None:
            for i in range(self._matrix.rows):
                for j in range(self._matrix.cols):
                    if self._place_condition(i, j):
                        result.append((i, j))
                        count += 1
                        if count >= n:
                            return result
            return result

        # 值条件搜索
        if self._condition is not None:
            if self._col is not None:
                for i in range(self._matrix.rows):
                    if self._condition(self._matrix.get(i, self._col)):
                        result.append((i, self._col))
                        count += 1
                        if count >= n:
                            return result
            else:
                for i in range(self._matrix.rows):
                    for j in range(self._matrix.cols):
                        if self._condition(self._matrix.get(i, j)):
                            result.append((i, j))
                            count += 1
                            if count >= n:
                                return result
            return result

        return result

    def last(self, n=1):
        """取后 n 个（从后往前搜索）"""
        if self._positions is not None:
            return self._positions[-n:]

        if self._matrix is None:
            return []

        result = []
        count = 0

        # 位置条件搜索
        if self._place_condition is not None:
            for i in range(self._matrix.rows - 1, -1, -1):
                for j in range(self._matrix.cols - 1, -1, -1):
                    if self._place_condition(i, j):
                        result.append((i, j))
                        count += 1
                        if count >= n:
                            result.reverse()
                            return result
            result.reverse()
            return result

        # 值条件搜索
        if self._condition is not None:
            if self._col is not None:
                for i in range(self._matrix.rows - 1, -1, -1):
                    if self._condition(self._matrix.get(i, self._col)):
                        result.append((i, self._col))
                        count += 1
                        if count >= n:
                            result.reverse()
                            return result
            else:
                for i in range(self._matrix.rows - 1, -1, -1):
                    for j in range(self._matrix.cols - 1, -1, -1):
                        if self._condition(self._matrix.get(i, j)):
                            result.append((i, j))
                            count += 1
                            if count >= n:
                                result.reverse()
                                return result
            result.reverse()
            return result

        return result

    def count(self):
        """返回匹配数量"""
        return len(self._compute())

    def __len__(self):
        return len(self._compute())

    def __bool__(self):
        return len(self.first(1)) > 0

    def __iter__(self):
        return iter(self._compute())

    def __getitem__(self, idx):
        return self._compute()[idx]

    def __repr__(self):
        total = len(self._compute())
        return f"SearchResult(matches={total})"

    def __add__(self, other):
        """合并两个搜索结果"""
        if not isinstance(other, SearchResult):
            raise TypeError(f"不能合并 {type(other)}")
        combined = self._compute() + other._compute()
        return SearchResult(positions=combined)


# ============================================================
# 矩阵数据库（读多写少）
# ============================================================

class ReadingSQL:
    """读多写少的矩阵数据库"""

    def __init__(self, data=None):
        self._data = []
        self.rows = 0
        self.cols = 0
        self._index = None

        if data is not None:
            self.load(data)

    def load(self, data):
        """加载数据"""
        self._data = []
        self.rows = len(data)
        self.cols = len(data[0]) if data else 0

        for i in range(self.rows):
            row = []
            for j in range(self.cols):
                row.append(data[i][j])
            self._data.append(row)

        # 重建全局索引
        self._index = _OrderedIndex()
        self._index.rebuild(self._data)

    def get(self, row, col):
        """获取值"""
        if row < 0 or row >= self.rows or col < 0 or col >= self.cols:
            return None
        return self._data[row][col]

    def set(self, row, col, value):
        """设置值（更新索引）"""
        if row < 0 or row >= self.rows or col < 0 or col >= self.cols:
            raise IndexError(f"位置 ({row}, {col}) 超出范围")

        old = self._data[row][col]
        if old == value:
            return

        self._data[row][col] = value
        self._index.remove(old, row, col)
        self._index.insert(value, row, col)

    def insert_row(self, row_data):
        """插入一行"""
        if self.cols == 0:
            self.cols = len(row_data)
        elif len(row_data) != self.cols:
            raise ValueError(f"行长度 {len(row_data)} 与列数 {self.cols} 不匹配")

        row_idx = self.rows
        self._data.append([])
        for j, val in enumerate(row_data):
            self._data[row_idx].append(val)
            self._index.insert(val, row_idx, j)
        self.rows += 1

    def insert_col(self, col_data):
        """插入一列"""
        if self.rows == 0:
            self.rows = len(col_data)
            self.cols = 1
            self._data = [[col_data[i]] for i in range(self.rows)]
            for i, val in enumerate(col_data):
                self._index.insert(val, i, 0)
            return

        if len(col_data) != self.rows:
            raise ValueError(f"列长度 {len(col_data)} 与行数 {self.rows} 不匹配")

        col_idx = self.cols
        for i, val in enumerate(col_data):
            self._data[i].append(val)
            self._index.insert(val, i, col_idx)
        self.cols += 1

    def delete_row(self, row_idx):
        """删除一行"""
        if row_idx < 0 or row_idx >= self.rows:
            raise IndexError(f"行 {row_idx} 超出范围")

        for j in range(self.cols):
            val = self._data[row_idx][j]
            self._index.remove(val, row_idx, j)
        del self._data[row_idx]
        self.rows -= 1

    def delete_col(self, col_idx):
        """删除一列"""
        if col_idx < 0 or col_idx >= self.cols:
            raise IndexError(f"列 {col_idx} 超出范围")

        for i in range(self.rows):
            val = self._data[i][col_idx]
            self._index.remove(val, i, col_idx)
            del self._data[i][col_idx]
        self.cols -= 1

    # ============================================================
    # 值搜索
    # ============================================================

    def search(self, value_or_condition):
        """全局值搜索"""
        if callable(value_or_condition):
            return SearchResult(self, condition=value_or_condition)
        else:
            positions = self._index.search_equal(value_or_condition)
            return SearchResult(positions=positions)

    def search_range(self, low, high):
        """范围查询 [low, high]（走索引）"""
        positions = self._index.search_range(low, high)
        return SearchResult(positions=positions)

    def search_less(self, value):
        """查询 < value（走索引）"""
        positions = self._index.search_less(value)
        return SearchResult(positions=positions)

    def search_greater(self, value):
        """查询 > value（走索引）"""
        positions = self._index.search_greater(value)
        return SearchResult(positions=positions)

    # ============================================================
    # 位置搜索（按坐标）
    # ============================================================

    def search_rect(self, row_start, row_end, col_start, col_end):
        """按矩形范围搜索 — O(面积)"""
        rs = max(0, row_start)
        re = min(self.rows, row_end)
        cs = max(0, col_start)
        ce = min(self.cols, col_end)

        result = []
        for i in range(rs, re):
            for j in range(cs, ce):
                result.append((i, j))     # 位置列表
        return SearchResult(positions=result)

    # ============================================================
    # 聚合
    # ============================================================

    def sum(self, col=None):
        """求和"""
        if col is None:
            total = 0
            for row in self._data:
                for val in row:
                    total += val
            return total
        return sum(self._data[i][col] for i in range(self.rows))

    def avg(self, col=None):
        """平均值"""
        if col is None:
            total = 0
            count = 0
            for row in self._data:
                for val in row:
                    total += val
                    count += 1
            return total / count if count > 0 else 0
        return self.sum(col) / self.rows if self.rows > 0 else 0

    def max(self, col=None):
        """最大值"""
        if col is None:
            return max(max(row) for row in self._data) if self._data else None
        return max(self._data[i][col] for i in range(self.rows)) if self.rows > 0 else None

    def min(self, col=None):
        """最小值"""
        if col is None:
            return min(min(row) for row in self._data) if self._data else None
        return min(self._data[i][col] for i in range(self.rows)) if self.rows > 0 else None

    def count(self, col=None):
        """计数"""
        if col is None:
            return self.rows * self.cols
        return self.rows

    # ============================================================
    # 展示
    # ============================================================

    def __repr__(self):
        return f"ReadingSQL(rows={self.rows}, cols={self.cols})"

    def __str__(self):
        if not self._data:
            return "[]"
        return "[\n  " + ",\n  ".join(str(row) for row in self._data) + "\n]"

    def head(self, n=5):
        """前 n 行"""
        if n >= self.rows:
            return self._data[:]
        return self._data[:n]

    def tail(self, n=5):
        """后 n 行"""
        if n >= self.rows:
            return self._data[:]
        return self._data[-n:]

    def to_list(self):
        """转为二维列表"""
        return [row[:] for row in self._data]

    def to_matrix(self):
        """转为 Matrix（如果可用）"""
        from gaskill import Matrix
        return Matrix(self._data)


# ============================================================
# 快捷函数
# ============================================================

def readingsql(data=None):
    """创建 ReadingSQL"""
    return ReadingSQL(data)


# ============================================================
# 导出
# ============================================================

__all__ = [
    "ReadingSQL",
    "readingsql",
    "SearchResult",
]
