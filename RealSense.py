import pyrealsense2 as rs

class RealSense:
    def __init__(self):
        self.pipeline = rs.pipeline()
        self.config = rs.config()

        self.is_color_enabled = False
        self.color_resolution = '320 x 240'
        self.is_depth_enabled = False
        self.depth_resolution = '320 x 240'
        self.is_infrared_enabled = False
        self.infrared_resolution = '640 x 360'

    def toggle_stream(self, settings):
        for stream_type in settings:
            try:
                enabled_key = f'is_{stream_type}_enabled'
                resolution_key = f'{stream_type}_resolution'
                setattr(self, enabled_key, settings[stream_type]['enabled'])
                setattr(self, resolution_key, settings[stream_type]['resolution'])
            except KeyError:
                print(f"Error: Missing key in settings for {stream_type}")

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