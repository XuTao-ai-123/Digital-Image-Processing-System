import os
import sys
import tkinter as tk

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.gui.main_window import MainWindow

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
    
    # 创建应用程序实例
    app = MainWindow(root)
    
    # 欢迎文本
    tk.Label(welcome, text="欢迎使用数字图像处理系统",
             font=("Arial", 16, "bold")).pack(expand=True)
    
    def on_welcome_close():
        welcome.destroy()
        root.deiconify()
        # 设置主窗口大小和位置
        window_width = 1600
        window_height = 1000
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    tk.Button(welcome, text="确定", command=on_welcome_close,
              width=10, height=2).pack(pady=20)
    
    root.mainloop()

if __name__ == "__main__":
    main()