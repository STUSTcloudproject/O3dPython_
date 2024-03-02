import tkinter as tk

class ToggleSwitch(tk.Canvas):
    def __init__(self, parent, pane, callback=None):
        super().__init__(parent, width=40, height=20, bg='red')  # 明确指定所有参数，不使用*args和**kwargs
        self.pane = pane
        self.callback = callback  # 保存回调函数
        self.is_on = False
        self.bind("<Button-1>", lambda event: self.__toggle(event, from_user=True))
        self.create_oval(2, 2, 22, 22, fill="white", outline="", tag="slider")

    def set_state(self, state):
        """设置开关的状态。"""
        if state != self.is_on:  # 只有当状态真的改变时才执行
            self.__toggle(from_user=False)  # 传递 from_user=False 表明这是程序调用

    def __toggle(self, event=None, from_user=True):
        self.is_on = not self.is_on
        if self.is_on:
            self.move("slider", 20, 0)
            self['bg'] = 'green'
        else:
            self.move("slider", -20, 0)
            self['bg'] = 'red'
        if self.callback and from_user:  # 仅在用户操作时调用回调函数
            self.callback('ToggleConfig', self.is_on, self.pane)