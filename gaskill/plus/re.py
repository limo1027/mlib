# ==================== 1. 词法分析器 ====================

class TokenType:
    CHAR = 0
    DOT = 1
    STAR = 2
    PLUS = 3
    QUESTION = 4
    LPAREN = 5
    RPAREN = 6
    PIPE = 7
    CARET = 8
    DOLLAR = 9
    LBRACKET = 10
    RBRACKET = 11
    EOF = 12
    ESCAPE_SEQ = 13
    LBRACE = 14
    RBRACE = 15
    COMMA = 16


class Token:
    def __init__(self, type_, value):
        self.type = type_
        self.value = value


class Lexer:
    def __init__(self, pattern):
        self.pattern = pattern
        self.pos = 0
        self.tokens = []
        self._tokenize()

    def _tokenize(self):
        pattern = self.pattern
        i = 0
        n = len(pattern)
        while i < n:
            c = pattern[i]
            if c == "\\" and i + 1 < n:
                i += 1
                escaped = pattern[i]
                if escaped in "wdDsS":
                    self.tokens.append(Token(TokenType.ESCAPE_SEQ, escaped))
                else:
                    self.tokens.append(Token(TokenType.CHAR, escaped))
                i += 1
            elif c == ".":
                self.tokens.append(Token(TokenType.DOT, "."))
                i += 1
            elif c == "*":
                self.tokens.append(Token(TokenType.STAR, "*"))
                i += 1
            elif c == "+":
                self.tokens.append(Token(TokenType.PLUS, "+"))
                i += 1
            elif c == "?":
                self.tokens.append(Token(TokenType.QUESTION, "?"))
                i += 1
            elif c == "(":
                self.tokens.append(Token(TokenType.LPAREN, "("))
                i += 1
            elif c == ")":
                self.tokens.append(Token(TokenType.RPAREN, ")"))
                i += 1
            elif c == "|":
                self.tokens.append(Token(TokenType.PIPE, "|"))
                i += 1
            elif c == "^":
                self.tokens.append(Token(TokenType.CARET, "^"))
                i += 1
            elif c == "$":
                self.tokens.append(Token(TokenType.DOLLAR, "$"))
                i += 1
            elif c == "[":
                self.tokens.append(Token(TokenType.LBRACKET, "["))
                i += 1
            elif c == "]":
                self.tokens.append(Token(TokenType.RBRACKET, "]"))
                i += 1
            elif c == "{":
                self.tokens.append(Token(TokenType.LBRACE, "{"))
                i += 1
            elif c == "}":
                self.tokens.append(Token(TokenType.RBRACE, "}"))
                i += 1
            elif c == ",":
                self.tokens.append(Token(TokenType.COMMA, ","))
                i += 1
            else:
                self.tokens.append(Token(TokenType.CHAR, c))
                i += 1
        self.tokens.append(Token(TokenType.EOF, ""))


# ==================== 2. 解析器 ====================

class ASTNode:
    def __init__(self, type_, value=None, children=None):
        self.type = type_
        self.value = value
        self.children = children if children is not None else []


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.has_start_anchor = False
        self.has_end_anchor = False

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def next(self):
        tok = self.peek()
        self.pos += 1
        return tok

    def parse(self):
        if self.peek() and self.peek().type == TokenType.CARET:
            self.next()
            self.has_start_anchor = True
        expr = self._parse_union()
        if self.peek() and self.peek().type == TokenType.DOLLAR:
            self.next()
            self.has_end_anchor = True
        return expr

    def _parse_union(self):
        left = self._parse_concat()
        if self.peek() and self.peek().type == TokenType.PIPE:
            self.next()
            right = self._parse_union()
            return ASTNode("union", None, [left, right])
        return left

    def _parse_concat(self):
        nodes = []
        while True:
            tok = self.peek()
            if not tok:
                break
            if tok.type in (TokenType.RPAREN, TokenType.PIPE, TokenType.EOF, TokenType.RBRACE):
                break
            node = self._parse_atom()
            if node:
                nodes.append(node)
            else:
                break
        if len(nodes) == 0:
            return ASTNode("char", "")
        if len(nodes) == 1:
            return nodes[0]
        return ASTNode("concat", None, nodes)

    def _parse_atom(self):
        tok = self.peek()
        if not tok:
            return None
        node = None
        if tok.type == TokenType.CHAR:
            self.next()
            node = ASTNode("char", tok.value)
        elif tok.type == TokenType.DOT:
            self.next()
            node = ASTNode("dot", ".")
        elif tok.type == TokenType.ESCAPE_SEQ:
            self.next()
            node = ASTNode("escape_seq", tok.value)
        elif tok.type == TokenType.LPAREN:
            self.next()
            node = self._parse_union()
            if self.peek() and self.peek().type == TokenType.RPAREN:
                self.next()
        elif tok.type == TokenType.LBRACKET:
            node = self._parse_char_class()
        else:
            return None
        if node:
            node = self._parse_quantifier(node)
        return node

    def _parse_char_class(self):
        self.next()  # consume '['
        chars = []
        negated = False
        if self.peek() and self.peek().value == "^":
            self.next()
            negated = True
        while True:
            tok = self.peek()
            if not tok or tok.type == TokenType.RBRACKET:
                break
            if tok.type == TokenType.CHAR:
                self.next()
                start = tok.value
                # 检查范围：当前是 '-' 且下一个是 CHAR？
                if self.peek() and self.peek().value == "-" and self.peek().type == TokenType.CHAR:
                    self.next()  # consume '-'
                    if self.peek() and self.peek().type == TokenType.CHAR:
                        end_tok = self.next()
                        end = end_tok.value
                        start_code = ord(start)
                        end_code = ord(end)
                        if start_code <= end_code:
                            for code in range(start_code, end_code + 1):
                                chars.append(chr(code))
                        else:
                            for code in range(end_code, start_code + 1):
                                chars.append(chr(code))
                    else:
                        chars.append(start)
                        chars.append("-")
                else:
                    chars.append(start)
            elif tok.type == TokenType.ESCAPE_SEQ:
                self.next()
                seq = tok.value
                expanded = self._expand_escape_seq(seq)
                chars.extend(expanded)
            else:
                # 其他 token（如 DOT, STAR, 等）在字符类中作为普通字符
                self.next()
                chars.append(tok.value)
        if self.peek() and self.peek().type == TokenType.RBRACKET:
            self.next()
        return ASTNode("char_class", {"negated": negated, "chars": chars})

    def _expand_escape_seq(self, seq):
        if seq == "w":
            chars = []
            for code in range(ord("A"), ord("Z")+1):
                chars.append(chr(code))
            for code in range(ord("a"), ord("z")+1):
                chars.append(chr(code))
            for code in range(ord("0"), ord("9")+1):
                chars.append(chr(code))
            chars.append("_")
            return chars
        elif seq == "W":
            return ["__NON_WORD__"]
        elif seq == "d":
            chars = []
            for code in range(ord("0"), ord("9")+1):
                chars.append(chr(code))
            return chars
        elif seq == "D":
            return ["__NON_DIGIT__"]
        elif seq == "s":
            return [" ", "\t", "\n", "\r", "\v", "\f"]
        elif seq == "S":
            return ["__NON_SPACE__"]
        return []

    def _parse_quantifier(self, node):
        tok = self.peek()
        if not tok:
            return node
        if tok.type == TokenType.STAR:
            self.next()
            return ASTNode("repeat", {"min": 0, "max": None}, [node])
        elif tok.type == TokenType.PLUS:
            self.next()
            return ASTNode("repeat", {"min": 1, "max": None}, [node])
        elif tok.type == TokenType.QUESTION:
            self.next()
            return ASTNode("repeat", {"min": 0, "max": 1}, [node])
        elif tok.type == TokenType.LBRACE:
            self.next()
            return self._parse_brace_quantifier(node)
        return node

    def _parse_brace_quantifier(self, node):
        tok = self.peek()
        if not tok or tok.type != TokenType.CHAR:
            return node
        num1 = ""
        while self.peek() and self.peek().type == TokenType.CHAR and self.peek().value.isdigit():
            num1 += self.next().value
        if not num1:
            return node
        min_count = int(num1)
        max_count = min_count
        if self.peek() and self.peek().type == TokenType.COMMA:
            self.next()
            if self.peek() and self.peek().type == TokenType.CHAR and self.peek().value.isdigit():
                num2 = ""
                while self.peek() and self.peek().type == TokenType.CHAR and self.peek().value.isdigit():
                    num2 += self.next().value
                max_count = int(num2)
            else:
                max_count = None
        if self.peek() and self.peek().type == TokenType.RBRACE:
            self.next()
        else:
            return node
        return ASTNode("repeat", {"min": min_count, "max": max_count}, [node])


# ==================== 3. 匹配引擎 ====================

class Matcher:
    def __init__(self, ast, has_start_anchor, has_end_anchor):
        self.ast = ast
        self.has_start_anchor = has_start_anchor
        self.has_end_anchor = has_end_anchor
        self.text = ""

    def _is_word_char(self, char):
        return ("a" <= char <= "z") or ("A" <= char <= "Z") or ("0" <= char <= "9") or char == "_"

    def _is_digit(self, char):
        return "0" <= char <= "9"

    def _is_space(self, char):
        return char in " \t\n\r\v\f"

    def _match_atom(self, node, pos):
        if pos > len(self.text):
            return -1
        if node.type == "char":
            if pos < len(self.text) and self.text[pos] == node.value:
                return pos + 1
            return -1
        elif node.type == "dot":
            if pos < len(self.text):
                return pos + 1
            return -1
        elif node.type == "escape_seq":
            if pos >= len(self.text):
                return -1
            char = self.text[pos]
            seq = node.value
            if seq == "w" and self._is_word_char(char):
                return pos + 1
            elif seq == "W" and not self._is_word_char(char):
                return pos + 1
            elif seq == "d" and self._is_digit(char):
                return pos + 1
            elif seq == "D" and not self._is_digit(char):
                return pos + 1
            elif seq == "s" and self._is_space(char):
                return pos + 1
            elif seq == "S" and not self._is_space(char):
                return pos + 1
            return -1
        elif node.type == "char_class":
            if pos >= len(self.text):
                return -1
            char = self.text[pos]
            data = node.value
            chars = data["chars"]
            negated = data["negated"]
            matched = False
            for elem in chars:
                if isinstance(elem, str):
                    if elem == "__NON_WORD__":
                        if not self._is_word_char(char):
                            matched = True
                            break
                    elif elem == "__NON_DIGIT__":
                        if not self._is_digit(char):
                            matched = True
                            break
                    elif elem == "__NON_SPACE__":
                        if not self._is_space(char):
                            matched = True
                            break
                    else:
                        if elem == char:
                            matched = True
                            break
            # 异或：若 negated 为 True，则匹配补集
            if matched ^ negated:
                return pos + 1
            return -1
        return -1

    def _match(self, node, pos):
        """返回所有可能的结束位置列表（从长到短排序）"""
        if node.type in ("char", "dot", "escape_seq", "char_class"):
            result = self._match_atom(node, pos)
            return [result] if result != -1 else []

        elif node.type == "concat":
            results = [pos]
            for child in node.children:
                new_results = []
                for p in results:
                    for next_p in self._match(child, p):
                        new_results.append(next_p)
                results = new_results
                if not results:
                    return []
            # 去重并排序（位置大的在前）
            seen = set()
            unique = []
            for p in sorted(results, reverse=True):
                if p not in seen:
                    seen.add(p)
                    unique.append(p)
            return unique

        elif node.type == "union":
            left = self._match(node.children[0], pos)
            right = self._match(node.children[1], pos)
            merged = left + right
            seen = set()
            unique = []
            for p in sorted(merged, reverse=True):
                if p not in seen:
                    seen.add(p)
                    unique.append(p)
            return unique

        elif node.type == "repeat":
            data = node.value
            min_count = data["min"]
            max_count = data["max"]
            child = node.children[0]

            # 使用迭代方式生成所有可能的重复次数
            # 先匹配至少 min 次
            positions = [pos]
            # 先强制匹配 min 次
            for _ in range(min_count):
                new_positions = []
                for p in positions:
                    for next_p in self._match(child, p):
                        new_positions.append(next_p)
                positions = new_positions
                if not positions:
                    return []

            # 现在 positions 是匹配了 min 次后的所有可能位置
            # 如果 max_count 有上限，则最多再匹配 (max_count - min_count) 次
            # 否则无限制
            all_positions = list(positions)  # 记录 min 次的结果
            if max_count is None:
                # 无限循环，但我们可以通过 BFS 收集所有可能
                # 使用一个队列，持续扩展
                queue = list(positions)
                while queue:
                    p = queue.pop()
                    # 尝试再匹配一次
                    for next_p in self._match(child, p):
                        if next_p not in all_positions:
                            all_positions.append(next_p)
                            queue.append(next_p)
            else:
                # 有限次数
                current = positions
                for _ in range(max_count - min_count):
                    next_level = []
                    for p in current:
                        for next_p in self._match(child, p):
                            if next_p not in all_positions:
                                all_positions.append(next_p)
                                next_level.append(next_p)
                    current = next_level
                    if not current:
                        break

            # 去重并排序（从长到短）
            seen = set()
            unique = []
            for p in sorted(all_positions, reverse=True):
                if p not in seen:
                    seen.add(p)
                    unique.append(p)
            return unique

        else:
            return []

    def match(self, text):
        self.text = text
        text_len = len(text)
        if self.has_start_anchor:
            starts = [0]
        else:
            starts = range(text_len + 1)
        for start in starts:
            for end in self._match(self.ast, start):
                if self.has_end_anchor:
                    if end == text_len:
                        return True
                else:
                    if end == text_len:
                        return True
        return False


# ==================== 4. 正则表达式引擎 ====================

class Regex:
    def __init__(self, pattern):
        self.pattern = pattern
        lexer = Lexer(pattern)
        parser = Parser(lexer.tokens)
        self.ast = parser.parse()
        self.has_start_anchor = parser.has_start_anchor
        self.has_end_anchor = parser.has_end_anchor
        self.matcher = Matcher(
            self.ast, self.has_start_anchor, self.has_end_anchor)

    def match(self, text):
        return self.matcher.match(text)
