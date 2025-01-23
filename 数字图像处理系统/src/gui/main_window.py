import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from ..gui.components import ControlPanel, DisplayPanel
from ..processors import GeometricProcessor, EnhanceProcessor, SmoothProcessor, SegmentProcessor

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("数字图像处理系统")
        
        # 初始化变量
        self.image = None
        self.photo_refs = {}
        self.current_transform = None
        
        # 创建主界面
        self.create_main_ui()
    
    def create_main_ui(self):
        # 创建主窗口的左右分区
        main_frame = tk.Frame(self.root)
        main_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        
        # 创建控制面板
        self.control_panel = ControlPanel(main_frame, self)
        
        # 创建显示面板
        self.display_panel = DisplayPanel(main_frame, self)
    
    def load_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")]
        )
        if file_path:
            try:
                self.image = Image.open(file_path)
                self.display_panel.update_original_image(self.image)
                messagebox.showinfo("提示", "图片打开成功！")
            except Exception as e:
                messagebox.showerror("错误", f"打开图片时出错：{str(e)}")
    
    def save_image(self):
        if hasattr(self, 'processed_image') and self.processed_image:
            save_path = filedialog.asksaveasfilename(defaultextension=".png")
            if save_path:
                self.processed_image.save(save_path)
                messagebox.showinfo("提示", "图片保存成功！")

    def update_results(self):
        """更新处理结果"""
        if not self.image or not self.current_transform:
            return
        
        params = self.control_panel.param_vars
        
        if self.current_transform == "geometric":
            # 几何变换处理
            translated = GeometricProcessor.translate(
                self.image, 
                params['translate_x'].get(), 
                params['translate_y'].get()
            )
            self.display_panel.update_result_image(0, translated, "平移变换")
            
            rotated = GeometricProcessor.rotate(self.image, params['rotate'].get())
            self.display_panel.update_result_image(1, rotated, "旋转变换")
            
            scaled = GeometricProcessor.scale(self.image, params['scale'].get())
            self.display_panel.update_result_image(2, scaled, "缩放变换")
            
            mirrored = self.image.transpose(Image.FLIP_LEFT_RIGHT)
            self.display_panel.update_result_image(3, mirrored, "镜像变换")

        elif self.current_transform == "enhance":
            # 图像增强处理
            brightened = EnhanceProcessor.adjust_brightness(
                self.image, 
                params['brightness'].get()
            )
            self.display_panel.update_result_image(0, brightened, "亮度调整")
            
            contrasted = EnhanceProcessor.adjust_contrast(
                self.image, 
                params['contrast'].get()
            )
            self.display_panel.update_result_image(1, contrasted, "对比度调整")
            
            equalized = EnhanceProcessor.equalize(self.image)
            self.display_panel.update_result_image(2, equalized, "直方图均衡化")
            
            self.display_panel.update_result_image(3, self.image, "原图对比")

        elif self.current_transform == "smooth":
            # 图像平滑处理
            mean = SmoothProcessor.mean_filter(
                self.image, 
                params['mean_radius'].get()
            )
            self.display_panel.update_result_image(0, mean, "均值滤波")
            
            gaussian = SmoothProcessor.gaussian_filter(
                self.image, 
                params['gaussian_radius'].get()
            )
            self.display_panel.update_result_image(1, gaussian, "高斯滤波")
            
            median = SmoothProcessor.median_filter(
                self.image, 
                params['median_radius'].get()
            )
            self.display_panel.update_result_image(2, median, "中值滤波")
            
            self.display_panel.update_result_image(3, self.image, "原图对比")

        elif self.current_transform == "segment":
            # 图像分割处理
            threshold = SegmentProcessor.threshold_segment(
                self.image, 
                params['threshold'].get()
            )
            self.display_panel.update_result_image(0, threshold, "阈值分割")
            
            edges = SegmentProcessor.canny_edge(
                self.image,
                params['edge_low'].get(),
                params['edge_high'].get()
            )
            self.display_panel.update_result_image(1, edges, "Canny边缘检测")
            
            # 使用图像中心点作为种子点
            w, h = self.image.size
            seed_point = (h//2, w//2)
            region = SegmentProcessor.region_growing(
                self.image,
                seed_point,
                params['region_threshold'].get()
            )
            self.display_panel.update_result_image(2, region, "区域生长")
            
            self.display_panel.update_result_image(3, self.image, "原图对比")

    def show_transform_results(self, transform_type):
        """显示变换结果"""
        if not self.image:
            messagebox.showerror("错误", "请先选择并加载图像！")
            return
        
        self.current_transform = transform_type
        self.update_results()