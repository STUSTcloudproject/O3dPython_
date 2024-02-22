import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import numpy as np
import cv2
import threading
from RealSense import RealSense  # 确保这里正确地导入了您的RealSense类

def process_color_image(color_image):
    # 处理彩色图像以供显示
    if color_image is None:
        return None
    color_colormap = cv2.cvtColor(color_image, cv2.COLOR_BGR2RGB)
    color_colormap = Image.fromarray(color_colormap)
    color_colormap = ImageTk.PhotoImage(image=color_colormap)
    return color_colormap

def process_depth_image(depth_image):
    # 处理深度图像以供显示
    if depth_image is None:
        return None
    depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
    depth_colormap = cv2.cvtColor(depth_colormap, cv2.COLOR_BGR2RGB)
    depth_colormap = Image.fromarray(depth_colormap)
    depth_colormap = ImageTk.PhotoImage(image=depth_colormap)
    return depth_colormap

def process_infrared_image(infrared_image):
    # 处理红外图像以供显示
    if infrared_image is None:
        return None
    infrared_colormap = cv2.cvtColor(infrared_image, cv2.COLOR_GRAY2RGB)
    infrared_colormap = Image.fromarray(infrared_colormap)
    infrared_colormap = ImageTk.PhotoImage(image=infrared_colormap)
    return infrared_colormap

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
        # 检查RealSense设备是否已经启动，如果未启动，则启动它
        if not self.rs_device.is_pipeline_started:
            self.update_real_sense()

    def stop_real_sense(self):
        # 停止RealSense设备
        self.rs_device.stop_pipeline()
    
    def update_real_sense(self):
        # 配置并启动RealSense设备
        settings = {
            'depth': {'enabled': True, 'resolution': '320 x 240'},
            'infrared': {'enabled': True, 'resolution': '320 x 240'},   
            'color': {'enabled': True, 'resolution': '640 x 360'}
        }
        self.rs_device.toggle_config(settings)
        self.rs_device.restart_pipeline()

    def update_images(self):
        # 更新Tkinter界面上的图像
        if self.rs_device.color_image is not None:
            self.color_label.image = process_color_image(self.rs_device.color_image)
            self.color_label.config(image=self.color_label.image)
        
        if self.rs_device.depth_image is not None:
            self.depth_label.image = process_depth_image(self.rs_device.depth_image)
            self.depth_label.config(image=self.depth_label.image)
        
        if self.rs_device.infrared_image is not None:
            self.infrared_label.image = process_infrared_image(self.rs_device.infrared_image)
            self.infrared_label.config(image=self.infrared_label.image)
        
        self.root.after(100, self.update_images)  # 每100毫秒更新一次图像

if __name__ == "__main__":
    root = tk.Tk()
    app = RealSenseApp(root)
    root.mainloop()
