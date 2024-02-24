import GUI
from PIL import Image, ImageTk
import threading
import tkinter
from RealSense import RealSense
from ImageProcessor import ImageProcessor
from SizeCalculator import SizeCalculator

class MainApp:
    def __init__(self):
        self.settings_lock = threading.Lock()
        self.settings = {
            "depth": {"enabled": False, "resolution": "320 x 240"},
            "infrared": {"enabled": False, "resolution": "640 x 360"},
            "color": {"enabled": False, "resolution": "320 x 240"},
        }
        self.app = GUI.App(toggle_callback=self.toggle_switch_changed)
        self.app.protocol("WM_DELETE_WINDOW", self.close_program)
        self.create_image_placeholders()
        self.image_processor = ImageProcessor()
        # RealSense实例将在__enter__方法中创建
        self.rs_device = None

    def __enter__(self):
        self.rs_device = RealSense().__enter__()  # 创建并初始化RealSense实例
        # 启动后台线程来监视settings并更新GUI
        self.update_thread = threading.Thread(target=self.monitor_settings_and_update_gui, daemon=True)
        self.update_thread.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # 清理RealSense资源
        if self.rs_device:
            self.rs_device.__exit__(exc_type, exc_val, exc_tb)

    def create_image_placeholders(self):
        # 创建红色和黑色图像作为占位符
        red = Image.new("RGB", (160, 120), "red")
        black = Image.new("RGB", (160, 120), "black")
        self.red_image = ImageTk.PhotoImage(red)
        self.black_image = ImageTk.PhotoImage(black)

    def toggle_switch_changed(self, is_on, pane):
        try:
            combo_value = pane.sub_frame.combo.get()
            stream_type = pane.title_label["text"].strip().lower().replace(" stream", "")
            print("Stream type:", stream_type)
            with self.settings_lock:
                if stream_type in self.settings:
                    self.settings[stream_type]["enabled"] = is_on
                    self.settings[stream_type]["resolution"] = combo_value
                else:
                    print(f"Unrecognized stream type: {stream_type}")
            self.stop_real_sense()
            self.restart_real_sense(self.settings)
            print(self.settings)
        except Exception as e:
            print(f"An error occurred: {e}")

    def restart_real_sense(self, settings):
        if not self.rs_device.is_pipeline_started:
            self.update_real_sense(settings)

    def stop_real_sense(self):
        if self.rs_device.is_pipeline_started:
            self.rs_device.stop_pipeline()
    
    def update_real_sense(self, settings):
        self.rs_device.toggle_config(settings)
        self.rs_device.restart_pipeline()

    def monitor_settings_and_update_gui(self):
        while True:
            with self.settings_lock:
                current_settings = self.settings.copy()
            
            # 使用主线程安全更新GUI
            self.app.after(0, lambda: self.update_gui_based_on_settings(current_settings))
            threading.Event().wait(0.1)  # 检查频率调整为每秒一次

    def update_gui_based_on_settings(self, settings):
        window_width, window_height = self.app.get_window_size()
        left_panel_width, right_panel_width = self.app.get_panel_widths()

        # 使用SizeCalculator计算目标尺寸
        target_width, target_height = SizeCalculator.calculate_target_size(window_height, right_panel_width)

        for stream_type, config in settings.items():
            target_image = self.black_image  # 默认为黑色图像
            if config["enabled"]:
                # 根据流类型获取相应的图像并处理
                if stream_type == "depth":
                    depth_image = self.rs_device.get_depth_image()
                    if depth_image is not None:
                        target_image = self.image_processor.process_and_resize_depth_image(depth_image, target_width, target_height)
                elif stream_type == "infrared":
                    infrared_image = self.rs_device.get_infrared_image()
                    if infrared_image is not None:
                        target_image = self.image_processor.process_and_resize_infrared_image(infrared_image, target_width, target_height)
                elif stream_type == "color":
                    color_image = self.rs_device.get_color_image()
                    if color_image is not None:
                        target_image = self.image_processor.process_and_resize_color_image(color_image, target_width, target_height)

            # 更新GUI中相应的图像显示
            if stream_type == "depth":
                self.app.set_depth_image(target_image)
            elif stream_type == "infrared":
                self.app.set_infrared_image(target_image)
            elif stream_type == "color":
                self.app.set_color_image(target_image)

    def close_program(self):
        # 先停止RealSense设备
        if self.rs_device:
            self.rs_device.stop_pipeline()
        # 然后销毁GUI应用
        try:
            self.app.destroy()
        except Exception as e:
            print(f"Error while destroying the app: {e}")

    def run(self):
        self.app.mainloop()

if __name__ == '__main__':
    with MainApp() as main_app:
        main_app.run()