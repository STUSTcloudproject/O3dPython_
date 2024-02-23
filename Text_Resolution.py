import pyrealsense2 as rs

class RealSenseTest:
    def __init__(self):
        self.pipeline = rs.pipeline()
        self.config = rs.config()

    def test_stream(self, stream_type, width, height, fps=30):
        try:
            if stream_type == 'color':
                self.config.enable_stream(rs.stream.color, width, height, rs.format.bgr8, fps)
            elif stream_type == 'depth':
                self.config.enable_stream(rs.stream.depth, width, height, rs.format.z16, fps)
            elif stream_type == 'infrared':
                self.config.enable_stream(rs.stream.infrared, 0, width, height, rs.format.y8, fps)
            
            # 尝试启动流以验证配置是否支持
            profile = self.pipeline.start(self.config)
            print(f"Stream {stream_type} with resolution {width}x{height} @ {fps}FPS is supported.")
            self.pipeline.stop()
        except Exception as e:
            print(f"Stream {stream_type} with resolution {width}x{height} @ {fps}FPS is not supported. Error: {e}")

# 创建测试实例
tester = RealSenseTest()

# 测试color流的分辨率
tester.test_stream('color', 640, 360)
tester.test_stream('color', 640, 480)

# 测试depth和infrared流的分辨率
tester.test_stream('depth', 320, 240)
tester.test_stream('infrared', 320, 240)
