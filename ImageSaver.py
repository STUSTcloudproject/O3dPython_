import os
import cv2
import datetime
import open3d as o3d
import numpy as np
from PIL import Image
import numpy as np
import pyrealsense2 as rs

class ImageSaver:
    @staticmethod
    def save_image(image, path, image_type='photo'):
        """將圖像保存為文件"""
        if isinstance(image, np.ndarray):
            # 如果圖像是 NumPy 數組，先轉換為 PIL 圖像
            image = Image.fromarray(image)
        try:
            # 保存圖像到指定路徑
            image.save(path)
            print(f"{image_type.capitalize()} image saved successfully at {path}")
        except Exception as e:
            print(f"Failed to save {image_type} image at {path}: {e}")

    @staticmethod
    def save_point_cloud(depth_image, depth_intrinsics, path, cloud_type):
        """使用open3d將深度圖像轉換為點雲並保存"""
        if depth_image is None:
            print("Depth image is None, cannot save point cloud.")
            return
        
        # 將深度圖像轉換為Open3D的圖像對象
        depth_o3d = o3d.geometry.Image(depth_image)
        
        # 創建Open3D的內參對象
        intrinsics_o3d = o3d.camera.PinholeCameraIntrinsic(
            depth_intrinsics.width,
            depth_intrinsics.height,
            depth_intrinsics.fx,
            depth_intrinsics.fy,
            depth_intrinsics.ppx,
            depth_intrinsics.ppy)
        
        # 從深度圖像創建點雲
        pcd = o3d.geometry.PointCloud.create_from_depth_image(
            depth_o3d, intrinsics_o3d)
        
        # 調整點雲的方向（這一步是可選的，根據需要調整）
        pcd.transform([[1, 0, 0, 0], [0, -1, 0, 0], [0, 0, -1, 0], [0, 0, 0, 1]])
        
        # 保存點雲到文件
        o3d.io.write_point_cloud(path, pcd)
        print(f"{cloud_type.capitalize()} point cloud saved successfully at {path}")

    @staticmethod
    def photo_capture(settings, depth_image=None, infrared_image=None, color_image=None, depth_intrinsics=None):
        """根據設置捕獲圖像並保存"""
        # 確定 history 文件夾的路徑
        history_path = os.path.join(os.getcwd(), "history")
        # 如果 history 目錄不存在，則創建
        os.makedirs(history_path, exist_ok=True)

        # 創建以當前時間命名的文件夾
        now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        session_path = os.path.join(history_path, now)
        # 使用 exist_ok=True 參數來避免 FileExistsError
        os.makedirs(session_path, exist_ok=True)

        # 根據設置保存深度圖像
        if settings.get('depth', {}).get('enabled') and depth_image is not None:
            depth_image_path = os.path.join(session_path, "depth.png")
            ImageSaver.save_image(depth_image, depth_image_path, "Depth")
            # 保存點雲文件
            if depth_image is not None and depth_intrinsics is not None:
                ply_path = os.path.join(session_path, "depth.ply")
                ImageSaver.save_point_cloud(depth_image, depth_intrinsics, ply_path, "Depth")

        # 根據設置保存紅外線圖像
        if settings.get('infrared', {}).get('enabled') and infrared_image is not None:
            infrared_image_path = os.path.join(session_path, "infrared.png")
            ImageSaver.save_image(infrared_image, infrared_image_path, "Infrared")

        # 根據設置保存彩色圖像
        if settings.get('color', {}).get('enabled') and color_image is not None:
            color_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2RGB)
            color_image_path = os.path.join(session_path, "color.png")
            ImageSaver.save_image(color_image, color_image_path, "Color")
