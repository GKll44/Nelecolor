import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageOps
import os
import sys
import webbrowser
import locale
from NelecolorConverter import NeleColorConverter

class NeleColor:
    def __init__(self, root):
        self.root = root
        self._init_language_system()  # 必须先初始化语言系统
        self.root.title(self.text["title"])
        self.root.geometry("800x650")
        self.root.configure(bg="#f5f5f5")  # 设置窗口背景色
        
        # 设置现代风格主题
        self.root.tk_setPalette(background='#f5f5f5', foreground='#333333',
                              activeBackground='#4a6baf', activeForeground='white')
        
        self._init_variables()  # 初始化变量
        self._load_icon()      # 加载图标
        self._setup_ui()       # 设置UI（最后调用，确保其他初始化完成）

    def _init_language_system(self):
        system_lang = locale.getdefaultlocale()[0] or "en"
        lang = "en" if system_lang.startswith("en") else "zh"
        lang = "jp" if system_lang.startswith("jp") else lang

        self.LANGUAGE_TEXTS = {
            "zh": {
                "title": "NeleColor",
                "menu_file": "文件",
                "menu_open": "打开",
                "menu_export": "导出图片",
                "menu_exit": "退出",
                "menu_tools": "工具",
                "menu_converter": "格式转换器",
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
                "image_files": "图片",
                "rotate_left": "左转",
                "rotate_right": "右转"
            },
            "en": {
                "title": "NeleColor",
                "menu_file": "File",
                "menu_open": "Open",
                "menu_export": "Export",
                "menu_exit": "Exit",
                "menu_tools": "Tools",
                "menu_converter": "Format Converter",
                "menu_help": "Help",
                "menu_docs": "Documentation",
                "menu_about": "About",
                "no_file": "No file selected",
                "resolution": "Resolution: -",
                "format": "Format: -",
                "select_file": "Please select file",
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
                "image_files": "Image",
                "rotate_left": "Rotate Left",
                "rotate_right": "Rotate Right"
            },
            "jp": {
                "title": "NeleColor",
                "menu_file": "ファイル",
                "menu_open": "開ける",
                "menu_export": "エクスポート",
                "menu_exit": "退出します",
                "menu_tools": "ツール",
                "menu_converter": "フォーマットコンバーター",
                "menu_help": "助け",
                "menu_docs": "NeleColor文書",
                "menu_about": "約",
                "no_file": "ファイルが選択されていません",
                "resolution": "解決策：-",
                "format": "フォーマット： -",
                "select_file": "ファイルを選択してください~~",
                "about_title": "約 NeleColor",
                "github": "GitHub",
                "bilibili": "Bilibili",
                "close": "閉じる",
                "success": "輸出された:\n{}",
                "error": "誤差",
                "error_parse": "解析に失敗しました:\n{}",
                "error_export": "エクスポートに失敗しました:\n{}",
                "error_docs": "文書を開くことに失敗しました:\n{}",
                "invalid_header": "無効なファイルヘッダー",
                "missing_pixels": "不足している{}ピクセル",
                "extra_pixels": "余分な{}ピクセル",
                "color_range": "カラー値が範囲外です (0-FF)",
                "file_type": "NeleColor ファイル",
                "image_files": "画像",
                "rotate_left": "左回転",
                "rotate_right": "右回転"
            }
        }
        self.text = self.LANGUAGE_TEXTS[lang]

    def _init_variables(self):
        """初始化变量"""
        self.file_path = None
        self.preview_image = None
        self.original_image = None
        self.image_info = {"width": 0, "height": 0, "ext": ""}
        # 初始化UI组件变量
        self.info_label = None
        self.resolution_label = None
        self.format_label = None
        self.preview_canvas = None
        self.export_menu_item = None
        self.rotate_left_btn = None
        self.rotate_right_btn = None

    def _load_icon(self):
        """加载程序图标"""
        try:
            base_path = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
            self.root.iconbitmap(os.path.join(base_path, "dev.ico"))
        except Exception:
            pass

    def _setup_ui(self):
        """设置用户界面"""
        # 菜单栏
        menubar = tk.Menu(self.root, bg="#f5f5f5", fg="#333333", bd=0)

        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0, bg="#f5f5f5", fg="#333333", bd=1)
        file_menu.add_command(
            label=self.text["menu_open"], 
            command=self._open_file,
            accelerator="Ctrl+O"
        )
        self.export_menu_item = file_menu.add_command(
            label=self.text["menu_export"], 
            command=self._export_image, 
            state=tk.DISABLED,
            accelerator="Ctrl+S"
        )
        file_menu.add_separator()
        file_menu.add_command(
            label=self.text["menu_exit"], 
            command=self.root.quit,
            accelerator="Alt+F4"
        )
        menubar.add_cascade(label=self.text["menu_file"], menu=file_menu)

        # 工具菜单
        tools_menu = tk.Menu(menubar, tearoff=0, bg="#f5f5f5", fg="#333333")
        tools_menu.add_command(
            label=self.text["menu_converter"], 
            command=self._open_converter
        )
        menubar.add_cascade(label=self.text["menu_tools"], menu=tools_menu)

        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0, bg="#f5f5f5", fg="#333333")
        help_menu.add_command(
            label=self.text["menu_docs"], 
            command=self._open_documentation,
            accelerator="F1"
        )
        help_menu.add_command(
            label=self.text["menu_about"], 
            command=self._show_about
        )
        menubar.add_cascade(label=self.text["menu_help"], menu=help_menu)

        self.root.config(menu=menubar)

        # 顶部信息区域
        top_frame = tk.Frame(self.root, bg="white", bd=1, relief=tk.SOLID, padx=10, pady=5)
        top_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 信息标签样式
        label_style = {
            "bg": "white",
            "fg": "#333333",
            "font": ("Microsoft YaHei", 10),
            "anchor": tk.W
        }
        
        self.info_label = tk.Label(top_frame, text=self.text["no_file"], **label_style)
        self.info_label.pack(fill=tk.X)
        
        self.resolution_label = tk.Label(top_frame, text=self.text["resolution"], **label_style)
        self.resolution_label.pack(fill=tk.X)
        
        self.format_label = tk.Label(top_frame, text=self.text["format"], **label_style)
        self.format_label.pack(fill=tk.X)

        # 图片预览区域
        self.preview_canvas = tk.Canvas(
            self.root, 
            bg="#f0f0f0", 
            bd=2, 
            relief=tk.GROOVE,
            highlightthickness=0
        )
        self.preview_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.preview_canvas.create_text(
            400, 300,
            text=self.text["select_file"],
            font=("Arial", 16),
            fill="gray"
        )

        # 底部工具栏
        toolbar = tk.Frame(
            self.root, 
            bg="#e1e1e1", 
            bd=1, 
            relief=tk.RAISED,
            padx=5, 
            pady=5
        )
        toolbar.pack(fill=tk.X, padx=10, pady=5)
        
        # 按钮样式
        button_style = {
            "bg": "#4a6baf",
            "fg": "white",
            "activebackground": "#3a5a9f",
            "activeforeground": "white",
            "bd": 0,
            "relief": tk.RAISED,
            "font": ("Microsoft YaHei", 10),
            "width": 8,
            "disabledforeground": "#aaaaaa"
        }
        
        # 旋转按钮
        tk.Label(toolbar, bg="#e1e1e1", width=2).pack(side=tk.LEFT)
        
        self.rotate_left_btn = tk.Button(
            toolbar,
            text="↺ " + self.text["rotate_left"],
            command=lambda: self._rotate_image(90),
            **button_style,
            state=tk.DISABLED
        )
        self.rotate_left_btn.pack(side=tk.LEFT, padx=2)
        
        self.rotate_right_btn = tk.Button(
            toolbar,
            text="↻ " + self.text["rotate_right"],
            command=lambda: self._rotate_image(-90),
            **button_style,
            state=tk.DISABLED
        )
        self.rotate_right_btn.pack(side=tk.LEFT, padx=2)
        
        # 键盘快捷键
        self.root.bind("<Control-o>", lambda e: self._open_file())
        self.root.bind("<Control-s>", lambda e: self._export_image() if self.export_menu_item['state'] == 'normal' else None)
        self.root.bind("<F1>", lambda e: self._open_documentation())

    def _open_converter(self):
        """打开格式转换器"""
        converter_window = tk.Toplevel(self.root)
        converter_window.title(self.text["menu_converter"])
        try:
            base_path = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
            converter_window.iconbitmap(os.path.join(base_path, "dev.ico"))
        except Exception:
            pass
        
        # Create the converter app in this window
        NeleColorConverter(converter_window)

    def _open_file(self):
        """打开文件"""
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
        """解析NeleColor文件"""
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
            
            # 分离编码格式信息
            if ":" in header_str:
                header_part, encoding = header_str.split(":", 1)
                encoding = encoding.lower()
            else:
                header_part = header_str
                encoding = "rgb"  # 默认RGB格式
            
            res_part, ext = header_part.split(".", 1)
            width, height = map(int, res_part.split("x"))
            ext = "." + ext
            
            pixel_data = f.read()
            
            # 根据编码格式计算预期数据量
            if encoding == "rgb":
                bytes_per_pixel = 3
            elif encoding == "rgba":
                bytes_per_pixel = 4
            else:
                raise ValueError(f"不支持的编码格式: {encoding}")
            
            expected = width * height * bytes_per_pixel
            actual = len(pixel_data)
            
            if actual < expected:
                raise ValueError(self.text["missing_pixels"].format((expected - actual) // bytes_per_pixel))
            elif actual > expected:
                raise ValueError(self.text["extra_pixels"].format((actual - expected) // bytes_per_pixel))
            
            # 创建图像
            if encoding == "rgb":
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
            else:  # rgba
                img = Image.new("RGBA", (width, height))
                pixels = img.load()
                
                index = 0
                for y in range(height):
                    for x in range(width):
                        r, g, b, a = pixel_data[index], pixel_data[index+1], pixel_data[index+2], pixel_data[index+3]
                        if not all(0 <= c <= 255 for c in (r, g, b, a)):
                            raise ValueError(self.text["color_range"])
                        pixels[x, y] = (r, g, b, a)
                        index += 4
            
            return img, ext
            
    def _update_file_info(self, filename):
        """更新文件信息显示"""
        if self.info_label:
            self.info_label.config(text=f"{filename}")
        if self.resolution_label:
            self.resolution_label.config(text=f"{self.text['resolution'][:-3]}: {self.image_info['width']}x{self.image_info['height']}")
        if self.format_label:
            self.format_label.config(text=f"{self.text['format'][:-3]}: {self.image_info['ext']}")

    def _show_preview(self, img):
        """显示图片预览"""
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
        """启用控制按钮"""
        if self.export_menu_item:
            self.export_menu_item.config(state=tk.NORMAL)
        if self.rotate_left_btn:
            self.rotate_left_btn.config(state=tk.NORMAL)
        if self.rotate_right_btn:
            self.rotate_right_btn.config(state=tk.NORMAL)

    def _rotate_image(self, angle):
        """旋转图片"""
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
        """导出图片"""
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
        """显示关于窗口"""
        about = tk.Toplevel(self.root)
        about.title(self.text["about_title"])
        about.geometry("400x300")
        about.resizable(False, False)
        about.configure(bg="#f5f5f5")
        
        try:
            base_path = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
            about.iconbitmap(os.path.join(base_path, "dev.ico"))
        except:
            pass
            
        # 标题
        tk.Label(
            about, 
            text="NeleColor", 
            font=("Arial", 18, "bold"),
            bg="#f5f5f5",
            fg="#333333"
        ).pack(pady=10)
        
        tk.Label(
            about, 
            text="by GKll44", 
            fg="#4a6baf",
            bg="#f5f5f5",
            font=("Arial", 12)
        ).pack()
        
        # 链接区域
        links = tk.Frame(about, bg="#f5f5f5")
        links.pack(pady=20)
        
        link_style = {
            "font": ("Arial", 11, "underline"),
            "fg": "#4a6baf",
            "bg": "#f5f5f5",
            "cursor": "hand2"
        }
        
        github = tk.Label(links, text=self.text["github"], **link_style)
        github.pack(anchor=tk.W)
        github.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/GKll44"))
        
        bilibili = tk.Label(links, text=self.text["bilibili"], **link_style)
        bilibili.pack(anchor=tk.W, pady=5)
        bilibili.bind("<Button-1>", lambda e: webbrowser.open("https://space.bilibili.com/3461577971861852"))
        
        # 关闭按钮
        tk.Button(
            about, 
            text=self.text["close"], 
            command=about.destroy, 
            width=10,
            bg="#4a6baf",
            fg="white",
            activebackground="#3a5a9f",
            activeforeground="white",
            bd=0,
            relief=tk.RAISED
        ).pack(pady=10)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='NeleColor Tools')
    subparsers = parser.add_subparsers(dest='command')
    
    # Encode command
    encode_parser = subparsers.add_parser('in', help='Encode image to .nelecolor format')
    encode_parser.add_argument('input', help='Input image path')
    encode_parser.add_argument('output', nargs='?', help='Output .nelecolor file path (default: input with .nelecolor extension)')
    encode_parser.add_argument('-g', '--encoding', help='Color encoding format (rgb or rgba)', 
                             choices=['rgb', 'rgba'], default='rgb')
    
    # Decode command
    decode_parser = subparsers.add_parser('out', help='Decode .nelecolor to image format')
    decode_parser.add_argument('input', help='Input .nelecolor file path')
    decode_parser.add_argument('output', nargs='?', help='Output image path (default: input with original extension)')
    
    args = parser.parse_args()
    
    if args.command == 'in':
        # Encoding operation
        try:
            img = Image.open(args.input)
            width, height = img.size
            input_ext = os.path.splitext(args.input)[1].lower()
            
            # Determine output path
            if args.output is None:
                output_path = os.path.splitext(args.input)[0] + '.nelecolor'
            else:
                output_path = args.output
            
            # Get pixel data based on encoding format
            if args.encoding == 'rgb':
                img = img.convert('RGB')
                pixel_data = img.tobytes()
            else:  # rgba
                img = img.convert('RGBA')
                pixel_data = img.tobytes()
            
            # Write to .nelecolor file
            with open(output_path, 'wb') as f:
                # Write header: resolution.ext:encoding
                header = f"{width}x{height}{input_ext}:{args.encoding}\n".encode('utf-8')
                f.write(header)
                f.write(pixel_data)
            
            print(f"Encoded to {output_path} with {args.encoding} format")
            
        except Exception as e:
            print(f"Error: {str(e)}")
            sys.exit(1)
            
    elif args.command == 'out':
        # Decoding operation
        try:
            img, original_ext = NeleColor._parse_nelecolor(None, args.input)
            
            # Determine output path
            if args.output is None:
                base_name = os.path.splitext(args.input)[0]
                output_path = base_name + original_ext
            else:
                output_path = args.output
            
            img.save(output_path)
            print(f"Decoded to {output_path}")
        except Exception as e:
            print(f"Error: {str(e)}")
            sys.exit(1)
    else:
        # Default GUI mode when no command is provided
        root = tk.Tk()
        app = NeleColor(root)
        root.mainloop()
