import unittest
from RealSense import RealSense  # 替换为您的模块名和类名

class TestRealSense(unittest.TestCase):

    def setUp(self):
        # 初始化RealSense设备
        self.rs = RealSense()

    def test_initialization(self):
        # 测试初始化
        self.assertFalse(self.rs.is_pipeline_started)
        self.assertFalse(self.rs.is_depth_enabled)
        self.assertFalse(self.rs.is_color_enabled)
        self.assertFalse(self.rs.is_infrared_enabled)

    def test_toggle_config(self):
        # 测试配置切换
        settings = {
            'depth': {'enabled': True, 'resolution': '320 x 240'},
            'color': {'enabled': True, 'resolution': '640 x 360'}
        }
        self.rs.toggle_config(settings)
        self.assertTrue(self.rs.is_depth_enabled)
        self.assertTrue(self.rs.is_color_enabled)
        self.assertEqual(self.rs.depth_resolution, '320 x 240')
        self.assertEqual(self.rs.color_resolution, '640 x 360')

    def test_pipeline_operations(self):
        # 测试流操作
        self.rs.toggle_config({
            'depth': {'enabled': True, 'resolution': '320 x 240'}
        })
        self.rs.config_streams()
        self.rs.restart_pipeline()
        self.assertTrue(self.rs.is_pipeline_started)
        self.rs.stop_pipeline()
        self.assertFalse(self.rs.is_pipeline_started)

    # 添加更多测试...

    def tearDown(self):
        # 清理资源
        self.rs.stop_pipeline()

if __name__ == '__main__':
    unittest.main()
