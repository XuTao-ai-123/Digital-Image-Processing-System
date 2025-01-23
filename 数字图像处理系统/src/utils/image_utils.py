from PIL import Image, ImageTk

class ImageUtils:
    @staticmethod
    def resize_to_fit(image, max_width, max_height):
        """调整图像大小以适应指定区域"""
        width_ratio = max_width / image.width
        height_ratio = max_height / image.height
        scale = min(width_ratio, height_ratio) * 0.9
        
        new_width = int(image.width * scale)
        new_height = int(image.height * scale)
        
        return image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    @staticmethod
    def create_photo_image(image, width, height):
        """创建适合显示的PhotoImage对象"""
        display_image = ImageUtils.resize_to_fit(image, width, height)
        return ImageTk.PhotoImage(display_image)