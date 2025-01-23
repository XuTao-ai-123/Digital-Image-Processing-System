from PIL import Image

class GeometricProcessor:
    @staticmethod
    def translate(image, tx, ty):
        return image.transform(
            image.size,
            Image.AFFINE,
            (1, 0, tx, 0, 1, ty)
        )
    
    @staticmethod
    def rotate(image, angle):
        return image.rotate(angle)
    
    @staticmethod
    def scale(image, scale_factor):
        width, height = image.size
        new_size = (
            max(1, int(width * scale_factor)),
            max(1, int(height * scale_factor))
        )
        scaled = Image.new('RGB', image.size, 'white')
        temp = image.resize(new_size, Image.Resampling.LANCZOS)
        x = (width - new_size[0]) // 2
        y = (height - new_size[1]) // 2
        scaled.paste(temp, (x, y))
        return scaled