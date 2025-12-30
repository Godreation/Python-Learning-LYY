#!/usr/bin/env python3
"""
像素艺术转换工具测试脚本
"""

import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from image_processor import ImageProcessor
from pixel_editor import PixelEditor
from export_manager import ExportManager

def test_image_processor():
    """测试图像处理器"""
    print("测试图像处理器...")
    
    processor = ImageProcessor()
    
    # 创建一个测试图像
    from PIL import Image
    import numpy as np
    
    # 创建简单的测试图像
    test_array = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    test_image = Image.fromarray(test_array)
    test_image.save("test_input.png")
    
    # 测试加载和处理
    if processor.load_image("test_input.png"):
        print("✓ 图像加载成功")
        
        # 测试处理
        processed = processor.process_image(
            pixel_size=10,
            palette_size=16,
            dither=True,
            outline=False,
            style="nes"
        )
        
        if processed:
            print("✓ 图像处理成功")
            processed.save("test_output.png")
            print("✓ 测试图像已保存为 test_output.png")
            
            # 测试调色板提取
            palette = processor.get_color_palette()
            print(f"✓ 提取到 {len(palette)} 种颜色")
        else:
            print("✗ 图像处理失败")
    else:
        print("✗ 图像加载失败")
    
    # 清理测试文件
    if os.path.exists("test_input.png"):
        os.remove("test_input.png")
    
    print()

def test_pixel_editor():
    """测试像素编辑器"""
    print("测试像素编辑器...")
    
    editor = PixelEditor()
    
    # 创建测试图像
    from PIL import Image
    import numpy as np
    
    test_array = np.ones((50, 50, 3), dtype=np.uint8) * 255  # 白色背景
    test_image = Image.fromarray(test_array)
    
    # 设置图像
    editor.set_image(test_image)
    print("✓ 图像设置成功")
    
    # 测试绘图
    editor.set_color((255, 0, 0))  # 红色
    editor.set_tool("pencil")
    editor.draw_pixel(10, 10)
    print("✓ 像素绘制成功")
    
    # 测试撤销
    if editor.undo():
        print("✓ 撤销功能正常")
    
    # 测试重做
    if editor.redo():
        print("✓ 重做功能正常")
    
    print()

def test_export_manager():
    """测试导出管理器"""
    print("测试导出管理器...")
    
    exporter = ExportManager()
    
    # 创建测试图像
    from PIL import Image
    import numpy as np
    
    test_array = np.random.randint(0, 255, (30, 30, 3), dtype=np.uint8)
    test_image = Image.fromarray(test_array)
    
    # 测试PNG导出
    if exporter.export_png(test_image, "test_export.png"):
        print("✓ PNG导出成功")
    
    # 测试ASCII转换
    ascii_art = exporter.image_to_ascii(test_image, width=40)
    if ascii_art:
        print("✓ ASCII转换成功")
        print("示例ASCII艺术:")
        print(ascii_art[:200] + "...")  # 显示前200个字符
    
    # 清理测试文件
    if os.path.exists("test_export.png"):
        os.remove("test_export.png")
    
    print()

def main():
    """主测试函数"""
    print("=" * 50)
    print("像素艺术转换工具测试")
    print("=" * 50)
    print()
    
    try:
        test_image_processor()
        test_pixel_editor()
        test_export_manager()
        
        print("=" * 50)
        print("所有测试完成！")
        print("=" * 50)
        
        # 测试GUI启动
        print("\n测试GUI启动...")
        try:
            from gui.pixel_art_gui import PixelArtGUI
            import tkinter as tk
            
            # 创建简单窗口测试
            root = tk.Tk()
            root.withdraw()  # 隐藏主窗口
            
            # 测试GUI类实例化
            app = PixelArtGUI(root)
            print("✓ GUI类实例化成功")
            
            root.destroy()
            
        except Exception as e:
            print(f"✗ GUI测试失败: {e}")
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()