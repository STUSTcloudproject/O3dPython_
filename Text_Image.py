import tkinter as tk
from tkinter import ttk
import cv2
import threading
from RealSense import RealSense  # 确保这里正确地导入了您的RealSense类
from ImageProcessor import ImageProcessor  # 导入ImageProcessor类

class RealSenseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("RealSense Viewer")

        self.color_label = ttk.Label(self.root)
        self.color_label.pack()

        self.depth_label = ttk.Label(self.root)
        self.depth_label.pack()

        self.infrared_label = ttk.Label(self.root)
        self.infrared_label.pack()

        self.color_image_ref = None
        self.depth_image_ref = None
        self.infrared_image_ref = None
        
        self.image_processor = ImageProcessor()  # 实例化ImageProcessor
        
        # 添加重启和停止按钮
        self.restart_button = ttk.Button(self.root, text="Restart", command=self.restart_real_sense)
        self.restart_button.pack()

        self.stop_button = ttk.Button(self.root, text="Stop", command=self.stop_real_sense)
        self.stop_button.pack()

        # 创建RealSense设备实例
        self.rs_device = RealSense()

        # 启动RealSense设备更新线程
        self.rs_thread = threading.Thread(target=self.update_real_sense, daemon=True)
        self.rs_thread.start()

        # 启动图像更新循环
        self.update_images()

    def restart_real_sense(self):
        if not self.rs_device.is_pipeline_started:
            self.update_real_sense()

    def stop_real_sense(self):
        self.rs_device.stop_pipeline()
    
    def update_real_sense(self):
        settings = {
            'depth': {'enabled': True, 'resolution': '320 x 240'},
            'infrared': {'enabled': True, 'resolution': '320 x 240'},   
            'color': {'enabled': True, 'resolution': '640 x 360'}
        }
        self.rs_device.toggle_config(settings)
        self.rs_device.restart_pipeline()

    def update_images(self):
        # 处理并更新彩色图像
        if self.rs_device.color_image is not None:
            color_image = self.rs_device.get_color_image()
            self.color_image_ref = self.image_processor.process_and_resize_color_image(color_image)
            self.color_label.config(image=self.color_image_ref)
        
        # 处理并更新深度图像
        if self.rs_device.depth_image is not None:
            depth_image = self.rs_device.get_depth_image()
            self.depth_image_ref = self.image_processor.process_and_resize_depth_image(depth_image)
            self.depth_label.config(image=self.depth_image_ref)
        
        # 处理并更新红外图像
        if self.rs_device.infrared_image is not None:
            infrared_image = self.rs_device.get_infrared_image()
            self.infrared_image_ref = self.image_processor.process_and_resize_infrared_image(infrared_image)
            self.infrared_label.config(image=self.infrared_image_ref)
        
        # 设置定时器，以定期更新图像
        self.root.after(100, self.update_images)

if __name__ == "__main__":
    root = tk.Tk()
    app = RealSenseApp(root)
    root.mainloop()
