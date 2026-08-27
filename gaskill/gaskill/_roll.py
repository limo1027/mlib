def parse_dice(expr):
    expr = expr.replace(" ", "")

    # 按加减号分割表达式
    parts = _split_expression(expr)

    result = {
        "expr": expr,
        "parts": [],
        "total": 0,
    }

    for part in parts:
        if "d" in part.lower():
            part_result = _parse_single_dice(part)
        else:
            part_result = _parse_number(part)

        result["parts"].append(part_result)
        result["total"] += part_result["value"]

    return result


def _split_expression(expr):
    parts = []
    current = ""

    for i, char in enumerate(expr):
        if char in "+-" and i > 0:
            parts.append(current)
            current = char
        else:
            current += char

    if current:
        parts.append(current)

    return parts


def _parse_single_dice(expr):
    d_pos = expr.lower().find("d")

    # 解析骰子数量
    count_str = expr[:d_pos]
    count = int(count_str) if count_str else 1

    # 解析剩余部分
    rest = expr[d_pos+1:]

    # 初始化结果
    result = {
        "expr": expr,
        "type": "dice",
        "count": count,
        "sides": 0,
        "modifier": None,
        "modifier_value": 0,
        "explode": None,
        "bonus": 0,
        "value": 0,  # 占位, 实际掷骰时计算
    }

    i = 0
    # 读骰子面数
    sides_str = ""
    while i < len(rest) and rest[i].isdigit():
        sides_str += rest[i]
        i += 1

    result["sides"] = int(sides_str)

    # 读修饰符
    if i < len(rest) and rest[i].isalpha():
        mod = rest[i]
        i += 1
        if i < len(rest) and rest[i].isalpha():
            mod += rest[i]
            i += 1
        result["modifier"] = mod

        # 读修饰符数值
        mod_val_str = ""
        while i < len(rest) and rest[i].isdigit():
            mod_val_str += rest[i]
            i += 1
        result["modifier_value"] = int(mod_val_str) if mod_val_str else 1

    # 读爆炸骰
    if i < len(rest) and rest[i] == "x":
        i += 1
        explode_str = ""
        while i < len(rest) and rest[i].isdigit():
            explode_str += rest[i]
            i += 1
        result["explode"] = int(explode_str)

    # 读加减
    if i < len(rest) and rest[i] in "+-":
        result["bonus"] = int(rest[i:])

    return result


def _parse_number(expr):
    return {
        "expr": expr,
        "type": "number",
        "value": int(expr),
    }


def roll_dice(parse_result, random_func):
    if parse_result["type"] == "number":
        return parse_result["value"]

    # 先掷出所有骰子
    rolls = [random_func(1, parse_result["sides"])
             for _ in range(parse_result["count"])]

    # 应用爆炸骰
    if parse_result["explode"]:
        rolls = _apply_explode(rolls, parse_result["sides"],
                               parse_result["explode"], random_func)

    # 应用修饰符
    if parse_result["modifier"] == "kh":
        rolls = sorted(rolls, reverse=True)[:parse_result["modifier_value"]]
    elif parse_result["modifier"] == "kl":
        rolls = sorted(rolls)[:parse_result["modifier_value"]]
    elif parse_result["modifier"] == "d":
        rolls = sorted(rolls)[parse_result["modifier_value"]:]

    return sum(rolls) + parse_result["bonus"]


def _apply_explode(rolls, sides, target, random_func):
    """递归应用爆炸骰"""
    result = rolls.copy()
    for roll in rolls:
        if roll == target:
            extra = random_func(1, sides)
            result.append(extra)
            if extra == target:  # 递归爆炸
                result.extend(_apply_explode(
                    [extra], sides, target, random_func))
    return result


def get_dice_info(expr):
    result = parse_dice(expr)
    info = {
        "expr": expr,
        "dice_count": 0,
        "total_sides": 0,
        "has_modifier": False,
        "has_explode": False,
    }

    for part in result["parts"]:
        if part["type"] == "dice":
            info["dice_count"] += part["count"]
            info["total_sides"] += part["sides"] * part["count"]
            if part["modifier"]:
                info["has_modifier"] = True
            if part["explode"]:
                info["has_explode"] = True

    return info
