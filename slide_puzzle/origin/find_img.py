import cv2
import numpy as np
import os

def find_block_positions(image_path, target_color, grid_size=6, exclude_color=None):
    # 检查文件是否存在
    if not os.path.exists(image_path):
        print(f"错误：文件 '{image_path}' 不存在。")
        return None

    # 读取图像
    img = cv2.imread(image_path)
    
    # 检查图像是否成功加载
    if img is None:
        print(f"错误：无法加载图像 '{image_path}'。")
        return None
    # 图像的宽度和高度
    width = img.shape[1]
    height = img.shape[0]

    # 添加图像预处理步骤
    img = cv2.GaussianBlur(img, (5, 5), 0)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    # 根据目标颜色设置 HSV 范围
    lower_color = np.array(target_color[0])
    upper_color = np.array(target_color[1])
    # 创建掩码
    mask = cv2.inRange(hsv, lower_color, upper_color)
    # 只有当目标颜色是黄色时才调整HSV范围
    if target_color == ([20, 100, 100], [30, 255, 255]):
        # 调整黄色的HSV范围
        lower_yellow = np.array([20, 100, 100])
        upper_yellow = np.array([30, 255, 255])
        
        mask = cv2.inRange(hsv, lower_yellow, upper_yellow)

    # 保存掩码图像
    print(f"正在保存掩码: {target_color}")
    # 微微增加浅绿色的范围
    if target_color == ([40, 150, 100], [80, 255, 255]):  # 绿色
        lower_green = np.array([38, 140, 100])  # 稍微降低下限
        upper_green = np.array([82, 255, 255])  # 稍微提高上限
        mask = cv2.inRange(hsv, lower_green, upper_green)
    if target_color == ([40, 150, 100], [80, 255, 255]):  # 绿色
        cv2.imwrite('img/green_mask.png', mask)
    elif target_color == ([0, 150, 150], [10, 255, 255]):  # 红色
        cv2.imwrite('img/red_mask.png', mask)
    elif target_color == ([20, 100, 100], [30, 255, 255]):  # 金色
        cv2.imwrite('img/gold_mask.png', mask)

    # 在find_block_positions函数中添加形态学操作
    kernel = np.ones((3,3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    # 使用RETR_EXTERNAL和CHAIN_APPROX_TC89_L1来检测所有轮廓
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_L1)

    print(f"图像尺寸: {img.shape}")
    print(f"掩码中非零像素数: {np.count_nonzero(mask)}")
    print(f"检测到的轮廓数: {len(contours)}")
    
    blocks = []
    cell_width = img.shape[1] // grid_size
    cell_height = img.shape[0] // grid_size
    
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        
        # 计算网格索引
        grid_x = x // cell_width
        grid_y = y // cell_height
        
        # 计算占据的网格数量
        grid_w = (x + w - 1) // cell_width - grid_x + 1
        grid_h = (y + h - 1) // cell_height - grid_y + 1
        
        # 检查每个占据的网格中的像素数量
        valid_cells = []
        for i in range(grid_w):
            for j in range(grid_h):
                cell_x = (grid_x + i) * cell_width
                cell_y = (grid_y + j) * cell_height
                cell_mask = mask[cell_y:cell_y+cell_height, cell_x:cell_x+cell_width]
                hit_pixels = np.count_nonzero(cell_mask)
                total_pixels = cell_width * cell_height
                hit_percentage = (hit_pixels / total_pixels) * 100
                if hit_percentage >= 10:
                    valid_cells.append((grid_x + i, grid_y + j))
                    print(f"命中单元格: ({grid_x + i}, {grid_y + j}), 命中像素百分比: {hit_percentage:.2f}%")
                else:
                    if target_color == ([20, 100, 100], [30, 255, 255]):  # 金色
                        if hit_percentage > 3:
                            valid_cells.append((grid_x + i, grid_y + j))
                            print(f"命中单元格: ({grid_x + i}, {grid_y + j}), 命中像素百分比: {hit_percentage:.2f}%")
        
        # 如果有有效的单元格,添加到块列表中
        if valid_cells:
            min_x = min(cell[0] for cell in valid_cells)
            min_y = min(cell[1] for cell in valid_cells)
            max_x = max(cell[0] for cell in valid_cells)
            max_y = max(cell[1] for cell in valid_cells)
            
            if target_color != [(20, 100, 100), (30, 255, 255)]:
                # 只为红色和绿色块检查边界
                is_left_edge = check_edge(mask, min_x, min_y, max_y, cell_width, cell_height, is_horizontal=True, is_start=True)
                is_right_edge = check_edge(mask, max_x, min_y, max_y, cell_width, cell_height, is_horizontal=True, is_start=False)
                is_top_edge = check_edge(mask, min_x, min_y, max_x, cell_width, cell_height, is_horizontal=False, is_start=True)
                is_bottom_edge = check_edge(mask, min_x, max_y, max_x, cell_width, cell_height, is_horizontal=False, is_start=False)
                blocks.append((min_x, min_y, max_x - min_x + 1, max_y - min_y + 1, is_left_edge, is_right_edge, is_top_edge, is_bottom_edge))
            else:
                # 金色块使用原来的处理方式
                blocks.append((min_x, min_y, max_x - min_x + 1, max_y - min_y + 1))

    return blocks

def check_edge(mask, x, y_start, y_end, cell_width, cell_height, is_horizontal, is_start):
    if is_horizontal:
        check_width = cell_width // 7
        check_x = x * cell_width + (0 if is_start else 6 * check_width)
        check_area = mask[y_start*cell_height:(y_end+1)*cell_height, check_x:check_x+check_width]
    else:
        check_height = cell_height // 7
        check_y = y_start * cell_height + (0 if is_start else 6 * check_height)
        check_area = mask[check_y:check_y+check_height, x*cell_width:(y_end+1)*cell_width]
    
    hit_percentage = (np.count_nonzero(check_area) / check_area.size) * 100
    return hit_percentage < 49

def merge_and_deduplicate_blocks(blocks, is_horizontal, is_gold=False):
    merged = []
    sorted_blocks = sorted(blocks, key=lambda b: (b[1], b[0]) if is_horizontal else (b[0], b[1]))
    
    for block in sorted_blocks:
        if not merged:
            merged.append(block)
        else:
            last = merged[-1]
            if is_horizontal:
                if block[1] == last[1] and block[0] == last[0] + last[2]:
                    # 只有当两个块在y轴上相同，并且在x轴上相邻时才合并
                    merged[-1] = (last[0], last[1], last[2] + block[2], last[3], last[4], block[5], last[6], last[7])
                else:
                    merged.append(block)
            else:
                if block[0] == last[0] and block[1] == last[1] + last[3]:
                    # 只有当两个块在x轴上相同，并且在y轴上相邻时才合并
                    merged[-1] = (last[0], last[1], last[2], last[3] + block[3], last[4], last[5], last[6], block[7])
                else:
                    merged.append(block)
    
    # 对于金色块，我们需要特殊处理
    if is_gold and len(merged) > 1:
        # 如果有多个金色块，我们只保留最大的一个
        largest_block = max(merged, key=lambda b: b[2] * b[3])
        merged = [largest_block]
    
    return merged

def process_image(image_path):
    # 定义颜色范围
    green_target_color_hsv = ([40, 150, 100], [80, 255, 255])
    red_target_color_hsv = ([0, 150, 150], [10, 255, 255])
    gold_target_color_hsv = ([20, 100, 100], [30, 255, 255])

    # 查找方块位置
    green_positions = find_block_positions(image_path, green_target_color_hsv)
    red_positions = find_block_positions(image_path, red_target_color_hsv)
    gold_positions = find_block_positions(image_path, gold_target_color_hsv)

    blocks = []

    # 处理绿色方块
    if green_positions:
        green_positions = merge_and_deduplicate_blocks(green_positions, is_horizontal=True)
        blocks.extend([(x, y, 'GREEN', w, h, 'horizontal') for x, y, w, h, _, _, _, _ in green_positions])

    # 处理红色方块
    if red_positions:
        red_positions = merge_and_deduplicate_blocks(red_positions, is_horizontal=False)
        blocks.extend([(x, y, 'RED', w, h, 'vertical') for x, y, w, h, _, _, _, _ in red_positions])

    # 处理金色方块
    if gold_positions:
        gold_positions = merge_and_deduplicate_blocks(gold_positions, is_horizontal=True, is_gold=True)
        if gold_positions:  # 确保有金色块
            x, y, w, h = gold_positions[0][:4]  # 只取第一个（也是唯一的）金色块
            blocks.append((x, y, 'GOLD', w, h, 'horizontal'))

    # 去除重复的块
    unique_blocks = []
    for block in blocks:
        if block not in unique_blocks:
            unique_blocks.append(block)

    # 打印统计信息
    print(f"绿色块数量: {len([b for b in unique_blocks if b[2] == 'GREEN'])}")
    print(f"红色块数量: {len([b for b in unique_blocks if b[2] == 'RED'])}")
    print(f"金色块数量: {len([b for b in unique_blocks if b[2] == 'GOLD'])}")

    return unique_blocks

# 切换到代码文件所在目录
os.chdir(os.path.dirname(os.path.abspath(__file__)))
print("当前工作目录:", os.getcwd())

# 示例使用
image_path = "img/sekuai.png"
result = process_image(image_path)
print(result)
