import cv2
from PIL import Image, ImageTk

class ImageProcessor:
    def __init__(self, target_width=160, target_height=120):
        self.target_width = target_width
        self.target_height = target_height

    def resize_image(self, image):
        """调整图像尺寸以适应设定的目标宽度和高度，保持图像原始比例。"""
        target_ratio = self.target_width / self.target_height
        original_ratio = image.width / image.height

        if target_ratio > original_ratio:
            scale = self.target_height / image.height
        else:
            scale = self.target_width / image.width

        new_width = int(image.width * scale)
        new_height = int(image.height * scale)

        resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        return resized_image

    def process_image(self, image_data, color_mode=cv2.COLOR_BGR2RGB):
        """通用图像处理方法，包括颜色转换和尺寸调整。"""
        if image_data is None:
            return None

        if color_mode == cv2.COLOR_BGR2RGB:  # 彩色图像
            image_colormap = cv2.cvtColor(image_data, color_mode)
        elif color_mode == "depth":  # 深度图像
            image_colormap = cv2.applyColorMap(cv2.convertScaleAbs(image_data, alpha=0.03), cv2.COLORMAP_JET)
        else:  # 红外图像
            image_colormap = cv2.cvtColor(image_data, cv2.COLOR_GRAY2RGB)

        pil_image = Image.fromarray(image_colormap)
        resized_image = self.resize_image(pil_image)
        image_colormap = ImageTk.PhotoImage(image=resized_image)
        return image_colormap

    def process_and_resize_color_image(self, color_image):
        """处理并返回调整尺寸后的彩色图像。"""
        return self.process_image(color_image, cv2.COLOR_BGR2RGB)

    def process_and_resize_depth_image(self, depth_image):
        """处理并返回调整尺寸后的深度图像。"""
        return self.process_image(depth_image, "depth")

    def process_and_resize_infrared_image(self, infrared_image):
        """处理并返回调整尺寸后的红外图像。"""
        return self.process_image(infrared_image, cv2.COLOR_GRAY2RGB)
