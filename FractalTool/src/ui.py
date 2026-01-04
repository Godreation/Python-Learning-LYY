import pygame
import sys
import numpy as np
from fractals import (
    mandelbrot_set, julia_set, burning_ship_set,
    IFSPresets, LSystemPresets, FractalTypes
)
from renderer import Renderer, ColorSchemes

class UIElement:
    """UI元素基类"""
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.visible = True
    
    def draw(self, surface):
        """绘制UI元素"""
        pass
    
    def handle_event(self, event):
        """处理事件"""
        return False

class Button(UIElement):
    """按钮类"""
    def __init__(self, x, y, width, height, text, callback, bg_color=(100, 100, 100), hover_color=(150, 150, 150), text_color=(255, 255, 255)):
        super().__init__(x, y, width, height)
        self.text = text
        self.callback = callback
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        # 尝试加载系统中文字体
        self.font = self._get_font()
    
    def _get_font(self):
        """获取支持中文的字体"""
        # 尝试加载几种常见的中文字体
        font_paths = [
            "C:/Windows/Fonts/simhei.ttf",  # 黑体
            "C:/Windows/Fonts/simsun.ttc",  # 宋体
            "C:/Windows/Fonts/msyh.ttc",    # 微软雅黑
        ]
        
        for font_path in font_paths:
            try:
                return pygame.font.Font(font_path, 24)
            except:
                continue
        
        # 如果无法加载中文字体，回退到默认字体
        return pygame.font.Font(None, 24)
    
    def draw(self, surface):
        """绘制按钮"""
        # 检查鼠标是否悬停
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            color = self.hover_color
        else:
            color = self.bg_color
        
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 2)
        
        # 绘制文本
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
    
    def handle_event(self, event):
        """处理按钮事件"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左键点击
                if self.rect.collidepoint(event.pos):
                    self.callback()
                    return True
        return False

class Slider(UIElement):
    """滑块类"""
    def __init__(self, x, y, width, height, min_val, max_val, initial_val, callback, label=""):
        super().__init__(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.callback = callback
        self.label = label
        # 尝试加载系统中文字体
        self.font = self._get_font()
        self.is_dragging = False
    
    def _get_font(self):
        """获取支持中文的字体"""
        # 尝试加载几种常见的中文字体
        font_paths = [
            "C:/Windows/Fonts/simhei.ttf",  # 黑体
            "C:/Windows/Fonts/simsun.ttc",  # 宋体
            "C:/Windows/Fonts/msyh.ttc",    # 微软雅黑
        ]
        
        for font_path in font_paths:
            try:
                return pygame.font.Font(font_path, 20)
            except:
                continue
        
        # 如果无法加载中文字体，回退到默认字体
        return pygame.font.Font(None, 20)
    
    def draw(self, surface):
        """绘制滑块"""
        # 绘制背景
        pygame.draw.rect(surface, (50, 50, 50), self.rect)
        pygame.draw.rect(surface, (100, 100, 100), self.rect, 2)
        
        # 绘制滑块位置
        slider_pos = self.rect.x + int((self.value - self.min_val) / (self.max_val - self.min_val) * (self.rect.width - 10))
        pygame.draw.rect(surface, (200, 200, 200), (slider_pos, self.rect.y, 10, self.rect.height))
        
        # 绘制标签和值
        if self.label:
            label_surface = self.font.render(f"{self.label}: {self.value:.2f}", True, (255, 255, 255))
            surface.blit(label_surface, (self.rect.x, self.rect.y - 25))
    
    def handle_event(self, event):
        """处理滑块事件"""
        handled = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                slider_pos = self.rect.x + int((self.value - self.min_val) / (self.max_val - self.min_val) * (self.rect.width - 10))
                slider_rect = pygame.Rect(slider_pos, self.rect.y, 10, self.rect.height)
                if slider_rect.collidepoint(event.pos):
                    self.is_dragging = True
                    handled = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                if self.is_dragging:
                    self.is_dragging = False
                    handled = True
        elif event.type == pygame.MOUSEMOTION:
            if self.is_dragging:
                # 更新滑块值
                rel_x = event.pos[0] - self.rect.x
                ratio = max(0, min(1, rel_x / (self.rect.width - 10)))
                self.value = self.min_val + ratio * (self.max_val - self.min_val)
                self.callback(self.value)
                handled = True
        return handled

class Dropdown(UIElement):
    """下拉菜单类"""
    def __init__(self, x, y, width, height, options, initial_selected, callback):
        super().__init__(x, y, width, height)
        self.options = options
        self.selected = initial_selected
        self.callback = callback
        # 尝试加载系统中文字体
        self.font = self._get_font()
        self.is_open = False
    
    def _get_font(self):
        """获取支持中文的字体"""
        # 尝试加载几种常见的中文字体
        font_paths = [
            "C:/Windows/Fonts/simhei.ttf",  # 黑体
            "C:/Windows/Fonts/simsun.ttc",  # 宋体
            "C:/Windows/Fonts/msyh.ttc",    # 微软雅黑
        ]
        
        for font_path in font_paths:
            try:
                return pygame.font.Font(font_path, 24)
            except:
                continue
        
        # 如果无法加载中文字体，回退到默认字体
        return pygame.font.Font(None, 24)
    
    def draw(self, surface):
        """绘制下拉菜单"""
        # 绘制主按钮
        pygame.draw.rect(surface, (100, 100, 100), self.rect)
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 2)
        
        # 绘制选中的选项
        text_surface = self.font.render(self.selected, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
        
        # 绘制下拉箭头
        arrow_points = [
            (self.rect.right - 20, self.rect.centery - 5),
            (self.rect.right - 10, self.rect.centery - 5),
            (self.rect.right - 15, self.rect.centery + 5)
        ]
        pygame.draw.polygon(surface, (255, 255, 255), arrow_points)
        
        # 绘制下拉选项
        if self.is_open:
            for i, option in enumerate(self.options):
                option_rect = pygame.Rect(self.rect.x, self.rect.y + (i + 1) * self.rect.height, self.rect.width, self.rect.height)
                pygame.draw.rect(surface, (80, 80, 80), option_rect)
                pygame.draw.rect(surface, (255, 255, 255), option_rect, 1)
                
                option_text = self.font.render(option, True, (255, 255, 255))
                option_text_rect = option_text.get_rect(center=option_rect.center)
                surface.blit(option_text, option_text_rect)
    
    def handle_event(self, event):
        """处理下拉菜单事件"""
        handled = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.rect.collidepoint(event.pos):
                    self.is_open = not self.is_open
                    handled = True
                elif self.is_open:
                    for i, option in enumerate(self.options):
                        option_rect = pygame.Rect(self.rect.x, self.rect.y + (i + 1) * self.rect.height, self.rect.width, self.rect.height)
                        if option_rect.collidepoint(event.pos):
                            self.selected = option
                            self.callback(self.selected)
                            self.is_open = False
                            handled = True
                            break
                    else:
                        self.is_open = False
                        handled = True
        return handled

class FractalUI:
    """分形工具UI主类"""
    
    def __init__(self, width=1200, height=800):
        # 初始化PyGame
        pygame.init()
        
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("分形探索工具")
        
        # 初始化渲染器
        self.renderer = Renderer()
        
        # 当前分形设置
        self.current_fractal = FractalTypes.MANDELBROT
        self.color_scheme = ColorSchemes.GRADIENT
        self.coloring_method = "smooth"
        self.max_iter = 100
        self.julia_c = -0.8 + 0.156j
        
        # 视图设置
        self.xmin, self.xmax = -2.5, 1.5
        self.ymin, self.ymax = -1.5, 1.5
        self.image_width, self.image_height = 800, 600
        
        # UI元素
        self.ui_elements = []
        self._create_ui_elements()
        
        # 渲染的图像
        self.rendered_image = None
        self.needs_render = True
        
        # 鼠标交互状态
        self.is_dragging = False
        self.last_mouse_pos = None
        self.zoom_factor = 1.1
    
    def _create_ui_elements(self):
        """创建UI元素"""
        # 分形类型选择 - 第一行左侧
        fractal_types = [FractalTypes.MANDELBROT, FractalTypes.JULIA, FractalTypes.BURNING_SHIP, 
                         FractalTypes.IFS, FractalTypes.L_SYSTEM]
        self.fractal_dropdown = Dropdown(10, 10, 180, 40, fractal_types, FractalTypes.MANDELBROT, self._on_fractal_change)
        self.ui_elements.append(self.fractal_dropdown)
        
        # 颜色方案选择 - 第一行中间
        color_schemes = [ColorSchemes.GRADIENT, ColorSchemes.JET, ColorSchemes.HSV, 
                         ColorSchemes.TWISTED, ColorSchemes.BLACK_AND_WHITE, 
                         ColorSchemes.FIRE, ColorSchemes.ICE]
        self.color_dropdown = Dropdown(200, 10, 180, 40, color_schemes, ColorSchemes.GRADIENT, self._on_color_scheme_change)
        self.ui_elements.append(self.color_dropdown)
        
        # 着色方法选择 - 第一行右侧
        coloring_methods = ["escape_time", "smooth", "distance_estimator"]
        self.coloring_dropdown = Dropdown(390, 10, 180, 40, coloring_methods, "smooth", self._on_coloring_method_change)
        self.ui_elements.append(self.coloring_dropdown)
        
        # 最大迭代次数滑块 - 左下角
        self.iteration_slider = Slider(10, 700, 350, 20, 10, 500, 100, self._on_max_iter_change, "最大迭代")
        self.ui_elements.append(self.iteration_slider)
        
        # Julia集合参数滑块（实部和虚部） - 左下角
        self.julia_real_slider = Slider(10, 650, 350, 20, -2.0, 2.0, -0.8, self._on_julia_real_change, "Julia实部")
        self.ui_elements.append(self.julia_real_slider)
        
        self.julia_imag_slider = Slider(10, 600, 350, 20, -2.0, 2.0, 0.156, self._on_julia_imag_change, "Julia虚部")
        self.ui_elements.append(self.julia_imag_slider)
        
        # 保存按钮 - 左下角
        self.save_button = Button(10, 750, 150, 40, "保存图像", self._on_save_click)
        self.ui_elements.append(self.save_button)
        
        # 渲染按钮 - 保存按钮右侧
        self.render_button = Button(170, 750, 150, 40, "渲染分形", self._on_render_click)
        self.ui_elements.append(self.render_button)
    
    def _on_fractal_change(self, value):
        """分形类型改变事件"""
        self.current_fractal = value
        self.needs_render = True
    
    def _on_color_scheme_change(self, value):
        """颜色方案改变事件"""
        self.color_scheme = value
        self.needs_render = True
    
    def _on_coloring_method_change(self, value):
        """着色方法改变事件"""
        self.coloring_method = value
        self.needs_render = True
    
    def _on_max_iter_change(self, value):
        """最大迭代次数改变事件"""
        self.max_iter = int(value)
        self.needs_render = True
    
    def _on_julia_real_change(self, value):
        """Julia实部改变事件"""
        self.julia_c = complex(value, self.julia_c.imag)
        self.needs_render = True
    
    def _on_julia_imag_change(self, value):
        """Julia虚部改变事件"""
        self.julia_c = complex(self.julia_c.real, value)
        self.needs_render = True
    
    def _on_render_click(self):
        """渲染按钮点击事件"""
        self.needs_render = True
    
    def _on_save_click(self):
        """保存按钮点击事件"""
        if self.rendered_image is not None:
            filename = f"../results/{self.current_fractal}_{pygame.time.get_ticks()}.png"
            self.renderer.save_image(self.rendered_image, filename)
            print(f"图像已保存到: {filename}")
    
    def _render_fractal(self):
        """渲染当前分形"""
        print(f"正在渲染 {self.current_fractal}...")
        
        if self.current_fractal == FractalTypes.MANDELBROT:
            # 渲染曼德博集合
            img = mandelbrot_set(self.xmin, self.xmax, self.ymin, self.ymax, 
                                self.image_width, self.image_height, self.max_iter)
            self.rendered_image = self.renderer.apply_coloring(img, self.max_iter, 
                                                               self.coloring_method, self.color_scheme)
        
        elif self.current_fractal == FractalTypes.JULIA:
            # 渲染朱利亚集合
            img = julia_set(self.julia_c, self.xmin, self.xmax, self.ymin, self.ymax, 
                           self.image_width, self.image_height, self.max_iter)
            self.rendered_image = self.renderer.apply_coloring(img, self.max_iter, 
                                                               self.coloring_method, self.color_scheme)
        
        elif self.current_fractal == FractalTypes.BURNING_SHIP:
            # 渲染燃烧船分形
            img = burning_ship_set(self.xmin, self.xmax, self.ymin, self.ymax, 
                                  self.image_width, self.image_height, self.max_iter)
            self.rendered_image = self.renderer.apply_coloring(img, self.max_iter, 
                                                               self.coloring_method, self.color_scheme)
        
        elif self.current_fractal == FractalTypes.IFS:
            # 渲染IFS分形（Barnsley蕨类）
            ifs = IFSPresets.barnsley_fern()
            img = ifs.generate(100000, self.image_width, self.image_height)
            # IFS生成的是二值图像，直接转换为RGB
            self.rendered_image = np.stack([img]*3, axis=-1)
        
        elif self.current_fractal == FractalTypes.L_SYSTEM:
            # 渲染L-系统（分形植物）
            lsystem = LSystemPresets.fractal_plant()
            string = lsystem.generate(5)
            self.rendered_image = lsystem.draw(string, self.image_width, self.image_height)
        
        print("渲染完成")
    
    def _world_to_screen(self, x, y):
        """将世界坐标转换为屏幕坐标"""
        screen_x = 400 + int((x - self.xmin) / (self.xmax - self.xmin) * self.image_width)
        screen_y = 10 + int((y - self.ymin) / (self.ymax - self.ymin) * self.image_height)
        return screen_x, screen_y
    
    def _screen_to_world(self, screen_x, screen_y):
        """将屏幕坐标转换为世界坐标"""
        # 检查是否在图像区域内
        if screen_x < 400 or screen_x > 400 + self.image_width or \
           screen_y < 10 or screen_y > 10 + self.image_height:
            return None, None
        
        # 转换为图像内部坐标
        img_x = screen_x - 400
        img_y = screen_y - 10
        
        # 转换为世界坐标
        world_x = self.xmin + (img_x / self.image_width) * (self.xmax - self.xmin)
        world_y = self.ymin + (img_y / self.image_height) * (self.ymax - self.ymin)
        
        return world_x, world_y
    
    def _zoom_view(self, screen_x, screen_y, zoom_in):
        """缩放视图"""
        # 计算缩放中心的世界坐标
        world_x, world_y = self._screen_to_world(screen_x, screen_y)
        if world_x is None or world_y is None:
            return
        
        # 计算当前视图范围
        current_width = self.xmax - self.xmin
        current_height = self.ymax - self.ymin
        
        # 计算新的视图范围
        if zoom_in:
            new_width = current_width / self.zoom_factor
            new_height = current_height / self.zoom_factor
        else:
            new_width = current_width * self.zoom_factor
            new_height = current_height * self.zoom_factor
        
        # 调整视图，使缩放中心保持在原来的屏幕位置
        self.xmin = world_x - (screen_x - 400) / self.image_width * new_width
        self.xmax = self.xmin + new_width
        self.ymin = world_y - (screen_y - 10) / self.image_height * new_height
        self.ymax = self.ymin + new_height
        
        self.needs_render = True
    
    def _pan_view(self, dx, dy):
        """平移视图"""
        # 计算平移距离对应的世界坐标
        world_dx = dx * (self.xmax - self.xmin) / self.image_width
        world_dy = dy * (self.ymax - self.ymin) / self.image_height
        
        # 更新视图范围
        self.xmin -= world_dx
        self.xmax -= world_dx
        self.ymin -= world_dy
        self.ymax -= world_dy
        
        self.needs_render = True
    
    def run(self):
        """运行UI主循环"""
        clock = pygame.time.Clock()
        
        while True:
            # 处理事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                # 处理UI事件
                ui_event_handled = False
                for element in self.ui_elements:
                    if element.handle_event(event):
                        ui_event_handled = True
                        break
                
                if not ui_event_handled:
                    # 处理视图交互事件
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:  # 左键点击
                            # 检查是否点击在图像区域
                            if 400 <= event.pos[0] <= 400 + self.image_width and \
                               10 <= event.pos[1] <= 10 + self.image_height:
                                self.is_dragging = True
                                self.last_mouse_pos = event.pos
                        elif event.button == 4:  # 滚轮向上（放大）
                            self._zoom_view(event.pos[0], event.pos[1], zoom_in=True)
                        elif event.button == 5:  # 滚轮向下（缩小）
                            self._zoom_view(event.pos[0], event.pos[1], zoom_in=False)
                    elif event.type == pygame.MOUSEBUTTONUP:
                        if event.button == 1:
                            self.is_dragging = False
                            self.last_mouse_pos = None
                    elif event.type == pygame.MOUSEMOTION:
                        if self.is_dragging:
                            # 计算拖拽距离
                            dx = event.pos[0] - self.last_mouse_pos[0]
                            dy = event.pos[1] - self.last_mouse_pos[1]
                            # 平移视图
                            self._pan_view(dx, dy)
                            # 更新鼠标位置
                            self.last_mouse_pos = event.pos
            
            # 渲染分形
            if self.needs_render:
                self._render_fractal()
                self.needs_render = False
            
            # 绘制UI
            self.screen.fill((30, 30, 30))
            
            # 绘制渲染的图像
            if self.rendered_image is not None:
                # 转换为PyGame表面
                img_surface = pygame.surfarray.make_surface(self.rendered_image)
                img_surface = pygame.transform.scale(img_surface, (self.image_width, self.image_height))
                self.screen.blit(img_surface, (400, 10))
            
            # 绘制UI元素
            for element in self.ui_elements:
                element.draw(self.screen)
            
            # 更新屏幕
            pygame.display.flip()
            clock.tick(60)

if __name__ == "__main__":
    ui = FractalUI()
    ui.run()
