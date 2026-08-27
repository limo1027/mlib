from .srandom import Random


class SGTsaver:
    """sgt存档器"""

    def __init__(self):
        self.saver_dicts = {}
        self.hasher = Random("sgt_checksum")

    def set_value(self, **kwargs):
        """设置值：set_value(score=100, name="hero")"""
        for key, value in kwargs.items():
            self.saver_dicts[key] = value
        return self

    def add(self, key, value):
        """添加单个值"""
        self.saver_dicts[key] = value
        return self

    def _value_to_str(self, value):
        """值转字符串"""
        if isinstance(value, str):
            return f'"{value}"'
        elif isinstance(value, bool):
            return "true" if value else "false"
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, (list, tuple)):
            return "[" + ",".join(f'"{v}"' for v in value) + "]"
        elif hasattr(value, "x") and hasattr(value, "y") and hasattr(value, "z"):
            return f"({value.x},{value.y},{value.z})"
        elif hasattr(value, "x") and hasattr(value, "y"):
            return f"({value.x},{value.y})"
        elif isinstance(value, dict):
            # 递归处理嵌套字典
            items = []
            for k, v in value.items():
                k_str = self._value_to_str(k) if isinstance(k, str) else str(k)
                v_str = self._value_to_str(v)
                items.append(f"{k_str}: {v_str}")
            return "{" + ", ".join(items) + "}"
        else:
            return str(value)

    def _parse_value(self, s, pos):
        """从位置 pos 开始解析一个值，返回 (value, new_pos)"""
        s = s.strip()
        if pos >= len(s):
            return None, pos

        # 跳过空格
        while pos < len(s) and s[pos] == " ":
            pos += 1

        if pos >= len(s):
            return None, pos

        ch = s[pos]

        # 字符串（单引号或双引号）
        if ch in ("'", '"'):
            quote = ch
            pos += 1
            start = pos
            while pos < len(s) and s[pos] != quote:
                pos += 1
            value = s[start:pos]
            pos += 1  # 跳过结束引号
            return value, pos

        # 字典
        if ch == "{":
            return self._parse_dict_from_pos(s, pos)

        # 列表
        if ch == "[":
            return self._parse_list_from_pos(s, pos)

        # 元组
        if ch == "(":
            return self._parse_tuple_from_pos(s, pos)

        # 数字、布尔、None 等
        start = pos
        while pos < len(s) and s[pos] not in (",", "}", "]", ")"):
            pos += 1
        token = s[start:pos].strip()

        # 尝试解析
        if token == "true":
            return True, pos
        elif token == "false":
            return False, pos
        elif token == "None" or token == "null":
            return None, pos
        else:
            try:
                return int(token), pos
            except ValueError:
                try:
                    return float(token), pos
                except ValueError:
                    return token, pos

    def _parse_dict_from_pos(self, s, pos):
        """从位置 pos 开始解析字典，返回 (dict, new_pos)"""
        if pos >= len(s) or s[pos] != "{":
            return None, pos

        pos += 1  # 跳过 '{'
        result = {}

        while pos < len(s):
            # 跳过空格
            while pos < len(s) and s[pos] == " ":
                pos += 1

            if pos >= len(s):
                break

            # 遇到 '}' 结束
            if s[pos] == "}":
                pos += 1
                break

            # 解析 key
            key, pos = self._parse_value(s, pos)
            if key is None:
                break

            # 跳过 ':'
            while pos < len(s) and s[pos] == " ":
                pos += 1
            if pos < len(s) and s[pos] == ":":
                pos += 1

            # 解析 value
            val, pos = self._parse_value(s, pos)

            result[key] = val

            # 跳过逗号
            while pos < len(s) and s[pos] == " ":
                pos += 1
            if pos < len(s) and s[pos] == ",":
                pos += 1

        return result, pos

    def _parse_list_from_pos(self, s, pos):
        """从位置 pos 开始解析列表，返回 (list, new_pos)"""
        if pos >= len(s) or s[pos] != "[":
            return None, pos

        pos += 1
        result = []

        while pos < len(s):
            while pos < len(s) and s[pos] == " ":
                pos += 1

            if pos >= len(s):
                break

            if s[pos] == "]":
                pos += 1
                break

            val, pos = self._parse_value(s, pos)
            result.append(val)

            while pos < len(s) and s[pos] == " ":
                pos += 1
            if pos < len(s) and s[pos] == ",":
                pos += 1

        return result, pos

    def _parse_tuple_from_pos(self, s, pos):
        """从位置 pos 开始解析元组，返回 (tuple, new_pos)"""
        if pos >= len(s) or s[pos] != "(":
            return None, pos

        pos += 1
        result = []

        while pos < len(s):
            while pos < len(s) and s[pos] == " ":
                pos += 1

            if pos >= len(s):
                break

            if s[pos] == ")":
                pos += 1
                break

            val, pos = self._parse_value(s, pos)
            result.append(val)

            while pos < len(s) and s[pos] == " ":
                pos += 1
            if pos < len(s) and s[pos] == ",":
                pos += 1

        return tuple(result), pos

    def _str_to_value(self, s):
        """字符串转值（入口函数）"""
        if not isinstance(s, str):
            return s

        s = s.strip()
        if not s:
            return s

        # 尝试解析
        result, _ = self._parse_value(s, 0)
        return result if result is not None else s

    def save(self, filename, use_hash=True):
        """保存到文件"""
        lines = []

        for key, value in self.saver_dicts.items():
            value_str = self._value_to_str(value)
            lines.append(f"#{key}={value_str}")

        if use_hash:
            content = "\n".join(
                [line for line in lines if line.startswith("#")])
            hash_value = self.hasher.hash(content)
            if hasattr(hash_value, "__iter__") and not isinstance(hash_value, (str, int)):
                hash_value = "".join(str(h) for h in hash_value)
            lines.append(f"hash={hash_value}")

        if isinstance(filename, str):
            with open(filename, "w") as f:
                f.write("\n".join(lines))
        else:
            filename.write("\n".join(lines))

        return True

    def load(self, filename, require_hash=True):
        """从文件加载"""
        self.saver_dicts = {}

        if isinstance(filename, str):
            with open(filename) as f:
                lines = f.readlines()
        else:
            lines = filename.read().split("\n")

        hash_lines = []
        saved_hash = None

        for line in lines:
            line = line.strip()
            if line.startswith("hash"):
                saved_hash = line[5:]
            if not line.startswith("#"):
                continue

            hash_lines.append(line)
            line = line[1:]

            if "=" not in line:
                continue

            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()

            self.saver_dicts[key] = self._str_to_value(value)

        if require_hash and saved_hash is None:
            raise ValueError("文件缺少校验和")
        if not saved_hash:
            return self.saver_dicts

        content = "\n".join([line for line in hash_lines])
        calc_hash = self.hasher.hash(content)
        calc_hash = "".join(str(h) for h in calc_hash)

        if str(calc_hash) != str(saved_hash):
            raise ValueError("文件被修改过")
        return self.saver_dicts

    def get(self, key, default=None):
        """获取值"""
        return self.saver_dicts.get(key, default)

    def __getitem__(self, key):
        """支持 [] 访问"""
        return self.saver_dicts[key]

    def __setitem__(self, key, value):
        """支持 [] 赋值"""
        self.saver_dicts[key] = value
        return self
