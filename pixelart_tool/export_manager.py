"""
导出管理器模块
负责将像素艺术导出为不同格式
"""

import numpy as np
from PIL import Image, ImageSequence
import imageio
import os

class ExportManager:
    """导出管理器类"""
    
    def __init__(self):
        self.ascii_chars = "@%#*+=-:. "  # ASCII字符梯度
    
    def export_png(self, image, file_path, quality=95):
        """导出为PNG格式"""
        try:
            image.save(file_path, 'PNG', optimize=True, quality=quality)
            return True
        except Exception as e:
            print(f"PNG导出错误: {e}")
            return False
    
    def export_gif(self, image, file_path, duration=100, loop=0):
        """导出为GIF格式"""
        try:
            # 如果是单帧图像，创建简单的动画效果
            if isinstance(image, list):
                # 多帧GIF
                images = image
            else:
                # 单帧图像，创建简单的闪烁效果
                images = [image]
                
                # 添加一些变体帧创建简单动画
                for i in range(3):
                    # 创建轻微变体
                    img_array = np.array(image)
                    
                    # 随机改变一些像素
                    mask = np.random.random(img_array.shape[:2]) < 0.1
                    variant = img_array.copy()
                    variant[mask] = np.random.randint(0, 256, size=(np.sum(mask), 3))
                    
                    images.append(Image.fromarray(variant))
            
            # 保存GIF
            images[0].save(
                file_path,
                save_all=True,
                append_images=images[1:],
                duration=duration,
                loop=loop,
                optimize=True
            )
            return True
        except Exception as e:
            print(f"GIF导出错误: {e}")
            return False
    
    def create_animated_pixelart(self, base_image, num_frames=8, animation_type="bounce"):
        """创建动画像素艺术"""
        frames = []
        
        if animation_type == "bounce":
            # 弹跳动画
            for i in range(num_frames):
                # 计算偏移量
                offset_y = int(5 * np.sin(2 * np.pi * i / num_frames))
                
                # 创建新图像
                new_img = Image.new('RGB', base_image.size, (255, 255, 255))
                
                # 粘贴偏移后的图像
                new_img.paste(base_image, (0, offset_y))
                frames.append(new_img)
        
        elif animation_type == "pulse":
            # 脉冲动画
            for i in range(num_frames):
                # 计算缩放因子
                scale = 1.0 + 0.1 * np.sin(2 * np.pi * i / num_frames)
                
                # 缩放图像
                new_size = (int(base_image.width * scale), int(base_image.height * scale))
                scaled = base_image.resize(new_size, Image.NEAREST)
                
                # 居中放置
                new_img = Image.new('RGB', base_image.size, (255, 255, 255))
                offset_x = (base_image.width - scaled.width) // 2
                offset_y = (base_image.height - scaled.height) // 2
                new_img.paste(scaled, (offset_x, offset_y))
                
                frames.append(new_img)
        
        elif animation_type == "color_cycle":
            # 颜色循环动画
            for i in range(num_frames):
                # 应用颜色变换
                img_array = np.array(base_image, dtype=np.float32)
                
                # 计算颜色偏移
                hue_shift = (i * 360 / num_frames) % 360
                
                # 转换为HSV进行颜色变换
                hsv_array = self.rgb_to_hsv(img_array)
                hsv_array[:, :, 0] = (hsv_array[:, :, 0] + hue_shift / 360) % 1.0
                
                # 转换回RGB
                rgb_array = self.hsv_to_rgb(hsv_array)
                
                frames.append(Image.fromarray(rgb_array.astype(np.uint8)))
        
        return frames
    
    def rgb_to_hsv(self, rgb):
        """RGB转HSV"""
        rgb = rgb / 255.0
        
        max_val = np.max(rgb, axis=2)
        min_val = np.min(rgb, axis=2)
        delta = max_val - min_val
        
        h = np.zeros_like(max_val)
        s = np.zeros_like(max_val)
        v = max_val
        
        # 计算色相
        mask = delta != 0
        
        # 红色通道最大
        red_max = (rgb[:, :, 0] == max_val) & mask
        h[red_max] = ((rgb[:, :, 1] - rgb[:, :, 2]) / delta)[red_max] % 6
        
        # 绿色通道最大
        green_max = (rgb[:, :, 1] == max_val) & mask
        h[green_max] = ((rgb[:, :, 2] - rgb[:, :, 0]) / delta)[green_max] + 2
        
        # 蓝色通道最大
        blue_max = (rgb[:, :, 2] == max_val) & mask
        h[blue_max] = ((rgb[:, :, 0] - rgb[:, :, 1]) / delta)[blue_max] + 4
        
        h = (h * 60) % 360 / 360
        
        # 计算饱和度
        s[mask] = delta[mask] / max_val[mask]
        
        return np.stack([h, s, v], axis=2)
    
    def hsv_to_rgb(self, hsv):
        """HSV转RGB"""
        h, s, v = hsv[:, :, 0], hsv[:, :, 1], hsv[:, :, 2]
        
        h = h * 6
        i = np.floor(h).astype(int)
        f = h - i
        
        p = v * (1 - s)
        q = v * (1 - f * s)
        t = v * (1 - (1 - f) * s)
        
        rgb = np.zeros_like(hsv)
        
        # 根据色相区间计算RGB
        cases = [
            (i == 0, [v, t, p]),
            (i == 1, [q, v, p]),
            (i == 2, [p, v, t]),
            (i == 3, [p, q, v]),
            (i == 4, [t, p, v]),
            (i == 5, [v, p, q])
        ]
        
        for condition, colors in cases:
            for j in range(3):
                rgb[condition, j] = colors[j]
        
        return rgb * 255
    
    def image_to_ascii(self, image, width=80, invert=False):
        """将图像转换为ASCII艺术"""
        # 调整图像大小
        aspect_ratio = image.height / image.width
        height = int(width * aspect_ratio * 0.55)  # 字符高宽比
        
        resized = image.resize((width, height), Image.LANCZOS)
        
        # 转换为灰度
        grayscale = resized.convert('L')
        
        # 获取像素数据
        pixels = np.array(grayscale)
        
        if invert:
            pixels = 255 - pixels
        
        # 将像素值映射到ASCII字符
        ascii_art = ""
        for row in pixels:
            for pixel in row:
                # 将0-255映射到字符索引
                char_index = int(pixel / 255 * (len(self.ascii_chars) - 1))
                ascii_art += self.ascii_chars[char_index]
            ascii_art += "\n"
        
        return ascii_art
    
    def save_ascii_art(self, ascii_text, file_path):
        """保存ASCII艺术到文件"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(ascii_text)
            return True
        except Exception as e:
            print(f"ASCII保存错误: {e}")
            return False
    
    def export_sprite_sheet(self, images, file_path, columns=4, spacing=2):
        """导出精灵表"""
        if not images:
            return False
        
        try:
            # 计算精灵表尺寸
            sprite_width = images[0].width
            sprite_height = images[0].height
            
            rows = (len(images) + columns - 1) // columns
            
            sheet_width = columns * (sprite_width + spacing) - spacing
            sheet_height = rows * (sprite_height + spacing) - spacing
            
            # 创建新图像
            sheet = Image.new('RGB', (sheet_width, sheet_height), (255, 255, 255))
            
            # 粘贴所有精灵
            for i, img in enumerate(images):
                row = i // columns
                col = i % columns
                
                x = col * (sprite_width + spacing)
                y = row * (sprite_height + spacing)
                
                sheet.paste(img, (x, y))
            
            sheet.save(file_path, 'PNG')
            return True
        
        except Exception as e:
            print(f"精灵表导出错误: {e}")
            return False
    
    def create_pixel_art_animation(self, base_image, animation_frames, output_path):
        """创建像素艺术动画"""
        try:
            # 创建动画帧
            frames = []
            
            for frame_data in animation_frames:
                frame_img = base_image.copy()
                
                # 应用动画变换
                if 'offset' in frame_data:
                    dx, dy = frame_data['offset']
                    new_img = Image.new('RGB', base_image.size, (255, 255, 255))
                    new_img.paste(frame_img, (dx, dy))
                    frame_img = new_img
                
                if 'scale' in frame_data:
                    scale = frame_data['scale']
                    new_size = (int(base_image.width * scale), int(base_image.height * scale))
                    frame_img = frame_img.resize(new_size, Image.NEAREST)
                
                frames.append(frame_img)
            
            # 保存为GIF
            return self.export_gif(frames, output_path)
        
        except Exception as e:
            print(f"动画创建错误: {e}")
            return False
    
    def batch_export(self, images, output_dir, base_name, formats=['png']):
        """批量导出"""
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            results = []
            
            for i, img in enumerate(images):
                for format_type in formats:
                    if format_type == 'png':
                        filename = f"{base_name}_{i:03d}.png"
                        filepath = os.path.join(output_dir, filename)
                        success = self.export_png(img, filepath)
                        
                    elif format_type == 'gif':
                        filename = f"{base_name}_{i:03d}.gif"
                        filepath = os.path.join(output_dir, filename)
                        success = self.export_gif([img], filepath)
                    
                    elif format_type == 'ascii':
                        filename = f"{base_name}_{i:03d}.txt"
                        filepath = os.path.join(output_dir, filename)
                        ascii_text = self.image_to_ascii(img)
                        success = self.save_ascii_art(ascii_text, filepath)
                    
                    results.append({
                        'file': filename,
                        'format': format_type,
                        'success': success
                    })
            
            return results
        
        except Exception as e:
            print(f"批量导出错误: {e}")
            return []