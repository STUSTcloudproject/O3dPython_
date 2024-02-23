import GUI
from PIL import Image, ImageTk
import threading
from tkinter import messagebox

class MainApp:
    def __init__(self):
        self.settings_lock = threading.Lock()  # 用于同步访问settings的锁
        self.settings = {
            "depth": {"enabled": False, "resolution": "320 x 240"},
            "infrared": {"enabled": False, "resolution": "640 x 360"},
            "color": {"enabled": False, "resolution": "320 x 240"},
        }
        self.app = GUI.App(toggle_callback=self.toggle_switch_changed)
        self.app.protocol("WM_DELETE_WINDOW", self.close_program)

        # 创建图像占位符
        self.create_image_placeholders()

        # 启动后台线程来监视settings并更新GUI
        self.update_thread = threading.Thread(target=self.monitor_settings_and_update_gui, daemon=True)
        self.update_thread.start()

    def create_image_placeholders(self):
        # 创建红色和黑色图像作为占位符
        red = Image.new("RGB", (160, 120), "red")
        black = Image.new("RGB", (160, 120), "black")
        self.red_image = ImageTk.PhotoImage(red)
        self.black_image = ImageTk.PhotoImage(black)

    def toggle_switch_changed(self, is_on, pane):
        try:
            combo_value = pane.sub_frame.combo.get()
            stream_type = pane.title_label["text"].strip().lower().replace(" stream", "")
            print("Stream type:", stream_type)
            with self.settings_lock:
                if stream_type in self.settings:
                    self.settings[stream_type]["enabled"] = is_on
                    self.settings[stream_type]["resolution"] = combo_value
                else:
                    print(f"Unrecognized stream type: {stream_type}")
            print(self.settings)
        except Exception as e:
            print(f"An error occurred: {e}")


    def monitor_settings_and_update_gui(self):
        while True:
            with self.settings_lock:
                current_settings = self.settings.copy()
            
            # 使用主线程安全更新GUI
            self.app.after(0, lambda: self.update_gui_based_on_settings(current_settings))
            threading.Event().wait(0.1)  # 检查频率调整为每秒一次

    def update_gui_based_on_settings(self, settings):
        # 根据settings的状态更新GUI
        for stream_type, config in settings.items():
            if config["enabled"]:
                if stream_type == "depth":
                    self.app.set_depth_image(self.red_image)
                elif stream_type == "infrared":
                    self.app.set_infrared_image(self.red_image)
                elif stream_type == "color":
                    self.app.set_color_image(self.red_image)
            else:
                if stream_type == "depth":
                    self.app.set_depth_image(self.black_image)
                elif stream_type == "infrared":
                    self.app.set_infrared_image(self.black_image)
                elif stream_type == "color":
                    self.app.set_color_image(self.black_image)

    def close_program(self):
        self.app.destroy()

    def run(self):
        self.app.mainloop()

if __name__ == '__main__':
    main_app = MainApp()
    main_app.run()
