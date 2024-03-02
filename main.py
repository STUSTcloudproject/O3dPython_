import GUI
from PIL import Image, ImageTk
import threading
import tkinter
from RealSense import RealSense
from ImageProcessor import ImageProcessor
from SizeCalculator import SizeCalculator
from ImageSaver import ImageSaver

class MainApp:
    def __init__(self):
        self.settings_lock = threading.Lock()
        self.settings = self.init_settings()
        self.app = GUI.App(toggle_callback=self.callback_function)
        self.app.protocol("WM_DELETE_WINDOW", self.close_program)
        self.create_image_placeholders()
        self.update_display_active = True
        self.rs_device = None

    def __enter__(self):
        self.rs_device = RealSense().__enter__()  # 创建并初始化RealSense实例
        device_list = self.rs_device.list_devices()  # 获取设备列表
        device_list.insert(0, "None")
        self.app.update_device_options(device_list)  # 更新GUI中的下拉框选项
        # 启动后台线程来监视settings并更新GUI
        self.update_thread = threading.Thread(target=self._update_display_loop, daemon=True)
        self.update_thread.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # 清理RealSense资源
        self.update_display_active = False
        if self.rs_device:
            self.rs_device.__exit__(exc_type, exc_val, exc_tb)

    def init_settings(self):
        return {
            "depth": {"enabled": False, "resolution": "320 x 240"},
            "infrared": {"enabled": False, "resolution": "640 x 360"},
            "color": {"enabled": False, "resolution": "320 x 240"},
            "device": {"selected": None},  # 添加了新的设置项
        }

    def create_image_placeholders(self):
        # 创建红色和黑色图像作为占位符
        black = Image.new("RGB", (160, 120), "black")
        self.black_image = ImageTk.PhotoImage(black)

    def callback_function(self, mode, is_on=False, pane=None, device_info=None):
        if mode == "ToggleConfig":
            self.toggle_config(is_on, pane)
        elif mode == "CapturePhoto":
            self.photo_capture()
        elif mode == "DeviceSelected":
            self.device_selected(device_info)
    
    def toggle_config(self, is_on=False, pane=None):
        try:
            combo_value = pane.get_combo_value()
            stream_type = pane.get_stream_type()
            print("Stream type:", stream_type)
            with self.settings_lock:
                if stream_type in self.settings and stream_type != "device":  # 排除 device 配置项
                    self.settings[stream_type]["enabled"] = is_on
                    self.settings[stream_type]["resolution"] = combo_value
                else:
                    print(f"Unrecognized stream type: {stream_type}")
            self.stop_real_sense()
            self.restart_real_sense(self.settings)
            print(self.settings)
        except Exception as e:
            print(f"An error occurred: {e}")

    def photo_capture(self):
        with self.settings_lock:
            if any(self.settings.get(stream, {}).get('enabled', False) for stream in ['depth', 'infrared', 'color']):    
                depth_intrinsics = self.rs_device.get_depth_intrinsics() if self.settings.get('depth', {}).get('enabled') else None
                ImageSaver.photo_capture(
                    self.settings,
                    depth_image=self.rs_device.get_depth_image() if self.settings.get('depth', {}).get('enabled') else None,
                    infrared_image=self.rs_device.get_infrared_image() if self.settings.get('infrared', {}).get('enabled') else None,
                    color_image=self.rs_device.get_color_image() if self.settings.get('color', {}).get('enabled') else None,
                    depth_intrinsics=depth_intrinsics  # 确保这里传递 depth_intrinsics
                )
                print("Photo capture succeeded.")
            else:
                print("No stream is enabled. Skipping photo capture.")
    
    def device_selected(self, device_info):
        serial_number = self.extract_serial_number(device_info)
        with self.settings_lock:
            self.settings = self.init_settings()
            self.settings["device"]["selected"] = serial_number
        self.stop_real_sense()
        self.restart_real_sense(self.settings)
        self.app.reset_toggle_switches()  # 重置 GUI 按钮状态
        print(f"Device selected: {device_info}")

    def extract_serial_number(self, device_info):
        # 提取设备序列号的逻辑
        start = device_info.find('(SN: ') + 5
        end = device_info.find(')', start)
        serial_number = device_info[start:end]
        return serial_number if start < end else None

    def restart_real_sense(self, settings):
        if not self.rs_device.is_pipeline_started:
            with self.settings_lock:
                self.rs_device.toggle_config(settings)
                self.rs_device.restart_pipeline()

    def stop_real_sense(self):
        if self.rs_device.is_pipeline_started:
            self.rs_device.stop_pipeline()
    
    def _update_display_loop(self):
        while self.update_display_active:
            with self.settings_lock:
                current_settings = self.settings.copy()
            
            # 使用主线程安全更新GUI
            self.app.after(0, lambda: self._update_gui_based_on_settings(current_settings))
            threading.Event().wait(0.1)  # 检查频率调整为每秒一次

    def _update_gui_based_on_settings(self, settings):
        window_width, window_height = self.app.get_window_size()
        left_panel_width, right_panel_width = self.app.get_panel_widths()

        # 使用SizeCalculator计算目标尺寸
        target_width, target_height = SizeCalculator.calculate_target_size(window_height, right_panel_width)

        for stream_type, config in settings.items():
            if stream_type == "device":  # 跳过 device 配置项
                continue
            target_image = self.black_image
            if "enabled" in config and config["enabled"]:  # 检查是否存在 "enabled"
                # 根据流类型获取相应的图像并处理
                if stream_type == "depth":
                    depth_image = self.rs_device.get_depth_image()
                    if depth_image is not None:
                        target_image = ImageProcessor.process_and_resize_depth_image(depth_image, target_width, target_height)
                elif stream_type == "infrared":
                    infrared_image = self.rs_device.get_infrared_image()
                    if infrared_image is not None:
                        target_image = ImageProcessor.process_and_resize_infrared_image(infrared_image, target_width, target_height)
                elif stream_type == "color":
                    color_image = self.rs_device.get_color_image()
                    if color_image is not None:
                        target_image = ImageProcessor.process_and_resize_color_image(color_image, target_width, target_height)

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