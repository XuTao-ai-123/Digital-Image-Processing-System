import tkinter as tk
from PIL import Image, ImageTk
import sys
import os

# 获取项目根目录
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.processors import GeometricProcessor, EnhanceProcessor, SmoothProcessor, SegmentProcessor

class ControlPanel:
    def __init__(self, parent, main_window):
        self.main_window = main_window
        self.frame = tk.Frame(parent, width=300)
        self.frame.pack(side=tk.LEFT, fill=tk.Y, padx=10)
        self.frame.pack_propagate(False)
        
        # 创建滚动区域
        self.create_scrollable_frame()
        
        # 初始化参数变量字典
        self.param_vars = {}
        
        # 在滚动框架中创建控件
        self.create_control_panel()
    
    def create_scrollable_frame(self):
        # 创建画布和滚动条
        self.canvas = tk.Canvas(self.frame, width=280)
        scrollbar = tk.Scrollbar(self.frame, orient="vertical", command=self.canvas.yview)
        
        # 创建滚动框架
        self.scrollable_frame = tk.Frame(self.canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        # 在画布上创建窗口
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", width=280)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # 放置滚动条和画布
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 绑定鼠标滚轮
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
    
    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    def create_control_panel(self):
        # 创建文件操作按钮
        self.create_file_controls()
        
        # 创建参数设置区域
        self.create_parameter_controls()
        
        # 创建处理按钮
        self.create_process_controls()
    
    def create_file_controls(self):
        file_frame = tk.LabelFrame(self.scrollable_frame, text="文件操作", padx=5, pady=5)
        file_frame.pack(fill=tk.X, pady=5)
        
        tk.Button(file_frame, text="打开图像",
                 command=self.main_window.load_image).pack(fill=tk.X, pady=2)
        tk.Button(file_frame, text="保存结果",
                 command=self.main_window.save_image).pack(fill=tk.X, pady=2)

    def create_parameter_controls(self):
        param_frame = tk.LabelFrame(self.scrollable_frame, text="参数设置", padx=5, pady=5)
        param_frame.pack(fill=tk.X, pady=5)

        # 定义所有参数
        all_params = {
            '几何变换': {
                'translate_x': ('X平移:', -100, 100, 0),
                'translate_y': ('Y平移:', -100, 100, 0),
                'rotate': ('旋转角度:', 0, 360, 90),
                'scale': ('缩放比例:', 0.1, 3.0, 1.0)
            },
            '图像增强': {
                'brightness': ('亮度:', 0.1, 3.0, 1.0),
                'contrast': ('对比度:', 0.1, 3.0, 1.0)
            },
            '图像平滑': {
                'mean_radius': ('均值半径:', 1, 20, 3),
                'gaussian_radius': ('高斯半径:', 1, 20, 3),
                'median_radius': ('中值半径:', 1, 20, 3)
            },
            '图像分割': {
                'threshold': ('阈值:', 0, 255, 128),
                'edge_low': ('Canny低阈值:', 0, 255, 50),
                'edge_high': ('Canny高阈值:', 0, 255, 150),
                'region_threshold': ('区域生长阈值:', 0, 255, 30)
            }
        }

        # 创建所有滑动条
        for category, params in all_params.items():
            group = tk.LabelFrame(param_frame, text=category)
            group.pack(fill=tk.X, pady=2)

            for key, (label, min_val, max_val, default) in params.items():
                frame = tk.Frame(group)
                frame.pack(fill=tk.X, pady=2)

                tk.Label(frame, text=label, width=10).pack(side=tk.LEFT)

                if isinstance(default, float):
                    var = tk.DoubleVar(value=default)
                    scale = tk.Scale(frame, from_=min_val, to=max_val,
                                   resolution=0.1, orient=tk.HORIZONTAL,
                                   variable=var)
                else:
                    var = tk.IntVar(value=default)
                    scale = tk.Scale(frame, from_=min_val, to=max_val,
                                   orient=tk.HORIZONTAL, variable=var)

                scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
                self.param_vars[key] = var

                # 修改事件绑定方式
                def on_scale_change(event, key=key):
                    if hasattr(self.main_window, 'current_transform'):
                        self.main_window.update_results()

                scale.bind("<B1-Motion>", on_scale_change)
                scale.bind("<ButtonRelease-1>", on_scale_change)

    def create_process_controls(self):
        process_frame = tk.LabelFrame(self.scrollable_frame, text="图像处理", padx=5, pady=5)
        process_frame.pack(fill=tk.X, pady=5)

        button_info = [
            ("几何变换", "geometric"),
            ("图像增强", "enhance"),
            ("图像平滑", "smooth"),
            ("图像分割", "segment")
        ]

        for text, command_type in button_info:
            btn = tk.Button(process_frame, text=text)
            btn.configure(command=lambda t=command_type: self.main_window.show_transform_results(t))
            btn.pack(fill=tk.X, pady=2)

class DisplayPanel:
    def __init__(self, parent, main_window):
        self.main_window = main_window
        self.frame = tk.Frame(parent)
        self.frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=10)
        
        self.create_display_panel()
    
    def create_display_panel(self):
        # 创建原图显示区域
        self.create_original_display()
        
        # 创建结果显示区域
        self.create_results_display()

    def create_original_display(self):
        # 原图显示在上方
        self.original_frame = tk.LabelFrame(self.frame, text="原始图像")
        self.original_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self.original_canvas = tk.Canvas(self.original_frame, width=800, height=400, bg='white')
        self.original_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def create_results_display(self):
        # 创建下方的4个结果显示区域
        self.results_frame = tk.Frame(self.frame)
        self.results_frame.pack(fill=tk.BOTH, expand=True)

        self.result_canvases = []
        for i in range(2):
            for j in range(2):
                frame = tk.LabelFrame(self.results_frame, text="处理结果")
                frame.grid(row=i, column=j, padx=5, pady=5, sticky="nsew")
                canvas = tk.Canvas(frame, width=400, height=300, bg='white')
                canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
                self.result_canvases.append(canvas)

        # 设置网格权重
        for i in range(2):
            self.results_frame.grid_columnconfigure(i, weight=1)
            self.results_frame.grid_rowconfigure(i, weight=1)

    def update_original_image(self, image):
        """更新原始图像显示"""
        self.update_canvas(self.original_canvas, image, "原始图像")

    def update_result_image(self, index, image, title):
        """更新处理结果图像显示"""
        if 0 <= index < len(self.result_canvases):
            self.update_canvas(self.result_canvases[index], image, title)

    def update_canvas(self, canvas, image, title):
        """更新单个画布的显示"""
        # 清除画布
        canvas.delete("all")
        
        # 获取画布尺寸
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()
        
        if canvas_width <= 1:  # 如果画布尺寸还未初始化
            canvas_width = 400
            canvas_height = 300

        # 计算缩放比例
        width_ratio = canvas_width / image.width
        height_ratio = canvas_height / image.height
        scale = min(width_ratio, height_ratio) * 0.9

        # 缩放图像
        display_width = int(image.width * scale)
        display_height = int(image.height * scale)
        display_image = image.resize((display_width, display_height), Image.Resampling.LANCZOS)

        # 创建PhotoImage对象
        photo = ImageTk.PhotoImage(display_image)
        # 保存引用防止被垃圾回收
        if not hasattr(canvas, 'images'):
            canvas.images = []
        canvas.images.append(photo)

        # 计算居中位置
        x = (canvas_width - display_width) // 2
        y = (canvas_height - display_height) // 2

        # 显示图像
        canvas.create_image(x, y, anchor=tk.NW, image=photo)
        
        # 更新标题
        canvas.master.configure(text=title)