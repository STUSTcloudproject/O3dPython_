import pyrealsense2 as rs
import numpy as np
import threading
import time

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

        self.depth_image = None
        self.color_image = None
        self.infrared_image = None

        self.thread = None
        self.lock = threading.Lock()


    def _stop_thread(self):
        if self.thread is not None and self.thread.is_alive():
            self.stop_event.set()  # 设置停止事件
            self.thread.join()  # 等待线程终止
    
    def toggle_config(self, settings):
        self._stop_thread()
        valid_stream_types = ['color', 'depth', 'infrared']
        for stream_type in settings:
            if stream_type not in valid_stream_types:
                raise KeyError(f"Invalid stream type: {stream_type}")
            
            stream_settings = settings[stream_type]
            if 'enabled' not in stream_settings or 'resolution' not in stream_settings:
                raise KeyError(f"Missing keys in settings for {stream_type}")
            
            enabled_key = f'is_{stream_type}_enabled'
            resolution_key = f'{stream_type}_resolution'
            
            setattr(self, enabled_key, stream_settings['enabled'])
            setattr(self, resolution_key, stream_settings['resolution'])


    def _config_streams(self):
        self.config = rs.config()
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
        self._stop_thread()  # 停止当前的处理线程
        try:
            self.stop_pipeline()  # 停止当前的pipeline
            self._config_streams()  # 根据最新的配置设置pipeline
            self.pipeline.start(self.config)  # 重新启动pipeline
            print("Pipeline started successfully")
            self.is_pipeline_started = True
            self._start_thread()  # 启动新的处理线程
        except Exception as e:
            self.is_pipeline_started = False
            print(f"An error occurred when restarting the pipeline: {e}")
            raise e


        
    def stop_pipeline(self):
        # 首先设置停止事件，通知运行中的线程停止其操作

        self._stop_thread()
        
        # 最后，停止pipeline
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
            self.stop_event.clear()  # 清除停止事件的状态，以便新线程可以正常运行
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

                with self.lock:  # 使用锁来确保线程安全
                    if self.is_depth_enabled:
                        depth_frame = frames.get_depth_frame()
                        if depth_frame:
                            self.depth_image = np.asanyarray(depth_frame.get_data())

                    if self.is_color_enabled:
                        color_frame = frames.get_color_frame()
                        if color_frame:
                            self.color_image = np.asanyarray(color_frame.get_data())

                    if self.is_infrared_enabled:
                        infrared_frame = frames.first(rs.stream.infrared)
                        if infrared_frame:
                            self.infrared_image = np.asanyarray(infrared_frame.get_data())
            else:
                # 如果pipeline没有启动，稍微延迟循环，减少CPU占用
                time.sleep(0.1)
            #print('running...')
            time.sleep(0.025)  # 控制循环频率

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
        self.stop_pipeline() #<- 1tab

if __name__ == "__main__":
    settings = {
        'depth': {'enabled': True, 'resolution': '320 x 240'},
        'infrared': {'enabled': True, 'resolution': '320 x 240'},   
        'color': {'enabled': True, 'resolution': '640 x 360'}     
    }

    with RealSense() as rs_device:
        rs_device.toggle_config(settings)
        rs_device.restart_pipeline()
        # 此处可以进行数据处理
        time.sleep(3)  # 假设的处理时间
    print("Program stopped")
