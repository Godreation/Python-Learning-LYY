import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
from PIL import Image, ImageTk
import time
from image_processor import ImageProcessor

class ImageProcessingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("批量图片处理工具")
        self.root.geometry("1200x800")
        
        # 初始化处理器
        self.processor = ImageProcessor()
        
        # 存储变量
        self.image_files = []
        self.processing_queue = []
        self.current_preview_index = -1
        self.operations = []
        self.output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "output")
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 顶部工具栏
        self.toolbar = ttk.Frame(self.main_frame)
        self.toolbar.pack(fill=tk.X, pady=(0, 10))
        
        # 添加文件按钮
        self.add_files_btn = ttk.Button(self.toolbar, text="添加文件", command=self.add_files)
        self.add_files_btn.pack(side=tk.LEFT, padx=5)
        
        # 添加文件夹按钮
        self.add_folder_btn = ttk.Button(self.toolbar, text="添加文件夹", command=self.add_folder)
        self.add_folder_btn.pack(side=tk.LEFT, padx=5)
        
        # 清除文件按钮
        self.clear_files_btn = ttk.Button(self.toolbar, text="清除文件", command=self.clear_files)
        self.clear_files_btn.pack(side=tk.LEFT, padx=5)
        
        # 设置输出目录按钮
        self.set_output_btn = ttk.Button(self.toolbar, text="设置输出目录", command=self.set_output_dir)
        self.set_output_btn.pack(side=tk.LEFT, padx=5)
        
        # 开始处理按钮
        self.start_process_btn = ttk.Button(self.toolbar, text="开始处理", command=self.start_processing)
        self.start_process_btn.pack(side=tk.LEFT, padx=5)
        
        # 主内容区域（左右布局）
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        
        # 左侧：文件列表和预览
        self.left_frame = ttk.Frame(self.content_frame, width=400)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 10))
        
        # 文件列表
        self.file_list_frame = ttk.LabelFrame(self.left_frame, text="文件列表")
        self.file_list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 文件列表树
        self.file_tree = ttk.Treeview(self.file_list_frame, columns=('name', 'size', 'path'), show='headings')
        self.file_tree.heading('name', text='文件名')
        self.file_tree.heading('size', text='大小')
        self.file_tree.heading('path', text='路径')
        self.file_tree.column('name', width=150)
        self.file_tree.column('size', width=80)
        self.file_tree.column('path', width=300)
        self.file_tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        # 文件列表滚动条
        self.file_scrollbar = ttk.Scrollbar(self.file_list_frame, orient=tk.VERTICAL, command=self.file_tree.yview)
        self.file_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.file_tree.configure(yscrollcommand=self.file_scrollbar.set)
        
        # 文件列表绑定事件
        self.file_tree.bind('<<TreeviewSelect>>', self.on_file_select)
        
        # 预览面板
        self.preview_frame = ttk.LabelFrame(self.left_frame, text="预览")
        self.preview_frame.pack(fill=tk.BOTH, expand=True)
        
        # 预览画布
        self.preview_canvas = tk.Canvas(self.preview_frame, bg="#f0f0f0")
        self.preview_canvas.pack(fill=tk.BOTH, expand=True)
        
        # 右侧：操作配置和处理队列
        self.right_frame = ttk.Frame(self.content_frame)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 操作配置面板
        self.operation_frame = ttk.LabelFrame(self.right_frame, text="操作配置")
        self.operation_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 操作类型选择
        self.operation_type_frame = ttk.Frame(self.operation_frame)
        self.operation_type_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(self.operation_type_frame, text="操作类型：").pack(side=tk.LEFT, padx=5)
        self.operation_type = ttk.Combobox(self.operation_type_frame, values=[
            "调整大小", "格式转换", "添加文字水印", "添加图片水印", "重命名", "压缩"
        ])
        self.operation_type.current(0)
        self.operation_type.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # 操作参数配置
        self.operation_params_frame = ttk.Frame(self.operation_frame)
        self.operation_params_frame.pack(fill=tk.BOTH, expand=True)
        
        # 根据操作类型显示不同的参数配置
        self.operation_type.bind('<<ComboboxSelected>>', self.update_operation_params)
        self.update_operation_params()
        
        # 添加操作按钮
        self.add_operation_btn = ttk.Button(self.operation_frame, text="添加操作", command=self.add_operation)
        self.add_operation_btn.pack(fill=tk.X, pady=(10, 0))
        
        # 处理队列和进度
        self.queue_frame = ttk.LabelFrame(self.right_frame, text="处理队列")
        self.queue_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 队列列表
        self.queue_tree = ttk.Treeview(self.queue_frame, columns=('operation', 'params'), show='headings')
        self.queue_tree.heading('operation', text='操作')
        self.queue_tree.heading('params', text='参数')
        self.queue_tree.column('operation', width=150)
        self.queue_tree.column('params', width=300)
        self.queue_tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        # 队列滚动条
        self.queue_scrollbar = ttk.Scrollbar(self.queue_frame, orient=tk.VERTICAL, command=self.queue_tree.yview)
        self.queue_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.queue_tree.configure(yscrollcommand=self.queue_scrollbar.set)
        
        # 移除操作按钮
        self.remove_operation_btn = ttk.Button(self.queue_frame, text="移除操作", command=self.remove_operation)
        self.remove_operation_btn.pack(fill=tk.X, pady=(10, 0))
        
        # 进度显示
        self.progress_frame = ttk.LabelFrame(self.right_frame, text="处理进度")
        self.progress_frame.pack(fill=tk.BOTH, expand=False, pady=(0, 10))
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, padx=5, pady=5)
        
        self.progress_label = ttk.Label(self.progress_frame, text="就绪")
        self.progress_label.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        # 处理前后对比视图
        self.compare_frame = ttk.LabelFrame(self.main_frame, text="处理前后对比")
        self.compare_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # 对比画布容器
        self.compare_canvas_frame = ttk.Frame(self.compare_frame)
        self.compare_canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        # 原图预览
        self.before_frame = ttk.LabelFrame(self.compare_canvas_frame, text="原图", width=400)
        self.before_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        self.before_canvas = tk.Canvas(self.before_frame, bg="#f0f0f0")
        self.before_canvas.pack(fill=tk.BOTH, expand=True)
        
        # 处理后预览
        self.after_frame = ttk.LabelFrame(self.compare_canvas_frame, text="处理后", width=400)
        self.after_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        self.after_canvas = tk.Canvas(self.after_frame, bg="#f0f0f0")
        self.after_canvas.pack(fill=tk.BOTH, expand=True)
        
        # 初始化操作参数
        self.operation_params = {}
    
    def add_files(self):
        """添加文件"""
        files = filedialog.askopenfilenames(
            title="选择图片文件",
            filetypes=[("图片文件", "*.jpg *.jpeg *.png *.webp *.bmp *.gif"), ("所有文件", "*")]
        )
        
        if files:
            for file_path in files:
                if file_path not in self.image_files:
                    self.image_files.append(file_path)
                    size = os.path.getsize(file_path)
                    size_str = f"{size/1024:.2f} KB"
                    name = os.path.basename(file_path)
                    self.file_tree.insert('', tk.END, values=(name, size_str, file_path))
    
    def add_folder(self):
        """添加文件夹"""
        folder = filedialog.askdirectory(title="选择文件夹")
        
        if folder:
            for root, dirs, files in os.walk(folder):
                for file in files:
                    if file.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.bmp', '.gif')):
                        file_path = os.path.join(root, file)
                        if file_path not in self.image_files:
                            self.image_files.append(file_path)
                            size = os.path.getsize(file_path)
                            size_str = f"{size/1024:.2f} KB"
                            name = os.path.basename(file_path)
                            self.file_tree.insert('', tk.END, values=(name, size_str, file_path))
    
    def clear_files(self):
        """清除文件列表"""
        if messagebox.askyesno("确认", "确定要清除所有文件吗？"):
            self.image_files = []
            for item in self.file_tree.get_children():
                self.file_tree.delete(item)
            self.clear_preview()
    
    def set_output_dir(self):
        """设置输出目录"""
        directory = filedialog.askdirectory(title="选择输出目录")
        if directory:
            self.output_dir = directory
            messagebox.showinfo("成功", f"输出目录已设置为：{directory}")
    
    def on_file_select(self, event):
        """文件选择事件"""
        selected_items = self.file_tree.selection()
        if selected_items:
            item = selected_items[0]
            file_path = self.file_tree.item(item, 'values')[2]
            self.show_preview(file_path)
    
    def show_preview(self, file_path):
        """显示图片预览"""
        try:
            img = Image.open(file_path)
            # 调整图片大小以适应预览窗口
            max_width = self.preview_canvas.winfo_width() - 20
            max_height = self.preview_canvas.winfo_height() - 20
            img.thumbnail((max_width, max_height), Image.LANCZOS)
            
            # 转换为Tkinter可用的图片格式
            photo = ImageTk.PhotoImage(img)
            
            # 清除画布
            self.preview_canvas.delete("all")
            
            # 计算居中位置
            x = (self.preview_canvas.winfo_width() - img.width) // 2
            y = (self.preview_canvas.winfo_height() - img.height) // 2
            
            # 显示图片
            self.preview_canvas.create_image(x, y, anchor=tk.NW, image=photo)
            
            # 保存引用，防止被垃圾回收
            self.preview_photo = photo
        except Exception as e:
            self.preview_canvas.delete("all")
            self.preview_canvas.create_text(150, 100, text=f"无法预览图片\n{str(e)}", anchor=tk.CENTER)
    
    def clear_preview(self):
        """清除预览"""
        self.preview_canvas.delete("all")
        self.before_canvas.delete("all")
        self.after_canvas.delete("all")
    
    def update_operation_params(self, event=None):
        """更新操作参数配置"""
        # 清除现有参数配置
        for widget in self.operation_params_frame.winfo_children():
            widget.destroy()
        
        # 获取当前操作类型
        op_type = self.operation_type.get()
        
        if op_type == "调整大小":
            # 调整大小参数
            ttk.Label(self.operation_params_frame, text="调整方式：").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
            resize_method = ttk.Combobox(self.operation_params_frame, values=["按比例", "固定大小"])
            resize_method.current(0)
            resize_method.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W, columnspan=2)
            
            ttk.Label(self.operation_params_frame, text="比例：").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
            scale_var = tk.DoubleVar(value=0.5)
            scale_entry = ttk.Entry(self.operation_params_frame, textvariable=scale_var)
            scale_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
            
            ttk.Label(self.operation_params_frame, text="宽度：").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
            width_var = tk.IntVar(value=800)
            width_entry = ttk.Entry(self.operation_params_frame, textvariable=width_var)
            width_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
            
            ttk.Label(self.operation_params_frame, text="高度：").grid(row=2, column=2, sticky=tk.W, padx=5, pady=5)
            height_var = tk.IntVar(value=600)
            height_entry = ttk.Entry(self.operation_params_frame, textvariable=height_var)
            height_entry.grid(row=2, column=3, padx=5, pady=5, sticky=tk.W)
            
            ttk.Label(self.operation_params_frame, text="保持宽高比：").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
            keep_ratio_var = tk.BooleanVar(value=True)
            keep_ratio_check = ttk.Checkbutton(self.operation_params_frame, variable=keep_ratio_var)
            keep_ratio_check.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
            
            self.operation_params = {
                'resize_method': resize_method,
                'scale': scale_var,
                'width': width_var,
                'height': height_var,
                'keep_ratio': keep_ratio_var
            }
        
        elif op_type == "格式转换":
            # 格式转换参数
            ttk.Label(self.operation_params_frame, text="目标格式：").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
            format_var = ttk.Combobox(self.operation_params_frame, values=["JPEG", "PNG", "WebP", "BMP", "GIF"])
            format_var.current(0)
            format_var.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W, columnspan=2)
            
            self.operation_params = {
                'format': format_var
            }
        
        elif op_type == "添加文字水印":
            # 文字水印参数
            ttk.Label(self.operation_params_frame, text="水印文字：").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
            text_var = tk.StringVar(value="水印")
            text_entry = ttk.Entry(self.operation_params_frame, textvariable=text_var)
            text_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W, columnspan=2)
            
            ttk.Label(self.operation_params_frame, text="位置：").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
            position_var = ttk.Combobox(self.operation_params_frame, values=["top-left", "top-right", "bottom-left", "bottom-right"])
            position_var.current(3)
            position_var.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
            
            ttk.Label(self.operation_params_frame, text="字体大小：").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
            font_size_var = tk.IntVar(value=20)
            font_size_entry = ttk.Entry(self.operation_params_frame, textvariable=font_size_var)
            font_size_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
            
            self.operation_params = {
                'text': text_var,
                'position': position_var,
                'font_size': font_size_var
            }
        
        elif op_type == "添加图片水印":
            # 图片水印参数
            ttk.Label(self.operation_params_frame, text="水印图片：").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
            watermark_path_var = tk.StringVar()
            watermark_entry = ttk.Entry(self.operation_params_frame, textvariable=watermark_path_var)
            watermark_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W, columnspan=2)
            
            def browse_watermark():
                path = filedialog.askopenfilename(title="选择水印图片", filetypes=[("图片文件", "*.png *.jpg *.jpeg")])
                if path:
                    watermark_path_var.set(path)
            
            browse_btn = ttk.Button(self.operation_params_frame, text="浏览", command=browse_watermark)
            browse_btn.grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)
            
            ttk.Label(self.operation_params_frame, text="位置：").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
            position_var = ttk.Combobox(self.operation_params_frame, values=["top-left", "top-right", "bottom-left", "bottom-right"])
            position_var.current(3)
            position_var.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
            
            ttk.Label(self.operation_params_frame, text="透明度：").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
            opacity_var = tk.DoubleVar(value=0.5)
            opacity_entry = ttk.Entry(self.operation_params_frame, textvariable=opacity_var)
            opacity_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
            
            self.operation_params = {
                'watermark_path': watermark_path_var,
                'position': position_var,
                'opacity': opacity_var
            }
        
        elif op_type == "重命名":
            # 重命名参数
            ttk.Label(self.operation_params_frame, text="命名规则：").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
            rename_pattern_var = tk.StringVar(value="image_{index}")
            rename_pattern_entry = ttk.Entry(self.operation_params_frame, textvariable=rename_pattern_var)
            rename_pattern_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W, columnspan=2)
            
            self.operation_params = {
                'rename_pattern': rename_pattern_var
            }
        
        elif op_type == "压缩":
            # 压缩参数
            ttk.Label(self.operation_params_frame, text="压缩质量：").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
            quality_var = tk.IntVar(value=85)
            quality_scale = ttk.Scale(self.operation_params_frame, from_=1, to=100, orient=tk.HORIZONTAL, variable=quality_var)
            quality_scale.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W, columnspan=2)
            
            quality_label = ttk.Label(self.operation_params_frame, textvariable=quality_var)
            quality_label.grid(row=0, column=3, sticky=tk.W, padx=5, pady=5)
            
            self.operation_params = {
                'quality': quality_var
            }
    
    def add_operation(self):
        """添加操作到队列"""
        op_type = self.operation_type.get()
        params = {}
        
        if op_type == "调整大小":
            resize_method = self.operation_params['resize_method'].get()
            if resize_method == "按比例":
                params = {
                    'scale': self.operation_params['scale'].get(),
                    'keep_aspect_ratio': self.operation_params['keep_ratio'].get()
                }
            else:
                params = {
                    'width': self.operation_params['width'].get(),
                    'height': self.operation_params['height'].get(),
                    'keep_aspect_ratio': self.operation_params['keep_ratio'].get()
                }
            operation = {'type': 'resize', 'params': params}
        
        elif op_type == "格式转换":
            params = {'format': self.operation_params['format'].get()}
            operation = {'type': 'convert', 'params': params}
        
        elif op_type == "添加文字水印":
            params = {
                'text': self.operation_params['text'].get(),
                'position': self.operation_params['position'].get(),
                'font_size': self.operation_params['font_size'].get()
            }
            operation = {'type': 'text_watermark', 'params': params}
        
        elif op_type == "添加图片水印":
            params = {
                'watermark_path': self.operation_params['watermark_path'].get(),
                'position': self.operation_params['position'].get(),
                'opacity': self.operation_params['opacity'].get()
            }
            operation = {'type': 'image_watermark', 'params': params}
        
        elif op_type == "重命名":
            params = {'rename_pattern': self.operation_params['rename_pattern'].get()}
            operation = {'type': 'rename', 'params': params}
        
        elif op_type == "压缩":
            params = {'quality': self.operation_params['quality'].get()}
            operation = {'type': 'compress', 'params': params}
        
        # 添加到操作列表
        self.operations.append(operation)
        
        # 添加到队列树
        params_str = "".join([f"{k}: {v}, " for k, v in params.items()])[:-2]
        self.queue_tree.insert('', tk.END, values=(op_type, params_str))
    
    def remove_operation(self):
        """从队列中移除操作"""
        selected_items = self.queue_tree.selection()
        if selected_items:
            for item in selected_items:
                index = self.queue_tree.index(item)
                if 0 <= index < len(self.operations):
                    del self.operations[index]
                self.queue_tree.delete(item)
    
    def start_processing(self):
        """开始处理"""
        if not self.image_files:
            messagebox.showwarning("警告", "请先添加图片文件")
            return
        
        if not self.operations:
            messagebox.showwarning("警告", "请先添加处理操作")
            return
        
        # 创建输出目录
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 禁用开始按钮
        self.start_process_btn.config(state=tk.DISABLED)
        
        # 重置进度
        self.progress_var.set(0)
        self.progress_label.config(text="开始处理...")
        
        # 启动处理线程
        threading.Thread(target=self.process_images, daemon=True).start()
    
    def process_images(self):
        """处理图片"""
        total_files = len(self.image_files)
        processed_files = 0
        
        try:
            for i, file_path in enumerate(self.image_files):
                # 处理单个图片
                output_path = os.path.join(self.output_dir, os.path.basename(file_path))
                
                # 执行所有操作
                temp_path = file_path
                for operation in self.operations:
                    op_type = operation['type']
                    params = operation['params']
                    
                    if op_type == 'resize':
                        temp_path = self.processor.resize_image(temp_path, temp_path, **params)
                    elif op_type == 'convert':
                        # 为格式转换生成新的输出路径
                        ext = params.get('format', 'JPEG').lower()
                        if ext == 'jpeg':
                            ext = 'jpg'
                        base_name = os.path.splitext(os.path.basename(temp_path))[0]
                        new_temp_path = os.path.join(self.output_dir, f'{base_name}.{ext}')
                        temp_path = self.processor.convert_format(temp_path, new_temp_path, **params)
                    elif op_type == 'text_watermark':
                        temp_path = self.processor.add_text_watermark(temp_path, temp_path, **params)
                    elif op_type == 'image_watermark':
                        temp_path = self.processor.add_image_watermark(temp_path, temp_path, **params)
                    elif op_type == 'rename':
                        temp_path = self.processor.rename_file(temp_path, self.output_dir, params['rename_pattern'], i+1)
                    elif op_type == 'compress':
                        temp_path = self.processor.compress_image(temp_path, temp_path, **params)
                
                # 更新进度
                processed_files += 1
                progress = (processed_files / total_files) * 100
                self.progress_var.set(progress)
                self.progress_label.config(text=f"处理中... ({processed_files}/{total_files})")
                
                # 模拟处理时间
                time.sleep(0.1)
            
            # 处理完成
            self.progress_label.config(text="处理完成！")
            messagebox.showinfo("成功", f"所有图片处理完成，结果保存在：{self.output_dir}")
        
        except Exception as e:
            self.progress_label.config(text="处理失败")
            messagebox.showerror("错误", f"处理过程中发生错误：{str(e)}")
        
        finally:
            # 启用开始按钮
            self.start_process_btn.config(state=tk.NORMAL)
    
    def show_compare(self, before_path, after_path):
        """显示处理前后对比"""
        # 显示原图
        try:
            before_img = Image.open(before_path)
            max_width = self.before_canvas.winfo_width() - 20
            max_height = self.before_canvas.winfo_height() - 20
            before_img.thumbnail((max_width, max_height), Image.LANCZOS)
            before_photo = ImageTk.PhotoImage(before_img)
            self.before_canvas.delete("all")
            x = (self.before_canvas.winfo_width() - before_img.width) // 2
            y = (self.before_canvas.winfo_height() - before_img.height) // 2
            self.before_canvas.create_image(x, y, anchor=tk.NW, image=before_photo)
            self.before_photo = before_photo
        except Exception as e:
            self.before_canvas.delete("all")
            self.before_canvas.create_text(150, 100, text=f"无法显示原图\n{str(e)}", anchor=tk.CENTER)
        
        # 显示处理后图片
        try:
            after_img = Image.open(after_path)
            max_width = self.after_canvas.winfo_width() - 20
            max_height = self.after_canvas.winfo_height() - 20
            after_img.thumbnail((max_width, max_height), Image.LANCZOS)
            after_photo = ImageTk.PhotoImage(after_img)
            self.after_canvas.delete("all")
            x = (self.after_canvas.winfo_width() - after_img.width) // 2
            y = (self.after_canvas.winfo_height() - after_img.height) // 2
            self.after_canvas.create_image(x, y, anchor=tk.NW, image=after_photo)
            self.after_photo = after_photo
        except Exception as e:
            self.after_canvas.delete("all")
            self.after_canvas.create_text(150, 100, text=f"无法显示处理后图片\n{str(e)}", anchor=tk.CENTER)

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageProcessingApp(root)
    root.mainloop()
