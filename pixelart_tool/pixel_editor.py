"""
像素编辑工具模块
实现像素级编辑、颜色选择和调色板管理
"""

import numpy as np
from PIL import Image, ImageDraw
import tkinter as tk
from tkinter import colorchooser

class PixelEditor:
    """像素编辑器类"""
    
    def __init__(self):
        self.image = None
        self.undo_stack = []
        self.redo_stack = []
        self.max_undo_steps = 50
        self.current_tool = "pencil"
        self.current_color = (255, 0, 0)  # 默认红色
        self.brush_size = 1
        
    def set_image(self, image):
        """设置要编辑的图像"""
        if image is not None:
            self.image = image.copy()
            self.save_state()
    
    def save_state(self):
        """保存当前状态到撤销栈"""
        if self.image is not None:
            # 保存图像副本
            state = self.image.copy()
            self.undo_stack.append(state)
            
            # 限制撤销步数
            if len(self.undo_stack) > self.max_undo_steps:
                self.undo_stack.pop(0)
            
            # 清空重做栈
            self.redo_stack.clear()
    
    def undo(self):
        """撤销操作"""
        if len(self.undo_stack) > 1:  # 保留至少一个状态
            # 将当前状态移到重做栈
            self.redo_stack.append(self.undo_stack.pop())
            # 恢复上一个状态
            self.image = self.undo_stack[-1].copy()
            return True
        return False
    
    def redo(self):
        """重做操作"""
        if self.redo_stack:
            # 恢复重做状态
            state = self.redo_stack.pop()
            self.image = state.copy()
            self.undo_stack.append(state)
            return True
        return False
    
    def set_tool(self, tool_name):
        """设置当前工具"""
        self.current_tool = tool_name
    
    def set_color(self, color):
        """设置当前颜色"""
        self.current_color = color
    
    def choose_color(self):
        """打开颜色选择器"""
        color = colorchooser.askcolor(title="选择颜色")
        if color[0] is not None:
            self.current_color = tuple(map(int, color[0]))
            return self.current_color
        return None
    
    def set_brush_size(self, size):
        """设置画笔大小"""
        self.brush_size = max(1, min(size, 10))  # 限制在1-10之间
    
    def draw_pixel(self, x, y):
        """绘制单个像素"""
        if self.image is None:
            return False
        
        self.save_state()
        
        img_array = np.array(self.image)
        height, width, _ = img_array.shape
        
        # 确保坐标在有效范围内
        x = max(0, min(x, width - 1))
        y = max(0, min(y, height - 1))
        
        if self.current_tool == "pencil":
            # 铅笔工具：绘制单个像素
            img_array[y, x] = self.current_color
            
        elif self.current_tool == "brush":
            # 画笔工具：绘制圆形区域
            radius = self.brush_size // 2
            for dy in range(-radius, radius + 1):
                for dx in range(-radius, radius + 1):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < width and 0 <= ny < height:
                        if dx*dx + dy*dy <= radius*radius:
                            img_array[ny, nx] = self.current_color
        
        elif self.current_tool == "eraser":
            # 橡皮擦工具：擦除像素（设置为透明或背景色）
            img_array[y, x] = (255, 255, 255)  # 白色背景
        
        elif self.current_tool == "fill":
            # 填充工具：区域填充
            self.flood_fill(x, y, img_array)
        
        self.image = Image.fromarray(img_array)
        return True
    
    def flood_fill(self, x, y, img_array):
        """洪水填充算法"""
        height, width, _ = img_array.shape
        target_color = img_array[y, x].copy()
        
        # 如果目标颜色已经是当前颜色，则不执行填充
        if np.array_equal(target_color, self.current_color):
            return
        
        # 使用队列实现BFS
        queue = [(x, y)]
        visited = set()
        
        while queue:
            cx, cy = queue.pop(0)
            
            # 检查边界和颜色匹配
            if (cx, cy) in visited or not (0 <= cx < width and 0 <= cy < height):
                continue
            
            if not np.array_equal(img_array[cy, cx], target_color):
                continue
            
            # 设置新颜色
            img_array[cy, cx] = self.current_color
            visited.add((cx, cy))
            
            # 添加相邻像素
            queue.extend([(cx+1, cy), (cx-1, cy), (cx, cy+1), (cx, cy-1)])
    
    def draw_line(self, start_x, start_y, end_x, end_y):
        """绘制直线"""
        if self.image is None:
            return False
        
        self.save_state()
        
        # 使用Bresenham算法绘制直线
        dx = abs(end_x - start_x)
        dy = abs(end_y - start_y)
        
        x, y = start_x, start_y
        
        # 确定步进方向
        sx = 1 if start_x < end_x else -1
        sy = 1 if start_y < end_y else -1
        
        err = dx - dy
        
        while True:
            self.draw_pixel(x, y)
            
            if x == end_x and y == end_y:
                break
            
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy
        
        return True
    
    def draw_rectangle(self, start_x, start_y, end_x, end_y, fill=False):
        """绘制矩形"""
        if self.image is None:
            return False
        
        self.save_state()
        
        img_array = np.array(self.image)
        height, width, _ = img_array.shape
        
        # 确保坐标在有效范围内
        x1, y1 = max(0, min(start_x, width-1)), max(0, min(start_y, height-1))
        x2, y2 = max(0, min(end_x, width-1)), max(0, min(end_y, height-1))
        
        if fill:
            # 填充矩形
            for y in range(min(y1, y2), max(y1, y2) + 1):
                for x in range(min(x1, x2), max(x1, x2) + 1):
                    img_array[y, x] = self.current_color
        else:
            # 绘制矩形边框
            for x in range(min(x1, x2), max(x1, x2) + 1):
                img_array[y1, x] = self.current_color
                img_array[y2, x] = self.current_color
            for y in range(min(y1, y2), max(y1, y2) + 1):
                img_array[y, x1] = self.current_color
                img_array[y, x2] = self.current_color
        
        self.image = Image.fromarray(img_array)
        return True
    
    def draw_circle(self, center_x, center_y, radius, fill=False):
        """绘制圆形"""
        if self.image is None:
            return False
        
        self.save_state()
        
        img_array = np.array(self.image)
        height, width, _ = img_array.shape
        
        if fill:
            # 填充圆形
            for y in range(max(0, center_y - radius), min(height, center_y + radius + 1)):
                for x in range(max(0, center_x - radius), min(width, center_x + radius + 1)):
                    if (x - center_x)**2 + (y - center_y)**2 <= radius**2:
                        img_array[y, x] = self.current_color
        else:
            # 绘制圆形边框
            for angle in range(0, 360, 1):
                rad = angle * np.pi / 180
                x = int(center_x + radius * np.cos(rad))
                y = int(center_y + radius * np.sin(rad))
                
                if 0 <= x < width and 0 <= y < height:
                    img_array[y, x] = self.current_color
        
        self.image = Image.fromarray(img_array)
        return True
    
    def pick_color(self, x, y):
        """拾取颜色"""
        if self.image is None:
            return None
        
        img_array = np.array(self.image)
        height, width, _ = img_array.shape
        
        if 0 <= x < width and 0 <= y < height:
            color = tuple(img_array[y, x])
            self.current_color = color
            return color
        
        return None
    
    def get_palette_colors(self, num_colors=16):
        """从图像中提取调色板颜色"""
        if self.image is None:
            return []
        
        img_array = np.array(self.image)
        
        # 获取所有像素颜色
        pixels = img_array.reshape(-1, 3)
        
        # 使用K-means聚类提取主要颜色
        from sklearn.cluster import KMeans
        
        kmeans = KMeans(n_clusters=num_colors, random_state=42)
        kmeans.fit(pixels)
        
        # 获取聚类中心
        palette_colors = kmeans.cluster_centers_.astype(int)
        
        return [tuple(color) for color in palette_colors]
    
    def apply_palette(self, palette):
        """应用调色板到图像"""
        if self.image is None or not palette:
            return False
        
        self.save_state()
        
        img_array = np.array(self.image)
        height, width, _ = img_array.shape
        
        # 将每个像素映射到调色板中最接近的颜色
        for y in range(height):
            for x in range(width):
                pixel = img_array[y, x]
                
                # 找到最接近的调色板颜色
                min_distance = float('inf')
                best_color = palette[0]
                
                for color in palette:
                    distance = np.sum((pixel - color) ** 2)
                    if distance < min_distance:
                        min_distance = distance
                        best_color = color
                
                img_array[y, x] = best_color
        
        self.image = Image.fromarray(img_array)
        return True