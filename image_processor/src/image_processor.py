from PIL import Image, ImageDraw, ImageFont
import os
import shutil
from datetime import datetime

class ImageProcessor:
    def __init__(self):
        pass
    
    def resize_image(self, image_path, output_path, width=None, height=None, scale=None, keep_aspect_ratio=True):
        """调整图片尺寸"""
        img = Image.open(image_path)
        
        if scale:
            # 按比例缩放
            new_width = int(img.width * scale)
            new_height = int(img.height * scale)
        elif width and height:
            if keep_aspect_ratio:
                # 保持宽高比，取最小缩放比例
                w_ratio = width / img.width
                h_ratio = height / img.height
                scale = min(w_ratio, h_ratio)
                new_width = int(img.width * scale)
                new_height = int(img.height * scale)
            else:
                # 不保持宽高比，直接调整为指定大小
                new_width = width
                new_height = height
        else:
            # 未指定参数，保持原大小
            new_width = img.width
            new_height = img.height
        
        resized_img = img.resize((new_width, new_height), Image.LANCZOS)
        resized_img.save(output_path)
        return output_path
    
    def convert_format(self, image_path, output_path, format):
        """转换图片格式"""
        img = Image.open(image_path)
        img.save(output_path, format=format)
        return output_path
    
    def add_text_watermark(self, image_path, output_path, text, position='bottom-right', font_size=20, color=(255, 255, 255, 128), font=None):
        """添加文字水印"""
        img = Image.open(image_path).convert('RGBA')
        draw = ImageDraw.Draw(img)
        
        if not font:
            try:
                font = ImageFont.truetype('arial.ttf', font_size)
            except:
                font = ImageFont.load_default()
        
        # 计算文字位置
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        img_width, img_height = img.size
        
        if position == 'top-left':
            x, y = 10, 10
        elif position == 'top-right':
            x, y = img_width - text_width - 10, 10
        elif position == 'bottom-left':
            x, y = 10, img_height - text_height - 10
        else:  # bottom-right
            x, y = img_width - text_width - 10, img_height - text_height - 10
        
        draw.text((x, y), text, fill=color, font=font)
        img.convert('RGB').save(output_path)
        return output_path
    
    def add_image_watermark(self, image_path, output_path, watermark_path, position='bottom-right', opacity=0.5):
        """添加图片水印"""
        img = Image.open(image_path).convert('RGBA')
        watermark = Image.open(watermark_path).convert('RGBA')
        
        # 调整水印大小
        watermark_width = int(img.width * 0.2)
        watermark_height = int(watermark.height * (watermark_width / watermark.width))
        watermark = watermark.resize((watermark_width, watermark_height), Image.LANCZOS)
        
        # 设置水印透明度
        alpha = watermark.split()[3]
        alpha = alpha.point(lambda p: p * opacity)
        watermark.putalpha(alpha)
        
        # 计算水印位置
        img_width, img_height = img.size
        watermark_width, watermark_height = watermark.size
        
        if position == 'top-left':
            x, y = 10, 10
        elif position == 'top-right':
            x, y = img_width - watermark_width - 10, 10
        elif position == 'bottom-left':
            x, y = 10, img_height - watermark_height - 10
        else:  # bottom-right
            x, y = img_width - watermark_width - 10, img_height - watermark_height - 10
        
        # 粘贴水印
        img.paste(watermark, (x, y), watermark)
        img.convert('RGB').save(output_path)
        return output_path
    
    def rename_file(self, original_path, output_dir, rename_pattern, index):
        """重命名文件"""
        base_name = os.path.basename(original_path)
        ext = os.path.splitext(base_name)[1]
        
        # 生成新文件名
        if '{index}' in rename_pattern:
            new_name = rename_pattern.format(index=index)
        elif '{timestamp}' in rename_pattern:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            new_name = rename_pattern.format(timestamp=timestamp)
        elif '{original}' in rename_pattern:
            original_name = os.path.splitext(base_name)[0]
            new_name = rename_pattern.format(original=original_name)
        else:
            new_name = f'{rename_pattern}_{index}'
        
        # 确保文件扩展名正确
        if not new_name.endswith(ext):
            new_name += ext
        
        new_path = os.path.join(output_dir, new_name)
        shutil.copy2(original_path, new_path)
        return new_path
    
    def compress_image(self, image_path, output_path, quality=85):
        """压缩图片"""
        img = Image.open(image_path)
        img.save(output_path, quality=quality, optimize=True)
        return output_path
    
    def process_image(self, image_path, output_dir, operations):
        """处理单个图片，执行多个操作"""
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成临时文件路径
        temp_path = os.path.join(output_dir, f'temp_{os.path.basename(image_path)}')
        shutil.copy2(image_path, temp_path)
        
        # 执行所有操作
        for operation in operations:
            op_type = operation['type']
            params = operation['params']
            
            if op_type == 'resize':
                temp_path = self.resize_image(temp_path, temp_path, **params)
            elif op_type == 'convert':
                # 为格式转换生成新的输出路径
                ext = params.get('format', 'JPEG').lower()
                if ext == 'jpeg':
                    ext = 'jpg'
                base_name = os.path.splitext(os.path.basename(temp_path))[0]
                new_temp_path = os.path.join(output_dir, f'{base_name}.{ext}')
                temp_path = self.convert_format(temp_path, new_temp_path, **params)
            elif op_type == 'text_watermark':
                temp_path = self.add_text_watermark(temp_path, temp_path, **params)
            elif op_type == 'image_watermark':
                temp_path = self.add_image_watermark(temp_path, temp_path, **params)
            elif op_type == 'compress':
                temp_path = self.compress_image(temp_path, temp_path, **params)
        
        return temp_path
