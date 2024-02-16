import pyrealsense2 as rs
import threading
import time

class RealSense:
    def __init__(self):
        self.pipeline = rs.pipeline()
        self.config = rs.config()
        self.is_thread_open = False

        self.is_pipeline_started = False
        
        self.is_depth_enabled = False
        self.depth_resolution = '320 x 240'
        self.is_infrared_enabled = False
        self.infrared_resolution = '320 x 240'
        self.is_color_enabled = False
        self.color_resolution = '640 x 360'

        self.thread = None
        self.lock = threading.Lock()

    def stop_thread(self):
        self.is_thread_open = False
        if self.thread is not None and self.thread.is_alive():
            self.thread.join()
    
    def toggle_config(self, settings):
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

    def restart_pipeline(self):      
        self.stop_thread()
        try:
            self.stop_pipeline()
            self.pipeline.start(self.config)
            self.is_pipeline_started = True      
            self.start_thread()
        except Exception as e:
            self.is_pipeline_started = False
            print(f"An error occurred when restarting the pipeline: {e}")
            raise e
        
    def stop_pipeline(self):
        try:
            if self.is_pipeline_started:
                self.pipeline.stop()
                self.is_pipeline_started = False
        except Exception as e:
            print(f"An error occurred when stopping the pipeline: {e}")
            raise e

    def start_thread(self):
        if self.thread is None or not self.thread.is_alive():
            self.thread = threading.Thread(target=self.run_thread)
            self.is_thread_open = True
            self.thread.start()

    def run_thread(self):
        while self.is_thread_open:
            print("Thread running...") 
            time.sleep(0.5)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_thread()
        if self.is_pipeline_started:
            self.stop_pipeline()

if __name__ == "__main__":
    settings = {
        'color': {'enabled': True, 'resolution': '640 x 480'},
        'depth': {'enabled': True, 'resolution': '640 x 480'},
        'infrared': {'enabled': True, 'resolution': '640 x 480'}        
    }

    with RealSense() as rs_device:
        rs_device.toggle_config(settings)
        rs_device.config_streams()
        rs_device.restart_pipeline()
        # 此处可以进行数据处理
        time.sleep(3)  # 假设的处理时间
    print("Pipeline stopped")