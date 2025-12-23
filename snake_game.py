import pygame
import sys
import random

# 初始化Pygame
pygame.init()

# 游戏参数设置
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
GAME_WIDTH = 600
GAME_HEIGHT = 400
GRID_SIZE = 20
FPS = 10  # 降低帧数以减慢蛇的移动速度

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)
DARK_GREEN = (0, 150, 0)

# 创建游戏窗口
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("贪吃蛇游戏")

# 设置字体 - 使用支持中文的系统字体
font = pygame.font.SysFont("SimHei", 36)
small_font = pygame.font.SysFont("SimHei", 24)

# 创建时钟对象
clock = pygame.time.Clock()

# 游戏区域位置
GAME_X = (WINDOW_WIDTH - GAME_WIDTH) // 2
GAME_Y = (WINDOW_HEIGHT - GAME_HEIGHT) // 2

# 蛇类
class Snake:
    def __init__(self):
        # 初始化蛇的位置和长度
        self.length = 3
        self.positions = [(GAME_WIDTH // 2, GAME_HEIGHT // 2)]
        self.direction = random.choice([pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT])
        self.next_direction = self.direction
        self.color = GREEN
        self.head_color = DARK_GREEN
        
        # 计算初始身体位置
        x, y = self.positions[0]
        for i in range(1, self.length):
            if self.direction == pygame.K_UP:
                self.positions.append((x, y + i * GRID_SIZE))
            elif self.direction == pygame.K_DOWN:
                self.positions.append((x, y - i * GRID_SIZE))
            elif self.direction == pygame.K_LEFT:
                self.positions.append((x + i * GRID_SIZE, y))
            elif self.direction == pygame.K_RIGHT:
                self.positions.append((x - i * GRID_SIZE, y))
    
    def change_direction(self, new_direction):
        # 防止蛇直接反向移动
        if new_direction == pygame.K_UP and self.direction != pygame.K_DOWN:
            self.next_direction = new_direction
        elif new_direction == pygame.K_DOWN and self.direction != pygame.K_UP:
            self.next_direction = new_direction
        elif new_direction == pygame.K_LEFT and self.direction != pygame.K_RIGHT:
            self.next_direction = new_direction
        elif new_direction == pygame.K_RIGHT and self.direction != pygame.K_LEFT:
            self.next_direction = new_direction
    
    def move(self):
        # 更新当前方向
        self.direction = self.next_direction
        
        # 获取蛇头位置
        head_x, head_y = self.positions[0]
        
        # 计算新的蛇头位置
        if self.direction == pygame.K_UP:
            new_head = (head_x, head_y - GRID_SIZE)
        elif self.direction == pygame.K_DOWN:
            new_head = (head_x, head_y + GRID_SIZE)
        elif self.direction == pygame.K_LEFT:
            new_head = (head_x - GRID_SIZE, head_y)
        elif self.direction == pygame.K_RIGHT:
            new_head = (head_x + GRID_SIZE, head_y)
        
        # 更新蛇的位置
        self.positions.insert(0, new_head)
        
        # 如果没有吃到食物，移除尾部
        if len(self.positions) > self.length:
            self.positions.pop()
    
    def grow(self):
        # 增加蛇的长度
        self.length += 1
    
    def draw(self):
        # 绘制蛇头
        head_x, head_y = self.positions[0]
        pygame.draw.rect(window, self.head_color, 
                         (GAME_X + head_x, GAME_Y + head_y, GRID_SIZE, GRID_SIZE))
        
        # 绘制蛇身
        for position in self.positions[1:]:
            x, y = position
            pygame.draw.rect(window, self.color, 
                             (GAME_X + x, GAME_Y + y, GRID_SIZE, GRID_SIZE))
    
    def get_head_position(self):
        # 返回蛇头位置
        return self.positions[0]
    
    def check_collision(self):
        # 检查是否碰撞边界
        head_x, head_y = self.positions[0]
        if head_x < 0 or head_x >= GAME_WIDTH or head_y < 0 or head_y >= GAME_HEIGHT:
            return True
        
        # 检查是否碰撞自身
        for position in self.positions[1:]:
            if position == self.positions[0]:
                return True
        
        return False

# 食物类
class Food:
    def __init__(self):
        self.position = (0, 0)
        self.color = RED
        self.randomize_position()
    
    def randomize_position(self, snake_positions=None):
        # 在游戏区域内随机生成食物位置（避免边界两格范围）
        grid_width = GAME_WIDTH // GRID_SIZE
        grid_height = GAME_HEIGHT // GRID_SIZE
        
        # 边界两格的安全范围
        min_grid = 2
        max_grid_x = grid_width - 3
        max_grid_y = grid_height - 3
        
        # 确保安全范围有效
        if min_grid > max_grid_x or min_grid > max_grid_y:
            # 如果游戏区域太小，使用默认范围
            min_grid = 0
            max_grid_x = grid_width - 1
            max_grid_y = grid_height - 1
        
        valid_position = False
        while not valid_position:
            # 随机生成网格位置（避开边界两格）
            grid_x = random.randint(min_grid, max_grid_x)
            grid_y = random.randint(min_grid, max_grid_y)
            
            # 转换为游戏区域坐标
            self.position = (grid_x * GRID_SIZE, grid_y * GRID_SIZE)
            
            # 检查是否与蛇的身体重叠
            if snake_positions:
                valid_position = self.position not in snake_positions
            else:
                valid_position = True
    
    def draw(self):
        # 绘制食物
        x, y = self.position
        pygame.draw.rect(window, self.color, 
                         (GAME_X + x, GAME_Y + y, GRID_SIZE, GRID_SIZE))
    
    def get_position(self):
        # 返回食物位置
        return self.position

# 绘制游戏界面

def draw_game_interface():
    # 填充背景
    window.fill(BLACK)
    
    # 绘制游戏区域边框
    pygame.draw.rect(window, WHITE, (GAME_X - 5, GAME_Y - 5, GAME_WIDTH + 10, GAME_HEIGHT + 10), 2)
    
    # 绘制游戏区域
    pygame.draw.rect(window, GRAY, (GAME_X, GAME_Y, GAME_WIDTH, GAME_HEIGHT))

# 绘制分数

def draw_score(score):
    score_text = font.render(f"分数: {score}", True, WHITE)
    window.blit(score_text, (20, 20))

# 绘制控制说明

def draw_controls():
    controls = [
        "方向键: 控制蛇的移动",
        "空格键: 暂停/继续游戏",
        "R键: 重新开始游戏",
        "ESC键: 退出游戏"
    ]
    
    for i, control in enumerate(controls):
        text = small_font.render(control, True, WHITE)
        window.blit(text, (20, WINDOW_HEIGHT - 100 + i * 25))

# 主游戏循环
def main():
    # 初始化游戏
    snake = Snake()
    food = Food()
    score = 0
    game_over = False
    paused = False
    
    running = True
    
    while running:
        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    # 暂停/继续游戏
                    if not game_over:
                        paused = not paused
                elif event.key == pygame.K_r:
                    # 重新开始游戏
                    snake = Snake()
                    food = Food()
                    score = 0
                    game_over = False
                    paused = False
                elif not game_over and not paused:
                    # 改变蛇的方向
                    snake.change_direction(event.key)
        
        # 绘制游戏界面
        draw_game_interface()
        
        if not game_over:
            if not paused:
                # 移动蛇
                snake.move()
                
                # 检查碰撞
                if snake.check_collision():
                    game_over = True
                
                # 检查是否吃到食物
                if snake.get_head_position() == food.get_position():
                    snake.grow()
                    score += 10
                    # 生成新的食物位置，避免与蛇身重叠
                    food.randomize_position(snake.positions)
            
            # 绘制蛇和食物
            snake.draw()
            food.draw()
            
            if paused:
                pause_text = font.render("游戏暂停", True, WHITE)
                window.blit(pause_text, (GAME_X + GAME_WIDTH // 2 - 80, GAME_Y + GAME_HEIGHT // 2))
        else:
            # 显示游戏结束信息
            game_over_text = font.render("游戏结束", True, RED)
            restart_text = small_font.render("按 R 键重新开始", True, WHITE)
            window.blit(game_over_text, (GAME_X + GAME_WIDTH // 2 - 80, GAME_Y + GAME_HEIGHT // 2 - 30))
            window.blit(restart_text, (GAME_X + GAME_WIDTH // 2 - 90, GAME_Y + GAME_HEIGHT // 2 + 10))
        
        # 绘制分数
        draw_score(score)
        
        # 绘制控制说明
        draw_controls()
        
        # 更新显示
        pygame.display.flip()
        
        # 控制游戏帧率
        clock.tick(FPS)

# 运行游戏
if __name__ == "__main__":
    main()
    pygame.quit()
    sys.exit()