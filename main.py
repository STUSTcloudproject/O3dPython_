import GUI
from PIL import Image, ImageTk
import threading
import tkinter
from RealSense import RealSense
from ImageProcessor import ImageProcessor
from ImageSaver import ImageSaver
from Settings import Settings

class MainApp:
    def __init__(self):
        self.settings = Settings()
        self.app = GUI.App(toggle_callback=self.callback_function)
        self.app.protocol("WM_DELETE_WINDOW", self.close_program)
        self.black_image = ImageTk.PhotoImage(Image.new("RGB", (160, 120), "black"))
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

    def callback_function(self, mode, is_on=False, pane=None, device_info=None):
        if mode == "ToggleConfig":
            self.toggle_config(is_on, pane)
        elif mode == "CapturePhoto":
            self.photo_capture()
        elif mode == "DeviceSelected":
            self.device_selected(device_info)
    
    def toggle_config(self, is_on=False, pane=None):
        # 直接调用Settings类的方法来更新设置
        self.settings.update_setting(pane.get_stream_type()  , enabled=is_on, resolution=pane.get_combo_value())
        self.restart_real_sense(self.settings)  # 假设你的Settings类有一个方法来获取所有设置
        print("Settings updated successfully.")

    def photo_capture(self):
        # 直接检查是否有流启用，如果没有，则打印信息并返回
        if not any(self.settings.is_stream_enabled(stream) for stream in ['depth', 'infrared', 'color']):
            print("No stream is enabled. Skipping photo capture.")
            return

        # 使用条件表达式直接在参数中获取图像和深度内参
        ImageSaver.photo_capture(
            self.settings.get_all_settings(),  # 获取所有设置
            depth_image=self.rs_device.get_depth_image() if self.settings.is_stream_enabled('depth') else None,
            infrared_image=self.rs_device.get_infrared_image() if self.settings.is_stream_enabled('infrared') else None,
            color_image=self.rs_device.get_color_image() if self.settings.is_stream_enabled('color') else None,
            depth_intrinsics=self.rs_device.get_depth_intrinsics() if self.settings.is_stream_enabled('depth') else None
        )
        print("Photo capture succeeded.")
    
    def device_selected(self, device_info):
        print(f"Device selected: {device_info}")
        serial_number = self.rs_device.extract_serial_number(device_info)
        # 使用Settings类的方法来重置和更新设备设置
        self.settings.reset_settings()
        self.settings.update_setting("device", selected_device=serial_number)
        self.restart_real_sense(self.settings)
        self.app.reset_toggle_switches()  # 重置GUI按钮状态
        print("Device selected successfully.")

    def restart_real_sense(self, settings):
        self.rs_device.toggle_config(settings)
        self.rs_device.restart_pipeline()

    def stop_real_sense(self):
        if self.rs_device.is_pipeline_started:
            self.rs_device.stop_pipeline()
    
    def _update_display_loop(self):
        while self.update_display_active:           
            self.app.after(0, lambda: self._update_gui_based_on_settings(self.settings))
            threading.Event().wait(0.1)  # 检查频率调整为每秒一次

    def _update_gui_based_on_settings(self, settings):
        window_width, window_height = self.app.get_window_size()
        left_panel_width, right_panel_width = self.app.get_panel_widths()
        target_width, target_height = ImageProcessor.calculate_target_size(window_height, right_panel_width)

        for stream_type in ['depth', 'infrared', 'color']:
            # 获取图像数据
            image_data = getattr(self.rs_device, f"get_{stream_type}_image")()

            # 调用select_image方法处理图像
            target_image = ImageProcessor.select_image(settings, image_data, stream_type, self.black_image, target_width, target_height)

            # 更新GUI中相应的图像显示
            getattr(self.app, f"set_{stream_type}_image")(target_image)


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