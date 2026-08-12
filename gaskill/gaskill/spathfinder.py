from .svector import vec2
from .srandom import Random


# ========== A* 寻路算法 ==========

def _heuristic(a, b, method='manhattan'):
    """计算启发式距离"""
    dx = abs(a[0] - b[0])
    dy = abs(a[1] - b[1])

    if method == 'manhattan':
        return dx + dy
    elif method == 'euclidean':
        return (dx**2 + dy**2) ** 0.5
    elif method == 'chebyshev':
        return max(dx, dy)
    elif method == 'octile':
        return max(dx, dy) + (1.41421356 - 1) * min(dx, dy)
    else:
        return dx + dy


def astar(grid, start, end, heuristic='manhattan', allow_diagonal=False):
    """A* 寻路算法 - 启发式最短路径搜索"""
    start = (int(start[0]), int(start[1]))
    end = (int(end[0]), int(end[1]))

    if not _is_passable(grid, start) or not _is_passable(grid, end):
        return None

    open_set = [start]
    came_from = {start: None}

    g_score = {start: 0}
    f_score = {start: _heuristic(start, end, heuristic)}

    while open_set:
        current = min(open_set, key=lambda x: f_score.get(x, float('inf')))

        if current == end:
            return _reconstruct_path(came_from, start, end)

        open_set.remove(current)

        x, y = current

        if allow_diagonal:
            neighbors = [
                (x+1, y), (x-1, y), (x, y+1), (x, y-1),
                (x+1, y+1), (x+1, y-1), (x-1, y+1), (x-1, y-1)
            ]
        else:
            neighbors = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]

        for neighbor in neighbors:
            if not _is_passable(grid, neighbor):
                continue

            dx = abs(neighbor[0] - current[0])
            dy = abs(neighbor[1] - current[1])

            if allow_diagonal and dx == 1 and dy == 1:
                move_cost = 1.41421356
            else:
                move_cost = 1

            tentative_g = g_score[current] + move_cost

            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score[neighbor] = tentative_g + \
                    _heuristic(neighbor, end, heuristic)

                if neighbor not in open_set:
                    open_set.append(neighbor)

    return None


def astar_weighted(grid, start, end, weight=1.0, heuristic='manhattan', allow_diagonal=False):
    """加权 A*算法 - 通过权重平衡速度和最优性"""
    start = (int(start[0]), int(start[1]))
    end = (int(end[0]), int(end[1]))

    if not _is_passable(grid, start) or not _is_passable(grid, end):
        return None

    open_set = [start]
    came_from = {start: None}

    g_score = {start: 0}
    f_score = {start: g_score[start] + weight *
               _heuristic(start, end, heuristic)}

    while open_set:
        current = min(open_set, key=lambda x: f_score.get(x, float('inf')))

        if current == end:
            return _reconstruct_path(came_from, start, end)

        open_set.remove(current)

        x, y = current

        if allow_diagonal:
            neighbors = [
                (x+1, y), (x-1, y), (x, y+1), (x, y-1),
                (x+1, y+1), (x+1, y-1), (x-1, y+1), (x-1, y-1)
            ]
        else:
            neighbors = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]

        for neighbor in neighbors:
            if not _is_passable(grid, neighbor):
                continue

            dx = abs(neighbor[0] - current[0])
            dy = abs(neighbor[1] - current[1])

            if allow_diagonal and dx == 1 and dy == 1:
                move_cost = 1.41421356
            else:
                move_cost = 1

            tentative_g = g_score[current] + move_cost

            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score[neighbor] = tentative_g + weight * \
                    _heuristic(neighbor, end, heuristic)

                if neighbor not in open_set:
                    open_set.append(neighbor)

    return None


# ========== Dijkstra 算法 ==========

def dijkstra(grid, start, end, weights=None, allow_diagonal=False):
    """Dijkstra 算法 - 带权图的最短路径"""
    start = (int(start[0]), int(start[1]))
    end = (int(end[0]), int(end[1]))

    if not _is_passable(grid, start) or not _is_passable(grid, end):
        return None

    open_set = [start]
    came_from = {start: None}
    dist = {start: 0}

    while open_set:
        current = min(open_set, key=lambda x: dist.get(x, float('inf')))

        if current == end:
            return _reconstruct_path(came_from, start, end)

        open_set.remove(current)

        x, y = current

        if allow_diagonal:
            neighbors = [
                (x+1, y), (x-1, y), (x, y+1), (x, y-1),
                (x+1, y+1), (x+1, y-1), (x-1, y+1), (x-1, y-1)
            ]
        else:
            neighbors = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]

        for neighbor in neighbors:
            if not _is_passable(grid, neighbor):
                continue

            dx = abs(neighbor[0] - current[0])
            dy = abs(neighbor[1] - current[1])

            if weights and neighbor in weights:
                move_cost = weights[neighbor]
            elif allow_diagonal and dx == 1 and dy == 1:
                move_cost = 1.41421356
            else:
                move_cost = 1

            new_dist = dist[current] + move_cost

            if neighbor not in dist or new_dist < dist[neighbor]:
                came_from[neighbor] = current
                dist[neighbor] = new_dist

                if neighbor not in open_set:
                    open_set.append(neighbor)

    return None


# ========== 双向 BFS ==========

def bidirectional_bfs(grid, start, end):
    """双向 BFS 寻路 - 从起点和终点同时搜索"""
    start = (int(start[0]), int(start[1]))
    end = (int(end[0]), int(end[1]))

    if not _is_passable(grid, start) or not _is_passable(grid, end):
        return None

    forward_queue = [start]
    backward_queue = [end]

    forward_visited = {start: None}
    backward_visited = {end: None}

    meeting_point = None

    while forward_queue and backward_queue:
        if forward_queue:
            current = forward_queue.pop(0)

            if current in backward_visited:
                meeting_point = current
                break

            x, y = current
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                neighbor = (x + dx, y + dy)

                if _is_passable(grid, neighbor) and neighbor not in forward_visited:
                    forward_visited[neighbor] = current
                    forward_queue.append(neighbor)

        if backward_queue:
            current = backward_queue.pop(0)

            if current in forward_visited:
                meeting_point = current
                break

            x, y = current
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                neighbor = (x + dx, y + dy)

                if _is_passable(grid, neighbor) and neighbor not in backward_visited:
                    backward_visited[neighbor] = current
                    backward_queue.append(neighbor)

    if meeting_point is None:
        return None

    path = []
    current = meeting_point
    while current is not None:
        path.append(current)
        current = forward_visited.get(current)
    path.reverse()

    current = backward_visited.get(meeting_point)
    while current is not None:
        path.append(current)
        current = backward_visited.get(current)

    return [vec2(x, y) for x, y in path]


def bfs(grid, start, end):
    """广度优先搜索寻路 - 保证最短路径"""
    # 转成元组好处理
    start = (int(start[0]), int(start[1]))
    end = (int(end[0]), int(end[1]))

    # 检查起点终点
    if not _is_passable(grid, start) or not _is_passable(grid, end):
        return None

    # 手动实现队列：列表 + 头尾指针
    queue = [start]          # 队列
    queue_head = 0           # 队头指针

    # 记录路径
    came_from = {start: None}

    # BFS主循环
    while queue_head < len(queue):
        current = queue[queue_head]
        queue_head += 1

        # 到达终点
        if current == end:
            return _reconstruct_path(came_from, start, end)

        x, y = current
        # 4方向探索
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            neighbor = (nx, ny)

            # 如果可走且没访问过
            if _is_passable(grid, neighbor) and neighbor not in came_from:
                came_from[neighbor] = current
                queue.append(neighbor)

    return None  # 没找到路径


def dfs_maker(width, height, start=(1, 1), seed=None):
    """深度优先搜索生成迷宫"""
    # 确保尺寸为奇数（保证墙壁厚度）
    random = Random(seed)
    if width % 2 == 0:
        width += 1
    if height % 2 == 0:
        height += 1

    # 初始化全墙迷宫
    maze = [[1 for _ in range(width)] for _ in range(height)]

    # 起点
    sx, sy = start
    maze[sy][sx] = 0

    # 栈
    stack = [(sx, sy)]

    # 方向（每次移动2格，保持墙壁厚度）
    dirs = [(0, 2), (2, 0), (0, -2), (-2, 0)]

    while stack:
        x, y = stack[-1]

        # 找未访问的邻居
        neighbors = []
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if (0 < nx < width-1 and 0 < ny < height-1 and
                    maze[ny][nx] == 1):
                neighbors.append((nx, ny, dx//2, dy//2))

        if neighbors:
            # 随机选一个邻居
            nx, ny, wx, wy = random.choice(neighbors)

            # 打通墙壁和邻居
            maze[y + wy][x + wx] = 0  # 中间的墙
            maze[ny][nx] = 0           # 邻居格子

            stack.append((nx, ny))
        else:
            # 回溯
            stack.pop()

    return maze


def _is_passable(grid, pos):
    """检查位置是否可通行"""
    x, y = pos
    if y < 0 or y >= len(grid) or x < 0 or x >= len(grid[0]):
        return False
    return grid[y][x] == 0


def _get_cost(cost_grid, pos):
    """获取位置的移动成本（-1表示不可通行，0表示无成本）"""
    x, y = pos
    if y < 0 or y >= len(cost_grid) or x < 0 or x >= len(cost_grid[0]):
        return float('inf')
    cost = cost_grid[y][x]
    if cost == -1:
        return float('inf')
    return max(0.0, float(cost))


def _reconstruct_path(came_from, start, end):
    """重建路径"""
    path = []
    current = end

    while current != start:
        path.append(current)
        current = came_from[current]

    path.append(start)
    path.reverse()

    # 转成vec2列表
    return [vec2(x, y) for x, y in path]


# ========== 成本网络寻路算法 ==========

def astar_cost(cost_grid, start, end, heuristic='manhattan', allow_diagonal=False):
    """A* 算法 - 支持成本网络（2维矩阵）输入"""
    start = (int(start[0]), int(start[1]))
    end = (int(end[0]), int(end[1]))

    start_cost = _get_cost(cost_grid, start)
    end_cost = _get_cost(cost_grid, end)

    if start_cost == float('inf') or end_cost == float('inf'):
        return None

    open_set = [start]
    came_from = {start: None}

    g_score = {start: 0}
    f_score = {start: _heuristic(start, end, heuristic)}

    while open_set:
        current = min(open_set, key=lambda x: f_score.get(x, float('inf')))

        if current == end:
            return _reconstruct_path(came_from, start, end)

        open_set.remove(current)

        x, y = current

        if allow_diagonal:
            neighbors = [
                (x+1, y), (x-1, y), (x, y+1), (x, y-1),
                (x+1, y+1), (x+1, y-1), (x-1, y+1), (x-1, y-1)
            ]
        else:
            neighbors = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]

        for neighbor in neighbors:
            move_cost = _get_cost(cost_grid, neighbor)
            if move_cost == float('inf'):
                continue

            dx = abs(neighbor[0] - current[0])
            dy = abs(neighbor[1] - current[1])

            # 对角线移动额外成本
            if allow_diagonal and dx == 1 and dy == 1:
                move_cost *= 1.41421356

            tentative_g = g_score[current] + move_cost

            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score[neighbor] = tentative_g + \
                    _heuristic(neighbor, end, heuristic)

                if neighbor not in open_set:
                    open_set.append(neighbor)

    return None


def dijkstra_cost(cost_grid, start, end, allow_diagonal=False):
    """Dijkstra 算法 - 支持成本网络（2维矩阵）输入"""
    start = (int(start[0]), int(start[1]))
    end = (int(end[0]), int(end[1]))

    start_cost = _get_cost(cost_grid, start)
    end_cost = _get_cost(cost_grid, end)

    if start_cost == float('inf') or end_cost == float('inf'):
        return None

    open_set = [start]
    came_from = {start: None}
    dist = {start: 0}

    while open_set:
        current = min(open_set, key=lambda x: dist.get(x, float('inf')))

        if current == end:
            return _reconstruct_path(came_from, start, end)

        open_set.remove(current)

        x, y = current

        if allow_diagonal:
            neighbors = [
                (x+1, y), (x-1, y), (x, y+1), (x, y-1),
                (x+1, y+1), (x+1, y-1), (x-1, y+1), (x-1, y-1)
            ]
        else:
            neighbors = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]

        for neighbor in neighbors:
            move_cost = _get_cost(cost_grid, neighbor)
            if move_cost == float('inf'):
                continue

            dx = abs(neighbor[0] - current[0])
            dy = abs(neighbor[1] - current[1])

            # 对角线移动额外成本
            if allow_diagonal and dx == 1 and dy == 1:
                move_cost *= 1.41421356

            new_dist = dist[current] + move_cost

            if neighbor not in dist or new_dist < dist[neighbor]:
                came_from[neighbor] = current
                dist[neighbor] = new_dist

                if neighbor not in open_set:
                    open_set.append(neighbor)

    return None


def get_path_cost(cost_grid, path, allow_diagonal=False):
    """计算路径的总成本"""
    if path is None or len(path) < 2:
        return 0.0

    total_cost = 0.0

    for i in range(len(path) - 1):
        x1, y1 = int(path[i].x), int(path[i].y)
        x2, y2 = int(path[i+1].x), int(path[i+1].y)

        dx = abs(x2 - x1)
        dy = abs(y2 - y1)

        move_cost = _get_cost(cost_grid, (x2, y2))

        if allow_diagonal and dx == 1 and dy == 1:
            move_cost *= 1.41421356

        total_cost += move_cost

    return total_cost


def create_cost_grid(grid, default_cost=1.0, wall_cost=-1.0, custom_costs=None):
    """从二进制网格创建成本网格"""
    height = len(grid)
    width = len(grid[0]) if height > 0 else 0

    cost_grid = []
    for y in range(height):
        row = []
        for x in range(width):
            if grid[y][x] == 0:
                # 可通行区域
                if custom_costs and (x, y) in custom_costs:
                    row.append(custom_costs[(x, y)])
                else:
                    row.append(default_cost)
            else:
                # 障碍物
                row.append(wall_cost)
        cost_grid.append(row)

    return cost_grid


def _neighbors_4(x, y, w, h):
    """四方向邻居，返回列表"""
    result = []
    if x > 0:
        result.append((x - 1, y, 1.0))
    if x < w - 1:
        result.append((x + 1, y, 1.0))
    if y > 0:
        result.append((x, y - 1, 1.0))
    if y < h - 1:
        result.append((x, y + 1, 1.0))
    return result


def _neighbors_8(x, y, w, h):
    """八方向邻居，返回列表"""
    result = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h:
                cost = 1.4142135623730951 if (dx != 0 and dy != 0) else 1.0
                result.append((nx, ny, cost))
    return result


def _find_min_cost_idx(arr, vals):
    """在 vals 中找到最小值对应的 arr 索引"""
    min_idx = 0
    min_val = vals[0]
    for i in range(1, len(vals)):
        if vals[i] < min_val:
            min_val = vals[i]
            min_idx = i
    return min_idx


def compute_flow_field(grid, goals, allow_diagonal=True, cost_map=None):
    """计算流场 (Flow Field)"""
    h = len(grid)
    if h == 0:
        return [], []
    w = len(grid[0])
    if w == 0:
        return [], []

    # ====== 1. 初始化 ======
    INF = 1e18
    integration = [[INF] * w for _ in range(h)]
    visited = [[0] * w for _ in range(h)]

    # 障碍物标记为 -1
    for y in range(h):
        for x in range(w):
            if grid[y][x] != 0:
                integration[y][x] = -1

    # 目标点入队（成本为 0）
    queue_x = []
    queue_y = []
    for gx, gy in goals:
        if 0 <= gx < w and 0 <= gy < h and grid[gy][gx] == 0:
            if integration[gy][gx] > 0:
                integration[gy][gx] = 0
                queue_x.append(gx)
                queue_y.append(gy)

    if not queue_x:
        return [], []

    # ====== 2. Dijkstra 计算积分场 ======
    head = 0
    while head < len(queue_x):
        x = queue_x[head]
        y = queue_y[head]
        head += 1

        if visited[y][x]:
            continue
        visited[y][x] = 1

        cur_cost = integration[y][x]

        # 获取邻居
        if allow_diagonal:
            neighbors = _neighbors_8(x, y, w, h)
        else:
            neighbors = _neighbors_4(x, y, w, h)

        for nx, ny, move_cost in neighbors:
            if grid[ny][nx] != 0:
                continue

            # 地形额外成本
            terrain_cost = 1.0
            if cost_map is not None:
                key = (nx, ny)
                # 手动遍历字典（避免依赖 dict.get）
                for k, v in cost_map:
                    if k[0] == nx and k[1] == ny:
                        terrain_cost = v
                        break

            new_cost = cur_cost + move_cost * terrain_cost

            if new_cost < integration[ny][nx]:
                integration[ny][nx] = new_cost
                queue_x.append(nx)
                queue_y.append(ny)

    # ====== 3. 生成流场 ======
    flow_field = [[(0.0, 0.0)] * w for _ in range(h)]

    for y in range(h):
        for x in range(w):
            if grid[y][x] != 0:
                continue

            cur = integration[y][x]
            if cur >= INF:
                continue

            # 如果本身就是目标，方向为零
            if cur == 0:
                flow_field[y][x] = (0.0, 0.0)
                continue

            # 找邻居中积分值最小的方向
            if allow_diagonal:
                neighbors = _neighbors_8(x, y, w, h)
            else:
                neighbors = _neighbors_4(x, y, w, h)

            best_dx = 0
            best_dy = 0
            best_cost = cur

            for nx, ny, _ in neighbors:
                if grid[ny][nx] != 0:
                    continue
                nc = integration[ny][nx]
                if nc < best_cost:
                    best_cost = nc
                    best_dx = nx - x
                    best_dy = ny - y

            # 归一化方向向量
            if best_dx != 0 or best_dy != 0:
                length = (best_dx * best_dx + best_dy * best_dy) ** 0.5
                flow_field[y][x] = (best_dx / length, best_dy / length)
            else:
                flow_field[y][x] = (0.0, 0.0)

    return flow_field, integration


def get_flow_direction(flow_field, x, y):
    """获取某个格子的流向"""
    if y < 0 or y >= len(flow_field):
        return (0.0, 0.0)
    if x < 0 or x >= len(flow_field[0]):
        return (0.0, 0.0)
    return flow_field[y][x]


def move_toward_flow(flow_field, x, y, speed):
    """按照流场移动一个单位"""
    gx = int(x)
    gy = int(y)

    # 边界检查
    if gy < 0 or gy >= len(flow_field):
        return (x, y)
    if gx < 0 or gx >= len(flow_field[0]):
        return (x, y)

    dx, dy = flow_field[gy][gx]

    if dx == 0 and dy == 0:
        return (x, y)

    return (x + dx * speed, y + dy * speed)


def visualize_flow_field(flow_field, symbols=None):
    """可视化流场（用于调试）"""
    if not flow_field:
        return ""

    if symbols is None:
        symbols = {
            (1, 0): "→",
            (-1, 0): "←",
            (0, 1): "↓",
            (0, -1): "↑",
            (1, 1): "↘",
            (-1, 1): "↙",
            (1, -1): "↗",
            (-1, -1): "↖",
            (0, 0): "·",
        }

    h = len(flow_field)
    w = len(flow_field[0])

    lines = []
    for y in range(h):
        row = []
        for x in range(w):
            dx, dy = flow_field[y][x]

            # 找最近的符号方向
            best_key = (0, 0)
            best_dist = 1e18
            for key in symbols:
                if key == (0, 0):
                    continue
                dist = (key[0] - dx) ** 2 + (key[1] - dy) ** 2
                if dist < best_dist:
                    best_dist = dist
                    best_key = key

            row.append(symbols.get(best_key, "·"))
        lines.append("".join(row))

    return "\n".join(lines)


def sample_flow_path(flow_field, start_x, start_y, steps=100):
    """采样一条从起点沿流场移动的路径"""
    path = [(float(start_x), float(start_y))]
    x, y = float(start_x), float(start_y)

    for _ in range(steps):
        nx, ny = move_toward_flow(flow_field, x, y, 1.0)
        # 如果没动，停止
        if abs(nx - x) < 0.001 and abs(ny - y) < 0.001:
            break
        x, y = nx, ny
        path.append((x, y))

    return path
