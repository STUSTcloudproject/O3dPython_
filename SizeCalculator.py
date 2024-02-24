class SizeCalculator:
    @staticmethod
    def calculate_target_size(window_height, right_panel_width):
        # 根据4:3的比例计算目标高度和宽度，确保图像不会被拉伸或压缩
        target_height_per_image = window_height // 3
        target_width = right_panel_width

        # 保持图像的4:3长宽比，同时确保图像能够在分配的空间中最大化显示
        target_height = min(target_height_per_image, target_width * 3 // 4)
        target_width = target_height * 4 // 3

        return target_width, target_height
