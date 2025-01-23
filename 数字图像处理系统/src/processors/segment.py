import cv2
import numpy as np
from PIL import Image

class SegmentProcessor:
    @staticmethod
    def threshold_segment(image, threshold):
        """阈值分割"""
        # 转换为灰度图
        gray = image.convert('L')
        # 阈值分割
        thresh = np.where(np.array(gray) < threshold, 0, 255)
        return Image.fromarray(thresh.astype(np.uint8))
    
    @staticmethod
    def canny_edge(image, low_threshold, high_threshold):
        """Canny边缘检测"""
        # 转换为OpenCV格式
        img_np = np.array(image)
        # 转换为灰度图
        gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        # 边缘检测
        edges = cv2.Canny(gray, low_threshold, high_threshold)
        return Image.fromarray(edges)
    
    @staticmethod
    def region_growing(image, seed_point, threshold):
        """区域生长"""
        # 转换为灰度图
        gray = image.convert('L')
        img_np = np.array(gray)
        rows, cols = img_np.shape
        
        # 初始化结果图像
        segmented = np.zeros_like(img_np)
        segmented[seed_point] = 255
        seed_value = img_np[seed_point]
        
        def get_neighbors(point):
            r, c = point
            neighbors = []
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    new_r, new_c = r + dr, c + dc
                    if 0 <= new_r < rows and 0 <= new_c < cols:
                        neighbors.append((new_r, new_c))
            return neighbors
        
        # 区域生长过程
        stack = [seed_point]
        while stack:
            current = stack.pop()
            for neighbor in get_neighbors(current):
                if segmented[neighbor] == 0 and \
                   abs(int(img_np[neighbor]) - int(seed_value)) < threshold:
                    segmented[neighbor] = 255
                    stack.append(neighbor)
        
        return Image.fromarray(segmented) 