# scsv.py - CSV 读写模块
# 纯 Python，零依赖，支持引号包裹和转义


# ============================================================
# 内部解析器
# ============================================================

def _parse_line(line, delimiter=",", quotechar='"'):
    """
    解析一行 CSV，返回字段列表
    支持引号包裹、引号转义（""）
    """
    if not line:
        return []

    result = []
    current = []
    in_quotes = False
    i = 0
    n = len(line)

    while i < n:
        c = line[i]

        if in_quotes:
            if c == quotechar:
                if i + 1 < n and line[i + 1] == quotechar:
                    current.append(quotechar)
                    i += 2
                else:
                    in_quotes = False
                    i += 1
            else:
                current.append(c)
                i += 1
        else:
            if c == quotechar:
                in_quotes = True
                i += 1
            elif c == delimiter:
                result.append("".join(current))
                current = []
                i += 1
            elif c == "\r":
                i += 1
            elif c == "\n":
                i += 1
            else:
                current.append(c)
                i += 1

    result.append("".join(current))
    return result


def _escape_field(field, delimiter=",", quotechar='"'):
    """
    转义一个字段
    """
    if not field:
        return ""

    needs_quote = (
        delimiter in field or
        quotechar in field or
        "\n" in field or
        "\r" in field
    )

    if not needs_quote:
        return field

    escaped = field.replace(quotechar, quotechar + quotechar)
    return quotechar + escaped + quotechar


# ============================================================
# 公共 API（文件对象版）
# ============================================================

def load_csv(fileobj, delimiter=",", quotechar='"', has_header=True):
    """
    从文件对象加载 CSV

    参数:
        fileobj: 文件对象（已打开，支持 readline / read）
        delimiter: 分隔符，默认逗号
        quotechar: 引号字符，默认双引号
        has_header: 是否包含表头

    返回:
        list[list[str]] 或 (list[str], list[list[str]]) 如果 has_header=True
    """
    lines = []
    for line in fileobj:
        line = line.rstrip("\n\r")
        if line.strip() == "":
            continue
        lines.append(line)

    rows = [_parse_line(line, delimiter, quotechar) for line in lines]

    if not rows:
        if has_header:
            return [], []
        return []

    if has_header:
        header = rows[0]
        data = rows[1:]
        return header, data
    else:
        return rows


def save_csv(fileobj, data, header=None, delimiter=",", quotechar='"'):
    """
    保存 CSV 到文件对象

    参数:
        fileobj: 文件对象（已打开，支持 write）
        data: list[list[str]] 数据
        header: 表头（可选）
        delimiter: 分隔符
        quotechar: 引号字符
    """
    if header:
        escaped = [_escape_field(str(h), delimiter, quotechar) for h in header]
        fileobj.write(delimiter.join(escaped) + "\n")

    for row in data:
        escaped = [_escape_field(str(cell), delimiter, quotechar)
                   for cell in row]
        fileobj.write(delimiter.join(escaped) + "\n")


# ============================================================
# 便捷函数（直接从文件路径）
# ============================================================

def load_csv_file(filepath, delimiter=",", quotechar='"', has_header=True, encoding="utf-8"):
    """从文件路径加载 CSV"""
    with open(filepath, encoding=encoding) as f:
        return load_csv(f, delimiter, quotechar, has_header)


def save_csv_file(filepath, data, header=None, delimiter=",", quotechar='"', encoding="utf-8"):
    """保存 CSV 到文件路径"""
    with open(filepath, "w", encoding=encoding) as f:
        save_csv(f, data, header, delimiter, quotechar)


# ============================================================
# 字符串操作（方便测试和内存操作）
# ============================================================

def load_csv_str(content, delimiter=",", quotechar='"', has_header=True):
    """从字符串加载 CSV"""
    lines = content.strip().split("\n")
    lines = [line.strip() for line in lines if line.strip()]
    rows = [_parse_line(line, delimiter, quotechar) for line in lines]

    if not rows:
        if has_header:
            return [], []
        return []

    if has_header:
        return rows[0], rows[1:]
    return rows


def save_csv_str(data, header=None, delimiter=",", quotechar='"'):
    """保存 CSV 为字符串"""
    lines = []
    if header:
        escaped = [_escape_field(str(h), delimiter, quotechar) for h in header]
        lines.append(delimiter.join(escaped))

    for row in data:
        escaped = [_escape_field(str(cell), delimiter, quotechar)
                   for cell in row]
        lines.append(delimiter.join(escaped))

    return "\n".join(lines)


# ============================================================
# 字典转换
# ============================================================

def dict_to_csv(data, fields=None, delimiter=",", quotechar='"'):
    """list[dict] → (header, rows)"""
    if not data:
        return [], []

    if fields is None:
        fields = list(data[0].keys())

    rows = []
    for item in data:
        row = [str(item.get(field, "")) for field in fields]
        rows.append(row)

    return fields, rows


def csv_to_dict(header, rows):
    """(header, rows) → list[dict]"""
    result = []
    for row in rows:
        item = {}
        for i, field in enumerate(header):
            item[field] = row[i] if i < len(row) else ""
        result.append(item)
    return result


# ============================================================
# 导出
# ============================================================

__all__ = [
    "load_csv",
    "save_csv",
    "load_csv_file",
    "save_csv_file",
    "load_csv_str",
    "save_csv_str",
    "dict_to_csv",
    "csv_to_dict",
]
