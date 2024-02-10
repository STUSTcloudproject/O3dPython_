import tkinter as tk
from tkinter import ttk
from ToggleSwitch import ToggleSwitch

class CollapsiblePane(tk.Frame):
    def __init__(self, parent, title="", toggle_callback=None):
        super().__init__(parent)

        # 建立標題區域框架button
        self.title_frame = ttk.Frame(self)
        self.title_frame.pack(fill="x", expand=1)
        
        # 使用 Label 來模擬 button
        self.details_button = ttk.Label(self.title_frame, width=2, text='▶', cursor="hand2")
        self.details_button.pack(side="left")
        self.details_button.bind("<Button-1>", self.__toggle)  # 綁定滑鼠左鍵點擊事件到 __toggle 函數

        # 在標題區域中添加標題標籤
        self.title_label = ttk.Label(self.title_frame, text=title)
        self.title_label.pack(side="left", fill="x", expand=1)

        self.toggle_switch = ToggleSwitch(self.title_frame, pane=self, callback=toggle_callback)
        self.toggle_switch.pack(side="right")

        # 建立子框架用於放置折疊的內容
        self.sub_frame = tk.Frame(self, relief="sunken", borderwidth=1)
        self._is_collapsed = False  # 面板的初始狀態為摺疊
        self.__toggle()  # 調用__toggle函數來應用初始狀態

    def __toggle(self, event=None):
        # 根據當前狀態切換面板的展開或摺疊
        if self._is_collapsed:
            self.sub_frame.pack(fill="x", expand=1)
            self.details_button.configure(text='▼')
        else:
            self.sub_frame.forget()
            self.details_button.configure(text='▶')
        self._is_collapsed = not self._is_collapsed