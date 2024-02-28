import os
import datetime
import open3d as o3d
import numpy as np
from PIL import Image
import numpy as np
import pyrealsense2 as rs

class ImageSaver:
    @staticmethod
    def save_image(image, path, image_type):
        """將圖像保存為文件"""
        img = Image.fromarray(image)
        img.save(path)
        print(f"{image_type.capitalize()} image saved successfully at {path}")

    @staticmethod
    def save_point_cloud(depth_image, depth_intrinsics, path, cloud_type):
        """使用open3d将深度图像转换为点云并保存"""
        if depth_image is None:
            print("Depth image is None, cannot save point cloud.")
            return
        
        # 将深度图像转换为Open3D的图像对象
        depth_o3d = o3d.geometry.Image(depth_image)
        
        # 创建Open3D的内参对象
        intrinsics_o3d = o3d.camera.PinholeCameraIntrinsic(
            depth_intrinsics.width,
            depth_intrinsics.height,
            depth_intrinsics.fx,
            depth_intrinsics.fy,
            depth_intrinsics.ppx,
            depth_intrinsics.ppy)
        
        # 从深度图像创建点云
        pcd = o3d.geometry.PointCloud.create_from_depth_image(
            depth_o3d, intrinsics_o3d)
        
        # 调整点云的方向（这一步是可选的，根据需要调整）
        pcd.transform([[1, 0, 0, 0], [0, -1, 0, 0], [0, 0, -1, 0], [0, 0, 0, 1]])
        
        # 保存点云到文件
        o3d.io.write_point_cloud(path, pcd)
        print(f"{cloud_type.capitalize()} point cloud saved successfully at {path}")

    @staticmethod
    def photo_capture(settings, depth_image=None, infrared_image=None, color_image=None, depth_intrinsics=None):
        """根据设置捕获图像并保存"""
        # 确定 history 文件夹的路径
        history_path = os.path.join(os.getcwd(), "history")
        if not os.path.exists(history_path):
            os.makedirs(history_path)

        # 创建以当前时间命名的文件夹
        now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        session_path = os.path.join(history_path, now)
        os.makedirs(session_path)

        # 根据设置保存深度图像
        if settings.get('depth', {}).get('enabled') and depth_image is not None:
            depth_image_path = os.path.join(session_path, "depth.png")
            ImageSaver.save_image(depth_image, depth_image_path, "Depth")
            # 保存点云文件
            if depth_image is not None and depth_intrinsics is not None:
                ply_path = os.path.join(session_path, "depth.ply")
                ImageSaver.save_point_cloud(depth_image, depth_intrinsics, ply_path, "Depth")

        # 根据设置保存红外线图像
        if settings.get('infrared', {}).get('enabled') and infrared_image is not None:
            infrared_image_path = os.path.join(session_path, "infrared.png")
            ImageSaver.save_image(infrared_image, infrared_image_path, "Infrared")

        # 根据设置保存彩色图像
        if settings.get('color', {}).get('enabled') and color_image is not None:
            color_image_path = os.path.join(session_path, "color.png")
            ImageSaver.save_image(color_image, color_image_path, "Color")
