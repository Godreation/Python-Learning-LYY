import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class DataProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("实验数据处理系统")
        self.root.geometry("1000x700")
        
        self.data = None
        self.current_figure = None
        
        # 创建主框架
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 顶部按钮栏
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(fill=tk.X, pady=5)
        
        # 导入按钮
        self.import_btn = ttk.Button(self.button_frame, text="导入Excel数据", command=self.import_excel)
        self.import_btn.pack(side=tk.LEFT, padx=5)
        
        # 导出按钮
        self.export_btn = ttk.Button(self.button_frame, text="导出Excel数据", command=self.export_excel, state=tk.DISABLED)
        self.export_btn.pack(side=tk.LEFT, padx=5)
        
        # 数据信息标签
        self.data_info = ttk.Label(self.button_frame, text="未导入数据")
        self.data_info.pack(side=tk.RIGHT, padx=5)
        
        # 中间分割框架
        self.middle_frame = ttk.Frame(self.main_frame)
        self.middle_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 左侧数据处理框架
        self.process_frame = ttk.LabelFrame(self.middle_frame, text="数据处理", padding="10")
        self.process_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # 数据预览表格
        self.preview_frame = ttk.LabelFrame(self.process_frame, text="数据预览", padding="10")
        self.preview_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 创建表格
        self.tree = ttk.Treeview(self.preview_frame)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 添加滚动条
        self.scrollbar = ttk.Scrollbar(self.preview_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        
        # 数据分析按钮
        self.analysis_frame = ttk.LabelFrame(self.process_frame, text="数据分析", padding="10")
        self.analysis_frame.pack(fill=tk.X, pady=5)
        
        self.describe_btn = ttk.Button(self.analysis_frame, text="统计描述", command=self.show_describe, state=tk.DISABLED)
        self.describe_btn.pack(side=tk.LEFT, padx=5)
        
        # 右侧可视化框架
        self.visual_frame = ttk.LabelFrame(self.middle_frame, text="数据可视化", padding="10")
        self.visual_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        
        # 图表类型选择
        self.chart_type_frame = ttk.Frame(self.visual_frame)
        self.chart_type_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(self.chart_type_frame, text="图表类型:").pack(side=tk.LEFT, padx=5)
        self.chart_type = ttk.Combobox(self.chart_type_frame, values=["折线图", "散点图", "柱状图", "直方图"])
        self.chart_type.pack(side=tk.LEFT, padx=5)
        self.chart_type.current(0)
        
        # X轴和Y轴选择
        self.axis_frame = ttk.Frame(self.visual_frame)
        self.axis_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(self.axis_frame, text="X轴:").pack(side=tk.LEFT, padx=5)
        self.x_axis = ttk.Combobox(self.axis_frame, state="readonly")
        self.x_axis.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        ttk.Label(self.axis_frame, text="Y轴:").pack(side=tk.LEFT, padx=5)
        self.y_axis = ttk.Combobox(self.axis_frame, state="readonly")
        self.y_axis.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        # 绘图按钮
        self.plot_btn = ttk.Button(self.visual_frame, text="生成图表", command=self.generate_plot, state=tk.DISABLED)
        self.plot_btn.pack(fill=tk.X, pady=5)
        
        # 保存图片按钮
        self.save_img_btn = ttk.Button(self.visual_frame, text="保存图片", command=self.save_plot, state=tk.DISABLED)
        self.save_img_btn.pack(fill=tk.X, pady=5)
        
        # 图表显示区域
        self.plot_frame = ttk.Frame(self.visual_frame)
        self.plot_frame.pack(fill=tk.BOTH, expand=True, pady=5)
    
    def import_excel(self):
        """导入Excel数据"""
        file_path = filedialog.askopenfilename(
            filetypes=[("Excel文件", "*.xlsx *.xls")],
            title="选择Excel文件"
        )
        
        if file_path:
            try:
                self.data = pd.read_excel(file_path)
                self.update_data_info()
                self.update_treeview()
                self.update_axis_options()
                self.enable_widgets()
                messagebox.showinfo("成功", "数据导入成功")
            except Exception as e:
                messagebox.showerror("错误", f"导入失败: {str(e)}")
    
    def export_excel(self):
        """导出Excel数据"""
        if self.data is not None:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel文件", "*.xlsx")],
                title="保存Excel文件"
            )
            
            if file_path:
                try:
                    self.data.to_excel(file_path, index=False)
                    messagebox.showinfo("成功", "数据导出成功")
                except Exception as e:
                    messagebox.showerror("错误", f"导出失败: {str(e)}")
    
    def update_data_info(self):
        """更新数据信息"""
        if self.data is not None:
            rows, cols = self.data.shape
            self.data_info.config(text=f"数据大小: {rows}行 × {cols}列")
    
    def update_treeview(self):
        """更新数据预览表格"""
        # 清空现有表格
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 设置列
        self.tree["columns"] = list(self.data.columns)
        self.tree["show"] = "headings"
        
        # 设置列标题
        for col in self.data.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        # 插入数据
        for _, row in self.data.iterrows():
            self.tree.insert("", tk.END, values=list(row))
    
    def update_axis_options(self):
        """更新坐标轴选项"""
        if self.data is not None:
            columns = list(self.data.columns)
            self.x_axis["values"] = columns
            self.y_axis["values"] = columns
            if columns:
                self.x_axis.current(0)
                self.y_axis.current(1 if len(columns) > 1 else 0)
    
    def enable_widgets(self):
        """启用控件"""
        self.export_btn.config(state=tk.NORMAL)
        self.describe_btn.config(state=tk.NORMAL)
        self.plot_btn.config(state=tk.NORMAL)
    
    def show_describe(self):
        """显示数据统计描述"""
        if self.data is not None:
            describe_df = self.data.describe()
            # 创建新窗口显示统计结果
            describe_window = tk.Toplevel(self.root)
            describe_window.title("统计描述")
            describe_window.geometry("600x400")
            
            # 创建表格
            tree = ttk.Treeview(describe_window)
            tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # 添加滚动条
            scrollbar = ttk.Scrollbar(describe_window, orient=tk.VERTICAL, command=tree.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            tree.configure(yscrollcommand=scrollbar.set)
            
            # 设置列
            tree["columns"] = list(describe_df.columns)
            tree["show"] = "headings"
            
            # 设置列标题
            for col in describe_df.columns:
                tree.heading(col, text=col)
                tree.column(col, width=100)
            
            # 插入数据
            for idx, row in describe_df.iterrows():
                values = [f"{val:.4f}" if isinstance(val, (int, float)) else str(val) for val in row]
                tree.insert("", tk.END, values=values, text=str(idx))
    
    def generate_plot(self):
        """生成图表"""
        if self.data is None:
            return
        
        x_col = self.x_axis.get()
        y_col = self.y_axis.get()
        chart_type = self.chart_type.get()
        
        if not x_col or not y_col:
            messagebox.showerror("错误", "请选择X轴和Y轴")
            return
        
        # 清空之前的图表
        for widget in self.plot_frame.winfo_children():
            widget.destroy()
        
        # 创建新图表
        fig, ax = plt.subplots(figsize=(8, 6))
        
        try:
            if chart_type == "折线图":
                ax.plot(self.data[x_col], self.data[y_col], marker='o')
            elif chart_type == "散点图":
                ax.scatter(self.data[x_col], self.data[y_col])
            elif chart_type == "柱状图":
                ax.bar(self.data[x_col], self.data[y_col])
            elif chart_type == "直方图":
                ax.hist(self.data[y_col], bins=10)
            
            ax.set_xlabel(x_col)
            ax.set_ylabel(y_col)
            ax.set_title(f"{chart_type}: {y_col} vs {x_col}")
            ax.grid(True, alpha=0.3)
            
            # 显示图表
            canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
            self.current_figure = fig
            self.save_img_btn.config(state=tk.NORMAL)
            
        except Exception as e:
            messagebox.showerror("错误", f"绘图失败: {str(e)}")
            plt.close(fig)
    
    def save_plot(self):
        """保存图表为图片"""
        if self.current_figure is None:
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG图片", "*.png"), ("JPG图片", "*.jpg"), ("SVG图片", "*.svg")],
            title="保存图表"
        )
        
        if file_path:
            try:
                self.current_figure.savefig(file_path, dpi=300, bbox_inches='tight')
                messagebox.showinfo("成功", "图片保存成功")
            except Exception as e:
                messagebox.showerror("错误", f"保存失败: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = DataProcessorApp(root)
    root.mainloop()
