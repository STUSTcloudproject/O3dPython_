import unittest
from RealSense import RealSense

class TestRealSense(unittest.TestCase):
    def setUp(self):
        self.rs = RealSense()

    def test_toggle_stream(self):
        settings = {
            'color': {'enabled': True, 'resolution': '640 x 480'},
            'depth': {'enabled': False, 'resolution': '320 x 240'},
            'infrared': {'enabled': True, 'resolution': '640 x 360'}
        }
        self.rs.toggle_stream(settings)
        self.assertEqual(self.rs.is_color_enabled, True)
        self.assertEqual(self.rs.color_resolution, '640 x 480')
        self.assertEqual(self.rs.is_depth_enabled, False)
        self.assertEqual(self.rs.depth_resolution, '320 x 240')
        self.assertEqual(self.rs.is_infrared_enabled, True)
        self.assertEqual(self.rs.infrared_resolution, '640 x 360')

    def test_config_streams(self):
        self.rs.is_color_enabled = True
        self.rs.color_resolution = '640 x 480'
        self.rs.is_depth_enabled = False
        self.rs.depth_resolution = '320 x 240'
        self.rs.is_infrared_enabled = True
        self.rs.infrared_resolution = '640 x 360'
        self.rs.config_streams()
        # Here you should add assertions that check the configuration of the streams.
        # As I don't have access to the rs.config() object, I can't provide these assertions.
Jn
if __name__ == '__main__':
    unittest.main()