import pygame
import sys
import random
from collections import deque

# 初始化Pygame
pygame.init()

# 定义颜色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GOLD = (255, 215, 0)

# 设置游戏窗口
WIDTH, HEIGHT = 600, 600
GRID_SIZE = 6
CELL_SIZE = WIDTH // GRID_SIZE
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("滑块拼图游戏")

class Block:
    def __init__(self, x, y, color, width, height, orientation):
        self.x = x
        self.y = y
        self.color = color
        self.width = width
        self.height = height
        self.orientation = orientation
        self.rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, width * CELL_SIZE, height * CELL_SIZE)
        self.drag_offset = (0, 0)

    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)

    def move(self, dx, dy):
        new_x = self.x + dx
        new_y = self.y + dy
        if 0 <= new_x <= GRID_SIZE - self.width and 0 <= new_y <= GRID_SIZE - self.height:
            self.x = new_x
            self.y = new_y
            self.rect.x = self.x * CELL_SIZE
            self.rect.y = self.y * CELL_SIZE

    def drag(self, mouse_x, mouse_y, all_blocks):
        new_x = (mouse_x - self.drag_offset[0]) / CELL_SIZE
        new_y = (mouse_y - self.drag_offset[1]) / CELL_SIZE
        
        if self.orientation == 'horizontal':
            dx = new_x - self.x
            if abs(dx) >= 0.5:  # 增加移动阈值
                move_amount = round(dx)
                if is_valid_move(self, move_amount, 0, all_blocks):
                    self.x += move_amount
                    self.rect.x = int(self.x * CELL_SIZE)
        else:  # vertical
            dy = new_y - self.y
            if abs(dy) >= 0.5:  # 增加移动阈值
                move_amount = round(dy)
                if is_valid_move(self, 0, move_amount, all_blocks):
                    self.y += move_amount
                    self.rect.y = int(self.y * CELL_SIZE)

    def get_state(self):
        return (self.x, self.y)

    def set_state(self, state):
        self.x, self.y = state
        self.rect.x = self.x * CELL_SIZE
        self.rect.y = self.y * CELL_SIZE

# 创建方块
blocks = [
    Block(3, 0, GREEN, 3, 1, 'horizontal'),
    Block(0, 3, GREEN, 2, 1, 'horizontal'),
    Block(2, 4, GREEN, 2, 1, 'horizontal'),
    Block(2, 5, GREEN, 3, 1, 'horizontal'),
    Block(0, 0, RED, 1, 2, 'vertical'),
    Block(0, 4, RED, 1, 2, 'vertical'),
    Block(1, 4, RED, 1, 2, 'vertical'),
    Block(2, 1, RED, 1, 2, 'vertical'),
    Block(3, 1, RED, 1, 2, 'vertical'),
    Block(4, 2, RED, 1, 3, 'vertical'),
    Block(5, 1, RED, 1, 3, 'vertical'),
    Block(0, 2, GOLD, 2, 1, 'horizontal')
]

# 在创建方块列表后，保存初始状态
initial_block_states = [block.get_state() for block in blocks]

def draw_grid():
    for x in range(0, WIDTH, CELL_SIZE):
        pygame.draw.line(screen, BLACK, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, CELL_SIZE):
        pygame.draw.line(screen, BLACK, (0, y), (WIDTH, y))

def is_valid_move(block, dx, dy, all_blocks):
    new_x = block.x + dx
    new_y = block.y + dy
    new_rect = pygame.Rect(int(new_x * CELL_SIZE), int(new_y * CELL_SIZE), 
                           block.rect.width, block.rect.height)
    if new_rect.left < 0 or new_rect.right > WIDTH or new_rect.top < 0 or new_rect.bottom > HEIGHT:
        return False
    for other_block in all_blocks:
        if other_block != block and new_rect.colliderect(other_block.rect):
            return False
    return True

def get_possible_moves(block, all_blocks):
    moves = []
    if block.orientation == 'horizontal':
        for dx in [-1, 1]:
            if is_valid_move(block, dx, 0, all_blocks):
                moves.append((dx, 0))
    else:
        for dy in [-1, 1]:
            if is_valid_move(block, 0, dy, all_blocks):
                moves.append((0, dy))
    return moves

def is_solved(blocks):
    gold_block = next(block for block in blocks if block.color == GOLD)
    return gold_block.x == 4 and gold_block.y == 2

def get_state(blocks):
    return tuple(block.get_state() for block in blocks)

def set_state(blocks, state):
    for block, block_state in zip(blocks, state):
        block.set_state(block_state)

def solve_puzzle(blocks):
    initial_state = get_state(blocks)
    queue = deque([(initial_state, [])])
    visited = set([initial_state])

    while queue:
        current_state, path = queue.popleft()

        if is_solved_state(current_state):
            return path

        for i, block_state in enumerate(current_state):
            block = blocks[i]
            for dx, dy in get_possible_moves_state(block_state, block.orientation, block.width, block.height, current_state):
                new_block_state = (block_state[0] + dx, block_state[1] + dy)
                new_state = list(current_state)
                new_state[i] = new_block_state
                new_state = tuple(new_state)
                
                if new_state not in visited:
                    new_path = path + [(i, dx, dy)]
                    queue.append((new_state, new_path))
                    visited.add(new_state)

    return None  # 如果没有找到解决方案

def is_solved_state(state):
    gold_block_state = state[11]  # 假设金块是第12个方块（索引11）
    return gold_block_state == (4, 2)

def get_possible_moves_state(block_state, orientation, width, height, all_states):
    moves = []
    x, y = block_state
    if orientation == 'horizontal':
        for dx in [-1, 1]:
            if is_valid_move_state((x+dx, y), block_state, orientation, width, height, all_states):
                moves.append((dx, 0))
    else:
        for dy in [-1, 1]:
            if is_valid_move_state((x, y+dy), block_state, orientation, width, height, all_states):
                moves.append((0, dy))
    return moves

def is_valid_move_state(new_pos, old_pos, orientation, width, height, all_states):
    x, y = new_pos
    old_x, old_y = old_pos
    if x < 0 or x + width > GRID_SIZE or y < 0 or y + height > GRID_SIZE:
        return False
    
    # 检查新位置是否与其他方块重叠
    for i, state in enumerate(all_states):
        if state == old_pos:  # 跳过当前方块
            continue
        other_x, other_y = state
        other_block = blocks[i]
        if (x < other_x + other_block.width and x + width > other_x and
            y < other_y + other_block.height and y + height > other_y):
            return False
    return True

def apply_solution(solution):
    if solution:
        for block_index, dx, dy in solution:
            block = blocks[block_index]
            start_x, start_y = block.rect.x, block.rect.y
            end_x, end_y = start_x + dx * CELL_SIZE, start_y + dy * CELL_SIZE
            
            # 添加简单的动画效果
            for step in range(1, 11):  # 将移动分成10个步骤
                block.rect.x = start_x + (end_x - start_x) * step // 10
                block.rect.y = start_y + (end_y - start_y) * step // 10
                
                # 重新绘制屏幕
                screen.fill(WHITE)
                draw_grid()
                for b in blocks:
                    b.draw()
                pygame.display.flip()
                pygame.time.wait(50)  # 每一小步等待50毫秒
            
            block.x = block.rect.x // CELL_SIZE
            block.y = block.rect.y // CELL_SIZE
    else:
        print("没有找到解决方案")

def reset_game():
    for block, initial_state in zip(blocks, initial_block_states):
        block.set_state(initial_state)

selected_block = None
solving = False

# 游戏主循环
running = True
clock = pygame.time.Clock()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_h:  # 按下 'h' 键
                solution = solve_puzzle(blocks)
                apply_solution(solution)
            elif event.key == pygame.K_r:  # 按下 'r' 键
                reset_game()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左键点击
                for block in blocks:
                    if block.rect.collidepoint(event.pos):
                        selected_block = block
                        mouse_x, mouse_y = event.pos
                        offset_x = mouse_x - block.rect.x
                        offset_y = mouse_y - block.rect.y
                        block.drag_offset = (offset_x, offset_y)
                        break
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # 左键释放
                selected_block = None
        elif event.type == pygame.MOUSEMOTION:
            if selected_block:
                selected_block.drag(event.pos[0], event.pos[1], blocks)

    # 绘制背景
    screen.fill(WHITE)
    
    # 绘制网格
    draw_grid()
    
    # 绘制所有方块
    for block in blocks:
        block.draw()
    
    # 更新显示
    pygame.display.flip()

    clock.tick(60)  # 限制帧率为60FPS

pygame.quit()
sys.exit()
