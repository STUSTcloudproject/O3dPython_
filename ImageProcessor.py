import cv2
from PIL import Image, ImageTk

class ImageProcessor:
    @staticmethod
    def _resize_image(image, target_width, target_height):
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

    @staticmethod
    def _process_image(image_data, color_mode, target_width, target_height):
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
        resized_image = ImageProcessor._resize_image(pil_image, target_width, target_height)
        image_colormap = ImageTk.PhotoImage(image=resized_image)
        return image_colormap
    
    @staticmethod
    def process_image_by_type(image_data, stream_type, target_width, target_height):
        """根据流类型选择正确的图像处理方法"""
        if stream_type == "depth":
            return ImageProcessor.process_and_resize_depth_image(image_data, target_width, target_height)
        elif stream_type == "infrared":
            return ImageProcessor.process_and_resize_infrared_image(image_data, target_width, target_height)
        elif stream_type == "color":
            return ImageProcessor.process_and_resize_color_image(image_data, target_width, target_height)
        else:
            return None
        
    @staticmethod
    def calculate_target_size(window_height, right_panel_width):
        # 根据4:3的比例计算目标高度和宽度，确保图像不会被拉伸或压缩
        target_height_per_image = window_height // 3
        target_width = right_panel_width

        # 保持图像的4:3长宽比，同时确保图像能够在分配的空间中最大化显示
        target_height = min(target_height_per_image, target_width * 3 // 4)
        target_width = target_height * 4 // 3

        return target_width, target_height
    
    @staticmethod
    def select_image(settings, window_height, right_panel_width, rs_device, black_image):
        target_width, target_height = ImageProcessor.calculate_target_size(window_height, right_panel_width)
        images = []
        for stream_type in ['depth', 'infrared', 'color']:
            if settings.is_stream_enabled(stream_type):
                image_data = getattr(rs_device, f"get_{stream_type}_image")()
                target_image = ImageProcessor.process_image_by_type(image_data, stream_type, target_width, target_height)
            else:
                target_image = black_image
            images.append(target_image)
        return images
        

    @staticmethod
    def process_and_resize_color_image(color_image, target_width, target_height):
        return ImageProcessor._process_image(color_image, cv2.COLOR_BGR2RGB, target_width, target_height)

    @staticmethod
    def process_and_resize_depth_image(depth_image, target_width, target_height):
        return ImageProcessor._process_image(depth_image, "depth", target_width, target_height)

    @staticmethod
    def process_and_resize_infrared_image(infrared_image, target_width, target_height):
        return ImageProcessor._process_image(infrared_image, cv2.COLOR_GRAY2RGB, target_width, target_height)
