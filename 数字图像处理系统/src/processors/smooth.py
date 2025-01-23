from PIL import ImageFilter

class SmoothProcessor:
    @staticmethod
    def mean_filter(image, radius):
        """均值滤波"""
        return image.filter(ImageFilter.BoxBlur(radius))
    
    @staticmethod
    def gaussian_filter(image, radius):
        """高斯滤波"""
        return image.filter(ImageFilter.GaussianBlur(radius))
    
    @staticmethod
    def median_filter(image, radius):
        """中值滤波"""
        return image.filter(ImageFilter.MedianFilter(size=radius)) 