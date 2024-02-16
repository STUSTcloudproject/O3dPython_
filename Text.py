import unittest
from RealSense import RealSense
import time

# 假定 RealSense 類已經定義在此處


class TestRealSense(unittest.TestCase):
    def setUp(self):
        self.rs = RealSense()

    def tearDown(self):
        self.rs.stop_thread()

    def test_initialization(self):
        """測試對象是否正確初始化"""
        self.assertFalse(self.rs.is_thread_open)
        self.assertFalse(self.rs.is_color_enabled)
        self.assertFalse(self.rs.is_depth_enabled)
        self.assertFalse(self.rs.is_infrared_enabled)
        self.assertIsNone(self.rs.thread)

    def test_toggle_config_valid_settings(self):
        """測試有效配置的應用"""
        settings = {
            "color": {"enabled": True, "resolution": "640 x 480"},
            "depth": {"enabled": True, "resolution": "640 x 480"},
        }
        self.rs.toggle_config(settings)
        self.assertTrue(self.rs.is_color_enabled)
        self.assertEqual(self.rs.color_resolution, "640 x 480")
        self.assertTrue(self.rs.is_depth_enabled)
        self.assertEqual(self.rs.depth_resolution, "640 x 480")

    def test_config_streams_and_thread_start(self):
        """測試配置流並啟動線程"""
        self.rs.config_streams()
        self.rs.start_thread()
        time.sleep(2)  # 給予時間讓線程啟動
        self.assertTrue(self.rs.thread.is_alive())

    def test_stop_thread(self):
        """測試停止線程"""
        self.rs.start_thread()
        time.sleep(1)  # 給予時間讓線程啟動
        self.rs.stop_thread()
        time.sleep(1)  # 給予時間讓線程停止
        self.assertFalse(self.rs.thread.is_alive())

    def test_toggle_config_while_thread_running(self):
        # 启动线程
        self.rs.start_thread()
        time.sleep(1)  # 给线程一些时间来启动

        # 提供一个有效的配置字典
        valid_settings = {
            "color": {"enabled": True, "resolution": "640 x 480"},
            "depth": {"enabled": True, "resolution": "640 x 480"},
        }

        # 使用有效的配置更新设置，并根据您的类设计，可能需要调用 config_streams 来应用配置并重启线程
        self.rs.toggle_config(valid_settings)
        self.rs.config_streams()

        time.sleep(2)  # 给线程一些时间来重新启动

        # 现在断言线程应该是活跃的
        self.assertTrue(
            self.rs.thread.is_alive(), "线程应该在调用 config_streams 后重新启动并运行"
        )

    def test_invalid_settings(self):
        """測試無效配置設置"""
        with self.assertRaises(KeyError):
            self.rs.toggle_config(
                {"nonexistent_stream": {"enabled": True, "resolution": "123 x 456"}}
            )


# 如果這個文件是作為主程序運行，則運行測試
if __name__ == "__main__":
    unittest.main()
