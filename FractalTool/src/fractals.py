import numpy as np
from numba import jit

@jit(nopython=True)
def mandelbrot(c, max_iter):
    """计算曼德博集合的逃逸时间"""
    z = 0
    for i in range(max_iter):
        z = z * z + c
        if abs(z) > 2:
            return i
    return max_iter

@jit(nopython=True)
def julia(z, c, max_iter):
    """计算朱利亚集合的逃逸时间"""
    for i in range(max_iter):
        z = z * z + c
        if abs(z) > 2:
            return i
    return max_iter

@jit(nopython=True)
def mandelbrot_set(xmin, xmax, ymin, ymax, width, height, max_iter):
    """生成曼德博集合图像"""
    r1 = np.linspace(xmin, xmax, width)
    r2 = np.linspace(ymin, ymax, height)
    img = np.empty((height, width))
    
    for i in range(height):
        for j in range(width):
            img[i, j] = mandelbrot(r1[j] + 1j * r2[i], max_iter)
    
    return img

@jit(nopython=True)
def julia_set(c, xmin, xmax, ymin, ymax, width, height, max_iter):
    """生成朱利亚集合图像"""
    r1 = np.linspace(xmin, xmax, width)
    r2 = np.linspace(ymin, ymax, height)
    img = np.empty((height, width))
    
    for i in range(height):
        for j in range(width):
            img[i, j] = julia(r1[j] + 1j * r2[i], c, max_iter)
    
    return img

@jit(nopython=True)
def burning_ship(c, max_iter):
    """计算燃烧船分形的逃逸时间"""
    z = 0
    for i in range(max_iter):
        z = (abs(z.real) + 1j * abs(z.imag)) ** 2 + c
        if abs(z) > 2:
            return i
    return max_iter

@jit(nopython=True)
def burning_ship_set(xmin, xmax, ymin, ymax, width, height, max_iter):
    """生成燃烧船分形图像"""
    r1 = np.linspace(xmin, xmax, width)
    r2 = np.linspace(ymin, ymax, height)
    img = np.empty((height, width))
    
    for i in range(height):
        for j in range(width):
            img[i, j] = burning_ship(r1[j] + 1j * r2[i], max_iter)
    
    return img

class IFS:
    """迭代函数系统"""
    def __init__(self, transformations, probabilities):
        """初始化IFS
        
        Args:
            transformations: 变换矩阵列表，每个矩阵为 [[a, b, c, d, e, f]]
            probabilities: 每个变换的概率列表
        """
        self.transformations = transformations
        self.probabilities = probabilities
    
    def generate(self, iterations, width, height):
        """生成IFS分形图像"""
        # 初始化点集
        points = np.zeros((iterations, 2))
        points[0] = [0, 0]  # 初始点
        
        # 应用变换
        for i in range(1, iterations):
            # 随机选择一个变换
            idx = np.random.choice(len(self.transformations), p=self.probabilities)
            a, b, c, d, e, f = self.transformations[idx]
            
            # 应用仿射变换
            x, y = points[i-1]
            points[i, 0] = a * x + b * y + e
            points[i, 1] = c * x + d * y + f
        
        # 将点映射到图像坐标
        x_min, x_max = np.min(points[:, 0]), np.max(points[:, 0])
        y_min, y_max = np.min(points[:, 1]), np.max(points[:, 1])
        
        img = np.zeros((height, width), dtype=np.uint8)
        
        for x, y in points:
            # 归一化到图像坐标
            px = int((x - x_min) / (x_max - x_min) * (width - 1))
            py = int((y - y_min) / (y_max - y_min) * (height - 1))
            py = height - 1 - py  # 反转y轴
            
            if 0 <= px < width and 0 <= py < height:
                img[py, px] = 255
        
        return img

class LSystem:
    """L-系统"""
    def __init__(self, axiom, rules, angle, length_factor=0.5):
        """初始化L-系统
        
        Args:
            axiom: 初始字符串
            rules: 替换规则字典
            angle: 旋转角度（度）
            length_factor: 长度缩放因子
        """
        self.axiom = axiom
        self.rules = rules
        self.angle = angle
        self.length_factor = length_factor
    
    def generate(self, iterations):
        """生成L-系统字符串"""
        string = self.axiom
        for _ in range(iterations):
            new_string = ""
            for char in string:
                new_string += self.rules.get(char, char)
            string = new_string
        return string
    
    def draw(self, string, width, height, start_length=100):
        """绘制L-系统
        
        Args:
            string: L-系统字符串
            width: 图像宽度
            height: 图像高度
            start_length: 初始线段长度
        """
        img = np.zeros((height, width, 3), dtype=np.uint8)
        
        # 初始位置和方向
        x, y = width // 2, height - 50
        angle = 90  # 向上
        
        stack = []
        length = start_length
        
        for char in string:
            if char in "FG":  # 前进并画线
                # 计算新位置
                rad = np.radians(angle)
                x2 = x + int(length * np.cos(rad))
                y2 = y - int(length * np.sin(rad))
                
                # 绘制线段
                self._draw_line(img, x, y, x2, y2, (255, 255, 255))
                
                # 更新位置
                x, y = x2, y2
            elif char == "f":  # 前进但不画线
                rad = np.radians(angle)
                x += int(length * np.cos(rad))
                y -= int(length * np.sin(rad))
            elif char == "+":  # 左转
                angle += self.angle
            elif char == "-":  # 右转
                angle -= self.angle
            elif char == "[":  # 保存状态
                stack.append((x, y, angle))
            elif char == "]":  # 恢复状态
                x, y, angle = stack.pop()
        
        return img
    
    def _draw_line(self, img, x1, y1, x2, y2, color):
        """绘制线段"""
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy
        
        while True:
            if 0 <= x1 < img.shape[1] and 0 <= y1 < img.shape[0]:
                img[y1, x1] = color
            
            if x1 == x2 and y1 == y2:
                break
            
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x1 += sx
            if e2 < dx:
                err += dx
                y1 += sy

# 预设IFS分形
class IFSPresets:
    @staticmethod
    def sierpinski_triangle():
        """ sierpinski 三角形 IFS"""
        transformations = [
            [0.5, 0, 0, 0.5, 0, 0],
            [0.5, 0, 0, 0.5, 0.5, 0],
            [0.5, 0, 0, 0.5, 0.25, 0.433]
        ]
        probabilities = [1/3, 1/3, 1/3]
        return IFS(transformations, probabilities)
    
    @staticmethod
    def barnsley_fern():
        """ Barnsley 蕨类植物 IFS"""
        transformations = [
            [0, 0, 0, 0.16, 0, 0],
            [0.85, 0.04, -0.04, 0.85, 0, 1.6],
            [0.2, -0.26, 0.23, 0.22, 0, 1.6],
            [-0.15, 0.28, 0.26, 0.24, 0, 0.44]
        ]
        probabilities = [0.01, 0.85, 0.07, 0.07]
        return IFS(transformations, probabilities)

# 预设L-系统
class LSystemPresets:
    @staticmethod
    def koch_snowflake():
        """科赫雪花"""
        return LSystem(
            axiom="F--F--F",
            rules={"F": "F+F--F+F"},
            angle=60
        )
    
    @staticmethod
    def dragon_curve():
        """龙曲线"""
        return LSystem(
            axiom="FX",
            rules={"X": "X+YF+", "Y": "-FX-Y"},
            angle=90
        )
    
    @staticmethod
    def fractal_plant():
        """分形植物"""
        return LSystem(
            axiom="X",
            rules={
                "X": "F-[[X]+X]+F[+FX]-X",
                "F": "FF"
            },
            angle=25
        )

class FractalTypes:
    """分形类型枚举"""
    MANDELBROT = "mandelbrot"
    JULIA = "julia"
    BURNING_SHIP = "burning_ship"
    IFS = "ifs"
    L_SYSTEM = "l_system"
