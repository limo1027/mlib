# sevent.py - 事件系统模块


class EventSystem:
    """事件系统类"""

    def __init__(self, dt=0.016):
        """初始化事件系统"""
        self.dt = dt
        self._listeners = {}
        self._once_listeners = {}
        self._times_listeners = {}
        self._conditional_listeners = {}
        self._delayed_events = []
        self._listener_id_counter = 0

    def _generate_id(self):
        """生成唯一的监听器 ID"""
        self._listener_id_counter += 1
        return self._listener_id_counter

    def on(self, event_name, handler):
        """永久监听事件"""
        if event_name not in self._listeners:
            self._listeners[event_name] = {}
        listener_id = self._generate_id()
        self._listeners[event_name][listener_id] = handler
        return listener_id

    def once(self, event_name, handler):
        """只运行一次的事件监听"""
        if event_name not in self._once_listeners:
            self._once_listeners[event_name] = {}
        listener_id = self._generate_id()
        self._once_listeners[event_name][listener_id] = {
            "handler": handler,
            "active": True,
        }
        return listener_id

    def times(self, count, event_name, handler):
        """运行固定次数后自动移除"""
        if event_name not in self._times_listeners:
            self._times_listeners[event_name] = {}
        listener_id = self._generate_id()
        self._times_listeners[event_name][listener_id] = {
            "handler": handler,
            "remaining": count,
            "total": count,
            "active": True,
        }
        return listener_id

    def when(self, event_name, condition, handler):
        """条件触发的事件监听"""
        if event_name not in self._conditional_listeners:
            self._conditional_listeners[event_name] = {}
        listener_id = self._generate_id()
        self._conditional_listeners[event_name][listener_id] = {
            "condition": condition,
            "handler": handler,
            "active": True,
        }
        return listener_id

    def wheel_once(self, event_name, condition, handler):
        """条件触发，只运行一次后自动移除"""
        if event_name not in self._conditional_listeners:
            self._conditional_listeners[event_name] = {}
        listener_id = self._generate_id()
        self._conditional_listeners[event_name][listener_id] = {
            "condition": condition,
            "handler": handler,
            "active": True,
            "once": True,
        }
        return listener_id

    def delay(self, delay_time, event_name, handler):
        """延迟触发事件"""
        listener_id = self._generate_id()
        self._delayed_events.append({
            "id": listener_id,
            "event_name": event_name,
            "handler": handler,
            "remaining_time": delay_time,
            "original_delay": delay_time,
            "triggered": False,
            "active": True,
        })
        return listener_id

    def emit(self, event_name, *args, **kwargs):
        """触发事件"""
        # 触发永久监听器
        if event_name in self._listeners:
            for handler in self._listeners[event_name].values():
                handler(*args, **kwargs)

        # 触发 once 监听器，然后标记为 inactive
        if event_name in self._once_listeners:
            for _listener_id, data in self._once_listeners[event_name].items():
                if data["active"]:
                    data["handler"](*args, **kwargs)
                    data["active"] = False

        # 触发 times 监听器
        if event_name in self._times_listeners:
            for _listener_id, data in self._times_listeners[event_name].items():
                if data["active"]:
                    data["handler"](*args, **kwargs)
                    data["remaining"] -= 1
                    if data["remaining"] <= 0:
                        data["active"] = False

        # 触发条件监听器
        if event_name in self._conditional_listeners:
            for _listener_id, data in self._conditional_listeners[event_name].items():
                try:
                    if data["active"] and data["condition"](*args, **kwargs):
                        data["handler"](*args, **kwargs)
                        # wheel_once 触发后自动标记为 inactive
                        if data.get("once", False):
                            data["active"] = False
                except Exception:
                    pass

    def update(self, dt=None):
        """更新事件系统（处理延迟事件）"""
        if dt is None:
            dt = self.dt

        # 处理延迟事件
        for event in self._delayed_events:
            if not event["triggered"] and event["active"]:
                event["remaining_time"] -= dt
                if event["remaining_time"] <= 0:
                    event["triggered"] = True
                    event["active"] = False
                    event["handler"]()

    def remove(self, event_name, listener_id):
        """移除指定的监听器"""
        if event_name in self._listeners:
            if listener_id in self._listeners[event_name]:
                del self._listeners[event_name][listener_id]
                return True

        if event_name in self._once_listeners:
            if listener_id in self._once_listeners[event_name]:
                del self._once_listeners[event_name][listener_id]
                return True

        if event_name in self._times_listeners:
            if listener_id in self._times_listeners[event_name]:
                del self._times_listeners[event_name][listener_id]
                return True

        if event_name in self._conditional_listeners:
            if listener_id in self._conditional_listeners[event_name]:
                del self._conditional_listeners[event_name][listener_id]
                return True

        return False

    def redo(self, event_name, listener_id):
        """重新激活监听器"""
        # 重新激活 once 监听器
        if event_name in self._once_listeners:
            if listener_id in self._once_listeners[event_name]:
                self._once_listeners[event_name][listener_id]["active"] = True
                return True

        # 重新激活 times 监听器
        if event_name in self._times_listeners:
            if listener_id in self._times_listeners[event_name]:
                data = self._times_listeners[event_name][listener_id]
                data["active"] = True
                data["remaining"] = data["total"]
                return True

        # 重新激活延迟事件
        for event in self._delayed_events:
            if event["id"] == listener_id and event["event_name"] == event_name:
                event["active"] = True
                event["triggered"] = False
                event["remaining_time"] = event["original_delay"]
                return True

        # 重新激活 wheel_once 监听器
        if event_name in self._conditional_listeners:
            if listener_id in self._conditional_listeners[event_name]:
                self._conditional_listeners[event_name][listener_id]["active"] = True
                return True

        return False

    def clear(self, event_name=None):
        """清除监听器"""
        if event_name is None:
            self._listeners = {}
            self._once_listeners = {}
            self._times_listeners = {}
            self._conditional_listeners = {}
            self._delayed_events = []
        else:
            if event_name in self._listeners:
                del self._listeners[event_name]
            if event_name in self._once_listeners:
                del self._once_listeners[event_name]
            if event_name in self._times_listeners:
                del self._times_listeners[event_name]
            if event_name in self._conditional_listeners:
                del self._conditional_listeners[event_name]
            self._delayed_events = [e for e in self._delayed_events if e["event_name"] != event_name]


event = EventSystem()
