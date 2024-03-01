import pyrealsense2 as rs

def list_realsense_devices():
    # 創建一個context對象，這是管理RealSense硬件連接的起點
    context = rs.context()
    # 獲取系統上連接的設備列表
    device_list = context.query_devices()
    if len(device_list) == 0:
        print("No RealSense devices were found.")
    else:
        print("Found the following RealSense devices:")
        for i, device in enumerate(device_list):
            # 獲取設備的名稱和序列號
            dev_name = device.get_info(rs.camera_info.name)
            serial_number = device.get_info(rs.camera_info.serial_number)
            print(f"Device {i}: {dev_name}, Serial Number: {serial_number}")

# 調用函數列出設備
list_realsense_devices()
