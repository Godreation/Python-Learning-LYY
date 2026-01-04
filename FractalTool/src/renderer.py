import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

class ColorSchemes:
    """着色方案枚举"""
    GRADIENT = "gradient"
    JET = "jet"
    HSV = "hsv"
    TWISTED = "twisted"
    BLACK_AND_WHITE = "black_and_white"
    FIRE = "fire"
    ICE = "ice"

class Renderer:
    """渲染器类，负责分形图像的渲染和着色"""
    
    def __init__(self):
        # 预定义颜色映射
        self.colormaps = {
            ColorSchemes.GRADIENT: plt.cm.viridis,
            ColorSchemes.JET: plt.cm.jet,
            ColorSchemes.HSV: plt.cm.hsv,
            ColorSchemes.BLACK_AND_WHITE: plt.cm.gray,
            ColorSchemes.FIRE: self._create_fire_colormap(),
            ColorSchemes.ICE: self._create_ice_colormap(),
            ColorSchemes.TWISTED: self._create_twisted_colormap()
        }
    
    def _create_fire_colormap(self):
        """创建火焰色图"""
        colors = [
            (0, 0, 0),      # 黑色
            (0.5, 0, 0),    # 深红色
            (1, 0, 0),      # 红色
            (1, 0.5, 0),    # 橙色
            (1, 1, 0),      # 黄色
            (1, 1, 1)       # 白色
        ]
        return LinearSegmentedColormap.from_list("fire", colors)
    
    def _create_ice_colormap(self):
        """创建冰蓝色图"""
        colors = [
            (0, 0, 0.5),    # 深蓝色
            (0, 0, 1),      # 蓝色
            (0, 0.5, 1),    # 亮蓝色
            (0.5, 1, 1),    # 青色
            (1, 1, 1)       # 白色
        ]
        return LinearSegmentedColormap.from_list("ice", colors)
    
    def _create_twisted_colormap(self):
        """创建扭曲色图"""
        colors = [
            (0, 0, 0),      # 黑色
            (0.5, 0, 0.5),  # 紫色
            (0, 0, 1),      # 蓝色
            (0, 1, 0),      # 绿色
            (1, 1, 0),      # 黄色
            (1, 0, 0),      # 红色
            (1, 1, 1)       # 白色
        ]
        return LinearSegmentedColormap.from_list("twisted", colors)
    
    def escape_time_coloring(self, img, max_iter, color_scheme=ColorSchemes.GRADIENT):
        """逃逸时间着色算法"""
        # 规范化迭代次数到 [0, 1]
        normalized = img / max_iter
        
        # 应用颜色映射
        cmap = self.colormaps[color_scheme]
        colored = cmap(normalized)
        
        # 转换为 RGB 图像 (0-255)
        return (colored[:, :, :3] * 255).astype(np.uint8)
    
    def smooth_coloring(self, img, max_iter, color_scheme=ColorSchemes.GRADIENT):
        """平滑着色算法"""
        # 计算平滑迭代次数
        smooth = np.where(img < max_iter, img - np.log2(np.log2(img + 1e-10)), max_iter)
        normalized = smooth / max_iter
        
        # 应用颜色映射
        cmap = self.colormaps[color_scheme]
        colored = cmap(normalized)
        
        return (colored[:, :, :3] * 255).astype(np.uint8)
    
    def distance_estimator_coloring(self, img, max_iter, color_scheme=ColorSchemes.GRADIENT):
        """距离估计器着色"""
        # 简单实现，基于逃逸时间的平滑着色
        return self.smooth_coloring(img, max_iter, color_scheme)
    
    def apply_coloring(self, img, max_iter, coloring_method="escape_time", color_scheme=ColorSchemes.GRADIENT):
        """应用着色方案
        
        Args:
            img: 原始分形图像
            max_iter: 最大迭代次数
            coloring_method: 着色方法 (escape_time, smooth, distance_estimator)
            color_scheme: 颜色方案
            
        Returns:
            着色后的RGB图像
        """
        if coloring_method == "escape_time":
            return self.escape_time_coloring(img, max_iter, color_scheme)
        elif coloring_method == "smooth":
            return self.smooth_coloring(img, max_iter, color_scheme)
        elif coloring_method == "distance_estimator":
            return self.distance_estimator_coloring(img, max_iter, color_scheme)
        else:
            raise ValueError(f"Unknown coloring method: {coloring_method}")
    
    def supersample(self, fractal_func, *args, supersample_factor=2, **kwargs):
        """超采样抗锯齿
        
        Args:
            fractal_func: 生成分形图像的函数
            *args: 传递给fractal_func的参数
            supersample_factor: 超采样因子
            **kwargs: 传递给fractal_func的关键字参数
            
        Returns:
            抗锯齿处理后的分形图像
        """
        # 获取原始尺寸
        width = kwargs.get('width', 800)
        height = kwargs.get('height', 800)
        
        # 生成高分辨率图像
        kwargs['width'] = width * supersample_factor
        kwargs['height'] = height * supersample_factor
        
        high_res_img = fractal_func(*args, **kwargs)
        
        # 下采样到原始尺寸
        if len(high_res_img.shape) == 2:  # 灰度图像
            img = Image.fromarray(high_res_img.astype(np.float32))
        else:  # RGB图像
            img = Image.fromarray(high_res_img.astype(np.uint8))
        
        img = img.resize((width, height), Image.LANCZOS)
        
        return np.array(img)
    
    def save_image(self, img, filename):
        """保存图像到文件"""
        if isinstance(img, np.ndarray):
            if len(img.shape) == 2:
                img = Image.fromarray(img.astype(np.uint8))
            else:
                img = Image.fromarray(img.astype(np.uint8))
        img.save(filename)
    
    def display_image(self, img):
        """显示图像"""
        if isinstance(img, np.ndarray):
            if len(img.shape) == 2:
                plt.imshow(img, cmap='gray')
            else:
                plt.imshow(img)
            plt.axis('off')
            plt.show()
        else:
            img.show()
    
    def apply_gamma_correction(self, img, gamma=1.0):
        """应用伽马校正"""
        # 确保图像在0-1范围内
        img_normalized = img / 255.0
        # 应用伽马校正
        corrected = np.power(img_normalized, gamma)
        # 转换回0-255范围
        return (corrected * 255).astype(np.uint8)
    
    def enhance_contrast(self, img, factor=1.5):
        """增强对比度"""
        # 确保图像在0-1范围内
        img_normalized = img / 255.0
        # 应用对比度增强
        mean = np.mean(img_normalized)
        enhanced = (img_normalized - mean) * factor + mean
        # 裁剪到0-1范围
        enhanced = np.clip(enhanced, 0, 1)
        # 转换回0-255范围
        return (enhanced * 255).astype(np.uint8)
