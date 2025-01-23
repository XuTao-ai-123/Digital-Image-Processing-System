from PIL import ImageEnhance, ImageOps

class EnhanceProcessor:
    @staticmethod
    def adjust_brightness(image, factor):
        enhancer = ImageEnhance.Brightness(image)
        return enhancer.enhance(factor)
    
    @staticmethod
    def adjust_contrast(image, factor):
        enhancer = ImageEnhance.Contrast(image)
        return enhancer.enhance(factor)
    
    @staticmethod
    def equalize(image):
        gray = image.convert('L')
        return ImageOps.equalize(gray)