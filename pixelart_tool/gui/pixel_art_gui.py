"""
像素艺术转换工具GUI界面
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
from PIL import Image, ImageTk
import os
import sys

# 添加父目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from image_processor import ImageProcessor
from pixel_editor import PixelEditor
from export_manager import ExportManager

class PixelArtGUI:
    """像素艺术GUI主类"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("像素艺术转换工具")
        
        # 初始化组件
        self.image_processor = ImageProcessor()
        self.pixel_editor = PixelEditor()
        self.export_manager = ExportManager()
        
        # 当前图像和预览
        self.current_image = None
        self.preview_image = None
        self.photo_image = None
        
        # GUI状态
        self.is_editing = False
        self.last_mouse_pos = None
        
        # 创建界面
        self.create_widgets()
        self.setup_layout()
        self.bind_events()
    
    def create_widgets(self):
        """创建界面组件"""
        
        # 菜单栏
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)
        
        # 文件菜单
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="打开图像", command=self.open_image)
        self.file_menu.add_command(label="保存图像", command=self.save_image)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="退出", command=self.root.quit)
        self.menu_bar.add_cascade(label="文件", menu=self.file_menu)
        
        # 编辑菜单
        self.edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.edit_menu.add_command(label="撤销", command=self.undo_edit)
        self.edit_menu.add_command(label="重做", command=self.redo_edit)
        self.menu_bar.add_cascade(label="编辑", menu=self.edit_menu)
        
        # 导出菜单
        self.export_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.export_menu.add_command(label="导出PNG", command=lambda: self.export_image('png'))
        self.export_menu.add_command(label="导出GIF", command=lambda: self.export_image('gif'))
        self.export_menu.add_command(label="导出ASCII", command=lambda: self.export_image('ascii'))
        self.menu_bar.add_cascade(label="导出", menu=self.export_menu)
        
        # 主框架
        self.main_frame = ttk.Frame(self.root)
        
        # 控制面板
        self.control_frame = ttk.LabelFrame(self.main_frame, text="控制面板", padding=10)
        
        # 像素大小控制
        self.pixel_size_label = ttk.Label(self.control_frame, text="像素大小:")
        self.pixel_size_var = tk.IntVar(value=10)
        self.pixel_size_scale = ttk.Scale(self.control_frame, from_=2, to=50, 
                                        variable=self.pixel_size_var, orient=tk.HORIZONTAL)
        self.pixel_size_value = ttk.Label(self.control_frame, text="10")
        
        # 颜色数量控制
        self.palette_size_label = ttk.Label(self.control_frame, text="颜色数量:")
        self.palette_size_var = tk.IntVar(value=16)
        self.palette_size_scale = ttk.Scale(self.control_frame, from_=2, to=256, 
                                          variable=self.palette_size_var, orient=tk.HORIZONTAL)
        self.palette_size_value = ttk.Label(self.control_frame, text="16")
        
        # 效果选项
        self.dither_var = tk.BooleanVar(value=True)
        self.dither_check = ttk.Checkbutton(self.control_frame, text="启用抖动", 
                                          variable=self.dither_var)
        
        self.outline_var = tk.BooleanVar(value=False)
        self.outline_check = ttk.Checkbutton(self.control_frame, text="添加轮廓", 
                                           variable=self.outline_var)
        
        # 风格选择
        self.style_label = ttk.Label(self.control_frame, text="艺术风格:")
        self.style_var = tk.StringVar(value="none")
        self.style_combo = ttk.Combobox(self.control_frame, textvariable=self.style_var,
                                       values=["none", "nes", "gameboy", "arcade"])
        
        # 处理按钮
        self.process_btn = ttk.Button(self.control_frame, text="应用效果", 
                                     command=self.process_image)
        
        # 编辑工具框架
        self.tool_frame = ttk.LabelFrame(self.control_frame, text="编辑工具")
        
        # 工具选择
        self.tool_var = tk.StringVar(value="pencil")
        self.pencil_btn = ttk.Radiobutton(self.tool_frame, text="铅笔", 
                                        variable=self.tool_var, value="pencil")
        self.brush_btn = ttk.Radiobutton(self.tool_frame, text="画笔", 
                                       variable=self.tool_var, value="brush")
        self.eraser_btn = ttk.Radiobutton(self.tool_frame, text="橡皮", 
                                        variable=self.tool_var, value="eraser")
        self.fill_btn = ttk.Radiobutton(self.tool_frame, text="填充", 
                                      variable=self.tool_var, value="fill")
        
        # 颜色选择
        self.color_frame = ttk.Frame(self.tool_frame)
        self.color_label = ttk.Label(self.color_frame, text="当前颜色:")
        self.color_canvas = tk.Canvas(self.color_frame, width=30, height=30, 
                                    bg='#ff0000', relief='sunken')
        self.color_btn = ttk.Button(self.color_frame, text="选择颜色", 
                                  command=self.choose_color)
        
        # 画笔大小
        self.brush_size_label = ttk.Label(self.tool_frame, text="画笔大小:")
        self.brush_size_var = tk.IntVar(value=1)
        self.brush_size_scale = ttk.Scale(self.tool_frame, from_=1, to=10, 
                                        variable=self.brush_size_var, orient=tk.HORIZONTAL)
        
        # 编辑模式切换
        self.edit_mode_var = tk.BooleanVar(value=False)
        self.edit_mode_btn = ttk.Checkbutton(self.control_frame, text="编辑模式", 
                                           variable=self.edit_mode_var, 
                                           command=self.toggle_edit_mode)
        
        # 预览区域
        self.preview_frame = ttk.LabelFrame(self.main_frame, text="预览", padding=10)
        self.canvas = tk.Canvas(self.preview_frame, bg='white', width=600, height=400)
        self.canvas_scroll_x = ttk.Scrollbar(self.preview_frame, orient=tk.HORIZONTAL, 
                                           command=self.canvas.xview)
        self.canvas_scroll_y = ttk.Scrollbar(self.preview_frame, orient=tk.VERTICAL, 
                                           command=self.canvas.yview)
        
        self.canvas.config(xscrollcommand=self.canvas_scroll_x.set,
                         yscrollcommand=self.canvas_scroll_y.set)
        
        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, 
                                  relief='sunken', anchor='w')
    
    def setup_layout(self):
        """设置布局"""
        
        # 主布局
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 控制面板布局
        self.control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        
        # 控制面板内容
        row = 0
        self.pixel_size_label.grid(row=row, column=0, sticky='w', pady=2)
        self.pixel_size_scale.grid(row=row, column=1, sticky='ew', pady=2)
        self.pixel_size_value.grid(row=row, column=2, padx=5, pady=2)
        row += 1
        
        self.palette_size_label.grid(row=row, column=0, sticky='w', pady=2)
        self.palette_size_scale.grid(row=row, column=1, sticky='ew', pady=2)
        self.palette_size_value.grid(row=row, column=2, padx=5, pady=2)
        row += 1
        
        self.dither_check.grid(row=row, column=0, columnspan=2, sticky='w', pady=2)
        row += 1
        
        self.outline_check.grid(row=row, column=0, columnspan=2, sticky='w', pady=2)
        row += 1
        
        self.style_label.grid(row=row, column=0, sticky='w', pady=2)
        self.style_combo.grid(row=row, column=1, sticky='ew', pady=2)
        row += 1
        
        self.process_btn.grid(row=row, column=0, columnspan=2, pady=10)
        row += 1
        
        # 编辑工具布局
        self.tool_frame.grid(row=row, column=0, columnspan=3, sticky='ew', pady=10)
        
        # 工具选择
        self.pencil_btn.grid(row=0, column=0, sticky='w')
        self.brush_btn.grid(row=0, column=1, sticky='w')
        self.eraser_btn.grid(row=1, column=0, sticky='w')
        self.fill_btn.grid(row=1, column=1, sticky='w')
        
        # 颜色选择
        self.color_frame.grid(row=2, column=0, columnspan=2, sticky='w', pady=5)
        self.color_label.pack(side=tk.LEFT)
        self.color_canvas.pack(side=tk.LEFT, padx=5)
        self.color_btn.pack(side=tk.LEFT)
        
        # 画笔大小
        self.brush_size_label.grid(row=3, column=0, sticky='w')
        self.brush_size_scale.grid(row=3, column=1, sticky='ew')
        
        # 编辑模式按钮
        self.edit_mode_btn.grid(row=row+1, column=0, columnspan=2, pady=10)
        
        # 预览区域布局
        self.preview_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.canvas.grid(row=0, column=0, sticky='nsew')
        self.canvas_scroll_x.grid(row=1, column=0, sticky='ew')
        self.canvas_scroll_y.grid(row=0, column=1, sticky='ns')
        
        self.preview_frame.grid_rowconfigure(0, weight=1)
        self.preview_frame.grid_columnconfigure(0, weight=1)
        
        # 状态栏
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 配置列权重
        self.control_frame.grid_columnconfigure(1, weight=1)
        self.tool_frame.grid_columnconfigure(1, weight=1)
    
    def bind_events(self):
        """绑定事件"""
        
        # 滑块值变化事件
        self.pixel_size_scale.configure(command=self.on_pixel_size_change)
        self.palette_size_scale.configure(command=self.on_palette_size_change)
        self.brush_size_scale.configure(command=self.on_brush_size_change)
        
        # 画布事件
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
    
    def on_pixel_size_change(self, value):
        """像素大小变化事件"""
        size = int(float(value))
        self.pixel_size_value.config(text=str(size))
    
    def on_palette_size_change(self, value):
        """调色板大小变化事件"""
        size = int(float(value))
        self.palette_size_value.config(text=str(size))
    
    def on_brush_size_change(self, value):
        """画笔大小变化事件"""
        size = int(float(value))
        self.pixel_editor.set_brush_size(size)
    
    def open_image(self):
        """打开图像文件"""
        file_path = filedialog.askopenfilename(
            title="选择图像文件",
            filetypes=[
                ("图像文件", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff"),
                ("所有文件", "*.*")
            ]
        )
        
        if file_path:
            if self.image_processor.load_image(file_path):
                self.current_image = self.image_processor.original_image
                self.update_preview()
                self.status_var.set(f"已加载: {os.path.basename(file_path)}")
            else:
                messagebox.showerror("错误", "无法加载图像文件")
    
    def process_image(self):
        """处理图像"""
        if self.current_image is None:
            messagebox.showwarning("警告", "请先打开图像文件")
            return
        
        try:
            # 获取参数
            pixel_size = self.pixel_size_var.get()
            palette_size = self.palette_size_var.get()
            dither = self.dither_var.get()
            outline = self.outline_var.get()
            style = self.style_var.get() if self.style_var.get() != "none" else None
            
            # 处理图像
            processed = self.image_processor.process_image(
                pixel_size, palette_size, dither, outline, style
            )
            
            if processed:
                self.preview_image = processed
                self.pixel_editor.set_image(processed)
                self.update_preview()
                self.status_var.set("图像处理完成")
            
        except Exception as e:
            messagebox.showerror("错误", f"处理图像时发生错误: {str(e)}")
    
    def update_preview(self):
        """更新预览"""
        if self.preview_image is None and self.current_image is None:
            return
        
        # 确定要显示的图像
        display_image = self.preview_image if self.preview_image else self.current_image
        
        # 调整显示大小
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            canvas_width, canvas_height = 600, 400
        
        # 计算缩放比例
        img_width, img_height = display_image.size
        scale_x = canvas_width / img_width
        scale_y = canvas_height / img_height
        scale = min(scale_x, scale_y, 1.0)  # 限制最大缩放为100%
        
        new_width = int(img_width * scale)
        new_height = int(img_height * scale)
        
        # 缩放图像
        resized = display_image.resize((new_width, new_height), Image.NEAREST)
        
        # 转换为PhotoImage
        self.photo_image = ImageTk.PhotoImage(resized)
        
        # 清空画布并显示图像
        self.canvas.delete("all")
        
        # 计算居中位置
        x = (canvas_width - new_width) // 2
        y = (canvas_height - new_height) // 2
        
        self.canvas.create_image(x, y, anchor=tk.NW, image=self.photo_image)
        
        # 更新滚动区域
        self.canvas.config(scrollregion=(0, 0, new_width, new_height))
    
    def toggle_edit_mode(self):
        """切换编辑模式"""
        self.is_editing = self.edit_mode_var.get()
        
        if self.is_editing:
            if self.preview_image is None:
                messagebox.showwarning("警告", "请先处理图像以进入编辑模式")
                self.edit_mode_var.set(False)
                return
            
            self.status_var.set("编辑模式已启用")
            # 启用编辑工具
            for widget in self.tool_frame.winfo_children():
                widget.configure(state='normal')
        else:
            self.status_var.set("编辑模式已禁用")
            # 禁用编辑工具
            for widget in self.tool_frame.winfo_children():
                widget.configure(state='disabled')
    
    def on_canvas_click(self, event):
        """画布点击事件"""
        if not self.is_editing or self.preview_image is None:
            return
        
        # 获取点击位置对应的图像坐标
        img_x, img_y = self.canvas_to_image_coords(event.x, event.y)
        
        if img_x is not None and img_y is not None:
            # 设置当前工具
            self.pixel_editor.set_tool(self.tool_var.get())
            
            # 执行编辑操作
            if self.tool_var.get() == "fill":
                self.pixel_editor.draw_pixel(img_x, img_y)
            else:
                self.pixel_editor.draw_pixel(img_x, img_y)
            
            # 更新预览
            self.preview_image = self.pixel_editor.image
            self.update_preview()
            
            self.last_mouse_pos = (img_x, img_y)
    
    def on_canvas_drag(self, event):
        """画布拖拽事件"""
        if not self.is_editing or self.preview_image is None or self.last_mouse_pos is None:
            return
        
        # 获取当前图像坐标
        img_x, img_y = self.canvas_to_image_coords(event.x, event.y)
        last_x, last_y = self.last_mouse_pos
        
        if img_x is not None and img_y is not None:
            # 绘制直线或连续点
            if self.tool_var.get() in ["pencil", "brush", "eraser"]:
                self.pixel_editor.draw_line(last_x, last_y, img_x, img_y)
            
            # 更新预览
            self.preview_image = self.pixel_editor.image
            self.update_preview()
            
            self.last_mouse_pos = (img_x, img_y)
    
    def on_canvas_release(self, event):
        """画布释放事件"""
        self.last_mouse_pos = None
    
    def canvas_to_image_coords(self, canvas_x, canvas_y):
        """将画布坐标转换为图像坐标"""
        if self.preview_image is None:
            return None, None
        
        # 获取图像显示信息
        img_width, img_height = self.preview_image.size
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        # 计算图像在画布中的位置
        scale_x = canvas_width / img_width
        scale_y = canvas_height / img_height
        scale = min(scale_x, scale_y, 1.0)
        
        new_width = int(img_width * scale)
        new_height = int(img_height * scale)
        
        x_offset = (canvas_width - new_width) // 2
        y_offset = (canvas_height - new_height) // 2
        
        # 转换为图像坐标
        img_x = int((canvas_x - x_offset) / scale)
        img_y = int((canvas_y - y_offset) / scale)
        
        # 检查边界
        if 0 <= img_x < img_width and 0 <= img_y < img_height:
            return img_x, img_y
        else:
            return None, None
    
    def choose_color(self):
        """选择颜色"""
        color = self.pixel_editor.choose_color()
        if color:
            # 更新颜色显示
            hex_color = '#{:02x}{:02x}{:02x}'.format(*color)
            self.color_canvas.config(bg=hex_color)
    
    def undo_edit(self):
        """撤销编辑"""
        if self.pixel_editor.undo():
            self.preview_image = self.pixel_editor.image
            self.update_preview()
            self.status_var.set("已撤销")
    
    def redo_edit(self):
        """重做编辑"""
        if self.pixel_editor.redo():
            self.preview_image = self.pixel_editor.image
            self.update_preview()
            self.status_var.set("已重做")
    
    def save_image(self):
        """保存图像"""
        if self.preview_image is None:
            messagebox.showwarning("警告", "没有可保存的图像")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="保存图像",
            defaultextension=".png",
            filetypes=[
                ("PNG图像", "*.png"),
                ("JPEG图像", "*.jpg"),
                ("所有文件", "*.*")
            ]
        )
        
        if file_path:
            if self.image_processor.save_image(file_path):
                self.status_var.set(f"图像已保存: {os.path.basename(file_path)}")
            else:
                messagebox.showerror("错误", "保存图像失败")
    
    def export_image(self, format_type):
        """导出图像"""
        if self.preview_image is None:
            messagebox.showwarning("警告", "没有可导出的图像")
            return
        
        if format_type == 'png':
            file_path = filedialog.asksaveasfilename(
                title="导出PNG",
                defaultextension=".png",
                filetypes=[("PNG图像", "*.png")]
            )
            if file_path:
                success = self.export_manager.export_png(self.preview_image, file_path)
        
        elif format_type == 'gif':
            file_path = filedialog.asksaveasfilename(
                title="导出GIF",
                defaultextension=".gif",
                filetypes=[("GIF图像", "*.gif")]
            )
            if file_path:
                success = self.export_manager.export_gif(self.preview_image, file_path)
        
        elif format_type == 'ascii':
            file_path = filedialog.asksaveasfilename(
                title="导出ASCII",
                defaultextension=".txt",
                filetypes=[("文本文件", "*.txt")]
            )
            if file_path:
                ascii_text = self.export_manager.image_to_ascii(self.preview_image)
                success = self.export_manager.save_ascii_art(ascii_text, file_path)
        
        if file_path and success:
            self.status_var.set(f"图像已导出: {os.path.basename(file_path)}")
        elif file_path:
            messagebox.showerror("错误", "导出图像失败")
    
    def on_resize(self, event):
        """窗口大小变化事件"""
        self.update_preview()