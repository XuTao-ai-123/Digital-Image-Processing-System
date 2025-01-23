import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import numpy as np
from PIL import Image, ImageTk, ImageFilter, ImageOps, ImageEnhance


class ImageProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("数字图像处理系统")

        # 初始化变量
        self.image = None
        self.photo_refs = {}

        # 直接创建主界面
        self.create_main_ui()

    def create_main_ui(self):
        # 创建主窗口的左右分区
        main_frame = tk.Frame(self.root)
        main_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        # 左侧控制面板
        left_panel = tk.Frame(main_frame, width=300)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=10)
        left_panel.pack_propagate(False)  # 固定宽度

        # 创建滚动区域
        scroll_frame = tk.Frame(left_panel)
        scroll_frame.pack(fill=tk.BOTH, expand=True)

        # 创建画布和滚动条
        canvas = tk.Canvas(scroll_frame, width=280)
        scrollbar = tk.Scrollbar(scroll_frame, orient="vertical", command=canvas.yview)

        # 创建内部框架
        scrollable_frame = tk.Frame(canvas)
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        # 创建窗口
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=280)

        # 配置画布
        canvas.configure(yscrollcommand=scrollbar.set)

        # 放置滚动条和画布
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 绑定鼠标滚轮
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # 在scrollable_frame中添加控件
        # 文件操作按钮
        file_frame = tk.LabelFrame(scrollable_frame, text="文件操作", padx=5, pady=5)
        file_frame.pack(fill=tk.X, pady=5)
        tk.Button(file_frame, text="打开图像", command=self.load_image).pack(fill=tk.X, pady=2)
        tk.Button(file_frame, text="保存结果", command=self.save_image).pack(fill=tk.X, pady=2)

        # 参数设置区域
        self.create_parameter_controls(scrollable_frame)

        # 图像处理按钮
        process_frame = tk.LabelFrame(scrollable_frame, text="图像处理", padx=5, pady=5)
        process_frame.pack(fill=tk.X, pady=5)

        button_info = [
            ("几何变换", "geometric"),
            ("图像增强", "enhance"),
            ("图像平滑", "smooth"),
            ("图像分割", "segment")
        ]

        for text, command_type in button_info:
            btn = tk.Button(process_frame, text=text)
            btn.configure(command=lambda t=command_type: self.show_transform_results(t))
            btn.pack(fill=tk.X, pady=2)

        # 更新滚动区域
        scrollable_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))

        # 右侧显示区域
        right_panel = tk.Frame(main_frame)
        right_panel.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=10)

        # 创建5个画布的容器
        self.canvas_frames = []
        self.canvases = []

        # 原图显示在上方
        original_frame = tk.LabelFrame(right_panel, text="原始图像")
        original_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        original_canvas = tk.Canvas(original_frame, width=800, height=400, bg='white')
        original_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.canvas_frames.append(original_frame)
        self.canvases.append(original_canvas)

        # 创建下方的4个结果显示区域
        results_frame = tk.Frame(right_panel)
        results_frame.pack(fill=tk.BOTH, expand=True)

        for i in range(2):
            for j in range(2):
                frame = tk.LabelFrame(results_frame, text="处理结果")
                frame.grid(row=i, column=j, padx=5, pady=5, sticky="nsew")
                canvas = tk.Canvas(frame, width=400, height=300, bg='white')
                canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
                self.canvas_frames.append(frame)
                self.canvases.append(canvas)

        # 设置网格权重
        for i in range(2):
            results_frame.grid_columnconfigure(i, weight=1)
            results_frame.grid_rowconfigure(i, weight=1)

    def create_parameter_controls(self, parent):
        param_frame = tk.LabelFrame(parent, text="参数设置", padx=5, pady=5)
        param_frame.pack(fill=tk.X, pady=5)

        self.param_vars = {}

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
                'edge_low': ('边缘低阈值:', 0, 255, 50),
                'edge_high': ('边缘高阈值:', 0, 255, 150)
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
                    if hasattr(self, 'current_transform'):
                        self.update_results()

                scale.bind("<B1-Motion>", on_scale_change)
                scale.bind("<ButtonRelease-1>", on_scale_change)

    def load_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")]
        )
        if file_path:
            try:
                self.image = Image.open(file_path)
                # 更新原图显示
                self.update_canvas(0, self.image, "原始图像")
                messagebox.showinfo("提示", "图片打开成功！")
            except Exception as e:
                messagebox.showerror("错误", f"打开图片时出错：{str(e)}")

    def display_original_image(self):
        # 清除原有内容
        self.original_canvas.delete("all")

        # 显示原始图片
        self.original_tk_image = ImageTk.PhotoImage(self.image)
        # 计算居中位置
        x = (500 - self.image.width) // 2
        y = (400 - self.image.height) // 2
        self.original_canvas.create_image(x, y, anchor=tk.NW, image=self.original_tk_image)
        self.original_canvas.create_text(250, 390, text="原始图像", fill="black")

    def display_processed_image(self, image):
        # 清除原有内容
        self.processed_canvas.delete("all")

        # 显示处理后的图片
        self.processed_tk_image = ImageTk.PhotoImage(image)
        # 计算居中位置
        x = (500 - image.width) // 2
        y = (400 - image.height) // 2
        self.processed_canvas.create_image(x, y, anchor=tk.NW, image=self.processed_tk_image)
        self.processed_canvas.create_text(250, 390, text="处理后的图像", fill="black")

    def display_results(self, transform_type):
        """显示处理结果"""
        if self.image is None:
            messagebox.showerror("错误", "请先选择并加载图像！")
            return

        try:
            if transform_type == "geometric":
                # 几何变换
                tx = int(self.param_entries['translate_x'].get())
                ty = int(self.param_entries['translate_y'].get())
                self.processed_image = self.image.transform(
                    self.image.size, Image.AFFINE, (1, 0, tx, 0, 1, ty)
                )
            elif transform_type == "enhance":
                # 图像增强
                gray = self.image.convert("L")
                self.processed_image = ImageOps.equalize(gray)
            elif transform_type == "smooth":
                # 图像平滑
                radius = int(self.param_entries['filter_radius'].get())
                self.processed_image = self.image.filter(ImageFilter.GaussianBlur(radius))
            elif transform_type == "segment":
                # 图像分割
                threshold = int(self.param_entries['threshold'].get())
                gray = self.image.convert("L")
                thresh = np.where(np.array(gray) < threshold, 0, 255)
                self.processed_image = Image.fromarray(thresh.astype(np.uint8))

            self.update_processed_image()

        except ValueError as e:
            messagebox.showerror("错误", "请输入有效的参数值！")
        except Exception as e:
            messagebox.showerror("错误", f"处理过程中出现错误：{str(e)}")

    def update_processed_image(self):
        # 更新显示处理后的图像
        if self.processed_image:
            # 确保处理后的图像大小与原一致
            if self.processed_image.size != self.image.size:
                self.processed_image = self.processed_image.resize(self.image.size, Image.Resampling.LANCZOS)
            self.display_processed_image(self.processed_image)

    def save_image(self):
        if self.processed_image:
            save_path = filedialog.asksaveasfilename(defaultextension=".png")
            if save_path:
                self.processed_image.save(save_path)
                messagebox.showinfo("提示", "图片保存成功！")

    def update_results(self):
        """根据当前选择的功能更新处理结果"""
        if not self.image:
            return

        print(f"更新结果: {self.current_transform}")  # 调试输出

        # 获取当前参数值
        params = {key: var.get() for key, var in self.param_vars.items()}

        # 更新原图显示
        self.update_canvas(0, self.image, "原始图像")

        try:
            # 根据当前选择的功能更新结果
            if self.current_transform == "geometric":
                self.update_geometric_results(params)
            elif self.current_transform == "enhance":
                self.update_enhance_results(params)
            elif self.current_transform == "smooth":
                self.update_smooth_results(params)
            elif self.current_transform == "segment":
                self.update_segment_results(params)
        except Exception as e:
            print(f"处理出错: {str(e)}")  # 调试输出

    def update_canvas(self, index, image, title):
        """更新单个画布的显示"""
        canvas = self.canvases[index]
        frame = self.canvas_frames[index]

        # 清除画布
        canvas.delete("all")
        canvas.configure(bg='white')

        # 获取画布尺寸
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()
        
        if canvas_width <= 1:  # 如果画布尺寸还未初始化
            canvas_width = 400
            canvas_height = 300

        # 计算缩放比例以适应画布
        width_ratio = canvas_width / image.width
        height_ratio = canvas_height / image.height
        scale = min(width_ratio, height_ratio) * 0.9  # 留出一些边距

        # 计算缩放后的尺寸
        display_width = int(image.width * scale)
        display_height = int(image.height * scale)

        # 缩放图像以适应画布
        display_image = image.resize((display_width, display_height), Image.Resampling.LANCZOS)

        # 创建PhotoImage对象
        if not hasattr(self, 'photo_refs'):
            self.photo_refs = {}
        self.photo_refs[index] = ImageTk.PhotoImage(display_image)

        # 计算居中位置
        x = (canvas_width - display_width) // 2
        y = (canvas_height - display_height) // 2

        # 显示图像
        canvas.create_image(x, y, anchor=tk.NW, image=self.photo_refs[index])

        # 更新标题
        frame.configure(text=title)

    def show_transform_results(self, transform_type):
        """显示选定类型的变换结果"""
        if self.image is None:
            messagebox.showerror("错误", "请先选择并加载图像！")
            return

        print(f"显示变换结果: {transform_type}")  # 调试输出
        self.current_transform = transform_type
        self.update_results()

    def update_geometric_results(self, params):
        """更新几何变换的结果"""
        # 1. 平移
        translated = self.image.transform(
            self.image.size,
            Image.AFFINE,
            (1, 0, params['translate_x'], 0, 1, params['translate_y'])
        )
        self.update_canvas(1, translated,
                           f"平移变换\n(X: {params['translate_x']}, Y: {params['translate_y']})")

        # 2. 旋转
        rotated = self.image.rotate(params['rotate'])
        self.update_canvas(2, rotated,
                           f"旋转变换\n(角度: {params['rotate']}°)")

        # 3. 缩放 - 整体缩放实现
        scale = params['scale']
        # 获取原始图像尺寸
        width, height = self.image.size
        # 计算新的尺寸
        new_size = (
            max(1, int(width * scale)),  # 确保尺寸至少为1
            max(1, int(height * scale))
        )
        # 创建新的空白图像（与原图大小相同）
        scaled = Image.new('RGB', self.image.size, 'white')
        # 缩放原始图像
        temp = self.image.resize(new_size, Image.Resampling.LANCZOS)
        # 计算居中位置
        x = (width - new_size[0]) // 2
        y = (height - new_size[1]) // 2
        # 将缩放后的图像粘贴到中心位置
        scaled.paste(temp, (x, y))
        self.update_canvas(3, scaled, f"缩放变换\n(比例: {scale:.1f})")

        # 4. 镜像
        mirrored = self.image.transpose(Image.FLIP_LEFT_RIGHT)
        self.update_canvas(4, mirrored, "镜像变换")

    def update_enhance_results(self, params):
        """更新图像增强的结果"""
        # 转换为灰度图像
        gray = self.image.convert('L')

        # 1. 原始灰度图
        self.update_canvas(1, gray, "灰度图像")

        # 2. 亮度调整
        brightness = ImageEnhance.Brightness(self.image)
        brightened = brightness.enhance(params['brightness'])
        self.update_canvas(2, brightened,
                           f"亮度增强\n(系数: {params['brightness']:.1f})")

        # 3. 对比度调整
        contrast = ImageEnhance.Contrast(self.image)
        contrasted = contrast.enhance(params['contrast'])
        self.update_canvas(3, contrasted,
                           f"对比度增强\n(系数: {params['contrast']:.1f})")

        # 4. 直方图均衡化
        equalized = ImageOps.equalize(gray)
        self.update_canvas(4, equalized, "直方图均衡化")

    def update_smooth_results(self, params):
        """更新图像平滑的结果"""
        # 1. 均值滤波
        mean_filtered = self.image.filter(
            ImageFilter.BoxBlur(params['mean_radius'])
        )
        self.update_canvas(1, mean_filtered,
                           f"均值滤波\n(半径: {params['mean_radius']})")

        # 2. 高斯滤波
        gaussian_filtered = self.image.filter(
            ImageFilter.GaussianBlur(params['gaussian_radius'])
        )
        self.update_canvas(2, gaussian_filtered,
                           f"高斯滤波\n(半径: {params['gaussian_radius']})")

        # 3. 中值滤波
        median_filtered = self.image.filter(
            ImageFilter.MedianFilter(params['median_radius'])
        )
        self.update_canvas(3, median_filtered,
                           f"中值滤波\n(半径: {params['median_radius']})")

        # 4. 原图（用于对比）
        self.update_canvas(4, self.image, "原图（对比）")

    def update_segment_results(self, params):
        """更新图像分割的结果"""
        # 转换为灰度图像
        gray = self.image.convert('L')
        gray_np = np.array(gray)

        # 1. Canny边缘检测
        edges = cv2.Canny(np.array(gray),
                          params['edge_low'],
                          params['edge_high'])
        edge_image = Image.fromarray(edges)
        self.update_canvas(1, edge_image,
                           f"Canny边缘检测\n(阈值: {params['edge_low']}-{params['edge_high']})")

        # 2. 阈值分割
        _, thresh = cv2.threshold(np.array(gray),
                                  params['threshold'], 255,
                                  cv2.THRESH_BINARY)
        threshold_image = Image.fromarray(thresh)
        self.update_canvas(2, threshold_image,
                           f"阈值分割\n(阈值: {params['threshold']})")

        # 3. 区域生长
        seed_point = (gray_np.shape[0] // 2, gray_np.shape[1] // 2)  # 使用图像中心点作为种子点
        segmented = self.region_growing(gray_np, seed_point, params['threshold'])
        region_image = Image.fromarray(segmented)
        self.update_canvas(3, region_image,
                           f"区域生长\n(阈值: {params['threshold']})")

        # 4. 原图（用于对比）
        self.update_canvas(4, self.image, "原图（对比）")

    def region_growing(self, image, seed_point, threshold):
        """区域生长算法"""
        rows, cols = image.shape
        segmented = np.zeros_like(image)
        segmented[seed_point] = 255
        seed_value = image[seed_point]

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

        stack = [seed_point]
        while stack:
            current = stack.pop()
            for neighbor in get_neighbors(current):
                if segmented[neighbor] == 0 and \
                        abs(int(image[neighbor]) - int(seed_value)) < threshold:
                    segmented[neighbor] = 255
                    stack.append(neighbor)

        return segmented


def main():
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口

    # 创建并显示欢迎窗口
    welcome = tk.Toplevel(root)
    welcome.title("欢迎")
    welcome.attributes('-topmost', True)

    # 设置欢迎窗口大小和位置
    window_width = 400
    window_height = 200
    screen_width = welcome.winfo_screenwidth()
    screen_height = welcome.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    welcome.geometry(f"{window_width}x{window_height}+{x}+{y}")

    # 设置欢迎窗口属性
    welcome.grab_set()
    welcome.protocol("WM_DELETE_WINDOW", lambda: None)

    # 创建应用程序实例
    app = ImageProcessorApp(root)

    # 欢迎文本
    tk.Label(welcome, text="欢迎使用数字图像处理系统",
             font=("Arial", 16, "bold")).pack(expand=True)

    def on_welcome_close():
        welcome.destroy()
        # 设置主窗口大小和位置
        window_width = 1600
        window_height = 1000
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        root.deiconify()

    tk.Button(welcome, text="确定", command=on_welcome_close,
              width=10, height=2).pack(pady=20)

    root.mainloop()


if __name__ == "__main__":
    main()
