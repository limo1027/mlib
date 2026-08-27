# sfsm.py - 有限状态机模块


class State:
    """状态基类"""

    def __init__(self, name):
        """初始化状态"""
        self.name = name
        self.state_machine = None

    def enter(self, old_state):
        """进入状态时调用"""
        pass

    def exit(self, new_state):
        """离开状态时调用"""
        pass

    def update(self, dt):
        """状态更新"""
        pass

    def handle_event(self, event):
        """处理事件"""
        return None

    def __repr__(self):
        return f"State({self.name})"


class StateMachine:
    """有限状态机"""

    def __init__(self, initial_state=None):
        """初始化状态机"""
        self._states = {}
        self._current_state = None
        self._previous_state = None
        self._is_locked = False

        if initial_state:
            self.add_state(initial_state)
            self.set_state(initial_state.name)

    def add_state(self, state):
        """添加状态"""
        state.state_machine = self
        self._states[state.name] = state

    def remove_state(self, state_name):
        """移除状态"""
        if state_name in self._states:
            del self._states[state_name]

    def set_state(self, state_name):
        """设置当前状态"""
        if self._is_locked:
            return False

        if state_name not in self._states:
            return False

        if self._current_state:
            self._current_state.exit(state_name)

        self._previous_state = self._current_state
        self._current_state = self._states[state_name]

        if self._current_state:
            self._current_state.enter(self._previous_state)

        return True

    def update(self, dt):
        """更新状态机"""
        if self._current_state:
            self._current_state.update(dt)

    def handle_event(self, event):
        """处理事件"""
        if not self._current_state:
            return False

        target_state = self._current_state.handle_event(event)

        if target_state and target_state in self._states:
            return self.set_state(target_state)

        return False

    def transition_to(self, state_name):
        """切换到状态"""
        return self.set_state(state_name)

    def revert_to_previous(self):
        """回到上一个状态"""
        if self._previous_state:
            return self.set_state(self._previous_state.name)
        return False

    def lock(self):
        """锁定状态机（禁止状态切换）"""
        self._is_locked = True

    def unlock(self):
        """解锁状态机"""
        self._is_locked = False

    @property
    def current_state(self):
        """当前状态"""
        return self._current_state

    @property
    def current_state_name(self):
        """当前状态名称"""
        return self._current_state.name if self._current_state else None

    @property
    def previous_state(self):
        """上一个状态"""
        return self._previous_state

    @property
    def states(self):
        """所有状态"""
        return self._states.copy()

    def has_state(self, state_name):
        """检查是否包含状态"""
        return state_name in self._states

    def clear(self):
        """清空所有状态"""
        self._states.clear()
        self._current_state = None
        self._previous_state = None
        self._is_locked = False

    def __repr__(self):
        state_name = self._current_state.name if self._current_state else "None"
        return f"StateMachine(current={state_name}, states={len(self._states)})"


class FunctionState(State):
    """函数式状态 - 使用回调函数定义行为"""

    def __init__(self, name, on_enter=None, on_exit=None, on_update=None, on_event=None):
        """初始化函数式状态"""
        super().__init__(name)
        self._on_enter = on_enter
        self._on_exit = on_exit
        self._on_update = on_update
        self._on_event = on_event

    def enter(self, old_state):
        if self._on_enter:
            self._on_enter(old_state)

    def exit(self, new_state):
        if self._on_exit:
            self._on_exit(new_state)

    def update(self, dt):
        if self._on_update:
            self._on_update(dt)

    def handle_event(self, event):
        if self._on_event:
            return self._on_event(event)
        return None


class StateTransition:
    """状态转换表 - 定义状态之间的转换规则"""

    def __init__(self):
        """初始化状态转换表"""
        self._transitions = {}

    def add_transition(self, from_state, to_state, condition=None):
        """添加状态转换"""
        if from_state not in self._transitions:
            self._transitions[from_state] = []

        self._transitions[from_state].append({
            "to": to_state,
            "condition": condition,
        })

    def get_transition(self, from_state, context=None):
        """获取可转换的目标状态"""
        if from_state not in self._transitions:
            return None

        for transition in self._transitions[from_state]:
            condition = transition["condition"]
            if condition is None or condition(context):
                return transition["to"]

        return None

    def clear(self):
        """清空转换表"""
        self._transitions.clear()

    def __repr__(self):
        return f"StateTransition(transitions={len(self._transitions)})"
