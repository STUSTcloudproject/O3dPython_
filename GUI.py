import threading
import tkinter as tk
from tkinter import ttk
from CollapsiblePane import CollapsiblePane

class App(tk.Tk):
    def __init__(self, toggle_callback=None):
        super().__init__()
        
        self.size_lock = threading.Lock()   
        
        # 設定應用視窗的標題和大小
        self.title('Intel RealSense Viewer')
        self.geometry('800x600')

        self.window_width = self.winfo_reqwidth()
        self.window_height = self.winfo_reqheight()
        self.left_panel_width = 200  # 初始值，稍后会根据实际情况更新
        self.right_panel_width = 600  # 假定初始值，稍后会根据实际情况更新
        
        # 建立一個可分隔視窗pane
        self.pane = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.pane.pack(fill=tk.BOTH, expand=1)

        # 在pane中添加左側和右側的面板
        self.left_panel = tk.Frame(self.pane, width=200)
        self.right_panel = tk.Frame(self.pane, width=200, bg='gray')
        self.pane.add(self.left_panel, weight=1)
        self.pane.add(self.right_panel, weight=3)

        self._setup_left_panel(toggle_callback)
        self._setup_right_panel()

        self.bind("<Configure>", self.on_window_resize)
    
    def get_window_size(self):
        with self.size_lock:
            return self.window_width, self.window_height

    def get_panel_widths(self):
        with self.size_lock:
            return self.left_panel_width, self.right_panel_width

    def on_window_resize(self, _):
        with self.size_lock:
            # 直接从窗口获取当前的尺寸，而不是依赖于event对象
            self.window_width = self.winfo_width()
            self.window_height = self.winfo_height()
            # 获取面板的当前宽度
            self.left_panel_width = self.left_panel.winfo_width()
            self.right_panel_width = self.right_panel.winfo_width()
        
        # 使用after延迟调用更新布局的方法，确保在主线程中进行
        #self.after(100, self.update_layout_based_on_size)


    def update_layout_based_on_size(self):
        window_width, window_height = self.get_window_size()
        left_panel_width, right_panel_width = self.get_panel_widths()
        
        print(f"Updated sizes - Window size: {window_width}x{window_height}, Left panel width: {left_panel_width}, Right panel width: {right_panel_width}")


    # 在每個摺疊面板中添加設定選項
    def _add_stream_setting(self, parent, options):
        # 添加詳細設定的標題
        ttk.Label(parent, text="Detailed Settings").pack(side="top", fill="x", expand=0)
        
        # 建立框架以組織下拉框和其標籤
        combo_frame = ttk.Frame(parent)
        combo_frame.pack(side="top", fill="x", expand=0)

        # 在下拉框旁添加標籤說明
        ttk.Label(combo_frame, text="Resolution : ").pack(side="left")
 
        # 建立下拉框
        parent.combo = ttk.Combobox(combo_frame, values=options, state='readonly')
        parent.combo.pack(side="left", fill="x", expand=1)
        parent.combo.current(0)  # 預設選擇第一個選項

        # 新增多個設置選項
        for i in range(1, 4):
            ttk.Checkbutton(parent, text=f"Setting Option {i}").pack(side="top", fill="x", expand=0)
    
    def _setup_left_panel(self, toggle_callback=None):
        # 添加可摺疊面板並設置其內容
        self.depth_stream = CollapsiblePane(self.left_panel, title="Depth Stream ", toggle_callback=toggle_callback)
        self.depth_stream.pack(fill="x", expand=0, padx=4, pady=4)  # 摺疊時不佔用額外空間
        self._add_stream_setting(self.depth_stream.sub_frame, ["320 x 240"])

        self.infrared_stream = CollapsiblePane(self.left_panel, title="Infrared Stream ", toggle_callback=toggle_callback)
        self.infrared_stream.pack(fill="x", expand=0, padx=4, pady=4)
        self._add_stream_setting(self.infrared_stream.sub_frame, ["320 x 240"])

        self.color_stream = CollapsiblePane(self.left_panel, title="Color Stream ", toggle_callback=toggle_callback)
        self.color_stream.pack(fill="x", expand=0, padx=4, pady=4)
        self._add_stream_setting(self.color_stream.sub_frame, ["640 x 360", "640 x 480"])

    def _setup_right_panel(self):
        # 確保 right_panel 能夠根據內容自動調整大小
        self.right_panel.pack_propagate(False)

        # 設置框架
        self.depth_frame = tk.Frame(self.right_panel, bg='gray')
        self.infrared_frame = tk.Frame(self.right_panel, bg='gray')
        self.color_frame = tk.Frame(self.right_panel, bg='gray')

        # 設置標籤
        self.depth_label = tk.Label(self.depth_frame, text='Depth', bg='black', fg='white')
        self.infrared_label = tk.Label(self.infrared_frame, text='Infrared', bg='black', fg='white')
        self.color_label = tk.Label(self.color_frame, text='Color', bg='black', fg='white')

        # 布局框架和標籤
        self._adjust_right_panel_layout()
    
    def _adjust_right_panel_layout(self):
        
        # 布局標籤
        self.depth_label.pack(fill=tk.BOTH, expand=True)
        self.infrared_label.pack(fill=tk.BOTH, expand=True)
        self.color_label.pack(fill=tk.BOTH, expand=True)

        self.depth_frame.pack(fill=tk.BOTH, expand=True)
        self.infrared_frame.pack(fill=tk.BOTH, expand=True)
        self.color_frame.pack(fill=tk.BOTH, expand=True)
        
    # 可以設定右側面板的圖片屬性
    def set_depth_image(self, image):
        self.depth_label.config(image=image)
        self.depth_label.image = image
    
    def set_infrared_image(self, image):
        self.infrared_label.config(image=image)
        self.infrared_label.image = image

    def set_color_image(self, image):
        self.color_label.config(image=image)
        self.color_label.image = image


if __name__ == '__main__':
    app = App()
    app.mainloop()