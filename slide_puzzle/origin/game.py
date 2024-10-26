import pygame
import sys
from collections import deque
import time
import os
# 打印当前目录
print(os.getcwd())
from find_img import process_image

# 初始化Pygame
pygame.init()

# 设置颜色
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GOLD = (255, 215, 0)

# 设置屏幕
WIDTH, HEIGHT = 600, 600
GRID_SIZE = 6  # 从 5 改为 6
CELL_SIZE = WIDTH // GRID_SIZE

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("方块迷宫游戏")

# 定义游戏对象
class Block:
    def __init__(self, x, y, color, width=1, height=1, move_direction='both'):
        self.x = x
        self.y = y
        self.color = color
        self.width = width
        self.height = height
        self.dragging = False
        self.offset_x = 0
        self.offset_y = 0
        self.move_direction = move_direction  # 'horizontal', 'vertical', 或 'both'

    def draw(self):
        # 绘制填充的矩形
        pygame.draw.rect(screen, self.color, (int(self.x * CELL_SIZE), int(self.y * CELL_SIZE), 
                         CELL_SIZE * self.width, CELL_SIZE * self.height))
        # 绘制白色边框
        pygame.draw.rect(screen, (255, 255, 255), (int(self.x * CELL_SIZE), int(self.y * CELL_SIZE), 
                         CELL_SIZE * self.width, CELL_SIZE * self.height), 2)

    def is_point_inside(self, x, y):
        return (self.x * CELL_SIZE <= x < (self.x + self.width) * CELL_SIZE and
                self.y * CELL_SIZE <= y < (self.y + self.height) * CELL_SIZE)

    def start_drag(self, mouse_x, mouse_y):
        self.dragging = True
        self.offset_x = mouse_x - self.x * CELL_SIZE
        self.offset_y = mouse_y - self.y * CELL_SIZE

    def end_drag(self):
        self.dragging = False
        self.x = round(self.x)
        self.y = round(self.y)

    def drag(self, mouse_x, mouse_y, other_blocks):
        if self.dragging:
            new_x = (mouse_x - self.offset_x) / CELL_SIZE
            new_y = (mouse_y - self.offset_y) / CELL_SIZE
            
            if self.move_direction == 'horizontal' or self.move_direction == 'both':
                if 0 <= new_x <= GRID_SIZE - self.width:
                    temp_x = new_x
                    if not self.check_collision(temp_x, self.y, other_blocks):
                        self.x = temp_x
            
            if self.move_direction == 'vertical' or self.move_direction == 'both':
                if 0 <= new_y <= GRID_SIZE - self.height:
                    temp_y = new_y
                    if not self.check_collision(self.x, temp_y, other_blocks):
                        self.y = temp_y

    def check_collision(self, new_x, new_y, other_blocks):
        for block in other_blocks:
            if block != self:
                if (new_x < block.x + block.width and
                    new_x + self.width > block.x and
                    new_y < block.y + block.height and
                    new_y + self.height > block.y):
                    return True
        return False

# 获取方块信息
image_path = "img/sekuai.png"
block_data = process_image(image_path)

# 初始化游戏对象
blocks = []
key = None

for x, y, color, width, height, move_direction in block_data:
    if color == 'GREEN':
        block = Block(x, y, GREEN, width, height, move_direction)
        blocks.append(block)
    elif color == 'RED':
        block = Block(x, y, RED, width, height, move_direction)
        blocks.append(block)
    elif color == 'GOLD':
        key = Block(x, y, GOLD, width, height, move_direction)

if key is None:
    key = Block(0, 2, GOLD, 2, 1, 'horizontal')  # 如果没有检测到金钥匙，使用默认值

# 添加全局变量
solution = None
current_step = 0
last_move_time = 0

def get_solution(blocks, key):
    initial_state = tuple((b.x, b.y) for b in blocks + [key])
    queue = deque([(initial_state, [])])
    visited = set([initial_state])

    while queue:
        state, path = queue.popleft()
        key_pos = state[-1]

        if key_pos[0] + key.width >= GRID_SIZE:
            return path

        for i, (x, y) in enumerate(state):
            block = blocks[i] if i < len(blocks) else key
            
            if block.move_direction in ['horizontal', 'both']:
                for dx in [-1, 1]:
                    new_x = x + dx
                    if 0 <= new_x <= GRID_SIZE - block.width:
                        new_state = list(state)
                        new_state[i] = (new_x, y)
                        new_state = tuple(new_state)
                        if new_state not in visited and not check_collision(new_state, blocks + [key]):
                            visited.add(new_state)
                            new_path = path + [(i, 'left' if dx == -1 else 'right')]
                            queue.append((new_state, new_path))

            if block.move_direction in ['vertical', 'both']:
                for dy in [-1, 1]:
                    new_y = y + dy
                    if 0 <= new_y <= GRID_SIZE - block.height:
                        new_state = list(state)
                        new_state[i] = (x, new_y)
                        new_state = tuple(new_state)
                        if new_state not in visited and not check_collision(new_state, blocks + [key]):
                            visited.add(new_state)
                            new_path = path + [(i, 'up' if dy == -1 else 'down')]
                            queue.append((new_state, new_path))

    return None  # 没有找到解决方案

def check_collision(state, blocks):
    for i, (x1, y1) in enumerate(state):
        block1 = blocks[i]
        for j, (x2, y2) in enumerate(state):
            if i != j:
                block2 = blocks[j]
                if (x1 < x2 + block2.width and x1 + block1.width > x2 and
                    y1 < y2 + block2.height and y1 + block1.height > y2):
                    return True
    return False

def get_solution_hint(blocks, key):
    global solution
    solution = get_solution(blocks, key)
    if solution is None:
        return "无法找到解决方案。"

    hint = "解题步骤：\n"
    for i, (block_index, direction) in enumerate(solution):
        block = blocks[block_index] if block_index < len(blocks) else key
        block_type = "红色块" if block.color == RED else "绿色块" if block.color == GREEN else "金钥匙"
        hint += f"{i+1}. 将位于 ({block.x}, {block.y}) 的{block_type}向{direction}移动\n"

    return hint

def move_block(block, direction):
    if direction == 'left':
        block.x -= 1
    elif direction == 'right':
        block.x += 1
    elif direction == 'up':
        block.y -= 1
    elif direction == 'down':
        block.y += 1

# 主游戏循环
running = True
selected_block = None
game_won = False
auto_solve = False

while running:
    current_time = time.time()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and not game_won and not auto_solve:  # 左键点击，且游戏未胜利，且不在自动解题中
                for block in blocks + [key]:
                    if block.is_point_inside(event.pos[0], event.pos[1]):
                        selected_block = block
                        block.start_drag(event.pos[0], event.pos[1])
                        break
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and selected_block:
                selected_block.end_drag()
                selected_block = None
        elif event.type == pygame.MOUSEMOTION:
            if selected_block and not auto_solve:
                selected_block.drag(event.pos[0], event.pos[1], blocks + [key])
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_h:  # 按 'H' 键显示提示并开始自动解题
                hint = get_solution_hint(blocks, key)
                print(hint)
                auto_solve = True
                current_step = 0
                last_move_time = current_time

    # 自动解题
    if auto_solve and solution and current_step < len(solution):
        if current_time - last_move_time >= 0.2:  # 每秒执行一步
            block_index, direction = solution[current_step]
            block = blocks[block_index] if block_index < len(blocks) else key
            move_block(block, direction)
            current_step += 1
            last_move_time = current_time
            
            if current_step == len(solution):
                auto_solve = False
                print("自动解题完成！")

    # 检查游戏是否胜利
    if key.x + key.width >= GRID_SIZE:
        game_won = True
        auto_solve = False

    # 绘制背景
    screen.fill(BLACK)

    # 绘制网格线
    for i in range(GRID_SIZE + 1):
        pygame.draw.line(screen, (50, 50, 50), (i * CELL_SIZE, 0), (i * CELL_SIZE, HEIGHT))
        pygame.draw.line(screen, (50, 50, 50), (0, i * CELL_SIZE), (WIDTH, i * CELL_SIZE))

    # 绘制所有方块
    for block in blocks + [key]:
        block.draw()

    # 绘制出口
    pygame.draw.polygon(screen, GOLD, [(WIDTH - 20, HEIGHT // 2 - 20), 
                                       (WIDTH, HEIGHT // 2), 
                                       (WIDTH - 20, HEIGHT // 2 + 20)])

    # 如果游戏胜利，显示胜利消息
    if game_won:
        font = pygame.font.Font(None, 74)
        text = font.render('success!', True, (255, 255, 255))
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(text, text_rect)

    pygame.display.flip()

pygame.quit()
sys.exit()
