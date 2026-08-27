from .smath import EPSILON, cos, sin, sqrt


class Matrix:
    """通用矩阵类"""

    def __init__(self, data):
        """初始化矩阵"""
        if not data:
            self.data = [[]]
            self.rows = 0
            self.cols = 0
        elif isinstance(data[0], (list, tuple)):
            self.data = [list(row) for row in data]
            self.rows = len(data)
            self.cols = len(data[0]) if data else 0
        else:
            self.data = [list(data)]
            self.rows = 1
            self.cols = len(data)

        if not self._is_valid():
            raise ValueError("矩阵每行的列数必须相同")

    def _is_valid(self):
        for row in self.data:
            if len(row) != self.cols:
                return False
        return True

    def __getitem__(self, key):
        i, j = key
        return self.data[i][j]

    def __setitem__(self, key, value):
        i, j = key
        self.data[i][j] = value

    def __repr__(self):
        return f"Matrix({self.data})"

    def __str__(self):
        if self.rows == 0:
            return "[]"

        col_widths = []
        for j in range(self.cols):
            max_width = max(len(str(self.data[i][j]))
                            for i in range(self.rows))
            col_widths.append(max_width)

        lines = []
        for row in self.data:
            line = "  ".join(str(val).rjust(
                col_widths[j]) for j, val in enumerate(row))
            lines.append(line)
        return "\n".join(lines)

    def __eq__(self, other):
        if not isinstance(other, Matrix):
            return False
        if self.rows != other.rows or self.cols != other.cols:
            return False
        for i in range(self.rows):
            for j in range(self.cols):
                if abs(self.data[i][j] - other.data[i][j]) > EPSILON:
                    return False
        return True

    def __add__(self, other):
        if self.rows != other.rows or self.cols != other.cols:
            raise ValueError(
                f"矩阵尺寸不匹配：({self.rows}x{self.cols}) vs ({other.rows}x{other.cols})")

        result = []
        for i in range(self.rows):
            row = [self.data[i][j] + other.data[i][j]
                   for j in range(self.cols)]
            result.append(row)
        return Matrix(result)

    def __sub__(self, other):
        if self.rows != other.rows or self.cols != other.cols:
            raise ValueError(
                f"矩阵尺寸不匹配：({self.rows}x{self.cols}) vs ({other.rows}x{other.cols})")

        result = []
        for i in range(self.rows):
            row = [self.data[i][j] - other.data[i][j]
                   for j in range(self.cols)]
            result.append(row)
        return Matrix(result)

    def __mul__(self, other):
        if isinstance(other, (int, float, complex)):
            result = []
            for i in range(self.rows):
                row = [val * other for val in self.data[i]]
                result.append(row)
            return Matrix(result)

        if isinstance(other, Matrix):
            if self.cols != other.rows:
                raise ValueError(
                    f"矩阵尺寸不匹配：({self.rows}x{self.cols}) * ({other.rows}x{other.cols})")

            result = []
            for i in range(self.rows):
                row = []
                for j in range(other.cols):
                    val = sum(self.data[i][k] * other.data[k][j]
                              for k in range(self.cols))
                    row.append(val)
                result.append(row)
            return Matrix(result)

        return NotImplemented

    def __rmul__(self, other):
        return self.__mul__(other)

    def __neg__(self):
        return self * (-1)

    def __truediv__(self, scalar):
        return self * (1 / scalar)

    def transpose(self):
        """转置矩阵"""
        if self.rows == 0:
            return Matrix([])

        result = []
        for j in range(self.cols):
            row = [self.data[i][j] for i in range(self.rows)]
            result.append(row)
        return Matrix(result)

    @property
    def T(self):
        """转置的简写"""
        return self.transpose()

    def trace(self):
        """迹（对角线元素之和）"""
        if self.rows != self.cols:
            raise ValueError("只有方阵才有迹")
        return sum(self.data[i][i] for i in range(self.rows))

    def det(self):
        """行列式（仅方阵）"""
        if self.rows != self.cols:
            raise ValueError("只有方阵才有行列式")

        n = self.rows

        if n == 1:
            return self.data[0][0]

        if n == 2:
            return self.data[0][0] * self.data[1][1] - self.data[0][1] * self.data[1][0]

        if n == 3:
            a = self.data
            return (a[0][0] * (a[1][1]*a[2][2] - a[1][2]*a[2][1]) -
                    a[0][1] * (a[1][0]*a[2][2] - a[1][2]*a[2][0]) +
                    a[0][2] * (a[1][0]*a[2][1] - a[1][1]*a[2][0]))

        return self._det_lu()

    def _det_lu(self):
        """使用 LU 分解计算行列式"""
        n = self.rows
        matrix = [row[:] for row in self.data]
        det = 1

        for i in range(n):
            pivot = i
            for j in range(i + 1, n):
                if abs(matrix[j][i]) > abs(matrix[pivot][i]):
                    pivot = j

            if pivot != i:
                matrix[i], matrix[pivot] = matrix[pivot], matrix[i]
                det *= -1

            if abs(matrix[i][i]) < EPSILON:
                return 0

            det *= matrix[i][i]

            for j in range(i + 1, n):
                factor = matrix[j][i] / matrix[i][i]
                for k in range(i, n):
                    matrix[j][k] -= factor * matrix[i][k]

        return det

    def inverse(self):
        """逆矩阵"""
        if self.rows != self.cols:
            raise ValueError("只有方阵才有逆矩阵")

        n = self.rows
        det = self.det()
        if abs(det) < EPSILON:
            raise ValueError("矩阵不可逆（行列式为 0）")

        if n == 1:
            return Matrix([[1 / self.data[0][0]]])

        if n == 2:
            a, b = self.data[0]
            c, d = self.data[1]
            return Matrix([[d/det, -b/det], [-c/det, a/det]])

        return self._inverse_gj()

    def _inverse_gj(self):
        """高斯 - 约旦消元法求逆"""
        n = self.rows

        augmented = []
        for i in range(n):
            row = self.data[i][:] + [0] * n
            row[n + i] = 1
            augmented.append(row)

        for col in range(n):
            pivot = col
            for row in range(col + 1, n):
                if abs(augmented[row][col]) > abs(augmented[pivot][col]):
                    pivot = row

            augmented[col], augmented[pivot] = augmented[pivot], augmented[col]

            pivot_val = augmented[col][col]
            if abs(pivot_val) < EPSILON:
                raise ValueError("矩阵不可逆")

            for j in range(2 * n):
                augmented[col][j] /= pivot_val

            for row in range(n):
                if row != col:
                    factor = augmented[row][col]
                    for j in range(2 * n):
                        augmented[row][j] -= factor * augmented[col][j]

        inverse_data = []
        for i in range(n):
            inverse_data.append(augmented[i][n:])

        return Matrix(inverse_data)

    def rank(self):
        """矩阵的秩"""
        matrix = [row[:] for row in self.data]
        m, n = self.rows, self.cols
        rank = 0

        for col in range(n):
            pivot_row = -1
            for row in range(rank, m):
                if abs(matrix[row][col]) > EPSILON:
                    pivot_row = row
                    break

            if pivot_row == -1:
                continue

            matrix[rank], matrix[pivot_row] = matrix[pivot_row], matrix[rank]

            pivot_val = matrix[rank][col]
            for j in range(n):
                matrix[rank][j] /= pivot_val

            for row in range(m):
                if row != rank:
                    factor = matrix[row][col]
                    for j in range(n):
                        matrix[row][j] -= factor * matrix[rank][j]

            rank += 1

        return rank

    def lu_decomposition(self):
        """LU 分解，返回 (L, U)"""
        if self.rows != self.cols:
            raise ValueError("LU 分解仅适用于方阵")

        n = self.rows
        L = Matrix.identity(n)
        U = self.copy()

        for k in range(n):
            if abs(U.data[k][k]) < EPSILON:
                raise ValueError("主元为 0，需要选主元")

            for i in range(k + 1, n):
                factor = U.data[i][k] / U.data[k][k]
                L.data[i][k] = factor

                for j in range(k, n):
                    U.data[i][j] -= factor * U.data[k][j]

        return L, U

    def copy(self):
        """深拷贝矩阵"""
        return Matrix([row[:] for row in self.data])

    def submatrix(self, row_start, row_end, col_start, col_end):
        """提取子矩阵"""
        result = []
        for i in range(row_start, row_end):
            row = self.data[i][col_start:col_end]
            result.append(row)
        return Matrix(result)

    def minor(self, i, j):
        """余子式（删除第 i 行第 j 列后的行列式）"""
        if self.rows != self.cols:
            raise ValueError("只有方阵才有余子式")

        sub = []
        for row in range(self.rows):
            if row == i:
                continue
            new_row = []
            for col in range(self.cols):
                if col == j:
                    continue
                new_row.append(self.data[row][col])
            sub.append(new_row)

        return Matrix(sub).det()

    def cofactor(self, i, j):
        """代数余子式"""
        return ((-1) ** (i + j)) * self.minor(i, j)

    def adjugate(self):
        """伴随矩阵"""
        if self.rows != self.cols:
            raise ValueError("只有方阵才有伴随矩阵")

        n = self.rows
        cofactor_matrix = []

        for i in range(n):
            row = []
            for j in range(n):
                row.append(self.cofactor(i, j))
            cofactor_matrix.append(row)

        return Matrix(cofactor_matrix).transpose()

    def frobenius_norm(self):
        """Frobenius 范数"""
        return sqrt(sum(val**2 for row in self.data for val in row))

    def infinity_norm(self):
        """无穷范数（行和范数）"""
        return max(sum(abs(val) for val in row) for row in self.data)

    def one_norm(self):
        """1-范数（列和范数）"""
        return max(sum(abs(self.data[i][j]) for i in range(self.rows)) for j in range(self.cols))

    def is_symmetric(self):
        """是否是对称矩阵"""
        if self.rows != self.cols:
            return False
        for i in range(self.rows):
            for j in range(i + 1, self.cols):
                if abs(self.data[i][j] - self.data[j][i]) > EPSILON:
                    return False
        return True

    def is_identity(self):
        """是否是单位矩阵"""
        if self.rows != self.cols:
            return False
        for i in range(self.rows):
            for j in range(self.cols):
                expected = 1 if i == j else 0
                if abs(self.data[i][j] - expected) > EPSILON:
                    return False
        return True

    def is_diagonal(self):
        """是否是对角矩阵"""
        if self.rows != self.cols:
            return False
        for i in range(self.rows):
            for j in range(self.cols):
                if i != j and abs(self.data[i][j]) > EPSILON:
                    return False
        return True

    def diagonal(self):
        """提取对角线元素"""
        return [self.data[i][i] for i in range(min(self.rows, self.cols))]

    def to_vector(self):
        """如果是行向量或列向量，转换为列表"""
        if self.rows == 1:
            return self.data[0]
        elif self.cols == 1:
            return [row[0] for row in self.data]
        else:
            raise ValueError("不是向量")


def matrix(data):
    """创建矩阵的快捷函数"""
    return Matrix(data)


def rotation_matrix_2d(theta):
    """2D 旋转矩阵"""
    c, s = cos(theta), sin(theta)
    return Matrix([[c, -s], [s, c]])


def rotation_matrix_x(theta):
    """3D 绕 X 轴旋转矩阵"""
    c, s = cos(theta), sin(theta)
    return Matrix([
        [1, 0, 0],
        [0, c, -s],
        [0, s, c],
    ])


def rotation_matrix_y(theta):
    """3D 绕 Y 轴旋转矩阵"""
    c, s = cos(theta), sin(theta)
    return Matrix([
        [c, 0, s],
        [0, 1, 0],
        [-s, 0, c],
    ])


def rotation_matrix_z(theta):
    """3D 绕 Z 轴旋转矩阵"""
    c, s = cos(theta), sin(theta)
    return Matrix([
        [c, -s, 0],
        [s, c, 0],
        [0, 0, 1],
    ])


def scaling_matrix_2d(sx, sy=None):
    """2D 缩放矩阵"""
    if sy is None:
        sy = sx
    return Matrix([[sx, 0], [0, sy]])


def scaling_matrix_3d(sx, sy=None, sz=None):
    """3D 缩放矩阵"""
    if sy is None:
        sy = sx
    if sz is None:
        sz = sx
    return Matrix([
        [sx, 0, 0],
        [0, sy, 0],
        [0, 0, sz],
    ])


def translation_matrix_2d(tx, ty):
    """2D 平移矩阵（齐次坐标，3×3）"""
    return Matrix([
        [1, 0, tx],
        [0, 1, ty],
        [0, 0, 1],
    ])


def translation_matrix_3d(tx, ty, tz):
    """3D 平移矩阵（齐次坐标，4×4）"""
    return Matrix([
        [1, 0, 0, tx],
        [0, 1, 0, ty],
        [0, 0, 1, tz],
        [0, 0, 0, 1],
    ])


def solve_linear(A, b):
    """解线性方程组 Ax = b"""
    if not isinstance(A, Matrix):
        A = Matrix(A)

    if isinstance(b, Matrix):
        b = b.to_vector()

    n = A.rows
    augmented = []

    for i in range(n):
        row = A.data[i][:] + [b[i]]
        augmented.append(row)

    for col in range(n):
        pivot = col
        for row in range(col + 1, n):
            if abs(augmented[row][col]) > abs(augmented[pivot][col]):
                pivot = row

        augmented[col], augmented[pivot] = augmented[pivot], augmented[col]

        pivot_val = augmented[col][col]
        if abs(pivot_val) < EPSILON:
            raise ValueError("方程组无唯一解")

        for j in range(n + 1):
            augmented[col][j] /= pivot_val

        for row in range(n):
            if row != col:
                factor = augmented[row][col]
                for j in range(n + 1):
                    augmented[row][j] -= factor * augmented[col][j]

    x = [augmented[i][n] for i in range(n)]
    return x


def eigenvalues_2x2(matrix):
    """计算 2x2 矩阵的特征值"""
    if not isinstance(matrix, Matrix):
        matrix = Matrix(matrix)

    if matrix.rows != 2 or matrix.cols != 2:
        raise ValueError("仅适用于 2x2 矩阵")

    a, b = matrix.data[0]
    c, d = matrix.data[1]

    trace = a + d
    det = a * d - b * c

    discriminant = trace * trace - 4 * det

    if discriminant >= 0:
        sqrt_disc = sqrt(discriminant)
        lambda1 = (trace + sqrt_disc) / 2
        lambda2 = (trace - sqrt_disc) / 2
        return [lambda1, lambda2]
    else:
        real_part = trace / 2
        imag_part = sqrt(-discriminant) / 2
        return [complex(real_part, imag_part), complex(real_part, -imag_part)]


def kronecker(A, B):
    """Kronecker 积"""
    if not isinstance(A, Matrix):
        A = Matrix(A)
    if not isinstance(B, Matrix):
        B = Matrix(B)

    result = []
    for i in range(A.rows):
        for ii in range(B.rows):
            row = []
            for j in range(A.cols):
                for jj in range(B.cols):
                    row.append(A.data[i][j] * B.data[ii][jj])
            result.append(row)

    return Matrix(result)


def outer_product(v1, v2):
    """外积"""
    if isinstance(v1, Matrix):
        v1 = v1.to_vector()
    if isinstance(v2, Matrix):
        v2 = v2.to_vector()

    result = []
    for val1 in v1:
        row = [val1 * val2 for val2 in v2]
        result.append(row)

    return Matrix(result)


def matrix_from_func(func, rows, cols=None, start=(0, 0)):
    """从函数创建矩阵"""
    if cols is None:
        cols = rows

    data = [[func(i+start[0], j+start[1]) for j in range(cols)]
            for i in range(rows)]
    return Matrix(data)
