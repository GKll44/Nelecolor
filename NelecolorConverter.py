import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
from PIL import ImageTk
import os

class NeleColorConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("NeleColor converter")
        self.root.geometry("800x500")
        
        self.image_path = None
        self.preview_image = None
        self.encoding_format = tk.StringVar(value="rgb")  # Default to RGB
        self.setup_ui()
    
    def setup_ui(self):
        self.preview_frame = tk.Frame(self.root, width=400, height=500, bg="#f0f0f0")
        self.preview_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.preview_frame.pack_propagate(False)
        
        self.preview_label = tk.Label(self.preview_frame, text="图片预览区域，导入后就会显示", bg="#f0f0f0")
        self.preview_label.pack(expand=True)
        
        self.control_frame = tk.Frame(self.root, width=400, height=500, padx=20, pady=20)
        self.control_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.control_frame.pack_propagate(False)
        
        # Encoding format selection
        format_frame = tk.Frame(self.control_frame)
        format_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(format_frame, text="编码格式:").pack(side=tk.LEFT)
        
        tk.Radiobutton(
            format_frame, 
            text="RGB", 
            variable=self.encoding_format, 
            value="rgb"
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Radiobutton(
            format_frame, 
            text="RGBA", 
            variable=self.encoding_format, 
            value="rgba"
        ).pack(side=tk.LEFT)
        
        # 导入
        self.import_btn = tk.Button(
            self.control_frame,
            text="导入图片",
            command=self.import_image,
            height=2,
            font=("Arial", 12)
        )
        self.import_btn.pack(fill=tk.X, pady=10)
        
        # 导出
        self.export_btn = tk.Button(
            self.control_frame,
            text="导出.nelecolor文件",
            command=self.export_nelecolor,
            state=tk.DISABLED,
            height=2,
            font=("Arial", 12)
        )
        self.export_btn.pack(fill=tk.X, pady=10)
        
        # 状态
        self.status_label = tk.Label(self.control_frame, text="等待导入图片...", fg="gray")
        self.status_label.pack(fill=tk.X, pady=10)
    
    def import_image(self):
        """导入图片并显示预览"""
        file_path = filedialog.askopenfilename(
            filetypes=[("图片文件", "*.png;*.jpg;*.jpeg;*.bmp")]
        )
        
        if not file_path:
            return
        
        try:
            self.image_path = file_path
            img = Image.open(file_path)
            
            # 调整预览大小
            max_size = (380, 480)
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            self.preview_image = ImageTk.PhotoImage(img)
            self.preview_label.config(image=self.preview_image, text="")
            
            self.export_btn.config(state=tk.NORMAL)
            self.status_label.config(
                text=f"已加载: {os.path.basename(file_path)} ({img.width}x{img.height})",
                fg="green"
            )
        
        except Exception as e:
            messagebox.showerror("错误", f"无法加载图片:\n{e}")
    
    def export_nelecolor(self):
        """导出为NeleColor格式"""
        if not self.image_path:
            return
        
        img = Image.open(self.image_path)
        width, height = img.size
        ext = os.path.splitext(self.image_path)[1].lower()  #指".png"
        
        default_name = os.path.splitext(os.path.basename(self.image_path))[0] + ".nelecolor"
        save_path = filedialog.asksaveasfilename(
            defaultextension=".nelecolor",
            initialfile=default_name,
            filetypes=[("NeleColor文件", "*.nelecolor")]#输出的文件以.nelecolor格式储存
        )
        
        if not save_path:
            return
        
        try:
            with open(save_path, "wb") as f:
                # 写入元信息头（包含编码格式）
                encoding = self.encoding_format.get()
                header = f"{width}x{height}{ext}:{encoding}\n"  # 例如 "256x256.png:rgba"
                f.write(header.encode("utf-8"))
                
                # 根据选择的格式写入像素数据
                if encoding == "rgb":
                    img = img.convert("RGB")
                    for y in range(height):
                        for x in range(width):
                            r, g, b = img.getpixel((x, y))
                            f.write(bytes([r, g, b]))
                else:  # rgba
                    img = img.convert("RGBA")
                    for y in range(height):
                        for x in range(width):
                            r, g, b, a = img.getpixel((x, y))
                            f.write(bytes([r, g, b, a]))
            
            messagebox.showinfo("成功", f"文件已导出为NeleColor格式:\n{save_path}")
            self.status_label.config(text=f"导出完成: {os.path.basename(save_path)}", fg="blue")
        
        except Exception as e:
            messagebox.showerror("错误", f"导出失败:\n{e}")
            self.status_label.config(text="导出失败", fg="red")

if __name__ == "__main__":
    root = tk.Tk()
    app = NeleColorConverter(root)
    root.mainloop()
