import GUI
from PIL import Image, ImageTk
import threading
import tkinter
from RealSense import RealSense
from ImageProcessor import ImageProcessor
from ImageSaver import ImageSaver
from Settings import Settings
from datetime import datetime

class MainApp:
    def __init__(self):
        self.settings = Settings()
        self.app = GUI.App(toggle_callback=self.callback_function)
        self.app.protocol("WM_DELETE_WINDOW", self.close_program) # 設置關閉窗口時的操作
        self.black_image = ImageTk.PhotoImage(Image.new("RGB", (160, 120), "black")) # 創建一個黑色的預設圖像
        self.update_display_active = True # 控制更新顯示的狀態
        self.rs_device = None # 初始化 RealSense 設備為 None
        self.recording_lock = threading.Lock()
        self.is_recording_enabled = False

    def __enter__(self):
        self.rs_device = RealSense().__enter__()  # 創建並初始化RealSense實例
        device_list = self.rs_device.list_devices()  # 獲取設備列表
        device_list.insert(0, "None") # 在列表開始處插入 "None" 選項
        self.app.update_device_options(device_list)  # 更新GUI中的設備選擇下拉菜單
        # 啟動後台線程以持續更新設置並刷新GUI
        self.update_thread = threading.Thread(target=self._update_display_loop, daemon=True)
        self.record_thread = threading.Thread(target=self.record_images, daemon=True)
        self.update_thread.start() # 啟動線程
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # 清理RealSense資源
        self.update_display_active = False # 停止顯示更新
        self.is_recording_enabled = False # 停止錄製
        if self.rs_device:
            self.rs_device.__exit__(exc_type, exc_val, exc_tb) # 正常退出RealSense資源

    def callback_function(self, mode, is_on=False, pane=None, device_info=None, is_recording=None):
        # 根據回調模式進行相對應操作
        if mode == "ToggleConfig":
            self.toggle_config(is_on, pane)
        elif mode == "CapturePhoto":
            self.photo_capture(is_recording)
        elif mode == "DeviceSelected":
            self.device_selected(device_info)
    
    def toggle_config(self, is_on=False, pane=None):
        # 使用設置來更新配置
        self.settings.update_setting(pane.get_stream_type(), enabled=is_on, resolution=pane.get_combo_value())
        self.restart_real_sense(self.settings) # 重新啟動 RealSense 設備以應用新設置

    def photo_capture(self, is_recording):
        # 檢查是否有啟用的流，若無則跳過拍照
        if not any(self.settings.is_stream_enabled(stream) for stream in ['depth', 'infrared', 'color']):
            print("No stream is enabled. Stopping recording.")
            self.app.stop_recording()  # 调用App类的stop_recording方法
            return
        else:
            with self.recording_lock:
                self.is_recording_enabled = is_recording
            if self.is_recording_enabled:
                #開啟record_images 使用線程
                self.record_thread = threading.Thread(target=self.record_images, daemon=True)
                self.record_thread.start()
            else:
                #等待線程結束
                self.record_thread.join()

    def record_images(self):
        while self.is_recording_enabled:
            with self.recording_lock:
                should_recorde = self.is_recording_enabled
            if should_recorde:
                ImageSaver.photo_capture(
                    self.settings.get_all_settings(),
                    depth_image=self.rs_device.get_depth_image() if self.settings.is_stream_enabled('depth') else None,
                    infrared_image=self.rs_device.get_infrared_image() if self.settings.is_stream_enabled('infrared') else None,
                    color_image=self.rs_device.get_color_image() if self.settings.is_stream_enabled('color') else None,
                    depth_intrinsics=self.rs_device.get_depth_intrinsics() if self.settings.is_stream_enabled('depth') else None,
                    time = str(datetime.now().timestamp()).replace('.', '_')
                )
        #threading.Event().wait(0.05)    

    def device_selected(self, device_info):
        # 處理設備選擇事件
        print(f"Device selected: {device_info}")
        serial_number = self.rs_device.extract_serial_number(device_info) # 從設備信息中提取序列號
        self.settings.reset_settings() # 重置設置
        self.settings.update_setting("device", selected_device=serial_number) # 更新設備設置
        self.restart_real_sense(self.settings) # 根據新設置重新啟動 RealSense
        self.app.reset_toggle_switches() # 重置 GUI 中的切換按鈕狀態

    def restart_real_sense(self, settings):
        # 根據新的設置重新啟動 RealSense 設備
        self.rs_device.toggle_config(settings)
        self.rs_device.restart_pipeline()

    def stop_real_sense(self):
        # 停止 RealSense 設備
        if self.rs_device.is_pipeline_started:
            self.rs_device.stop_pipeline()
    
    def _update_display_loop(self):
        # 更新顯示的循環
        while self.update_display_active:           
            self.app.after(0, lambda: self._update_gui_based_on_settings(self.settings))
            threading.Event().wait(0.1)  # 進行輕量級的睡眠以減少 CPU 使用

    def _update_gui_based_on_settings(self, settings):
        # 根據設置更新 GUI 顯示
        window_width, window_height = self.app.get_window_size()
        left_panel_width, right_panel_width = self.app.get_panel_widths()
        target_width, target_height = ImageProcessor.calculate_target_size(window_height, right_panel_width)

        for stream_type in ['depth', 'infrared', 'color']:
            # 獲取相應類型的圖像數據
            image_data = getattr(self.rs_device, f"get_{stream_type}_image")()

            # 處理圖像並更新 GUI
            target_image = ImageProcessor.select_image(settings, image_data, stream_type, self.black_image, target_width, target_height)
            getattr(self.app, f"set_{stream_type}_image")(target_image) # 更新 GUI 中的圖像顯示

    def close_program(self):
        # 關閉程序前的清理工作
        if self.rs_device:
            self.rs_device.stop_pipeline() # 停止 RealSense 設備
        try:
            self.app.destroy() # 銷毀 GUI 應用
        except Exception as e:
            print(f"Error while destroying the app: {e}")

    def run(self):
        self.app.mainloop() # 運行 GUI 應用

if __name__ == '__main__':
    with MainApp() as main_app:
        main_app.run()
