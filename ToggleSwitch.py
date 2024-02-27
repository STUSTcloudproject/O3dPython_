import tkinter as tk

class ToggleSwitch(tk.Canvas):
    def __init__(self, parent, pane, callback=None):
        super().__init__(parent, width=40, height=20, bg='red')  # 明确指定所有参数，不使用*args和**kwargs
        self.pane = pane
        self.callback = callback  # 保存回调函数
        self.is_on = False
        self.bind("<Button-1>", self.__toggle)
        self.create_oval(2, 2, 22, 22, fill="white", outline="", tag="slider")

    def __toggle(self, event):
        self.is_on = not self.is_on
        if self.is_on:
            self.move("slider", 20, 0)
            self['bg'] = 'green'
        else:
            self.move("slider", -20, 0)
            self['bg'] = 'red'
        if self.callback:  # 检查回调函数是否存在
            self.callback('ToggleConfig', self.is_on, self.pane)  # 调用回调函数，并传递开关的当前状态