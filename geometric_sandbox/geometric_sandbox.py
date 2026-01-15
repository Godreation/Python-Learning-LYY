import math
import random
import time
import pygame
import sys

class GeometricSandbox:
    def __init__(self, width=800, height=600, num_particles=100):
        self.width = width
        self.height = height
        self.num_particles = num_particles
        
        # 物理参数
        self.gravity_strength = 0.5
        self.mouse_repel_strength = 2.0
        self.damping = 0.98
        self.boundary_stiffness = 0.1
        
        # 模拟状态
        self.particles = []
        self.mouse_pos = [width // 2, height // 2]
        self.paused = False
        self.running = True
        
        # 性能统计
        self.frame_count = 0
        self.start_time = time.perf_counter()
        
        # 初始化Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("几何物理沙盒模拟器")
        self.clock = pygame.time.Clock()
        
        # 颜色定义
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.RED = (255, 0, 0)
        self.BLUE = (0, 0, 255)
        self.GREEN = (0, 255, 0)
        self.YELLOW = (255, 255, 0)
        
        # 初始化粒子
        self._init_particles()
    
    def _init_particles(self):
        """初始化粒子系统"""
        self.particles = []
        for _ in range(self.num_particles):
            x = random.uniform(50, self.width - 50)
            y = random.uniform(50, self.height - 50)
            vx = random.uniform(-1, 1)
            vy = random.uniform(-1, 1)
            
            self.particles.append({
                'x': x, 'y': y,
                'vx': vx, 'vy': vy
            })
    
    def _calculate_distance(self, x1, y1, x2, y2):
        """计算两点间距离"""
        return math.hypot(x2 - x1, y2 - y1)
    
    def _apply_gravity(self, particle):
        """应用中心引力"""
        center_x, center_y = self.width // 2, self.height // 2
        dx = center_x - particle['x']
        dy = center_y - particle['y']
        distance = self._calculate_distance(particle['x'], particle['y'], center_x, center_y)
        
        if distance > 0.1:
            force_factor = self.gravity_strength / (distance ** 3 + 0.1)
            particle['vx'] += dx * force_factor
            particle['vy'] += dy * force_factor
    
    def _apply_mouse_force(self, particle):
        """应用鼠标斥力"""
        dx = particle['x'] - self.mouse_pos[0]
        dy = particle['y'] - self.mouse_pos[1]
        distance = self._calculate_distance(particle['x'], particle['y'], 
                                           self.mouse_pos[0], self.mouse_pos[1])
        
        if distance < 50 and distance > 0.1:
            force_factor = self.mouse_repel_strength / (distance ** 2 + 0.1)
            particle['vx'] += dx * force_factor
            particle['vy'] += dy * force_factor
    
    def _apply_boundary_forces(self, particle):
        """应用边界斥力"""
        boundary = 50
        
        # 左边界
        if particle['x'] < boundary:
            force = self.boundary_stiffness / ((particle['x'] - boundary + 10.1) ** 2)
            particle['vx'] += force
        
        # 右边界
        if particle['x'] > self.width - boundary:
            force = self.boundary_stiffness / ((self.width - boundary - particle['x'] + 10.1) ** 2)
            particle['vx'] -= force
        
        # 上边界
        if particle['y'] < boundary:
            force = self.boundary_stiffness / ((particle['y'] - boundary + 10.1) ** 2)
            particle['vy'] += force
        
        # 下边界
        if particle['y'] > self.height - boundary:
            force = self.boundary_stiffness / ((self.height - boundary - particle['y'] + 10.1) ** 2)
            particle['vy'] -= force
    
    def _handle_particle_collisions(self):
        """处理粒子间碰撞"""
        # 简化碰撞检测，减少计算量
        for i in range(len(self.particles)):
            for j in range(i + 1, len(self.particles)):
                p1 = self.particles[i]
                p2 = self.particles[j]
                
                distance = self._calculate_distance(p1['x'], p1['y'], p2['x'], p2['y'])
                
                if distance < 10:
                    # 一维弹性碰撞简化版
                    p1['vx'], p2['vx'] = p2['vx'], p1['vx']
                    p1['vy'], p2['vy'] = p2['vy'], p1['vy']
                    
                    # 轻微弹开
                    if distance > 0:
                        push_factor = (10 - distance) * 0.01
                        dx = p2['x'] - p1['x']
                        dy = p2['y'] - p1['y']
                        p1['vx'] -= dx * push_factor
                        p1['vy'] -= dy * push_factor
                        p2['vx'] += dx * push_factor
                        p2['vy'] += dy * push_factor
    
    def _update_particles(self, dt):
        """更新粒子状态"""
        for particle in self.particles:
            # 应用各种力
            self._apply_gravity(particle)
            self._apply_mouse_force(particle)
            self._apply_boundary_forces(particle)
            
            # 欧拉积分
            particle['x'] += particle['vx'] * dt
            particle['y'] += particle['vy'] * dt
            
            # 阻尼
            particle['vx'] *= self.damping
            particle['vy'] *= self.damping
        
        # 处理碰撞
        self._handle_particle_collisions()
    
    def _render_frame(self):
        """渲染一帧"""
        # 填充背景
        self.screen.fill(self.BLACK)
        
        # 绘制边界
        pygame.draw.rect(self.screen, (30, 30, 30), (50, 50, self.width - 100, self.height - 100), 1)
        
        # 绘制粒子
        for particle in self.particles:
            x, y = int(particle['x']), int(particle['y'])
            pygame.draw.circle(self.screen, self.WHITE, (x, y), 3)
        
        # 绘制中心吸引子
        center_x, center_y = self.width // 2, self.height // 2
        pygame.draw.circle(self.screen, self.YELLOW, (center_x, center_y), 8)
        
        # 绘制鼠标力源
        mouse_x, mouse_y = int(self.mouse_pos[0]), int(self.mouse_pos[1])
        pygame.draw.circle(self.screen, self.RED, (mouse_x, mouse_y), 10, 1)
        
        # 计算系统能量（动能）
        total_energy = sum(p['vx']**2 + p['vy']**2 for p in self.particles)
        
        # 计算帧率
        current_time = time.perf_counter()
        elapsed_time = current_time - self.start_time
        fps = self.frame_count / elapsed_time if elapsed_time > 0 else 0
        
        # 绘制状态信息
        try:
            # 尝试使用系统字体（支持中文）
            font = pygame.font.SysFont("SimHei", 36)
        except:
            # 如果系统字体不可用，使用默认字体
            font = pygame.font.Font(None, 36)
        status_text = font.render(f"帧率: {fps:.1f} | 粒子数: {len(self.particles)} | 能量: {total_energy:.0f}", True, self.WHITE)
        self.screen.blit(status_text, (10, 10))
        
        # 绘制控制说明
        try:
            # 尝试使用系统字体（支持中文）
            control_font = pygame.font.SysFont("SimHei", 24)
        except:
            # 如果系统字体不可用，使用默认字体
            control_font = pygame.font.Font(None, 24)
        control_text = control_font.render("空格:暂停/继续 | R:重置 | A/Z:引力 | Q:退出", True, self.WHITE)
        self.screen.blit(control_text, (10, self.height - 30))
        
        # 更新显示
        pygame.display.flip()
        
        self.frame_count += 1
    
    def _handle_input(self):
        """处理输入"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif event.key == pygame.K_r:
                    self._init_particles()
                elif event.key == pygame.K_a:
                    self.gravity_strength = min(2.0, self.gravity_strength + 0.1)
                elif event.key == pygame.K_z:
                    self.gravity_strength = max(0.1, self.gravity_strength - 0.1)
                elif event.key == pygame.K_q:
                    self.running = False
            elif event.type == pygame.MOUSEMOTION:
                self.mouse_pos = list(event.pos)
    
    def run(self):
        """主运行循环"""
        while self.running:
            # 处理输入
            self._handle_input()
            
            # 更新物理
            if not self.paused:
                dt = 1.0 / 60.0  # 固定时间步长
                self._update_particles(dt)
            
            # 渲染
            self._render_frame()
            
            # 控制帧率
            self.clock.tick(60)
        
        # 退出Pygame
        pygame.quit()

def main():
    """主函数"""
    try:
        width, height = 800, 600
        num_particles = random.randint(50, 200)
        
        sandbox = GeometricSandbox(width, height, num_particles)
        sandbox.run()
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()