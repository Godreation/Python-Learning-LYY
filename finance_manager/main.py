#!/usr/bin/env python3
"""
个人财务管理系统 - 主程序入口
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

def check_dependencies():
    """检查必要的依赖包是否已安装"""
    required_packages = {
        'pandas': '数据处理和分析',
        'matplotlib': '图表生成',
        'openpyxl': 'Excel文件处理'
    }
    
    missing_packages = []
    
    for package, description in required_packages.items():
        try:
            __import__(package)
        except ImportError:
            missing_packages.append((package, description))
    
    return missing_packages

def install_dependencies():
    """安装缺失的依赖包"""
    missing_packages = check_dependencies()
    
    if not missing_packages:
        return True
    
    print("检测到缺失的依赖包:")
    for package, description in missing_packages:
        print(f"  - {package}: {description}")
    
    response = input("\n是否自动安装这些依赖包？(y/n): ").lower().strip()
    
    if response in ['y', 'yes', '是']:
        try:
            import subprocess
            import sys
            
            for package, _ in missing_packages:
                print(f"正在安装 {package}...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            
            print("\n所有依赖包安装完成！")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"安装失败: {e}")
            return False
    else:
        print("请手动安装依赖包后重新运行程序。")
        print("安装命令: pip install pandas matplotlib openpyxl")
        return False

def main():
    """主程序入口"""
    # 检查并安装依赖
    if not install_dependencies():
        input("按回车键退出...")
        return
    
    # 导入GUI模块
    try:
        from gui import FinanceManagerGUI
    except ImportError as e:
        print(f"导入模块失败: {e}")
        input("按回车键退出...")
        return
    
    # 创建主窗口
    root = tk.Tk()
    
    # 设置窗口图标（如果有的话）
    try:
        if hasattr(sys, '_MEIPASS'):
            # PyInstaller打包后的路径
            icon_path = os.path.join(sys._MEIPASS, 'icon.ico')
        else:
            # 开发环境路径
            icon_path = os.path.join(os.path.dirname(__file__), 'icon.ico')
        
        if os.path.exists(icon_path):
            root.iconbitmap(icon_path)
    except:
        pass  # 图标文件不存在也没关系
    
    # 创建应用
    app = FinanceManagerGUI(root)
    
    # 处理窗口关闭事件
    def on_closing():
        if messagebox.askokcancel("退出", "确定要退出个人财务管理系统吗？"):
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # 启动主循环
    try:
        root.mainloop()
    except Exception as e:
        print(f"程序运行错误: {e}")
        input("按回车键退出...")

if __name__ == "__main__":
    main()