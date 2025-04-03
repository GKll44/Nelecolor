import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageOps
import os
import sys
import webbrowser
import locale

class NeleColorMain:
    def __init__(self, root):
        self.root = root
        self._init_language_system()  # 必须先初始化语言系统
        self.root.title(self.text["title"])
        self.root.geometry("800x650")
        self._load_icon()
        self._init_variables()
        self._setup_ui()

    def _init_language_system(self):
        """Initialize language texts based on system language"""
        system_lang = locale.getdefaultlocale()[0] or "en"
        lang = "en" if system_lang.startswith("en") else "zh"
        
        self.LANGUAGE_TEXTS = {
            "zh": {
                "title": "NeleColor",
                "menu_file": "文件",
                "menu_open": "打开",
                "menu_export": "导出图片",
                "menu_exit": "退出",
                "menu_help": "帮助",
                "menu_docs": "NeleColor文档",
                "menu_about": "关于本程序",
                "no_file": "未选择文件",
                "resolution": "分辨率: -",
                "format": "原格式: -",
                "select_file": "请选择文件 (*^▽^*)",
                "about_title": "关于 NeleColor",
                "github": "作者GitHub",
                "bilibili": "作者Bilibili",
                "close": "关闭",
                "success": "图片已导出:\n{}",
                "error": "错误",
                "error_parse": "解析失败:\n{}",
                "error_export": "导出失败:\n{}",
                "error_docs": "打开文档失败:\n{}",
                "invalid_header": "无效文件头",
                "missing_pixels": "缺少{}像素",
                "extra_pixels": "多余{}像素",
                "color_range": "颜色值越界 (0-FF)",
                "file_type": "NeleColor文件",
                "image_files": "图片文件"
            },
            "en": {
                "title": "NeleColor",
                "menu_file": "File",
                "menu_open": "Open",
                "menu_export": "Export",
                "menu_exit": "Exit",
                "menu_help": "Help",
                "menu_docs": "Documentation",
                "menu_about": "About",
                "no_file": "No file selected",
                "resolution": "Resolution: -",
                "format": "Format: -",
                "select_file": "Please select file (*^▽^*)",
                "about_title": "About NeleColor",
                "github": "GitHub",
                "bilibili": "Bilibili",
                "close": "Close",
                "success": "Exported:\n{}",
                "error": "Error",
                "error_parse": "Parse error:\n{}",
                "error_export": "Export failed:\n{}",
                "error_docs": "Can't open docs:\n{}",
                "invalid_header": "Invalid header",
                "missing_pixels": "Missing {} pixels",
                "extra_pixels": "Extra {} pixels",
                "color_range": "Color out of range (0-FF)",
                "file_type": "NeleColor Files",
                "image_files": "Image Files"
            }
        }
        self.text = self.LANGUAGE_TEXTS[lang]

    def _init_variables(self):
        self.file_path = None
        self.preview_image = None
        self.original_image = None
        self.image_info = {"width": 0, "height": 0, "ext": ""}

    def _load_icon(self):
        try:
            base_path = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
            self.root.iconbitmap(os.path.join(base_path, "dev.ico"))
        except Exception:
            pass

    def _setup_ui(self):
        # 菜单栏
        menubar = tk.Menu(self.root)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label=self.text["menu_open"], command=self._open_file)
        self.export_menu_item = file_menu.add_command(
            label=self.text["menu_export"], 
            command=self._export_image, 
            state=tk.DISABLED
        )
        file_menu.add_separator()
        file_menu.add_command(label=self.text["menu_exit"], command=self.root.quit)
        menubar.add_cascade(label=self.text["menu_file"], menu=file_menu)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label=self.text["menu_docs"], command=self._open_documentation)
        help_menu.add_command(label=self.text["menu_about"], command=self._show_about)
        menubar.add_cascade(label=self.text["menu_help"], menu=help_menu)
        self.root.config(menu=menubar)

        # 顶部信息区域
        top_frame = tk.Frame(self.root)
        top_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.info_label = tk.Label(top_frame, text=self.text["no_file"], anchor=tk.W)
        self.info_label.pack(fill=tk.X)
        
        self.resolution_label = tk.Label(top_frame, text=self.text["resolution"], anchor=tk.W)
        self.resolution_label.pack(fill=tk.X)
        
        self.format_label = tk.Label(top_frame, text=self.text["format"], anchor=tk.W)
        self.format_label.pack(fill=tk.X)

        # 图片预览区域
        self.preview_canvas = tk.Canvas(self.root, bg="#f0f0f0", bd=2, relief=tk.SUNKEN)
        self.preview_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.preview_canvas.create_text(
            400, 300,
            text=self.text["select_file"],
            font=("Arial", 16),
            fill="gray"
        )

        # 底部工具栏
        toolbar = tk.Frame(self.root)
        toolbar.pack(fill=tk.X, padx=10, pady=5)
        
        # 旋转按钮
        self.rotate_left_btn = tk.Button(
            toolbar,
            text="↺",
            command=lambda: self._rotate_image(90),
            width=8,
            state=tk.DISABLED
        )
        self.rotate_right_btn = tk.Button(
            toolbar,
            text="↻",
            command=lambda: self._rotate_image(-90),
            width=8,
            state=tk.DISABLED
        )
        tk.Label(toolbar, width=2).pack(side=tk.LEFT)
        self.rotate_left_btn.pack(side=tk.LEFT, padx=2)
        self.rotate_right_btn.pack(side=tk.LEFT, padx=2)

    def _open_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[(self.text["file_type"], "*.nelecolor")]
        )
        if not file_path:
            return

        try:
            img, ext = self._parse_nelecolor(file_path)
            self.file_path = file_path
            self.original_image = img.copy()
            
            self.image_info.update({
                "width": img.width,
                "height": img.height,
                "ext": ext
            })
            
            self._update_file_info(os.path.basename(file_path))
            self._show_preview(img)
            self._enable_controls()
            
        except Exception as e:
            messagebox.showerror(self.text["error"], self.text["error_parse"].format(str(e)))

    def _parse_nelecolor(self, file_path):
        with open(file_path, "rb") as f:
            header = b""
            while True:
                byte = f.read(1)
                if byte == b"\n":
                    break
                header += byte
            
            header_str = header.decode("utf-8")
            if "x" not in header_str or "." not in header_str:
                raise ValueError(self.text["invalid_header"])
            
            res_part, ext = header_str.split(".", 1)
            width, height = map(int, res_part.split("x"))
            ext = "." + ext
            
            pixel_data = f.read()
            expected = width * height * 3
            actual = len(pixel_data)
            
            if actual < expected:
                raise ValueError(self.text["missing_pixels"].format((expected - actual) // 3))
            elif actual > expected:
                raise ValueError(self.text["extra_pixels"].format((actual - expected) // 3))
            
            img = Image.new("RGB", (width, height))
            pixels = img.load()
            
            index = 0
            for y in range(height):
                for x in range(width):
                    r, g, b = pixel_data[index], pixel_data[index+1], pixel_data[index+2]
                    if not all(0 <= c <= 255 for c in (r, g, b)):
                        raise ValueError(self.text["color_range"])
                    pixels[x, y] = (r, g, b)
                    index += 3
            
            return img, ext

    def _update_file_info(self, filename):
        self.info_label.config(text=f"{filename}")
        self.resolution_label.config(text=f"{self.text['resolution'][:-3]}: {self.image_info['width']}x{self.image_info['height']}")
        self.format_label.config(text=f"{self.text['format'][:-3]}: {self.image_info['ext']}")

    def _show_preview(self, img):
        canvas_width = max(self.preview_canvas.winfo_width(), 780)
        canvas_height = max(self.preview_canvas.winfo_height(), 480)
        
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

    def _enable_controls(self):
        self.export_menu_item.config(state=tk.NORMAL)
        self.rotate_left_btn.config(state=tk.NORMAL)
        self.rotate_right_btn.config(state=tk.NORMAL)

    def _rotate_image(self, angle):
        if not self.original_image:
            return
            
        self.original_image = self.original_image.rotate(angle, expand=True)
        self.image_info.update({
            "width": self.original_image.width,
            "height": self.original_image.height
        })
        self._update_file_info(os.path.basename(self.file_path))
        self._show_preview(self.original_image)

    def _export_image(self):
        if not self.file_path or not self.original_image:
            return
            
        default_name = f"{os.path.splitext(os.path.basename(self.file_path))[0]}{self.image_info['ext']}"
        save_path = filedialog.asksaveasfilename(
            defaultextension=self.image_info['ext'],
            initialfile=default_name,
            filetypes=[(self.text["image_files"], f"*{self.image_info['ext']}")]
        )
        if not save_path:
            return
            
        try:
            self.original_image.save(save_path)
            messagebox.showinfo(self.text["success"][:2], self.text["success"].format(save_path))
        except Exception as e:
            messagebox.showerror(self.text["error"], self.text["error_export"].format(str(e)))

    def _open_documentation(self):
         try:
             webbrowser.open("https://gkll44.github.io/NeleColorDocuments.github.io/")
         except Exception as e:
             messagebox.showerror(self.text["error"], self.text["error_docs"].format(str(e)))

    def _show_about(self):
        about = tk.Toplevel(self.root)
        about.title(self.text["about_title"])
        about.geometry("400x300")
        about.resizable(False, False)
        
        try:
            base_path = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
            about.iconbitmap(os.path.join(base_path, "dev.ico"))
        except:
            pass
            
        tk.Label(about, text="NeleColor", font=("Arial", 18, "bold")).pack(pady=10)
        tk.Label(about, text="by GKll44", fg="green").pack()
        
        # 链接区域
        links = tk.Frame(about)
        links.pack(pady=20)
        
        github = tk.Label(links, text=self.text["github"], fg="blue", cursor="hand2")
        github.pack(anchor=tk.W)
        github.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/GKll44"))
        
        bilibili = tk.Label(links, text=self.text["bilibili"], fg="blue", cursor="hand2")
        bilibili.pack(anchor=tk.W, pady=5)
        bilibili.bind("<Button-1>", lambda e: webbrowser.open("https://space.bilibili.com/3461577971861852"))
        
        tk.Button(about, text=self.text["close"], command=about.destroy, width=10).pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = NeleColorMain(root)
    root.mainloop()
