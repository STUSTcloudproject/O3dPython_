import os
import cv2
import numpy as np
import open3d as o3d

class ImageSaver:
    def __init__(self):
        # 为每种图像数据类型提供一个容器
        self.depth_images = []  # 存储深度图像数据
        self.infrared_images = []  # 存储红外线图像数据
        self.color_images = []  # 存储彩色图像数据
        # 设置基础路径属性
        self.base_path = os.path.join(os.getcwd(), "history")
        # 初始化路径和目录
        self.initialize_paths()

    def initialize_paths(self):
        """
        初始化基础路径和创建必要的目录结构。
        """
        os.makedirs(self.base_path, exist_ok=True)
        streams = ['depth', 'infrared', 'color', 'depth_ply']
        for stream in streams:
            os.makedirs(os.path.join(self.base_path, stream), exist_ok=True)

    def photo_capture(self, settings, depth_image=None, infrared_image=None, color_image=None, depth_intrinsics=None, time=None):
        """
        根据设置将图像数据存储到相应的容器中。
        """
        if settings.get('depth', {}).get('enabled') and depth_image is not None:
            self.depth_images.append((depth_image, depth_intrinsics, time))

        if settings.get('infrared', {}).get('enabled') and infrared_image is not None:
            self.infrared_images.append((infrared_image, time))

        if settings.get('color', {}).get('enabled') and color_image is not None:
            self.color_images.append((color_image, time))

    def save_all_images(self):
        """
        从容器中读出所有数据并保存为图片，使用内部设定的路径。
        """
        self.save_images(self.depth_images, 'depth')
        self.save_images(self.infrared_images, 'infrared')
        self.save_images(self.color_images, 'color')
        self.clear_containers()

    def save_images(self, image_list, image_type):
        """
        遍历指定类型的图像列表，并保存图像到指定的内部路径。
        """
        type_path = os.path.join(self.base_path, image_type)
        for idx, data in enumerate(image_list):
            time = data[-1]
            file_path = os.path.join(type_path, f"{time}.png")
            if image_type == 'depth':
                image, depth_intrinsics, _ = data
                self.save_depth_image(image, file_path)
                if depth_intrinsics is not None:
                    ply_path = os.path.join(self.base_path, "depth_ply", f"{time}.ply")
                    self.save_point_cloud(image, depth_intrinsics, ply_path)
            elif image_type == 'color':
                image, _ = data
                cv2.imwrite(file_path, cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
            else:  # infrared
                image, _ = data
                cv2.imwrite(file_path, image)
            print(f"{image_type.capitalize()} image saved successfully at {file_path}")

    def save_depth_image(self, depth_image, path):
        """
        保存深度图像。
        """
        cv2.imwrite(path, depth_image)

    def save_point_cloud(self, depth_image, depth_intrinsics, path):
        """
        使用open3d将深度图像转换为点云并保存。
        """
        depth_o3d = o3d.geometry.Image(depth_image)
        intrinsics_o3d = o3d.camera.PinholeCameraIntrinsic(depth_intrinsics.width, depth_intrinsics.height, depth_intrinsics.fx, depth_intrinsics.fy, depth_intrinsics.ppx, depth_intrinsics.ppy)
        pcd = o3d.geometry.PointCloud.create_from_depth_image(depth_o3d, intrinsics_o3d)
        pcd.transform([[1, 0, 0, 0], [0, -1, 0, 0], [0, 0, -1, 0], [0, 0, 0, 1]])
        o3d.io.write_point_cloud(path, pcd)
        print(f"Point cloud saved successfully at {path}")

    def clear_containers(self):
        """
        清空所有容器。
        """
        self.depth_images.clear()
        self.infrared_images.clear()
        self.color_images.clear()

# 注意：此代码示例仅供参考，需要根据您的具体应用环境进行适当调整。
