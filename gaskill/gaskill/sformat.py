__package__ = "gaskill.gaskill"
from .srandom import Random


def uuid4(obj):
    """任意对象转UUID"""
    return Random(str(obj)).uuid()


def superscript(n):
    """数字转上标字符串"""
    n = int(n)
    if 0 <= n <= 9:
        return chr([8304, 185, 178, 179, 8308, 8309, 8310, 8311, 8312, 8313][n])
    result = ""
    for i in str(n):
        result += superscript(i)
    return result


def visual_len(t):
    t = str(t)
    return sum(2 if '\u4e00' <= c <= '\u9fff' else 1 for c in t)


def center(s, width):
    """按视觉宽度居中对齐（粗略版：中文算2，英文算1）"""
    s = str(s)
    s_len = visual_len(s)
    padding = width - s_len
    left = padding // 2
    right = padding - left
    return ' ' * left + s + ' ' * right


def table(data, border_style="unicode", shows={"left": 5, "right": 5, "top": 5, "bottom": 5}):
    """精美表格"""
    shows = {"left": shows["left"], "right": shows["right"],
             "top": shows["top"]-1, "bottom": shows["bottom"]+1}
    if not data:
        return ""

    # 确定表头和数据
    table_data = data
    # 计算列宽
    col_widths = []
    for col in range(len(table_data[0])):
        max_width = max(visual_len(row[col]) for row in table_data)
        col_widths.append(max_width + 2)  # 左右各加1空格

    # 边框字符集
    styles = {
        "unicode": {
            "top_left": "┌", "top_mid": "┬", "top_right": "┐",
            "mid_left": "├", "mid_mid": "┼", "mid_right": "┤",
            "bottom_left": "└", "bottom_mid": "┴", "bottom_right": "┘",
            "hline": "─", "vline": "│", "header_mid": "┼"
        },
        "ascii": {
            "top_left": "+", "top_mid": "+", "top_right": "+",
            "mid_left": "+", "mid_mid": "+", "mid_right": "+",
            "bottom_left": "+", "bottom_mid": "+", "bottom_right": "+",
            "hline": "-", "vline": "|", "header_mid": "+"
        },
        "double": {
            "top_left": "╔", "top_mid": "╦", "top_right": "╗",
            "mid_left": "╠", "mid_mid": "╬", "mid_right": "╣",
            "bottom_left": "╚", "bottom_mid": "╩", "bottom_right": "╝",
            "hline": "═", "vline": "║", "header_mid": "╬"
        },
        "rounded": {
            "top_left": "╭", "top_mid": "┬", "top_right": "╮",
            "mid_left": "├", "mid_mid": "┼", "mid_right": "┤",
            "bottom_left": "╰", "bottom_mid": "┴", "bottom_right": "╯",
            "hline": "─", "vline": "│", "header_mid": "┼"
        }
    }

    s = styles.get(border_style, styles["unicode"])

    def make_line(left, mid, right, widths):
        """生成横线"""
        parts = [s["hline"] * w for w in widths]
        return left + mid.join(parts) + right

    lines = []

    header_cells = []
    widths = []
    for j, val in enumerate(table_data[0]):
        if j == shows["left"]:
            header_cells.append(f"{center('...', col_widths[j])}")
            widths.append(col_widths[j])
            continue
        if j > shows["left"] and j < len(table_data[0]) - shows["right"]:
            continue
        header_cells.append(f"{center(str(val), col_widths[j])}")
        widths.append(col_widths[j])
    lines.append(
        make_line(s["top_left"], s["top_mid"], s["top_right"], widths))

    lines.append(s["vline"] + s["vline"].join(header_cells) + s["vline"])

    lines.append(
        make_line(s["mid_left"], s["header_mid"], s["mid_right"], widths))

    for i, row in enumerate(table_data[1:]):
        cells = []
        if i == shows["top"]:
            string = s["vline"] + \
                center(".....", sum(widths) + len(widths) - 1) + s["vline"]
            lines.append(string)
            continue
        elif i > shows["top"] and i < len(table_data) - shows["bottom"]:
            continue
        else:
            for j, val in enumerate(row):
                if j == shows["left"]:
                    cells.append(f"{'...'.center(col_widths[j])}")
                    continue
                if j > shows["left"] and j < len(row) - shows["right"]:
                    continue
                cells.append(f"{center(str(val), col_widths[j])}")
        lines.append(s["vline"] + s["vline"].join(cells) + s["vline"])
        if i < len(table_data) - 2:
            lines.append(
                make_line(s["mid_left"], s["mid_mid"], s["mid_right"], widths))

    lines.append(make_line(s["bottom_left"],
                 s["bottom_mid"], s["bottom_right"], widths))

    return "\n".join(lines)


def ordinal(number):
    """数字转序数字符串"""
    try:
        number = int(number)
    except ValueError:
        raise ValueError(f"不支持的类型: {type(number)}")

    # 先处理 11,12,13
    if 10 <= number % 100 <= 20:
        return str(number) + "th"

    if number == 1:
        return str(number) + "st"
    elif number == 2:
        return str(number) + "nd"
    elif number == 3:
        return str(number) + "rd"
    elif number < 10:
        return str(number) + "th"
    else:
        return str(number)[:-1] + ordinal(str(number)[-1:])


def to_poly(expr, use_star=False):
    """表达式转多项式字符串"""
    if not expr:
        return expr

    expr = expr.replace("^", "**")
    expr = expr.replace(" ", "")

    terms = []
    current = ""
    for char in expr:
        if char == '+' and current:
            terms.append(current)
            current = ""
        elif char == '-' and current:
            terms.append(current)
            current = "-"
        else:
            current += char
    if current:
        terms.append(current)

    parsed_terms = {}  # 变量部分 -> 系数

    for term in terms:
        if not term:
            continue

        var_start = -1
        for i, char in enumerate(term):
            if char.isalpha():
                var_start = i
                break

        if var_start == -1:
            coeff = float(term) if '.' in term else int(term)
            parsed_terms[""] = parsed_terms.get("", 0) + coeff
            continue

        # 系数部分
        coeff_str = term[:var_start]
        if not coeff_str or coeff_str == '+':
            coeff = 1
        elif coeff_str == '-':
            coeff = -1
        else:
            coeff = float(coeff_str) if '.' in coeff_str else int(coeff_str)

        # 变量部分
        var_part = term[var_start:]

        # 处理 x10 的情况
        if len(var_part) > 1 and var_part[0].isalpha() and var_part[1:].isdigit():
            extra_coeff = int(var_part[1:])
            coeff *= extra_coeff
            var_part = var_part[0]

        parsed_terms[var_part] = parsed_terms.get(var_part, 0) + coeff

    result_terms = []

    for var in sorted(parsed_terms.keys()):
        if var == "":
            continue
        coeff = parsed_terms[var]
        if coeff == 0:
            continue

        if coeff == 1:
            coeff_str = ""
        elif coeff == -1:
            coeff_str = "-"
        else:
            coeff_str = str(coeff)

        if use_star:
            var_str = var.replace("**", "^")
        else:
            var_str = var

        if coeff_str:
            if use_star:
                result_terms.append(f"{coeff_str}{var_str}")
            else:
                result_terms.append(f"{coeff_str}*{var_str}")
        else:
            result_terms.append(var_str)

    if "" in parsed_terms and parsed_terms[""] != 0:
        result_terms.append(str(parsed_terms[""]))

    if not result_terms:
        return "0"

    result = result_terms[0]
    for term in result_terms[1:]:
        if term.startswith('-'):
            result += term
        else:
            result += "+" + term

    return result


def number_to_english(n):
    """把整数转成英语单词形式，适合对话文本"""
    if n == 0:
        return "zero"

    # 1-19 特殊形式
    units = ["", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine",
             "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen",
             "seventeen", "eighteen", "nineteen"]

    # 整十
    tens = ["", "", "twenty", "thirty", "forty", "fifty",
            "sixty", "seventy", "eighty", "ninety"]

    # 千以上单位
    thousands = ["", "thousand", "million", "billion", "trillion",
                 "quadrillion", "quintillion", "sextillion", "septillion",
                 "octillion", "nonillion", "decillion"]

    def _convert_three_digits(num):
        """处理 1-999"""
        if num == 0:
            return ""
        if num < 20:
            return units[num]
        if num < 100:
            ten = tens[num // 10]
            unit = units[num % 10]
            return ten + ("-" + unit if unit else "")
        # 100-999
        hundred = units[num // 100] + " hundred"
        rest = num % 100
        if rest == 0:
            return hundred
        return hundred + " and " + _convert_three_digits(rest)

    if n < 0:
        return "negative " + number_to_english(-n)

    result = []
    group_index = 0
    while n > 0:
        group = n % 1000
        if group != 0:
            group_str = _convert_three_digits(group)
            if thousands[group_index]:
                group_str += " " + thousands[group_index]
            result.insert(0, group_str)
        n //= 1000
        group_index += 1

    return " ".join(result).strip()


def english_to_number(s):
    """把英语单词形式转成整数，适合解析对话文本"""
    if not s or s.strip() == "":
        return 0

    s = s.strip().lower().replace("-", " ").replace(" and ", " ")

    # 处理负数
    if s.startswith("negative "):
        return -english_to_number(s[9:])

    if s == "zero":
        return 0

    # 单词映射表
    units = {
        "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4,
        "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
        "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13,
        "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17,
        "eighteen": 18, "nineteen": 19
    }

    tens = {
        "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50,
        "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90
    }

    scales = {
        "hundred": 100,
        "thousand": 1000,
        "million": 1000000,
        "billion": 1000000000,
        "trillion": 1000000000000,
        "quadrillion": 1000000000000000,
        "quintillion": 1000000000000000000,
        "sextillion": 10**21,
        "septillion": 10**24,
        "octillion": 10**27,
        "nonillion": 10**30,
        "decillion": 10**33
    }

    words = s.split()
    total = 0
    current = 0

    i = 0
    while i < len(words):
        word = words[i]

        # 处理 1-19
        if word in units:
            current += units[word]

        # 处理整十
        elif word in tens:
            current += tens[word]

        # 处理 hundred
        elif word == "hundred":
            current *= 100

        # 处理千以上单位
        elif word in scales:
            if current == 0:
                current = 1
            total += current * scales[word]
            current = 0

        # 处理带连字符的 twenty-one 之类的（已经替换成空格）
        i += 1

    return total + current


def insert(base_str, place, insert_str):
    """在字符串位置插入子字符串"""
    pos = place
    new_s = base_str[:pos] + insert_str + base_str[pos:]
    return new_s


def encode(string):
    """编码（将字符串转换为数字序列）"""
    if not string:
        return ""
    codes = []
    for char in string:
        code = ord(char)
        code_str = str(code)
        length_param = len(code_str)
        codes.append(str(length_param))
        codes.append(code_str)
    return ''.join(codes)


def decode(encoded):
    """解码（即使被截断也能尽量恢复）"""
    result = ""
    i = 0
    chars_decoded = 0
    warning = None
    while i < len(encoded):
        # 检查是否还有足够长度读长度标记
        if i + 1 > len(encoded):
            warning = f"警告: 长度标记被截断，已解码 {chars_decoded} 个字符"
            break

        length_param = int(encoded[i])
        i += 1

        # 检查是否还有足够长度读数据
        if i + length_param > len(encoded):
            warning = f"警告: 第{chars_decoded+1}个字符的数据被截断"
            break

        code_str = encoded[i:i + length_param]
        if not code_str.isdigit():
            warning = "检测到编码意外被修改 - 不是全数字"
            break
        i += length_param
        if not int(code_str) <= 1114111:
            warning = "检测到编码意外被修改 - 数字过大"
            break
        result += chr(int(code_str))
        chars_decoded += 1
    if warning:
        return result, warning
    else:
        return result


def time_format(seconds, mode='auto'):
    if seconds < 0:
        sign = "-"
        seconds = -seconds
    else:
        sign = ""

    seconds = int(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    if mode == 'full' or mode == 'colons':
        return f"{sign}{hours:02d}:{minutes:02d}:{secs:02d}"

    if mode == 'short':
        parts = []
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        if secs > 0 or not parts:
            parts.append(f"{secs}s")
        return sign + " ".join(parts)

    if mode == 'words':
        parts = []
        if hours == 1:
            parts.append("1 hour")
        elif hours > 1:
            parts.append(f"{hours} hours")
        if minutes == 1:
            parts.append("1 minute")
        elif minutes > 1:
            parts.append(f"{minutes} minutes")
        if secs == 1:
            parts.append("1 second")
        elif secs > 1:
            parts.append(f"{secs} seconds")
        if not parts:
            return "0 seconds"
        return sign + " ".join(parts)

    if seconds < 60:
        return sign + f"{secs}s"
    elif seconds < 3600:
        if secs == 0:
            return sign + f"{minutes}m"
        return sign + f"{minutes}m {secs}s"
    elif seconds < 86400:
        if minutes == 0 and secs == 0:
            return sign + f"{hours}h"
        elif secs == 0:
            return sign + f"{hours}h {minutes}m"
        return sign + f"{hours}h {minutes}m {secs}s"
    else:
        days = seconds // 86400
        remainder = seconds % 86400
        hours = remainder // 3600
        if remainder == 0:
            return sign + f"{days}d"
        return sign + f"{days}d {hours}h"


def file_size(size_bytes, mode='auto', decimal=False):
    """将字节数转换为可读的文件大小格式"""
    if size_bytes < 0:
        sign = "-"
        size_bytes = -size_bytes
    else:
        sign = ""

    if mode == 'bits':
        size_bits = size_bytes * 8
        units = ['b', 'Kb', 'Mb', 'Gb', 'Tb', 'Pb', 'Eb', 'Zb', 'Yb']
        divisor = 1000
        size_val = size_bits
    elif mode == 'si':
        units = ['B', 'KB', 'MB(ten)', 'GB(ten)', 'TB(ten)',
                 'PB(ten)', 'EB(ten)', 'ZB(ten)', 'YB(ten)']
        divisor = 1000
        size_val = size_bytes
    elif mode == 'binary':
        units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
        divisor = 1024
        size_val = size_bytes
    elif mode == 'short':
        units = ['B', 'K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y']
        divisor = 1024
        size_val = size_bytes
    elif mode == 'full':
        units = ['bytes', 'kilobytes', 'megabytes', 'gigabytes', 'terabytes',
                 'petabytes', 'exabytes', 'zettabytes', 'yottabytes']
        divisor = 1024
        size_val = size_bytes
    else:  # auto
        return file_size(size_bytes, 'binary' if decimal else 'si', decimal)

    if size_val == 0:
        if mode == 'short':
            return sign + "0"
        elif mode == 'full':
            return sign + "0 bytes"
        else:
            return sign + f"0 {units[0]}"

    # 找到合适的单位
    unit_index = 0
    while size_val >= divisor and unit_index < len(units) - 1:
        size_val /= divisor
        unit_index += 1

    # 确定小数位数
    if decimal is False:
        if mode == 'short':
            dec = 0
        else:
            dec = 0 if size_val >= 10 else (1 if size_val >= 1 else 2)
    else:
        dec = decimal

    # 格式化数值
    if dec == 0:
        val_str = str(int(size_val))
    else:
        format_str = f"{{:.{dec}f}}"
        val_str = format_str.format(size_val).rstrip('0').rstrip('.')

    # 根据不同模式返回格式
    if mode == 'short':
        return sign + val_str + units[unit_index]
    elif mode == 'full':
        unit_name = units[unit_index]
        if val_str == '1' and unit_name != 'bytes':
            unit_name = unit_name[:-1]  # 单数形式
        return sign + val_str + " " + unit_name
    elif mode == 'bits' and unit_index > 0:
        # 比特单位通常用小写 b
        unit = units[unit_index]
        if unit.endswith('b'):
            unit = unit[0].upper() + unit[1] if len(unit) > 1 else unit
        return sign + val_str + " " + unit
    else:
        return sign + val_str + " " + units[unit_index]


# 生成 10000 个 UUID，看有没有重复
uuids = set()
collisions = 0
for i in range(100000):
    uid = uuid4(str(i))
    if uid in uuids:
        collisions += 1
        print(i)
    uuids.add(uid)
print(f"碰撞次数: {collisions}")
