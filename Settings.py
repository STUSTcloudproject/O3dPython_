import threading

class Settings:
    def __init__(self):
        self.lock = threading.Lock()
        self.settings = self.init_settings()

    def init_settings(self):
        """初始化设置字典"""
        return {
            "depth": {"enabled": False, "resolution": "320 x 240"},
            "infrared": {"enabled": False, "resolution": "640 x 360"},
            "color": {"enabled": False, "resolution": "320 x 240"},
            "device": {"selected": None},
        }

    def update_setting(self, stream_type, enabled=None, resolution=None, selected_device=None):
        print(f"Updating settings: {stream_type}, {enabled}, {resolution}, {selected_device}")
        with self.lock:
            try:
                if stream_type in self.settings:
                    if enabled is not None:
                        self.settings[stream_type]["enabled"] = enabled
                    if resolution is not None:
                        self.settings[stream_type]["resolution"] = resolution
                    if selected_device is not None:
                        self.settings["device"]["selected"] = selected_device
                else:
                    raise ValueError(f"Invalid setting type: {stream_type}")
            except Exception as e:
                raise Exception(f"Error occurred while updating settings: {e}")

    def get_stream_info(self, stream_type):
        """获取指定流的启用状态和分辨率信息"""
        with self.lock:
            stream_settings = self.settings.get(stream_type, {'enabled': False, 'resolution': ''})
            return stream_settings.get('enabled', False), stream_settings.get('resolution', '')

    def get_setting(self, stream_type):
        """安全获取特定设置项"""
        with self.lock:
            return self.settings.get(stream_type, None)

    def reset_settings(self):
        """重置设置为初始值"""
        with self.lock:
            self.settings = self.init_settings()

    def is_stream_enabled(self, stream_type):
        """检查指定流是否启用"""
        with self.lock:
            stream_settings = self.settings.get(stream_type)
            if stream_settings:
                return stream_settings.get('enabled', False)
            return False
        
    def get_all_settings(self):
        """获取所有设置的副本"""
        with self.lock:
            return self.settings.copy()

