import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageOps
import os
import sys

class NeleColorParserApp:#主程序，制作者：GKll44
    def __init__(self, root):
        self.root = root
        self.root.title("NeleColor")
        self.root.geometry("800x650")
        self.load_icon()
        
    def load_icon(self):
        """更健壮的图标加载方法"""
        try:
            if getattr(sys, 'frozen', False):
                # 打包后模式
                base_path = sys._MEIPASS
            else:
                # 开发模式
                base_path = os.path.dirname(os.path.abspath(__file__))
            
            icon_path = os.path.join(base_path, "icon.ico")
            self.root.iconbitmap(icon_path)
        except Exception as e:
            print(f"加载图标失败: {e}")  # 调试用，可移除
            pass  # 失败时使用默认图标
        
        self.file_path = None
        self.preview_image = None
        self.original_image = None  # raw image(听说过没)
        self.image_info = {"width": 0, "height": 0, "ext": ""}
        
        self.setup_ui()
    
    def setup_ui(self):
        # 菜单
        self.menubar = tk.Menu(self.root)
        
        # 文件
        self.file_menu = tk.Menu(self.menubar, tearoff=0)
        self.file_menu.add_command(label="打开", command=self.open_file)
        self.file_menu.add_command(label="导出图片", command=self.export_image, state=tk.DISABLED)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="退出", command=self.root.quit)
        self.menubar.add_cascade(label="文件", menu=self.file_menu)
        
        self.root.config(menu=self.menubar)
        
        # 三调曲
        self.top_frame = tk.Frame(self.root)
        self.top_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.middle_frame = tk.Frame(self.root)
        self.middle_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.bottom_frame = tk.Frame(self.root)
        self.bottom_frame.pack(fill=tk.X, padx=10, pady=5)
        
        #定义文件信息，防止你不知道
        self.info_label = tk.Label(self.top_frame, text="你还没选择文件呢", anchor=tk.W)
        self.info_label.pack(fill=tk.X, pady=2)
        
        self.resolution_label = tk.Label(self.top_frame, text="分辨率: -", anchor=tk.W)
        self.resolution_label.pack(fill=tk.X, pady=2)
        
        self.format_label = tk.Label(self.top_frame, text="原格式: -", anchor=tk.W)
        self.format_label.pack(fill=tk.X, pady=2)
        
        #图片预览
        self.preview_canvas = tk.Canvas(self.middle_frame, bg="#f0f0f0", bd=2, relief=tk.SUNKEN)
        self.preview_canvas.pack(fill=tk.BOTH, expand=True)
        
        self.preview_text = self.preview_canvas.create_text(
            400, 300, 
            text="请选择文件(*^▽^*)", 
            font=("Arial", 16), 
            fill="gray"
        )
        
        #工具栏
        self.toolbar = tk.Frame(self.bottom_frame)
        self.toolbar.pack(fill=tk.X)
        
        # 是旋转按钮！！1
        self.rotate_left_btn = tk.Button(
            self.toolbar, 
            text="↺",  #脖子扭扭
            command=lambda: self.rotate_image(90),
            width=8,
            font=("Arial", 10, "bold")
        )
        self.rotate_right_btn = tk.Button(
            self.toolbar, 
            text="↻", #屁股扭扭
            command=lambda: self.rotate_image(-90),
            width=8,
            font=("Arial", 10, "bold")
        )
        
        # 添加一些间距，不要让它们合起来了啊啊啊啊o((>ω< ))o
        tk.Label(self.toolbar, width=2).pack(side=tk.LEFT)
        
        # 旋转button
        self.rotate_left_btn.pack(side=tk.LEFT, padx=2)
        self.rotate_right_btn.pack(side=tk.LEFT, padx=2)
        
        # 初始先禁用
        self.rotate_left_btn.config(state=tk.DISABLED)
        self.rotate_right_btn.config(state=tk.DISABLED)
    
    def open_file(self):
        """打开.nelecolor文件并显示预览"""
        file_path = filedialog.askopenfilename(
            filetypes=[("NeleColor文件", "*.nelecolor")]
        )
        
        if not file_path:
            return
        
        try:
            self.file_path = file_path
            img, ext = self.parse_nelecolor(file_path)
            self.original_image = img.copy()  # 保存图像
            
            self.image_info = {
                "width": img.width,
                "height": img.height,
                "ext": ext
            }
            
            self.info_label.config(text=f"文件: {os.path.basename(file_path)}")
            self.resolution_label.config(text=f"分辨率: {img.width}x{img.height}")
            self.format_label.config(text=f"格式: {ext}")
            
            # 不会把不会吧，还有人不知道这段代码是什么吧？！！！！
            self.show_preview(img)
            
            self.file_menu.entryconfig("导出图片", state=tk.NORMAL)
            self.rotate_left_btn.config(state=tk.NORMAL)
            self.rotate_right_btn.config(state=tk.NORMAL)
            
        except Exception as e:
            messagebox.showerror("错误", f"无法解析文件:\n{e}")
    
    def parse_nelecolor(self, file_path):#最让我头疼的就是解析文件这段，折腾了我4个小时
        """查看.nelecolor文件"""
        with open(file_path, "rb") as f:
            # 元信息
            header = b""
            while True:
                byte = f.read(1)
                if byte == b"\n":  # 换行符表示头结束
                    break
                header += byte
            
            header_str = header.decode("utf-8")
            if "x" not in header_str or "." not in header_str:
                raise ValueError("无效的.nelecolor文件头格式")
                """既然格式是我创作的，这里就讲些原理：假设你知道每个像素点的十六进制颜色，就将每个像素点的十六进制颜色以十六进制源码输入颜色，并解析"""
            # 
            resolution_part, ext = header_str.split(".", 1)
            width, height = map(int, resolution_part.split("x"))
            ext = "." + ext  # 添加点为断点
            
            pixel_data = f.read()
            expected_size = width * height * 3
            actual_size = len(pixel_data)
            
            if actual_size < expected_size:
                missing_pixels = (expected_size - actual_size) // 3
                raise ValueError(f"缺少{missing_pixels}个像素点！")
            elif actual_size > expected_size:
                extra_pixels = (actual_size - expected_size) // 3
                raise ValueError(f"多了{extra_pixels}个像素点！")
            
            img = Image.new("RGB", (width, height))
            pixels = img.load()
            
            index = 0
            for y in range(height):
                for x in range(width):
                    r = pixel_data[index]
                    g = pixel_data[index + 1]
                    b = pixel_data[index + 2]
                    
                    if not (0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255):
                        raise ValueError("颜色超出范围！（0-FF）")
                    
                    pixels[x, y] = (r, g, b)
                    index += 3
            
            return img, ext
    
    def show_preview(self, img):
        canvas_width = self.preview_canvas.winfo_width()
        canvas_height = self.preview_canvas.winfo_height()
        
        if canvas_width < 10 or canvas_height < 10: 
            canvas_width, canvas_height = 780, 480
        
        ratio = min(
            (canvas_width - 20) / img.width,
            (canvas_height - 20) / img.height
        )
        new_size = (int(img.width * ratio), int(img.height * ratio))
        
        img_resized = img.resize(new_size, Image.Resampling.LANCZOS)
        self.preview_image = ImageTk.PhotoImage(img_resized)
        
        self.preview_canvas.delete("all")
        self.preview_canvas.create_image(
            canvas_width // 2,
            canvas_height // 2,
            image=self.preview_image
        )
    
    def rotate_image(self, angle):
        if not self.original_image:
            return
        
        rotated_img = self.original_image.rotate(angle, expand=True)
        self.original_image = rotated_img
        
        self.image_info["width"] = rotated_img.width
        self.image_info["height"] = rotated_img.height
        self.resolution_label.config(text=f"分辨率: {rotated_img.width}x{rotated_img.height}")
        
        self.show_preview(rotated_img)
    
    def export_image(self):
        if not self.file_path or not self.original_image:
            return
        
        base_name = os.path.splitext(os.path.basename(self.file_path))[0]
        default_name = f"{base_name}{self.image_info['ext']}"
        
        save_path = filedialog.asksaveasfilename(
            defaultextension=self.image_info['ext'],
            initialfile=default_name,
            filetypes=[("图片文件", f"*{self.image_info['ext']}")]
        )
        
        if not save_path:
            return
        
        try:
            self.original_image.save(save_path)
            messagebox.showinfo("成功", f"图片已导出为:\n{save_path}o(*￣▽￣*)ブ")
        except Exception as e:
            messagebox.showerror("错误", f"导出失败:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = NeleColorParserApp(root)
    root.mainloop()