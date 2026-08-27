from gaskill import ABC, Rect, abstractmethod

_render_handlers = {}


def draw(cmd_type):
    """装饰器：注册某种指令类型的渲染函数"""
    def decorator(func):
        _render_handlers[cmd_type] = func
        return func
    return decorator


def render_all(components):
    """渲染所有组件"""
    all_cmds = []
    for comp in components:
        cmds = comp.render()
        if cmds:
            for cmd in cmds:
                handler = _render_handlers.get(cmd["type"])
                if handler:
                    handler(cmd)
                all_cmds.append(cmd)
    return all_cmds


class UI(ABC):
    """UI 元素抽象基类"""

    def __init__(self, x, y, width, height):
        self.rect = Rect(x, y, width, height)
        self.visible = True

    @abstractmethod
    def render(self):
        """渲染（子类必须实现）"""
        pass

    def handle_event(self, event):
        """处理事件（可选实现）"""
        pass

    def config(self, **kwargs):
        for k, v in kwargs.items():
            if k in ("x", "y", "width", "height"):
                setattr(self.rect, k, v)
            elif hasattr(self, k):
                setattr(self, k, v)

    def destroy(self):
        """销毁元素"""
        self.visible = False

    def is_visible(self):
        return self.visible


class Label:
    """文本标签"""

    def __init__(self, x, y, width, height, text="", **kwargs):
        self.rect = Rect(x, y, width, height)
        self.text = text
        self.color = kwargs.get("color", (240, 240, 240))
        self.text_color = kwargs.get("text_color", (0, 0, 0))
        self.align = kwargs.get("align", "left")  # left/center/right
        self.visible = True

    def render(self):
        """返回绘制指令"""
        if not self.visible:
            return []

        cmds = []

        # 背景
        cmds.append({
            "type": "rect",
            "rect": self.rect,  # 直接传Rect对象
            "color": self.color,
        })

        # 文字位置计算
        text_x = self.rect.x + 5  # 默认 left
        if self.align == "center":
            text_x = self.rect.x + (self.rect.w - len(self.text) * 8) // 2
        elif self.align == "right":
            text_x = self.rect.right - len(self.text) * 8 - 5

        cmds.append({
            "type": "text",
            "text": self.text,
            "x": text_x,
            "y": self.rect.y + (self.rect.h - 12) // 2,
            "color": self.text_color,
        })

        return cmds

    def destroy(self):
        self.visible = False

    def config(self, **kwargs):
        for k, v in kwargs.items():
            if k in ("x", "y", "width", "height"):
                setattr(self.rect, k, v)
            elif hasattr(self, k):
                setattr(self, k, v)

    def enter(self, mouse_x, mouse_y):
        """鼠标是否进入"""
        return self.rect.collide_point(mouse_x, mouse_y)


class Button:
    """按钮"""

    def __init__(self, x, y, width, height, text="", **kwargs):
        self.rect = Rect(x, y, width, height)
        self.text = text
        self.color = kwargs.get("color", (200, 200, 200))
        self.hover_color = kwargs.get("hover_color", (220, 220, 220))
        self.press_color = kwargs.get("press_color", (160, 160, 160))
        self.text_color = kwargs.get("text_color", (0, 0, 0))
        self.border = kwargs.get("border", True)
        self.radius = kwargs.get("radius", 3)
        self.visible = True

        # 状态
        self.hover = False
        self.pressed = False

    def render(self):
        """返回绘制指令"""
        if not self.visible:
            return []

        cmds = []

        # 根据状态选颜色
        if self.pressed:
            bg = self.press_color
        elif self.hover:
            bg = self.hover_color
        else:
            bg = self.color

        # 背景
        cmds.append({
            "type": "rect",
            "rect": self.rect,
            "color": bg,
            "radius": self.radius,
        })

        # 边框
        if self.border:
            cmds.append({
                "type": "outline",
                "rect": self.rect,
                "color": (100, 100, 100),
                "radius": self.radius,
            })

        # 文字（居中）
        text_x = self.rect.x + (self.rect.w - len(self.text) * 8) // 2
        text_y = self.rect.y + (self.rect.h - 12) // 2
        cmds.append({
            "type": "text",
            "text": self.text,
            "x": text_x,
            "y": text_y,
            "color": self.text_color,
        })

        return cmds

    def destroy(self):
        """销毁组件"""
        self.visible = False

    def config(self, **kwargs):
        """设置组件参数"""
        for k, v in kwargs.items():
            if k in ("x", "y", "width", "height"):
                setattr(self.rect, k, v)
            elif hasattr(self, k):
                setattr(self, k, v)

    def handle_event(self, mouse_pos, keys):
        """更新悬停状态并返回是否进入"""
        self.hover = self.rect.collide_point(mouse_pos[0], mouse_pos[1])
        return self.hover

    def press(self):
        """按下"""
        self.pressed = True

    def release(self):
        """释放"""
        self.pressed = False
        if self.hover:
            return True  # 点击完成
        return False


class Bar:
    """血量条/进度条"""

    def __init__(self, x, y, width, height, value=1.0, **kwargs):
        self.rect = Rect(x, y, width, height)
        self.value = max(0.0, min(1.0, value))  # 0-1
        self.bg_color = kwargs.get("bg_color", (60, 60, 60))
        self.fill_color = kwargs.get("fill_color", (255, 50, 50))
        self.text_color = kwargs.get("text_color", (255, 255, 255))
        self.show_text = kwargs.get("show_text", True)
        self.orientation = kwargs.get("orientation", "horizontal")
        self.visible = True

    def render(self):
        """返回绘制指令"""
        if not self.visible:
            return []

        cmds = []

        # 背景
        cmds.append({
            "type": "rect",
            "rect": self.rect,
            "color": self.bg_color,
        })

        # 填充部分
        if self.orientation == "horizontal":
            fill_rect = Rect(
                self.rect.x,
                self.rect.y,
                int(self.rect.w * self.value),
                self.rect.h,
            )
        else:  # 垂直
            fill_h = int(self.rect.h * self.value)
            fill_rect = Rect(
                self.rect.x,
                self.rect.y + self.rect.h - fill_h,
                self.rect.w,
                fill_h,
            )

        cmds.append({
            "type": "rect",
            "rect": fill_rect,
            "color": self.fill_color,
        })

        # 显示百分比
        if self.show_text:
            text = f"{int(self.value * 100)}%"
            text_x = self.rect.x + (self.rect.w - len(text) * 8) // 2
            text_y = self.rect.y + (self.rect.h - 12) // 2
            cmds.append({
                "type": "text",
                "text": text,
                "x": text_x,
                "y": text_y,
                "color": self.text_color,
            })

        return cmds

    def destroy(self):
        """销毁组件"""
        self.visible = False

    def config(self, **kwargs):
        """设置组件参数"""
        for k, v in kwargs.items():
            if k == "value":
                self.value = max(0.0, min(1.0, v))
            elif k in ("x", "y", "width", "height"):
                setattr(self.rect, k, v)
            elif hasattr(self, k):
                setattr(self, k, v)

    def enter(self, mouse_x, mouse_y):
        """鼠标是否进入"""
        return self.rect.collide_point(mouse_x, mouse_y)

    def set_hp(self, current, max_hp):
        """快捷设置血量"""
        self.value = current / max_hp


class Entry:
    """单行文本框"""

    def __init__(self, x, y, width, height, text="", **kwargs):
        self.rect = Rect(x, y, width, height)
        self.text = text
        self.placeholder = kwargs.get("placeholder", "")
        self.color = kwargs.get("color", (255, 255, 255))
        self.text_color = kwargs.get("text_color", (0, 0, 0))
        self.placeholder_color = kwargs.get(
            "placeholder_color", (150, 150, 150))
        self.border = kwargs.get("border", True)
        self.radius = kwargs.get("radius", 3)
        self.cursor_blink_tim = kwargs.get("cursor_blink_tim", 1000)
        self.visible = True
        self.capslock = False
        # 状态
        self.focused = False
        self.cursor_pos = len(text)  # 光标位置（字符索引）

        # 事件记忆
        self._last_keys = set()
        self._last_mouse_left = False
        self._time = 0

    def render(self):
        """返回绘制指令"""
        if not self.visible:
            return []

        cmds = []

        # 背景
        cmds.append({
            "type": "rect",
            "rect": self.rect,
            "color": self.color,
            "radius": self.radius,
        })

        # 边框
        if self.border:
            border_color = (100, 100, 200) if self.focused else (100, 100, 100)
            cmds.append({
                "type": "outline",
                "rect": self.rect,
                "color": border_color,
                "radius": self.radius,
                "width": 2 if self.focused else 1,
            })

        # 显示的文本
        display_text = self.text if self.text else self.placeholder
        text_color = self.text_color if self.text else self.placeholder_color

        # 计算文本起始 X（考虑内边距）
        padding = 5
        text_x = self.rect.x + padding

        # 如果有文本且光标不是最后，需要滚动显示
        visible_start = 0
        text_width = len(display_text) * 8  # 估算字符宽度

        if self.focused and self.cursor_pos > 0:
            # 简单滚动：光标保持在可见区域
            cursor_x = text_x + text_width
            if cursor_x > self.rect.right - padding:
                visible_start = (
                    cursor_x - (self.rect.right - padding)) // 8 + 1

        visible_text = display_text[visible_start:]
        visible_text = visible_text[:max(1, (self.rect.w - padding * 2) // 8)]

        cmds.append({
            "type": "text",
            "text": visible_text,
            "x": text_x,
            "y": self.rect.y + (self.rect.h - 12) // 2,
            "color": text_color,
        })

        # 光标（聚焦时显示）
        if self.focused and self._time % (2 * self.cursor_blink_tim) < self.cursor_blink_tim:
            cursor_x = text_x + (self.cursor_pos - visible_start) * 8
            cmds.append({
                "type": "rect",
                "rect": Rect(cursor_x, self.rect.y + 4, 2, self.rect.h - 8),
                "color": (0, 0, 0),
            })

        return cmds

    def handle_event(self, mouse_pos, keys, dt):
        """
        处理事件
        mouse_pos: (x, y) 鼠标的坐标(x坐标, y坐标)
        keys: 一个列表, 表示按下的按键
        """
        self._time += dt
        self._time = self._time % self.cursor_blink_tim
        if not self.visible:
            return False

        mouse_x, mouse_y = mouse_pos

        # 1. 鼠标点击聚焦/失焦
        mouse_left_pressed = "mouse_left" in keys
        if mouse_left_pressed and not self._last_mouse_left:
            was_focused = self.focused
            self.focused = self.rect.collide_point(mouse_x, mouse_y)

            if was_focused and not self.focused:
                return True  # 提交
            elif self.focused:
                click_x = mouse_x - (self.rect.x + 5)
                if click_x > 0:
                    self.cursor_pos = min(len(self.text), click_x // 8)
                else:
                    self.cursor_pos = 0

        self._last_mouse_left = mouse_left_pressed

        if not self.focused:
            return False

        # 2. 找出新按下的键
        new_keys = keys - self._last_keys

        for key in new_keys:
            if key == "left":
                self.cursor_pos = max(0, self.cursor_pos - 1)
            elif key == "right":
                self.cursor_pos = min(len(self.text), self.cursor_pos + 1)
            elif key == "home":
                self.cursor_pos = 0
            elif key == "end":
                self.cursor_pos = len(self.text)
            elif key == "CapsLock":
                self.capslock = not self.capslock
            elif key == "backspace":
                if self.cursor_pos > 0:
                    self.text = self.text[:self.cursor_pos -
                                          1] + self.text[self.cursor_pos:]
                    self.cursor_pos -= 1
            elif key == "delete":
                if self.cursor_pos < len(self.text):
                    self.text = self.text[:self.cursor_pos] + \
                        self.text[self.cursor_pos + 1:]
            elif key == "enter":
                self.focused = False
                return True
            elif len(key) == 1:
                shift = "shift" in keys
                char = key.upper() if (shift ^ self.capslock) else key.lower()
                self.text = self.text[:self.cursor_pos] + \
                    char + self.text[self.cursor_pos:]
                self.cursor_pos += 1
            elif key == "space":
                self.text = self.text[:self.cursor_pos] + \
                    " " + self.text[self.cursor_pos:]
                self.cursor_pos += 1

        self._last_keys = keys.copy()
        return False

    def destroy(self):
        """销毁组件"""
        self.visible = False

    def config(self, **kwargs):
        """设置组件参数"""
        for k, v in kwargs.items():
            if k in ("x", "y", "width", "height"):
                setattr(self.rect, k, v)
            elif hasattr(self, k):
                setattr(self, k, v)

    def enter(self, mouse_x, mouse_y):
        return self.rect.collide_point(mouse_x, mouse_y)
