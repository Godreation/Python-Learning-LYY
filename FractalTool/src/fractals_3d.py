import numpy as np
from numba import jit
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.ndimage import gaussian_filter

class Fractal3D:
    """3D分形类"""
    
    @staticmethod
    @jit(nopython=True)
    def mandelbulb(c, power=8, max_iter=50):
        """计算曼德球的逃逸时间
        
        Args:
            c: 复数 (x, y, z)
            power: 曼德球的幂次
            max_iter: 最大迭代次数
            
        Returns:
            逃逸时间或max_iter
        """
        x, y, z = c
        x0, y0, z0 = x, y, z
        
        for i in range(max_iter):
            # 计算半径和角度
            r = np.sqrt(x**2 + y**2 + z**2)
            theta = np.arctan2(np.sqrt(x**2 + y**2), z)
            phi = np.arctan2(y, x)
            
            # 计算下一次迭代
            r_pow = r ** power
            sin_theta_pow = np.sin(theta * power)
            
            x = r_pow * sin_theta_pow * np.cos(phi * power) + x0
            y = r_pow * sin_theta_pow * np.sin(phi * power) + y0
            z = r_pow * np.cos(theta * power) + z0
            
            # 检查逃逸条件
            if x**2 + y**2 + z**2 > 4:
                return i
        
        return max_iter
    
    @staticmethod
    def mandelbulb_set(xmin, xmax, ymin, ymax, zmin, zmax, width, height, depth, power=8, max_iter=50):
        """生成曼德球集合
        
        Args:
            xmin, xmax: x轴范围
            ymin, ymax: y轴范围
            zmin, zmax: z轴范围
            width, height, depth: 体素尺寸
            power: 曼德球的幂次
            max_iter: 最大迭代次数
            
        Returns:
            3D数组，表示每个体素的逃逸时间
        """
        # 创建网格
        x = np.linspace(xmin, xmax, width)
        y = np.linspace(ymin, ymax, height)
        z = np.linspace(zmin, zmax, depth)
        
        # 初始化结果数组
        vol = np.zeros((depth, height, width), dtype=np.float32)
        
        # 计算每个体素
        for k in range(depth):
            for j in range(height):
                for i in range(width):
                    vol[k, j, i] = Fractal3D.mandelbulb((x[i], y[j], z[k]), power, max_iter)
            print(f"处理层 {k+1}/{depth}")
        
        return vol
    
    @staticmethod
    def generate_perlin_noise_3d(shape, scale=10.0, octaves=4, persistence=0.5, lacunarity=2.0):
        """生成3D Perlin噪声
        
        Args:
            shape: 输出形状 (depth, height, width)
            scale: 基础缩放
            octaves: 八度数量
            persistence: 持久性
            lacunarity: 间隙度
            
        Returns:
            3D噪声数组
        """
        # 简化实现，使用多层正弦波叠加模拟Perlin噪声
        depth, height, width = shape
        noise = np.zeros((depth, height, width))
        
        for octave in range(octaves):
            freq = lacunarity ** octave
            amp = persistence ** octave
            
            # 生成网格坐标
            x = np.linspace(0, scale * freq, width, endpoint=False)
            y = np.linspace(0, scale * freq, height, endpoint=False)
            z = np.linspace(0, scale * freq, depth, endpoint=False)
            
            # 生成三维网格
            xx, yy, zz = np.meshgrid(x, y, z, indexing='ij')
            
            # 生成正弦波叠加
            octave_noise = amp * np.sin(xx) * np.cos(yy) * np.sin(zz)
            noise += octave_noise
        
        # 归一化到 [-1, 1]
        noise = noise / np.max(np.abs(noise))
        return noise
    
    @staticmethod
    def generate_fractal_terrain(width, height, scale=50.0, octaves=6, persistence=0.5, lacunarity=2.0):
        """生成3D分形地形
        
        Args:
            width, height: 地形尺寸
            scale: 基础缩放
            octaves: 八度数量
            persistence: 持久性
            lacunarity: 间隙度
            
        Returns:
            2D高度图
        """
        # 生成2D分形噪声
        x = np.linspace(0, scale, width, endpoint=False)
        y = np.linspace(0, scale, height, endpoint=False)
        xx, yy = np.meshgrid(x, y)
        
        terrain = np.zeros((height, width))
        
        for octave in range(octaves):
            freq = lacunarity ** octave
            amp = persistence ** octave
            
            noise = amp * np.sin(xx * freq) * np.cos(yy * freq)
            terrain += noise
        
        # 归一化到 [0, 1]
        terrain = (terrain + 1) / 2
        return terrain
    
    @staticmethod
    def render_terrain(terrain, title="3D分形地形"):
        """渲染3D分形地形
        
        Args:
            terrain: 2D高度图
            title: 图表标题
        """
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        # 创建网格
        x = np.arange(terrain.shape[1])
        y = np.arange(terrain.shape[0])
        xx, yy = np.meshgrid(x, y)
        
        # 绘制表面
        surf = ax.plot_surface(xx, yy, terrain, cmap='terrain', 
                              linewidth=0, antialiased=False)
        
        # 添加颜色条
        fig.colorbar(surf, shrink=0.5, aspect=5)
        
        ax.set_title(title)
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('高度')
        
        plt.show()
    
    @staticmethod
    def simple_volume_rendering(vol, threshold=0.5, step=0.1):
        """简单体渲染
        
        Args:
            vol: 3D体素数组
            threshold: 阈值
            step: 采样步长
            
        Returns:
            2D投影图像
        """
        # 简化实现，沿z轴投影
        depth, height, width = vol.shape
        
        # 创建输出图像
        img = np.zeros((height, width), dtype=np.float32)
        
        # 沿z轴积分
        for k in range(depth):
            slice_vol = vol[k] / np.max(vol)
            img += slice_vol * (slice_vol > threshold) * step
        
        # 归一化
        img = img / np.max(img)
        return img
    
    @staticmethod
    def render_mandelbulb_slice(mandelbulb_vol, slice_index, axis='z', title="曼德球切片"):
        """渲染曼德球的2D切片
        
        Args:
            mandelbulb_vol: 3D曼德球体素数据
            slice_index: 切片索引
            axis: 切片轴 ('x', 'y', 'z')
            title: 图表标题
        """
        # 获取切片
        if axis == 'x':
            slice_data = mandelbulb_vol[:, :, slice_index]
        elif axis == 'y':
            slice_data = mandelbulb_vol[:, slice_index, :]
        else:  # z轴
            slice_data = mandelbulb_vol[slice_index, :, :]
        
        # 渲染切片
        plt.figure(figsize=(8, 8))
        plt.imshow(slice_data, cmap='viridis')
        plt.colorbar(label='逃逸时间')
        plt.title(title)
        plt.axis('off')
        plt.show()
    
    @staticmethod
    def generate_mandelbulb_slices(xmin=-2, xmax=2, ymin=-2, ymax=2, zmin=-2, zmax=2,
                                 width=100, height=100, depth=100, power=8, max_iter=50):
        """生成曼德球并渲染几个切片
        
        Args:
            xmin, xmax, ymin, ymax, zmin, zmax: 渲染范围
            width, height, depth: 体素尺寸
            power: 曼德球的幂次
            max_iter: 最大迭代次数
        """
        # 生成曼德球
        print("正在生成曼德球...")
        mandelbulb_vol = Fractal3D.mandelbulb_set(xmin, xmax, ymin, ymax, zmin, zmax,
                                                 width, height, depth, power, max_iter)
        
        # 渲染中心切片
        center_idx = depth // 2
        Fractal3D.render_mandelbulb_slice(mandelbulb_vol, center_idx, axis='z',
                                         title=f"曼德球Z轴切片 (索引: {center_idx})")
        
        return mandelbulb_vol
    
    @staticmethod
    def generate_and_render_terrain(width=200, height=200):
        """生成并渲染3D分形地形
        
        Args:
            width, height: 地形尺寸
        """
        # 生成分形地形
        print("正在生成3D分形地形...")
        terrain = Fractal3D.generate_fractal_terrain(width, height)
        
        # 渲染地形
        Fractal3D.render_terrain(terrain)
        return terrain

if __name__ == "__main__":
    # 示例用法
    
    # 生成并渲染曼德球切片
    # mandelbulb_vol = Fractal3D.generate_mandelbulb_slices(width=50, height=50, depth=50)
    
    # 生成并渲染3D分形地形
    terrain = Fractal3D.generate_and_render_terrain(width=100, height=100)
