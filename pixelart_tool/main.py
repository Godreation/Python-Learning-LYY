#!/usr/bin/env python3
"""
像素艺术转换工具主程序
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import sys

# 添加项目路径到系统路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gui.pixel_art_gui import PixelArtGUI

def main():
    """主函数"""
    root = tk.Tk()
    root.title("像素艺术转换工具")
    root.geometry("1200x800")
    
    # 创建主界面
    app = PixelArtGUI(root)
    
    # 启动主循环
    root.mainloop()

if __name__ == "__main__":
    main()