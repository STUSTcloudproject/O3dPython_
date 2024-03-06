import tkinter as tk

class ToggleSwitch(tk.Canvas):
    def __init__(self, parent, pane, callback=None):
        super().__init__(parent, width=40, height=20, bg='red')  # 明確指定所有參數，不使用*args和**kwargs
        self.pane = pane
        self.callback = callback  # 保存回調函數
        self.is_on = False
        self.bind("<Button-1>", lambda event: self.__toggle(event, from_user=True))
        self.create_oval(2, 2, 22, 22, fill="white", outline="", tag="slider")

    def set_state(self, state):
        """設置開關的狀態。"""
        if state != self.is_on:  # 只有當狀態真的改變時才執行
            self.__toggle(from_user=False)  # 傳遞 from_user=False 表明這是程序調用

    def __toggle(self, event=None, from_user=True):
        self.is_on = not self.is_on
        if self.is_on:
            self.move("slider", 20, 0)
            self['bg'] = 'green'
        else:
            self.move("slider", -20, 0)
            self['bg'] = 'red'
        if self.callback and from_user:  # 僅在用戶操作時調用回調函數
            self.callback('ToggleConfig', self.is_on, self.pane)
