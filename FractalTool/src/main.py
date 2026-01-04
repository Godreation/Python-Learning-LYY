#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
分形探索工具 - 主入口文件

该工具用于生成和探索各种分形图案，包括：
- 曼德博集合和朱利亚集合
- 迭代函数系统（IFS）
- L-系统（用于植物模拟）
- 3D分形（曼德球、分形地形）

使用方法：
1. 运行UI界面：python main.py ui
2. 生成动画：python main.py animation [animation_type]
3. 生成3D分形：python main.py 3d [3d_type]
"""

import sys
import argparse
from ui import FractalUI
from animation import FractalAnimator
from fractals_3d import Fractal3D

def run_ui():
    """运行UI界面"""
    print("启动分形探索工具UI...")
    ui = FractalUI()
    ui.run()

def run_animation(animation_type):
    """运行动画生成"""
    print(f"生成{animation_type}动画...")
    animator = FractalAnimator()
    
    if animation_type == "julia":
        animator.julia_animation()
    elif animation_type == "mandelbrot_zoom":
        animator.mandelbrot_zoom_animation()
    elif animation_type == "burning_ship":
        animator.burning_ship_animation()
    elif animation_type == "lsystem_growth":
        animator.lsystem_growth_animation()
    else:
        print(f"未知的动画类型: {animation_type}")
        print("可用的动画类型: julia, mandelbrot_zoom, burning_ship, lsystem_growth")

def run_3d(three_d_type):
    """运行3D分形生成"""
    print(f"生成{three_d_type} 3D分形...")
    
    if three_d_type == "terrain":
        Fractal3D.generate_and_render_terrain()
    elif three_d_type == "mandelbulb":
        Fractal3D.generate_mandelbulb_slices(width=50, height=50, depth=50)
    else:
        print(f"未知的3D分形类型: {three_d_type}")
        print("可用的3D分形类型: terrain, mandelbulb")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="分形探索工具")
    parser.add_argument("command", choices=["ui", "animation", "3d"], help="要执行的命令")
    parser.add_argument("type", nargs="?", help="命令类型（适用于animation和3d命令）")
    
    args = parser.parse_args()
    
    if args.command == "ui":
        run_ui()
    elif args.command == "animation":
        if args.type:
            run_animation(args.type)
        else:
            parser.error("animation命令需要指定类型")
    elif args.command == "3d":
        if args.type:
            run_3d(args.type)
        else:
            parser.error("3d命令需要指定类型")

if __name__ == "__main__":
    main()
