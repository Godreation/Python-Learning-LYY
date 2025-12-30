"""
图像处理核心模块
负责图像的分辨率降低、颜色减少和抖动算法
"""

import numpy as np
from PIL import Image
import cv2

class ImageProcessor:
    """图像处理器类"""
    
    def __init__(self):
        self.original_image = None
        self.processed_image = None
        self.pixel_size = 10
        self.color_palette_size = 16
        self.dither_enabled = True
        self.outline_enabled = False
        
    def load_image(self, image_path):
        """加载图像"""
        try:
            self.original_image = Image.open(image_path)
            return True
        except Exception as e:
            print(f"加载图像错误: {e}")
            return False
    
    def resize_image(self, width=None, height=None):
        """调整图像大小"""
        if self.original_image is None:
            return None
            
        if width is None and height is None:
            # 使用像素大小计算新尺寸
            width = self.original_image.width // self.pixel_size
            height = self.original_image.height // self.pixel_size
        
        resized = self.original_image.resize((width, height), Image.NEAREST)
        return resized
    
    def reduce_colors_kmeans(self, image, num_colors=16):
        """使用K-means算法减少颜色数量"""
        # 转换为numpy数组
        img_array = np.array(image)
        
        # 重塑为像素列表
        pixels = img_array.reshape(-1, 3)
        
        # 转换为float32
        pixels = np.float32(pixels)
        
        # 定义K-means参数
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
        flags = cv2.KMEANS_RANDOM_CENTERS
        
        # 应用K-means
        _, labels, centers = cv2.kmeans(pixels, num_colors, None, criteria, 10, flags)
        
        # 转换为uint8
        centers = np.uint8(centers)
        
        # 重新映射像素
        segmented_data = centers[labels.flatten()]
        segmented_image = segmented_data.reshape(img_array.shape)
        
        return Image.fromarray(segmented_image)
    
    def reduce_colors_palette(self, image, num_colors=16):
        """使用调色板减少颜色数量"""
        # 转换为调色板模式
        if image.mode != 'P':
            # 先转换为RGB确保一致性
            rgb_image = image.convert('RGB')
            # 转换为调色板模式
            palette_image = rgb_image.convert('P', palette=Image.ADAPTIVE, colors=num_colors)
            # 转换回RGB以便显示
            result = palette_image.convert('RGB')
            return result
        return image
    
    def floyd_steinberg_dithering(self, image):
        """Floyd-Steinberg抖动算法"""
        img_array = np.array(image, dtype=np.float32)
        height, width, channels = img_array.shape
        
        for y in range(height - 1):
            for x in range(1, width - 1):
                old_pixel = img_array[y, x].copy()
                
                # 量化到最近的调色板颜色
                new_pixel = np.round(old_pixel / 85) * 85
                img_array[y, x] = new_pixel
                
                # 计算量化误差
                quant_error = old_pixel - new_pixel
                
                # 扩散误差到相邻像素
                img_array[y, x+1] += quant_error * 7/16
                img_array[y+1, x-1] += quant_error * 3/16
                img_array[y+1, x] += quant_error * 5/16
                img_array[y+1, x+1] += quant_error * 1/16
        
        # 确保值在有效范围内
        img_array = np.clip(img_array, 0, 255)
        return Image.fromarray(img_array.astype(np.uint8))
    
    def add_outline(self, image, outline_color=(0, 0, 0), threshold=50):
        """添加轮廓线"""
        img_array = np.array(image)
        height, width, _ = img_array.shape
        
        # 创建轮廓掩码
        outline_mask = np.zeros((height, width), dtype=bool)
        
        # 检测边缘
        for y in range(1, height-1):
            for x in range(1, width-1):
                current_pixel = img_array[y, x]
                
                # 检查相邻像素的差异
                neighbors = [
                    img_array[y-1, x], img_array[y+1, x],
                    img_array[y, x-1], img_array[y, x+1]
                ]
                
                for neighbor in neighbors:
                    diff = np.sum(np.abs(current_pixel - neighbor))
                    if diff > threshold:
                        outline_mask[y, x] = True
                        break
        
        # 应用轮廓
        result_array = img_array.copy()
        result_array[outline_mask] = outline_color
        
        return Image.fromarray(result_array)
    
    def apply_retro_effect(self, image, style="nes"):
        """应用复古游戏风格效果"""
        img_array = np.array(image)
        
        if style == "nes":
            # NES风格：有限的调色板
            palette = [
                [0, 0, 0], [255, 0, 0], [0, 255, 0], [0, 0, 255],
                [255, 255, 0], [255, 0, 255], [0, 255, 255], [255, 255, 255]
            ]
            
        elif style == "gameboy":
            # Game Boy风格：绿色调
            palette = [
                [15, 56, 15], [48, 98, 48], [139, 172, 15], [155, 188, 15]
            ]
            
        elif style == "arcade":
            # 街机风格：鲜艳色彩
            palette = [
                [255, 0, 0], [0, 255, 0], [0, 0, 255], [255, 255, 0],
                [255, 0, 255], [0, 255, 255], [255, 128, 0], [128, 0, 255]
            ]
        
        else:
            return image
        
        # 将图像颜色映射到调色板
        height, width, _ = img_array.shape
        result_array = np.zeros_like(img_array)
        
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
                
                result_array[y, x] = best_color
        
        return Image.fromarray(result_array)
    
    def process_image(self, pixel_size=None, palette_size=None, dither=None, outline=None, style=None):
        """处理图像的主要方法"""
        if self.original_image is None:
            return None
        
        # 更新参数
        if pixel_size is not None:
            self.pixel_size = pixel_size
        if palette_size is not None:
            self.color_palette_size = palette_size
        if dither is not None:
            self.dither_enabled = dither
        if outline is not None:
            self.outline_enabled = outline
        
        # 第一步：调整大小
        resized = self.resize_image()
        
        # 第二步：减少颜色
        if self.color_palette_size < 256:
            reduced = self.reduce_colors_palette(resized, self.color_palette_size)
        else:
            reduced = resized
        
        # 第三步：应用抖动
        if self.dither_enabled:
            dithered = self.floyd_steinberg_dithering(reduced)
        else:
            dithered = reduced
        
        # 第四步：添加轮廓
        if self.outline_enabled:
            outlined = self.add_outline(dithered)
        else:
            outlined = dithered
        
        # 第五步：应用风格
        if style:
            styled = self.apply_retro_effect(outlined, style)
        else:
            styled = outlined
        
        self.processed_image = styled
        return styled
    
    def get_color_palette(self, image=None):
        """获取图像的颜色调色板"""
        if image is None:
            if self.processed_image is None:
                return []
            image = self.processed_image
        
        img_array = np.array(image)
        
        # 获取唯一颜色
        unique_colors = np.unique(img_array.reshape(-1, 3), axis=0)
        return [tuple(color) for color in unique_colors]
    
    def save_image(self, file_path, format='PNG'):
        """保存处理后的图像"""
        if self.processed_image is not None:
            self.processed_image.save(file_path, format)
            return True
        return False