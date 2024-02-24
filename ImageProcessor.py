import cv2
from PIL import Image, ImageTk

class ImageProcessor:
    def __init__(self):
        pass  # 不再需要初始化目标宽度和高度

    def _resize_image(self, image, target_width, target_height):
        """根据传入的目标宽度和高度调整图像尺寸，保持图像原始比例。"""
        target_ratio = target_width / target_height
        original_ratio = image.width / image.height

        if target_ratio > original_ratio:
            scale = target_height / image.height
        else:
            scale = target_width / image.width

        new_width = int(image.width * scale)
        new_height = int(image.height * scale)

        resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        return resized_image

    def _process_image(self, image_data, color_mode, target_width, target_height):
        """通用图像处理方法，包括颜色转换和尺寸调整，根据传入的宽度和高度调整图像大小。"""
        if image_data is None:
            return None

        if color_mode == cv2.COLOR_BGR2RGB:  # 彩色图像
            image_colormap = cv2.cvtColor(image_data, color_mode)
        elif color_mode == "depth":  # 深度图像
            image_colormap = cv2.applyColorMap(cv2.convertScaleAbs(image_data, alpha=0.03), cv2.COLORMAP_JET)
        else:  # 红外图像
            image_colormap = cv2.cvtColor(image_data, cv2.COLOR_GRAY2RGB)

        pil_image = Image.fromarray(image_colormap)
        resized_image = self._resize_image(pil_image, target_width, target_height)
        image_colormap = ImageTk.PhotoImage(image=resized_image)
        return image_colormap

    # 对于彩色、深度和红外图像处理方法，添加目标宽度和高度参数
    def process_and_resize_color_image(self, color_image, target_width, target_height):
        return self._process_image(color_image, cv2.COLOR_BGR2RGB, target_width, target_height)

    def process_and_resize_depth_image(self, depth_image, target_width, target_height):
        return self._process_image(depth_image, "depth", target_width, target_height)

    def process_and_resize_infrared_image(self, infrared_image, target_width, target_height):
        return self._process_image(infrared_image, cv2.COLOR_GRAY2RGB, target_width, target_height)
