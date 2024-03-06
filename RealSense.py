import pyrealsense2 as rs
import numpy as np
import threading
import time
from Settings import Settings

class RealSense:
    def __init__(self):
        self.pipeline = rs.pipeline()
        self.config = rs.config()
        self.stop_event = threading.Event()

        self.is_pipeline_started = False

        self.is_depth_enabled = False
        self.depth_resolution = '320 x 240'
        self.is_infrared_enabled = False
        self.infrared_resolution = '320 x 240'
        self.is_color_enabled = False
        self.color_resolution = '640 x 360'
        self.device = 'None'

        self.depth_frame = None
        self.depth_image = None
        self.color_image = None
        self.infrared_image = None

        self.thread = None
        self.lock = threading.Lock()

    def _stop_thread(self):
        if self.thread is not None and self.thread.is_alive():
            self.stop_event.set()  # 設置停止事件
            self.thread.join()  # 等待線程終止
    
    def toggle_config(self, settings_instance):
        self.stop_pipeline()
        # 定義流類型到屬性名稱的映射
        stream_type_mapping = {
            'color': ('is_color_enabled', 'color_resolution'),
            'depth': ('is_depth_enabled', 'depth_resolution'),
            'infrared': ('is_infrared_enabled', 'infrared_resolution'),
        }

        # 使用Settings實例中的新方法更新RealSense類的屬性
        for stream_type, (enabled_attr, resolution_attr) in stream_type_mapping.items():
            is_enabled, resolution = settings_instance.get_stream_info(stream_type)
            setattr(self, enabled_attr, is_enabled)
            setattr(self, resolution_attr, resolution)

        # 特殊處理設備設置
        self.device = settings_instance.get_setting('device').get('selected', 'None') if settings_instance.get_setting('device') else 'None'

    def _config_streams(self):
        self.config = rs.config()
        # 如果已選擇設備，則使用設備的序列號進行配置
        if self.device != 'None':
            print(f"Configuring for device with serial number: {self.device}")
            self.config.enable_device(self.device)
        else:
            print("No device selected, configuring for any connected device.")

        for stream_type in ['color', 'depth', 'infrared']:
            enabled_key = f'is_{stream_type}_enabled'
            resolution_key = f'{stream_type}_resolution'
            if getattr(self, enabled_key):
                resolution_no_spaces = ''.join(getattr(self, resolution_key).split())
                parts = resolution_no_spaces.split('x')
                if stream_type == 'color':
                    self.config.enable_stream(rs.stream.color, int(parts[0]), int(parts[1]), rs.format.bgr8, 30)
                elif stream_type == 'depth':
                    self.config.enable_stream(rs.stream.depth, int(parts[0]), int(parts[1]), rs.format.z16, 30)
                elif stream_type == 'infrared':
                    self.config.enable_stream(rs.stream.infrared, 0, int(parts[0]), int(parts[1]), rs.format.y8, 30)

    def restart_pipeline(self):
        self._stop_thread()  # 停止當前的處理線程
        self._config_streams()  # 根據最新的配置設置pipeline
        # 在 _config_streams() 調用後再檢查 self.device
        if self.device == 'None':
            print("No device selected, cannot restart pipeline.")
            return  # 早期返回，不執行後續操作

        try:
            self.stop_pipeline()  # 停止當前的pipeline
            self.pipeline.start(self.config)  # 重新啟動pipeline
            print("Pipeline started successfully")
            self.is_pipeline_started = True
            self._start_thread()  # 啟動新的處理線程
        except Exception as e:
            self.is_pipeline_started = False
            print(f"An error occurred when restarting the pipeline: {e}")

    def stop_pipeline(self):
        # 首先設置停止事件，通知運行中的線程停止其操作

        self._stop_thread()
        
        # 最後，停止pipeline
        try:
            if self.is_pipeline_started:
                self.pipeline.stop()
                self.is_pipeline_started = False
                print("Pipeline successfully stopped.")
        except Exception as e:
            print(f"An error occurred when stopping the pipeline: {e}")
            raise e

    def _start_thread(self):
        if self.thread is None or not self.thread.is_alive():
            self.stop_event.clear()  # 清除停止事件的狀態，以便新線程可以正常運行
            self.thread = threading.Thread(target=self._run_thread)
            self.thread.start()

    def _run_thread(self):
        while not self.stop_event.is_set():
            if self.is_pipeline_started and not self.stop_event.is_set():
                try:
                    frames = self.pipeline.wait_for_frames()
                except RuntimeError as e:
                    print(f"RealSense error: {e}")
                    continue
                except Exception as e:
                    print(f"Unexpected error: {e}")
                    continue

                with self.lock:  # 使用鎖來確保線程安全
                    if self.is_depth_enabled:
                        self.depth_frame = frames.get_depth_frame()
                        if self.depth_frame:
                            self.depth_image = np.asanyarray(self.depth_frame.get_data())

                    if self.is_color_enabled:
                        color_frame = frames.get_color_frame()
                        if color_frame:
                            self.color_image = np.asanyarray(color_frame.get_data())

                    if self.is_infrared_enabled:
                        infrared_frame = frames.first(rs.stream.infrared)
                        if infrared_frame:
                            self.infrared_image = np.asanyarray(infrared_frame.get_data())
            else:
                # 如果pipeline沒有啟動，稍微延遲循環，減少CPU佔用
                time.sleep(0.1)
            # 控制循環頻率

    def get_depth_intrinsics(self):
        with self.lock:
            if self.is_pipeline_started and self.is_depth_enabled:
                profile = self.pipeline.get_active_profile()
                depth_profile = rs.video_stream_profile(profile.get_stream(rs.stream.depth))
                intrinsics = depth_profile.get_intrinsics()
                return intrinsics
            else:
                print("Pipeline has not started or depth stream is not enabled.")
                return None

    def list_devices(self):
        # 使用pyrealsense2查詢連接的設備
        ctx = rs.context()
        devices = ctx.query_devices()
        if not devices:
            print("No RealSense devices were found.")
            return []

        device_list = []
        for dev in devices:
            # 獲取設備的序列號作為唯一標識
            device_serial = dev.get_info(rs.camera_info.serial_number)
            device_name = dev.get_info(rs.camera_info.name)
            device_desc = f"{device_name} (SN: {device_serial})"
            device_list.append(device_desc)

        return device_list

    def extract_serial_number(self, device_info):
        # 提取設備序列號的邏輯
        if device_info != "None" and device_info is not None:
            start = device_info.find('(SN: ') + 5
            end = device_info.find(')', start)
            serial_number = device_info[start:end]
            return serial_number if start < end else None
        else:
            return "None"

    def get_depth_frame(self):
        with self.lock:
            return self.depth_frame

    def get_depth_image(self):
        with self.lock:
            return np.copy(self.depth_image) if self.depth_image is not None else None

    def get_color_image(self):
        with self.lock:
            return np.copy(self.color_image) if self.color_image is not None else None

    def get_infrared_image(self):
        with self.lock:
            return np.copy(self.infrared_image) if self.infrared_image is not None else None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._stop_thread()
        self.stop_pipeline()

if __name__ == "__main__":
    settings = {
        'depth': {'enabled': True, 'resolution': '320 x 240'},
        'infrared': {'enabled': True, 'resolution': '320 x 240'},   
        'color': {'enabled': True, 'resolution': '640 x 360'}     
    }

    with RealSense() as rs_device:
        print(rs_device.list_devices())
        rs_device.toggle_config(settings)
        rs_device.restart_pipeline()
        # 此處可以進行數據處理
        time.sleep(3)  # 假設的處理時間
    print("Program stopped")
