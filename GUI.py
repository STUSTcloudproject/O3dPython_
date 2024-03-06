import threading
import tkinter as tk
from tkinter import ttk
from CollapsiblePane import CollapsiblePane

class App(tk.Tk):
    def __init__(self, toggle_callback=None):
        super().__init__()
        
        self.toggle_callback = toggle_callback
        
        self.size_lock = threading.Lock()   
        
        # 設定應用視窗的標題和大小
        self.title('Intel RealSense Viewer')
        self.geometry('800x600')

        self.window_width = self.winfo_reqwidth()
        self.window_height = self.winfo_reqheight()
        self.left_panel_width = 200  # 初始值，稍後會根據實際情況更新
        self.right_panel_width = 600  # 假定初始值，稍後會根據實際情況更新
        
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

        self.bind("<Configure>", self._on_window_resize)
    
    def get_window_size(self):
        with self.size_lock:
            return self.window_width, self.window_height

    def get_panel_widths(self):
        with self.size_lock:
            return self.left_panel_width, self.right_panel_width

    def _on_window_resize(self, _):
        with self.size_lock:
            # 直接從窗口獲取當前的尺寸，而不是依賴於event對象
            self.window_width = self.winfo_width()
            self.window_height = self.winfo_height()
            # 獲取面板的當前寬度
            self.left_panel_width = self.left_panel.winfo_width()
            self.right_panel_width = self.right_panel.winfo_width()
        
        # 使用after延遲調用更新佈局的方法，確保在主線程中進行
        #self.after(100, self._update_layout_based_on_size)

    def _update_layout_based_on_size(self):
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
    
    def _add_device_selector(self, parent, title, device_options):
        # 創建設備選擇的框架
        device_frame = ttk.Frame(parent)
        device_frame.pack(side="top", fill="x", expand=0, padx=4, pady=4)

        # 在設備選擇框架中添加標籤和下拉框
        ttk.Label(device_frame, text=title).pack(side="left")
        self.device_combobox = ttk.Combobox(device_frame, values=device_options, state='readonly')  # 將combobox存儲為類的屬性
        self.device_combobox.pack(side="left", fill="x", expand=1)
        if device_options:  # 檢查列表是否不為空
            self.device_combobox.current(0)  # 默認選擇第一個設備
        
        # 綁定<<ComboboxSelected>>事件到事件處理函數
        self.device_combobox.bind("<<ComboboxSelected>>", self.on_device_selected)

    def on_device_selected(self, event=None):
        selected_device = self.device_combobox.get()
        if selected_device == "None":
            self._hide_stream_options()
        else:
            self._show_stream_options()
            # 在這裡調用toggle_callback回調函數，並傳遞選定的設備信息
        if self.toggle_callback:
            self.toggle_callback(mode="DeviceSelected", device_info=selected_device)

    def update_device_options(self, device_options):
        """更新設備選擇下拉框的選項"""
        if hasattr(self, 'device_combobox'):
            self.device_combobox['values'] = device_options
            if device_options:
                self.device_combobox.current(0)  # 默認選擇第一個設備
                selected_device = self.device_combobox.get()
                if selected_device == "None":
                    self._hide_stream_options()
            else:
                self.device_combobox.set('')  # 如果沒有選項，則清空下拉框

    def _setup_left_panel(self, toggle_callback=None):
        # 首先添加設備選擇器
        self._add_device_selector(self.left_panel, "Device: ", [""])

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

        # 在左側面板底部添加一個名為"拍照"的按鈕
        self.capture_button = tk.Button(self.left_panel, text="Capture", width=20, height=3, command=self.capture_photo)
        self.capture_button.pack(side="bottom", fill="x", padx=8, pady=8)

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

        # 佈局框架和標籤
        self._adjust_right_panel_layout()
    
    def capture_photo(self):
        click_callback = self.toggle_callback
        if click_callback is not None:
            click_callback('CapturePhoto')
        else:
            print("Photo function is not yet available")
        
    
    def _adjust_right_panel_layout(self):
        
        # 佈局標籤
        self.depth_label.pack(fill=tk.BOTH, expand=True)
        self.infrared_label.pack(fill=tk.BOTH, expand=True)
        self.color_label.pack(fill=tk.BOTH, expand=True)

        self.depth_frame.pack(fill=tk.BOTH, expand=True)
        self.infrared_frame.pack(fill=tk.BOTH, expand=True)
        self.color_frame.pack(fill=tk.BOTH, expand=True)

    def _hide_stream_options(self):
        """隱藏流選項和捕獲按鈕"""
        self.depth_stream.pack_forget()
        self.infrared_stream.pack_forget()
        self.color_stream.pack_forget()
        self.capture_button.pack_forget()

    def _show_stream_options(self):
        """顯示流選項和捕獲按鈕"""
        self.depth_stream.pack(fill="x", expand=0, padx=4, pady=4)
        self.infrared_stream.pack(fill="x", expand=0, padx=4, pady=4)
        self.color_stream.pack(fill="x", expand=0, padx=4, pady=4)
        self.capture_button.pack(side="bottom", fill="x", padx=8, pady=8)

    def reset_toggle_switches(self):
        """重置所有流的開關狀態為 'off'。"""
        for pane in [self.depth_stream, self.infrared_stream, self.color_stream]:
            pane.toggle_switch.set_state(False)
        
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
