import math
import random
import time
import os
import sys

class GeometricSandbox:
    def __init__(self, width=80, height=40, num_particles=100):
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
        
        # 初始化粒子
        self._init_particles()
        
        # 设置终端
        self._setup_terminal()
    
    def _init_particles(self):
        """初始化粒子系统"""
        self.particles = []
        for _ in range(self.num_particles):
            x = random.uniform(5, self.width - 5)
            y = random.uniform(5, self.height - 5)
            vx = random.uniform(-1, 1)
            vy = random.uniform(-1, 1)
            
            self.particles.append({
                'x': x, 'y': y,
                'vx': vx, 'vy': vy
            })
    
    def _setup_terminal(self):
        """设置终端显示参数"""
        os.system('cls' if os.name == 'nt' else 'clear')
        sys.stdout.write('\033[?25l')  # 隐藏光标
        sys.stdout.flush()
    
    def _cleanup_terminal(self):
        """恢复终端设置"""
        sys.stdout.write('\033[?25h')  # 显示光标
        sys.stdout.flush()
    
    def _calculate_distance(self, x1, y1, x2, y2):
        """计算两点间距离"""
        return math.hypot(x2 - x1, y2 - y1)
    
    def _apply_gravity(self, particle):
        """应用中心引力"""
        center_x, center_y = self.width // 2, self.height // 2
        dx = center_x - particle['x']
        dy = center_y - particle['y']
        distance = self._calculate_distance(particle['x'], particle['y'], center_x, center_y)
        
        if distance > 0.1:  # 避免除以零
            # 三维空间衰减：F = G * (中心 - 粒子位置) / r³
            force_factor = self.gravity_strength / (distance ** 3 + 0.1)
            particle['vx'] += dx * force_factor
            particle['vy'] += dy * force_factor
    
    def _apply_mouse_force(self, particle):
        """应用鼠标斥力"""
        dx = particle['x'] - self.mouse_pos[0]
        dy = particle['y'] - self.mouse_pos[1]
        distance = self._calculate_distance(particle['x'], particle['y'], 
                                           self.mouse_pos[0], self.mouse_pos[1])
        
        if distance < 15 and distance > 0.1:
            # F = 斥力强度 * (粒子 - 鼠标) / r²
            force_factor = self.mouse_repel_strength / (distance ** 2 + 0.1)
            particle['vx'] += dx * force_factor
            particle['vy'] += dy * force_factor
    
    def _apply_boundary_forces(self, particle):
        """应用边界斥力"""
        # 左边界
        if particle['x'] < 5:
            force = self.boundary_stiffness / ((particle['x'] + 0.1) ** 2)
            particle['vx'] += force
        
        # 右边界
        if particle['x'] > self.width - 5:
            force = self.boundary_stiffness / ((self.width - particle['x'] + 0.1) ** 2)
            particle['vx'] -= force
        
        # 上边界
        if particle['y'] < 5:
            force = self.boundary_stiffness / ((particle['y'] + 0.1) ** 2)
            particle['vy'] += force
        
        # 下边界
        if particle['y'] > self.height - 5:
            force = self.boundary_stiffness / ((self.height - particle['y'] + 0.1) ** 2)
            particle['vy'] -= force
    
    def _handle_particle_collisions(self):
        """处理粒子间碰撞"""
        for i in range(len(self.particles)):
            for j in range(i + 1, len(self.particles)):
                p1 = self.particles[i]
                p2 = self.particles[j]
                
                distance = self._calculate_distance(p1['x'], p1['y'], p2['x'], p2['y'])
                
                if distance < 2:  # 碰撞距离阈值
                    # 一维弹性碰撞简化版：交换速度分量
                    p1['vx'], p2['vx'] = p2['vx'], p1['vx']
                    p1['vy'], p2['vy'] = p2['vy'], p1['vy']
                    
                    # 轻微弹开
                    if distance > 0:
                        push_factor = (2 - distance) * 0.1
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
            
            # 欧拉积分：pos += velocity * dt
            particle['x'] += particle['vx'] * dt
            particle['y'] += particle['vy'] * dt
            
            # 阻尼
            particle['vx'] *= self.damping
            particle['vy'] *= self.damping
        
        # 处理碰撞
        self._handle_particle_collisions()
    
    def _render_frame(self):
        """渲染一帧到终端"""
        # 创建双缓冲字符数组
        buffer = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        
        # 绘制粒子
        for particle in self.particles:
            x = int(particle['x'])
            y = int(particle['y'])
            
            if 0 <= x < self.width and 0 <= y < self.height:
                buffer[y][x] = '·'
        
        # 绘制中心吸引子
        center_x, center_y = self.width // 2, self.height // 2
        if 0 <= center_x < self.width and 0 <= center_y < self.height:
            buffer[center_y][center_x] = '◉'
        
        # 绘制鼠标力源
        mouse_x, mouse_y = int(self.mouse_pos[0]), int(self.mouse_pos[1])
        if 0 <= mouse_x < self.width and 0 <= mouse_y < self.height:
            buffer[mouse_y][mouse_x] = '+'
        
        # 计算系统能量（动能）
        total_energy = sum(p['vx']**2 + p['vy']**2 for p in self.particles)
        
        # 计算帧率
        current_time = time.perf_counter()
        elapsed_time = current_time - self.start_time
        fps = self.frame_count / elapsed_time if elapsed_time > 0 else 0
        
        # 构建显示字符串
        output_lines = []
        
        # 添加状态信息
        status_line = f"帧率: {fps:.1f} | 粒子数: {len(self.particles)} | 能量: {total_energy:.0f}"
        output_lines.append(status_line)
        
        # 添加模拟区域
        for row in buffer:
            output_lines.append(''.join(row))
        
        # 添加控制说明
        controls_line = "空格:暂停/继续 | R:重置 | A/Z:引力 | Q:退出"
        output_lines.append(controls_line)
        
        # 一次性输出（双缓冲）
        sys.stdout.write('\033[H')  # 光标回到左上角
        sys.stdout.write('\n'.join(output_lines))
        sys.stdout.flush()
        
        self.frame_count += 1
    
    def _handle_input(self):
        """处理键盘输入"""
        try:
            import msvcrt
            if msvcrt.kbhit():
                key = msvcrt.getch().decode('utf-8')
                
                if key == ' ':
                    self.paused = not self.paused
                elif key == 'r' or key == 'R':
                    self._init_particles()
                elif key == 'a' or key == 'A':
                    self.gravity_strength = min(2.0, self.gravity_strength + 0.1)
                elif key == 'z' or key == 'Z':
                    self.gravity_strength = max(0.1, self.gravity_strength - 0.1)
                elif key == 'q' or key == 'Q':
                    self.running = False
                
                # 方向键控制鼠标位置
                elif key == '\xe0':  # 方向键前缀
                    arrow_key = msvcrt.getch().decode('utf-8')
                    if arrow_key == 'H':  # 上
                        self.mouse_pos[1] = max(0, self.mouse_pos[1] - 1)
                    elif arrow_key == 'P':  # 下
                        self.mouse_pos[1] = min(self.height - 1, self.mouse_pos[1] + 1)
                    elif arrow_key == 'K':  # 左
                        self.mouse_pos[0] = max(0, self.mouse_pos[0] - 1)
                    elif arrow_key == 'M':  # 右
                        self.mouse_pos[0] = min(self.width - 1, self.mouse_pos[0] + 1)
        except:
            pass  # 非Windows系统或输入不可用
    
    def run(self):
        """主运行循环"""
        target_fps = 30
        frame_time = 1.0 / target_fps
        
        last_time = time.perf_counter()
        
        try:
            while self.running:
                current_time = time.perf_counter()
                dt = current_time - last_time
                
                if dt >= frame_time:
                    self._handle_input()
                    
                    if not self.paused:
                        self._update_particles(dt)
                    
                    self._render_frame()
                    last_time = current_time
                
                # 避免过度占用CPU
                time.sleep(0.001)
        
        except KeyboardInterrupt:
            pass
        finally:
            self._cleanup_terminal()

def main():
    """主函数"""
    try:
        # 获取终端尺寸
        columns, rows = os.get_terminal_size()
        width = min(80, columns - 1)
        height = min(40, rows - 3)  # 留出行显示状态信息
        
        num_particles = random.randint(50, 200)
        
        sandbox = GeometricSandbox(width, height, num_particles)
        sandbox.run()
        
    except Exception as e:
        print(f"错误: {e}")
        print("请确保终端尺寸足够大（至少80x40）")

if __name__ == "__main__":
    main()