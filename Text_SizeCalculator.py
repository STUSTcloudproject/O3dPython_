import tkinter as tk
from GUI import App  # 替换your_gui_module为包含App类的模块名
from SizeCalculator import SizeCalculator  # 替换your_size_calculator_module为包含SizeCalculator类的模块名
from threading import Thread, Event
import time

# 这是一个后台线程函数，用于定期计算并打印尺寸
def periodic_size_calculation(stop_event):
    while not stop_event.is_set():
        # 假设窗口高度和右侧面板宽度
        window_height = 600
        right_panel_width = 400

        # 使用SizeCalculator计算目标尺寸
        target_width, target_height = SizeCalculator.calculate_target_size(window_height, right_panel_width)

        # 打印计算结果
        print(f"Periodic calculation - Target width: {target_width}, Target height: {target_height}")

        # 等待3秒
        time.sleep(1)

def test_size_calculator():
    # 实例化GUI
    app = App()

    # 创建一个事件对象，用于在程序结束时通知线程停止
    stop_event = Event()

    # 创建并启动后台线程
    background_thread = Thread(target=periodic_size_calculation, args=(stop_event,))
    background_thread.start()

    try:
        # 启动GUI主循环
        app.mainloop()
    finally:
        # 当GUI关闭时，设置停止事件并等待后台线程结束
        stop_event.set()
        background_thread.join()

if __name__ == "__main__":
    test_size_calculator()
