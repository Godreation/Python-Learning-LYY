import numpy as np
import cv2
import os
from fractals import (
    mandelbrot_set, julia_set, burning_ship_set,
    IFSPresets, LSystemPresets, FractalTypes
)
from renderer import Renderer, ColorSchemes

class FractalAnimator:
    """分形动画生成器"""
    
    def __init__(self):
        self.renderer = Renderer()
    
    def generate_animation(self, fractal_type, width, height, duration, fps, output_path, 
                          params_start, params_end, color_scheme=ColorSchemes.GRADIENT,
                          coloring_method="smooth", max_iter=100):
        """生成分形动画
        
        Args:
            fractal_type: 分形类型
            width, height: 图像尺寸
            duration: 动画时长（秒）
            fps: 帧率
            output_path: 输出视频路径
            params_start: 起始参数
            params_end: 结束参数
            color_scheme: 颜色方案
            coloring_method: 着色方法
            max_iter: 最大迭代次数
        """
        # 计算总帧数
        total_frames = int(duration * fps)
        
        # 创建视频写入器
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        try:
            for frame in range(total_frames):
                # 计算当前参数插值
                t = frame / total_frames
                current_params = self._interpolate_params(params_start, params_end, t)
                
                # 渲染当前帧
                img = self._render_frame(fractal_type, width, height, current_params, 
                                       color_scheme, coloring_method, max_iter)
                
                # 转换为BGR格式（OpenCV使用BGR）
                img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
                
                # 写入视频
                out.write(img_bgr)
                
                # 打印进度
                if frame % 10 == 0:
                    print(f"生成帧 {frame}/{total_frames} ({frame/total_frames*100:.1f}%)")
        finally:
            # 释放视频写入器
            out.release()
        
        print(f"动画已保存到: {output_path}")
    
    def _interpolate_params(self, params_start, params_end, t):
        """插值计算当前参数"""
        if isinstance(params_start, complex) and isinstance(params_end, complex):
            # 复数插值
            real = params_start.real + (params_end.real - params_start.real) * t
            imag = params_start.imag + (params_end.imag - params_start.imag) * t
            return complex(real, imag)
        elif isinstance(params_start, tuple) and isinstance(params_end, tuple):
            # 元组插值
            return tuple(s + (e - s) * t for s, e in zip(params_start, params_end))
        elif isinstance(params_start, list) and isinstance(params_end, list):
            # 列表插值
            return [s + (e - s) * t for s, e in zip(params_start, params_end)]
        else:
            # 标量插值
            return params_start + (params_end - params_start) * t
    
    def _render_frame(self, fractal_type, width, height, params, color_scheme, coloring_method, max_iter):
        """渲染单帧分形图像"""
        if fractal_type == FractalTypes.MANDELBROT:
            # 曼德博集合动画，参数为视图范围
            xmin, xmax, ymin, ymax = params
            img = mandelbrot_set(xmin, xmax, ymin, ymax, width, height, max_iter)
            return self.renderer.apply_coloring(img, max_iter, coloring_method, color_scheme)
        
        elif fractal_type == FractalTypes.JULIA:
            # 朱利亚集合动画，参数为c值
            c = params
            xmin, xmax = -2.0, 2.0
            ymin, ymax = -2.0, 2.0
            img = julia_set(c, xmin, xmax, ymin, ymax, width, height, max_iter)
            return self.renderer.apply_coloring(img, max_iter, coloring_method, color_scheme)
        
        elif fractal_type == FractalTypes.BURNING_SHIP:
            # 燃烧船分形动画，参数为视图范围
            xmin, xmax, ymin, ymax = params
            img = burning_ship_set(xmin, xmax, ymin, ymax, width, height, max_iter)
            return self.renderer.apply_coloring(img, max_iter, coloring_method, color_scheme)
        
        elif fractal_type == FractalTypes.L_SYSTEM:
            # L-系统动画，参数为迭代次数
            iterations = int(params)
            lsystem = LSystemPresets.fractal_plant()
            string = lsystem.generate(iterations)
            return lsystem.draw(string, width, height)
        
        else:
            raise ValueError(f"不支持的分形类型: {fractal_type}")
    
    def julia_animation(self, width=800, height=600, duration=10, fps=30, output_path="../results/julia_animation.mp4",
                       c_start=-0.8+0.156j, c_end=0.285+0.01j):
        """生成朱利亚集合动画（c值变化）"""
        self.generate_animation(
            fractal_type=FractalTypes.JULIA,
            width=width,
            height=height,
            duration=duration,
            fps=fps,
            output_path=output_path,
            params_start=c_start,
            params_end=c_end,
            color_scheme=ColorSchemes.GRADIENT,
            coloring_method="smooth",
            max_iter=100
        )
    
    def mandelbrot_zoom_animation(self, width=800, height=600, duration=10, fps=30, output_path="../results/mandelbrot_zoom.mp4",
                                 x_start=-2.5, x_end=0.27, y_start=-1.5, y_end=1.5,
                                 zoom_center=(-0.743643887037158704752191506114774, 0.131825904205311970493132056385139)):
        """生成曼德博集合缩放动画"""
        # 计算起始和结束视图范围
        params_start = (x_start, x_end, y_start, y_end)
        
        # 计算缩放后的视图范围
        zoom_factor = 100  # 缩放倍数
        current_width = x_end - x_start
        current_height = y_end - y_start
        new_width = current_width / zoom_factor
        new_height = current_height / zoom_factor
        
        params_end = (
            zoom_center[0] - new_width / 2,
            zoom_center[0] + new_width / 2,
            zoom_center[1] - new_height / 2,
            zoom_center[1] + new_height / 2
        )
        
        self.generate_animation(
            fractal_type=FractalTypes.MANDELBROT,
            width=width,
            height=height,
            duration=duration,
            fps=fps,
            output_path=output_path,
            params_start=params_start,
            params_end=params_end,
            color_scheme=ColorSchemes.GRADIENT,
            coloring_method="smooth",
            max_iter=100
        )
    
    def burning_ship_animation(self, width=800, height=600, duration=10, fps=30, output_path="../results/burning_ship_animation.mp4"):
        """生成燃烧船分形动画"""
        params_start = (-2.5, 1.5, -2.0, 1.0)
        params_end = (-1.8, -1.7, -0.1, 0.1)  # 聚焦到一个有趣的区域
        
        self.generate_animation(
            fractal_type=FractalTypes.BURNING_SHIP,
            width=width,
            height=height,
            duration=duration,
            fps=fps,
            output_path=output_path,
            params_start=params_start,
            params_end=params_end,
            color_scheme=ColorSchemes.FIRE,
            coloring_method="smooth",
            max_iter=100
        )
    
    def lsystem_growth_animation(self, width=800, height=600, duration=5, fps=10, output_path="../results/lsystem_growth.mp4"):
        """生成分形植物生长动画"""
        self.generate_animation(
            fractal_type=FractalTypes.L_SYSTEM,
            width=width,
            height=height,
            duration=duration,
            fps=fps,
            output_path=output_path,
            params_start=1,
            params_end=6,
            color_scheme=ColorSchemes.GRADIENT,
            coloring_method="smooth",
            max_iter=100
        )
    
    def generate_parameter_animation(self, fractal_type, param_name, param_range, width=800, height=600,
                                   duration=10, fps=30, output_path="../results/parameter_animation.mp4"):
        """生成参数变化动画"""
        # 根据参数名和范围生成分形动画
        pass

if __name__ == "__main__":
    # 示例用法
    animator = FractalAnimator()
    
    # 生成朱利亚集合动画
    # animator.julia_animation()
    
    # 生成曼德博集合缩放动画
    # animator.mandelbrot_zoom_animation()
    
    # 生成燃烧船分形动画
    # animator.burning_ship_animation()
    
    # 生成分形植物生长动画
    animator.lsystem_growth_animation()
