import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QListWidgetItem, QLabel, QPushButton, QTextEdit,
    QSplitter, QGroupBox, QGridLayout, QTabWidget, QLineEdit,
    QComboBox, QSpinBox, QCheckBox, QToolBar, QAction, QMenuBar,
    QMenu, QDialog, QFormLayout, QFileDialog, QMessageBox, QInputDialog
)
from PyQt5.QtCore import Qt, QMimeData, QPoint, QSize, QDateTime
from PyQt5.QtGui import QIcon, QDragEnterEvent, QDropEvent

class FileItem:
    def __init__(self, file_path):
        self.original_path = file_path
        self.filename = os.path.basename(file_path)
        self.directory = os.path.dirname(file_path)
        self.new_filename = self.filename
        self.status = "pending"

class BatchRenameTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("批量文件重命名工具")
        self.setGeometry(100, 100, 1200, 800)
        
        # 初始化变量
        self.file_list = []
        self.rename_rules = []
        self.undo_stack = []
        self.redo_stack = []
        self.current_rule = None
        
        # 创建主布局
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        
        # 创建工具栏
        self.create_toolbar()
        
        # 创建菜单栏
        self.create_menu()
        
        # 创建主分割器
        main_splitter = QSplitter(Qt.Horizontal)
        
        # 左侧面板：文件列表和拖放区域
        left_panel = self.create_left_panel()
        main_splitter.addWidget(left_panel)
        
        # 中间面板：规则构建器
        middle_panel = self.create_middle_panel()
        main_splitter.addWidget(middle_panel)
        
        # 右侧面板：预览和任务队列
        right_panel = self.create_right_panel()
        main_splitter.addWidget(right_panel)
        
        # 设置分割器比例
        main_splitter.setSizes([400, 400, 400])
        
        main_layout.addWidget(main_splitter)
        self.setCentralWidget(main_widget)
        
        # 允许拖放
        self.setAcceptDrops(True)
    
    def create_toolbar(self):
        toolbar = QToolBar("主工具栏")
        self.addToolBar(toolbar)
        
        # 添加操作按钮
        add_files_action = QAction("添加文件", self)
        add_files_action.triggered.connect(self.add_files)
        toolbar.addAction(add_files_action)
        
        add_folder_action = QAction("添加文件夹", self)
        add_folder_action.triggered.connect(self.add_folder)
        toolbar.addAction(add_folder_action)
        
        remove_files_action = QAction("移除选中", self)
        remove_files_action.triggered.connect(self.remove_selected_files)
        toolbar.addAction(remove_files_action)
        
        clear_all_action = QAction("清空列表", self)
        clear_all_action.triggered.connect(self.clear_file_list)
        toolbar.addAction(clear_all_action)
        
        toolbar.addSeparator()
        
        rename_action = QAction("执行重命名", self)
        rename_action.triggered.connect(self.execute_rename)
        toolbar.addAction(rename_action)
        
        undo_action = QAction("撤销", self)
        undo_action.triggered.connect(self.undo_rename)
        toolbar.addAction(undo_action)
        
        redo_action = QAction("重做", self)
        redo_action.triggered.connect(self.redo_rename)
        toolbar.addAction(redo_action)
    
    def create_menu(self):
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("文件")
        file_menu.addAction("添加文件", self.add_files)
        file_menu.addAction("添加文件夹", self.add_folder)
        file_menu.addSeparator()
        file_menu.addAction("退出", self.close)
        
        # 规则菜单
        rule_menu = menubar.addMenu("规则")
        rule_menu.addAction("保存规则模板", self.save_rule_template)
        rule_menu.addAction("加载规则模板", self.load_rule_template)
        rule_menu.addAction("分享规则模板", self.share_rule_template)
        
        # 帮助菜单
        help_menu = menubar.addMenu("帮助")
        help_menu.addAction("关于", self.show_about)
    
    def create_left_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # 拖放区域
        drop_area = QGroupBox("文件拖放区域")
        drop_layout = QVBoxLayout(drop_area)
        
        self.drop_label = QLabel("将文件或文件夹拖放到此处")
        self.drop_label.setAlignment(Qt.AlignCenter)
        self.drop_label.setStyleSheet("border: 2px dashed #ccc; padding: 20px; border-radius: 5px;")
        drop_layout.addWidget(self.drop_label)
        
        # 文件列表
        files_group = QGroupBox("文件列表")
        files_layout = QVBoxLayout(files_group)
        
        self.file_list_widget = QListWidget()
        self.file_list_widget.setSelectionMode(QListWidget.ExtendedSelection)
        files_layout.addWidget(self.file_list_widget)
        
        # 文件统计
        self.file_stats_label = QLabel("共 0 个文件")
        files_layout.addWidget(self.file_stats_label)
        
        layout.addWidget(drop_area)
        layout.addWidget(files_group)
        
        return panel
    
    def create_middle_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # 规则构建器标签页
        self.rule_tabs = QTabWidget()
        
        # 替换规则
        replace_tab = self.create_replace_rule_tab()
        self.rule_tabs.addTab(replace_tab, "替换")
        
        # 插入规则
        insert_tab = self.create_insert_rule_tab()
        self.rule_tabs.addTab(insert_tab, "插入")
        
        # 删除规则
        delete_tab = self.create_delete_rule_tab()
        self.rule_tabs.addTab(delete_tab, "删除")
        
        # 序列规则
        sequence_tab = self.create_sequence_rule_tab()
        self.rule_tabs.addTab(sequence_tab, "序列")
        
        # 正则表达式规则
        regex_tab = self.create_regex_rule_tab()
        self.rule_tabs.addTab(regex_tab, "正则表达式")
        
        # 元数据规则
        metadata_tab = self.create_metadata_rule_tab()
        self.rule_tabs.addTab(metadata_tab, "元数据")
        
        # 智能重命名规则
        smart_tab = self.create_smart_rename_tab()
        self.rule_tabs.addTab(smart_tab, "智能重命名")
        
        layout.addWidget(self.rule_tabs)
        
        # 规则管理
        rule_management = QGroupBox("规则管理")
        rule_layout = QHBoxLayout(rule_management)
        
        add_rule_btn = QPushButton("添加规则")
        add_rule_btn.clicked.connect(self.add_rule)
        rule_layout.addWidget(add_rule_btn)
        
        remove_rule_btn = QPushButton("移除规则")
        remove_rule_btn.clicked.connect(self.remove_rule)
        rule_layout.addWidget(remove_rule_btn)
        
        clear_rules_btn = QPushButton("清空规则")
        clear_rules_btn.clicked.connect(self.clear_rules)
        rule_layout.addWidget(clear_rules_btn)
        
        layout.addWidget(rule_management)
        
        return panel
    
    def create_smart_rename_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 智能重命名选项
        smart_options_group = QGroupBox("智能重命名选项")
        smart_layout = QFormLayout(smart_options_group)
        
        self.smart_type_combo = QComboBox()
        self.smart_type_combo.addItems(["自动识别", "电视剧集", "照片日期整理"])
        smart_layout.addRow("智能类型:", self.smart_type_combo)
        
        layout.addWidget(smart_options_group)
        
        return tab
    
    def create_replace_rule_tab(self):
        tab = QWidget()
        layout = QFormLayout(tab)
        
        self.find_text_edit = QLineEdit()
        layout.addRow("查找文本:", self.find_text_edit)
        
        self.replace_text_edit = QLineEdit()
        layout.addRow("替换为:", self.replace_text_edit)
        
        self.case_sensitive_check = QCheckBox("区分大小写")
        layout.addRow(self.case_sensitive_check)
        
        return tab
    
    def create_insert_rule_tab(self):
        tab = QWidget()
        layout = QFormLayout(tab)
        
        self.insert_position_spin = QSpinBox()
        self.insert_position_spin.setMinimum(0)
        self.insert_position_spin.setMaximum(9999)
        layout.addRow("插入位置:", self.insert_position_spin)
        
        self.insert_text_edit = QLineEdit()
        layout.addRow("插入文本:", self.insert_text_edit)
        
        return tab
    
    def create_delete_rule_tab(self):
        tab = QWidget()
        layout = QFormLayout(tab)
        
        self.delete_start_spin = QSpinBox()
        self.delete_start_spin.setMinimum(0)
        self.delete_start_spin.setMaximum(9999)
        layout.addRow("起始位置:", self.delete_start_spin)
        
        self.delete_length_spin = QSpinBox()
        self.delete_length_spin.setMinimum(1)
        self.delete_length_spin.setMaximum(9999)
        layout.addRow("删除长度:", self.delete_length_spin)
        
        return tab
    
    def create_sequence_rule_tab(self):
        tab = QWidget()
        layout = QFormLayout(tab)
        
        self.sequence_prefix_edit = QLineEdit()
        layout.addRow("前缀:", self.sequence_prefix_edit)
        
        self.sequence_start_spin = QSpinBox()
        self.sequence_start_spin.setMinimum(1)
        self.sequence_start_spin.setMaximum(999999)
        layout.addRow("起始数字:", self.sequence_start_spin)
        
        self.sequence_step_spin = QSpinBox()
        self.sequence_step_spin.setMinimum(1)
        self.sequence_step_spin.setMaximum(999)
        layout.addRow("步长:", self.sequence_step_spin)
        
        self.sequence_padding_spin = QSpinBox()
        self.sequence_padding_spin.setMinimum(1)
        self.sequence_padding_spin.setMaximum(10)
        layout.addRow("数字位数:", self.sequence_padding_spin)
        
        self.sequence_suffix_edit = QLineEdit()
        layout.addRow("后缀:", self.sequence_suffix_edit)
        
        return tab
    
    def create_regex_rule_tab(self):
        tab = QWidget()
        layout = QFormLayout(tab)
        
        self.regex_pattern_edit = QLineEdit()
        layout.addRow("正则表达式:", self.regex_pattern_edit)
        
        self.regex_replace_edit = QLineEdit()
        layout.addRow("替换模板:", self.regex_replace_edit)
        
        return tab
    
    def create_metadata_rule_tab(self):
        tab = QWidget()
        layout = QFormLayout(tab)
        
        self.metadata_type_combo = QComboBox()
        self.metadata_type_combo.addItems(["EXIF 日期", "创建时间", "修改时间", "音乐标签"])
        layout.addRow("元数据类型:", self.metadata_type_combo)
        
        self.metadata_format_edit = QLineEdit("YYYY-MM-DD_HH-mm-ss")
        layout.addRow("日期格式:", self.metadata_format_edit)
        
        return tab
    
    def create_right_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # 预览区域
        preview_group = QGroupBox("实时预览")
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_list_widget = QListWidget()
        preview_layout.addWidget(self.preview_list_widget)
        
        layout.addWidget(preview_group)
        
        # 规则模板管理
        template_group = QGroupBox("规则模板")
        template_layout = QVBoxLayout(template_group)
        
        self.template_list_widget = QListWidget()
        template_layout.addWidget(self.template_list_widget)
        
        template_buttons_layout = QHBoxLayout()
        save_template_btn = QPushButton("保存模板")
        save_template_btn.clicked.connect(self.save_rule_template)
        template_buttons_layout.addWidget(save_template_btn)
        
        load_template_btn = QPushButton("加载模板")
        load_template_btn.clicked.connect(self.load_rule_template)
        template_buttons_layout.addWidget(load_template_btn)
        
        delete_template_btn = QPushButton("删除模板")
        delete_template_btn.clicked.connect(self.delete_rule_template)
        template_buttons_layout.addWidget(delete_template_btn)
        
        template_layout.addLayout(template_buttons_layout)
        
        layout.addWidget(template_group)
        
        # 任务队列
        queue_group = QGroupBox("任务队列")
        queue_layout = QVBoxLayout(queue_group)
        
        self.queue_list_widget = QListWidget()
        queue_layout.addWidget(self.queue_list_widget)
        
        layout.addWidget(queue_group)
        
        return panel
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        for url in urls:
            file_path = url.toLocalFile()
            if os.path.isfile(file_path):
                self.add_file(file_path)
            elif os.path.isdir(file_path):
                self.add_folder_files(file_path)
        event.acceptProposedAction()
    
    def add_files(self):
        file_paths, _ = QFileDialog.getOpenFileNames(self, "选择文件")
        for file_path in file_paths:
            self.add_file(file_path)
    
    def add_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "选择文件夹")
        if folder_path:
            self.add_folder_files(folder_path)
    
    def add_folder_files(self, folder_path):
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                self.add_file(file_path)
    
    def add_file(self, file_path):
        if file_path not in [item.original_path for item in self.file_list]:
            file_item = FileItem(file_path)
            self.file_list.append(file_item)
            list_item = QListWidgetItem(file_item.filename)
            self.file_list_widget.addItem(list_item)
            self.update_file_stats()
            self.update_preview()
    
    def remove_selected_files(self):
        selected_items = self.file_list_widget.selectedItems()
        for item in selected_items:
            row = self.file_list_widget.row(item)
            self.file_list_widget.takeItem(row)
            del self.file_list[row]
        self.update_file_stats()
        self.update_preview()
    
    def clear_file_list(self):
        self.file_list.clear()
        self.file_list_widget.clear()
        self.update_file_stats()
        self.update_preview()
    
    def update_file_stats(self):
        self.file_stats_label.setText(f"共 {len(self.file_list)} 个文件")
    
    def update_preview(self):
        self.preview_list_widget.clear()
        for i, file_item in enumerate(self.file_list):
            # 应用当前规则生成预览
            preview_filename = self.apply_rules(file_item.filename, i)
            item_text = f"{file_item.filename} -> {preview_filename}"
            list_item = QListWidgetItem(item_text)
            self.preview_list_widget.addItem(list_item)
    
    def extract_metadata(self, file_path, metadata_type):
        """提取文件元数据"""
        metadata_value = ""
        
        if metadata_type == "EXIF 日期":
            try:
                from PIL import Image
                from PIL.ExifTags import TAGS
                
                with Image.open(file_path) as img:
                    exif_data = img._getexif()
                    if exif_data:
                        for tag, value in exif_data.items():
                            tag_name = TAGS.get(tag, tag)
                            if tag_name == 'DateTimeOriginal':
                                metadata_value = value
                                break
            except Exception as e:
                pass
        
        elif metadata_type == "创建时间":
            try:
                stat_info = os.stat(file_path)
                create_time = stat_info.st_ctime
                dt = QDateTime.fromSecsSinceEpoch(int(create_time))
                metadata_value = dt.toString("yyyy-MM-dd_HH-mm-ss")
            except Exception as e:
                pass
        
        elif metadata_type == "修改时间":
            try:
                stat_info = os.stat(file_path)
                modify_time = stat_info.st_mtime
                dt = QDateTime.fromSecsSinceEpoch(int(modify_time))
                metadata_value = dt.toString("yyyy-MM-dd_HH-mm-ss")
            except Exception as e:
                pass
        
        elif metadata_type == "音乐标签":
            try:
                from mutagen.easyid3 import EasyID3
                from mutagen.mp3 import MP3
                from mutagen.flac import FLAC
                
                # 尝试不同的音乐格式
                try:
                    audio = EasyID3(file_path)
                    if 'title' in audio:
                        metadata_value = audio['title'][0]
                    elif 'artist' in audio:
                        metadata_value = audio['artist'][0]
                except Exception:
                    try:
                        audio = MP3(file_path, ID3=EasyID3)
                        if 'title' in audio:
                            metadata_value = audio['title'][0]
                    except Exception:
                        try:
                            audio = FLAC(file_path)
                            if 'title' in audio:
                                metadata_value = audio['title'][0]
                        except Exception:
                            pass
            except Exception as e:
                pass
        
        return metadata_value
    
    def smart_rename(self, filename, file_path):
        """智能重命名功能"""
        import re
        name, ext = os.path.splitext(filename)
        new_name = name
        
        # 1. 电视剧集识别
        # 匹配常见的剧集格式：S01E02, 第01集, Episode 02, 01x02等
        episode_patterns = [
            r'S(\d{1,2})E(\d{1,2})',  # S01E02格式
            r'(\d{1,2})x(\d{1,2})',    # 01x02格式
            r'第(\d{1,3})集',           # 第01集格式
            r'Episode\s*(\d{1,3})'     # Episode 02格式
        ]
        
        for pattern in episode_patterns:
            match = re.search(pattern, name, re.IGNORECASE)
            if match:
                if pattern == r'S(\d{1,2})E(\d{1,2})' or pattern == r'(\d{1,2})x(\d{1,2})':
                    # S01E02或01x02格式
                    season = int(match.group(1))
                    episode = int(match.group(2))
                    new_name = f"S{season:02d}E{episode:02d}"
                elif pattern == r'第(\d{1,3})集':
                    # 第01集格式
                    episode = int(match.group(1))
                    new_name = f"第{episode:02d}集"
                elif pattern == r'Episode\s*(\d{1,3})':
                    # Episode 02格式
                    episode = int(match.group(1))
                    new_name = f"Episode {episode:02d}"
                break
        
        # 2. 照片日期整理
        # 检查文件是否为图片
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']
        if ext.lower() in image_extensions:
            # 尝试从EXIF获取日期
            exif_date = self.extract_metadata(file_path, "EXIF 日期")
            if exif_date:
                try:
                    from datetime import datetime
                    dt = datetime.strptime(exif_date, "%Y:%m:%d %H:%M:%S")
                    new_name = dt.strftime("%Y-%m-%d_%H-%M-%S")
                except Exception as e:
                    pass
            else:
                # 从文件创建时间获取日期
                create_time = self.extract_metadata(file_path, "创建时间")
                if create_time:
                    new_name = create_time.replace(":", "-")
        
        return new_name + ext
    
    def apply_rules(self, filename, index):
        new_filename = filename
        name, ext = os.path.splitext(new_filename)
        
        # 获取文件路径
        file_path = self.file_list[index].original_path if index < len(self.file_list) else ""
        
        for rule in self.rename_rules:
            rule_type = rule["type"]
            params = rule["params"]
            
            if rule_type == "替换":
                find_text = params["find"]
                replace_text = params["replace"]
                case_sensitive = params["case_sensitive"]
                
                if case_sensitive:
                    name = name.replace(find_text, replace_text)
                else:
                    name = name.lower().replace(find_text.lower(), replace_text)
            
            elif rule_type == "插入":
                position = params["position"]
                insert_text = params["text"]
                
                if position <= len(name):
                    name = name[:position] + insert_text + name[position:]
                else:
                    name += insert_text
            
            elif rule_type == "删除":
                start = params["start"]
                length = params["length"]
                
                if start < len(name):
                    end = start + length
                    name = name[:start] + name[end:]
            
            elif rule_type == "序列":
                prefix = params["prefix"]
                start = params["start"]
                step = params["step"]
                padding = params["padding"]
                suffix = params["suffix"]
                
                sequence_number = start + (index * step)
                sequence_str = f"{sequence_number:0{padding}d}"
                name = f"{prefix}{sequence_str}{suffix}"
            
            elif rule_type == "正则表达式":
                import re
                pattern = params["pattern"]
                replace_template = params["replace"]
                
                try:
                    name = re.sub(pattern, replace_template, name)
                except re.error:
                    pass
            
            elif rule_type == "元数据":
                metadata_type = params["type"]
                format_str = params["format"]
                
                metadata_value = self.extract_metadata(file_path, metadata_type)
                if metadata_value:
                    # 替换日期格式
                    if metadata_type in ["EXIF 日期", "创建时间", "修改时间"]:
                        # 尝试解析原始日期格式并转换
                        try:
                            # 假设EXIF日期格式为 "YYYY:MM:DD HH:MM:SS"
                            from datetime import datetime
                            if ":" in metadata_value:
                                dt = datetime.strptime(metadata_value, "%Y:%m:%d %H:%M:%S")
                            else:
                                dt = datetime.strptime(metadata_value, "%Y-%m-%d_%H-%M-%S")
                            formatted_date = dt.strftime(format_str.replace("YYYY", "%Y").replace("MM", "%m").replace("DD", "%d").replace("HH", "%H").replace("mm", "%M").replace("ss", "%S"))
                            name = formatted_date
                        except Exception as e:
                            name = metadata_value
                    else:
                        name = metadata_value
            
            elif rule_type == "智能重命名":
                # 应用智能重命名
                smart_name = self.smart_rename(filename, file_path)
                name = os.path.splitext(smart_name)[0]
        
        return name + ext
    
    def add_rule(self):
        # 添加当前规则到规则列表
        rule_type = self.rule_tabs.currentText()
        rule = {
            "type": rule_type,
            "params": {}
        }
        
        if rule_type == "替换":
            rule["params"] = {
                "find": self.find_text_edit.text(),
                "replace": self.replace_text_edit.text(),
                "case_sensitive": self.case_sensitive_check.isChecked()
            }
        elif rule_type == "插入":
            rule["params"] = {
                "position": self.insert_position_spin.value(),
                "text": self.insert_text_edit.text()
            }
        elif rule_type == "删除":
            rule["params"] = {
                "start": self.delete_start_spin.value(),
                "length": self.delete_length_spin.value()
            }
        elif rule_type == "序列":
            rule["params"] = {
                "prefix": self.sequence_prefix_edit.text(),
                "start": self.sequence_start_spin.value(),
                "step": self.sequence_step_spin.value(),
                "padding": self.sequence_padding_spin.value(),
                "suffix": self.sequence_suffix_edit.text()
            }
        elif rule_type == "正则表达式":
            rule["params"] = {
                "pattern": self.regex_pattern_edit.text(),
                "replace": self.regex_replace_edit.text()
            }
        elif rule_type == "元数据":
            rule["params"] = {
                "type": self.metadata_type_combo.currentText(),
                "format": self.metadata_format_edit.text()
            }
        elif rule_type == "智能重命名":
            rule["params"] = {
                "smart_type": self.smart_type_combo.currentText()
            }
        
        self.rename_rules.append(rule)
        self.update_preview()
    
    def remove_rule(self):
        # 移除选中的规则
        pass
    
    def clear_rules(self):
        self.rename_rules.clear()
        self.update_preview()
    
    def execute_rename(self):
        # 保存当前状态到撤销栈
        current_state = [{
            "original_path": item.original_path,
            "old_filename": item.filename,
            "new_filename": item.new_filename
        } for item in self.file_list]
        self.undo_stack.append(current_state)
        self.redo_stack.clear()
        
        # 执行重命名
        for i, file_item in enumerate(self.file_list):
            old_path = file_item.original_path
            new_filename = self.apply_rules(file_item.filename, i)
            new_path = os.path.join(file_item.directory, new_filename)
            
            # 避免文件名冲突
            if os.path.exists(new_path) and new_path != old_path:
                base_name, ext = os.path.splitext(new_filename)
                counter = 1
                while os.path.exists(new_path):
                    new_filename = f"{base_name}_{counter}{ext}"
                    new_path = os.path.join(file_item.directory, new_filename)
                    counter += 1
            
            # 执行重命名
            try:
                os.rename(old_path, new_path)
                file_item.filename = new_filename
                file_item.original_path = new_path
                file_item.status = "completed"
            except Exception as e:
                file_item.status = f"error: {str(e)}"
        
        # 更新界面
        self.update_file_list_display()
        self.update_preview()
        
        # 添加到任务队列
        self.add_to_task_queue("重命名完成", f"成功重命名 {len(self.file_list)} 个文件")
    
    def update_file_list_display(self):
        self.file_list_widget.clear()
        for item in self.file_list:
            list_item = QListWidgetItem(item.filename)
            self.file_list_widget.addItem(list_item)
    
    def add_to_task_queue(self, title, description):
        task_text = f"{title}: {description}"
        self.queue_list_widget.addItem(task_text)
    
    def undo_rename(self):
        if not self.undo_stack:
            return
        
        # 获取上一个状态
        last_state = self.undo_stack.pop()
        current_state = []
        
        # 执行撤销
        for state_item in last_state:
            old_path = os.path.join(os.path.dirname(state_item["original_path"]), state_item["old_filename"])
            new_path = state_item["original_path"]
            
            try:
                os.rename(new_path, old_path)
                current_state.append({
                    "original_path": old_path,
                    "old_filename": state_item["new_filename"],
                    "new_filename": state_item["old_filename"]
                })
            except Exception as e:
                pass
        
        # 更新撤销重做栈
        self.redo_stack.append(current_state)
        
        # 更新文件列表
        self.reload_file_list()
    
    def redo_rename(self):
        if not self.redo_stack:
            return
        
        # 获取下一个状态
        next_state = self.redo_stack.pop()
        current_state = []
        
        # 执行重做
        for state_item in next_state:
            old_path = state_item["original_path"]
            new_path = os.path.join(os.path.dirname(old_path), state_item["new_filename"])
            
            try:
                os.rename(old_path, new_path)
                current_state.append({
                    "original_path": new_path,
                    "old_filename": state_item["old_filename"],
                    "new_filename": state_item["new_filename"]
                })
            except Exception as e:
                pass
        
        # 更新撤销重做栈
        self.undo_stack.append(current_state)
        
        # 更新文件列表
        self.reload_file_list()
    
    def reload_file_list(self):
        # 重新加载文件列表
        original_files = [item.original_path for item in self.file_list]
        self.file_list.clear()
        for file_path in original_files:
            if os.path.exists(file_path):
                self.add_file(file_path)
        self.update_file_stats()
        self.update_preview()
    
    def save_rule_template(self):
        # 保存规则模板
        import json
        
        template_name, ok = QInputDialog.getText(self, "保存模板", "请输入模板名称:")
        if ok and template_name:
            template = {
                "name": template_name,
                "rules": self.rename_rules
            }
            
            # 保存到文件
            templates_dir = os.path.join(os.path.dirname(__file__), "templates")
            os.makedirs(templates_dir, exist_ok=True)
            
            template_file = os.path.join(templates_dir, f"{template_name}.json")
            with open(template_file, "w", encoding="utf-8") as f:
                json.dump(template, f, indent=2, ensure_ascii=False)
            
            # 更新模板列表
            self.load_template_list()
    
    def load_rule_template(self):
        # 加载规则模板
        import json
        
        # 显示模板选择对话框
        templates_dir = os.path.join(os.path.dirname(__file__), "templates")
        if not os.path.exists(templates_dir):
            os.makedirs(templates_dir)
        
        template_files = [f for f in os.listdir(templates_dir) if f.endswith(".json")]
        
        if not template_files:
            QMessageBox.information(self, "提示", "没有可用的规则模板")
            return
        
        template_names = [os.path.splitext(f)[0] for f in template_files]
        template_name, ok = QInputDialog.getItem(self, "加载模板", "请选择模板:", template_names, 0, False)
        
        if ok and template_name:
            template_file = os.path.join(templates_dir, f"{template_name}.json")
            with open(template_file, "r", encoding="utf-8") as f:
                template = json.load(f)
            
            self.rename_rules = template["rules"]
            self.update_preview()
    
    def delete_rule_template(self):
        # 删除规则模板
        import json
        
        # 显示模板选择对话框
        templates_dir = os.path.join(os.path.dirname(__file__), "templates")
        if not os.path.exists(templates_dir):
            os.makedirs(templates_dir)
        
        template_files = [f for f in os.listdir(templates_dir) if f.endswith(".json")]
        
        if not template_files:
            QMessageBox.information(self, "提示", "没有可用的规则模板")
            return
        
        template_names = [os.path.splitext(f)[0] for f in template_files]
        template_name, ok = QInputDialog.getItem(self, "删除模板", "请选择要删除的模板:", template_names, 0, False)
        
        if ok and template_name:
            template_file = os.path.join(templates_dir, f"{template_name}.json")
            if os.path.exists(template_file):
                os.remove(template_file)
                self.load_template_list()
    
    def load_template_list(self):
        # 加载模板列表
        self.template_list_widget.clear()
        
        templates_dir = os.path.join(os.path.dirname(__file__), "templates")
        if not os.path.exists(templates_dir):
            os.makedirs(templates_dir)
        
        template_files = [f for f in os.listdir(templates_dir) if f.endswith(".json")]
        for template_file in template_files:
            template_name = os.path.splitext(template_file)[0]
            self.template_list_widget.addItem(template_name)
    
    def share_rule_template(self):
        # 分享规则模板
        import json
        
        if not self.rename_rules:
            QMessageBox.information(self, "提示", "没有可分享的规则")
            return
        
        # 生成分享链接或保存为文件
        share_content = json.dumps(self.rename_rules, indent=2, ensure_ascii=False)
        
        save_path, _ = QFileDialog.getSaveFileName(self, "保存规则模板", "rule_template.json", "JSON Files (*.json)")
        if save_path:
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(share_content)
            QMessageBox.information(self, "提示", f"规则模板已保存到: {save_path}")
    
    def show_about(self):
        # 显示关于对话框
        QMessageBox.about(self, "关于", "批量文件重命名工具 v1.0\n使用 PyQt5 开发")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BatchRenameTool()
    window.show()
    sys.exit(app.exec_())
