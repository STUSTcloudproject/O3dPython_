import pyrealsense2 as rs
import threading
import time

class RealSense:
    def __init__(self):
        self.pipeline = rs.pipeline()
        self.config = rs.config()
        self.is_thread_open = False
        
        self.is_color_enabled = False
        self.color_resolution = '320 x 240'
        self.is_depth_enabled = False
        self.depth_resolution = '320 x 240'
        self.is_infrared_enabled = False
        self.infrared_resolution = '640 x 360'

        self.thread = None

    def stop_thread(self):
        self.is_thread_open = False
        if self.thread is not None and self.thread.is_alive():
            self.thread.join()
    
    def toggle_config(self, settings):
        self.stop_thread()
    
        # 定义有效的流类型
        valid_stream_types = ['color', 'depth', 'infrared']
    
        for stream_type in settings:
            # 检查流类型是否有效
            if stream_type not in valid_stream_types:
                raise KeyError(f"Invalid stream type: {stream_type}")
        
            # 构建启用键和解析度键
            enabled_key = f'is_{stream_type}_enabled'
            resolution_key = f'{stream_type}_resolution'
        
            # 直接设置属性，这里假设settings字典格式是正确的
            # 如果settings中缺少必要的键，这将直接抛出KeyError
            setattr(self, enabled_key, settings[stream_type]['enabled'])
            setattr(self, resolution_key, settings[stream_type]['resolution'])


    def config_streams(self):
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
        
        self.start_thread()

    def start_thread(self):
        if self.thread is None or not self.thread.is_alive():
            self.thread = threading.Thread(target=self.run_thread)
            self.is_thread_open = True
            self.thread.start()

    def run_thread(self):
        while self.is_thread_open:
            time.sleep(1)
            print("Thread running...")
