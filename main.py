import GUI
from PIL import Image, ImageTk

settings = {
    "depth": {"enabled": False, "resolution": "320 x 240"},
    "infrared": {"enabled": False, "resolution": "640 x 360"},
    "color": {"enabled": False, "resolution": "320 x 240"}
}

def update_image(is_on,stream_type):
    if is_on:
        if stream_type == "depth":
            app.set_depth_image(red_image)
        elif stream_type == "infrared":
            app.set_infrared_image(red_image)
        elif stream_type == "color":
            app.set_color_image(red_image)
    else:
        if stream_type == "depth":
            app.set_depth_image(black_image)
        elif stream_type == "infrared":
            app.set_infrared_image(black_image)
        elif stream_type == "color":
            app.set_color_image(black_image)    

def toggle_switch_changed(is_on, pane):
    try:
        combo_value = pane.sub_frame.combo.get()
        stream_type = pane.title_label['text'].split()[0].lower()     
        if stream_type in settings:
            settings[stream_type]["enabled"] = is_on
            settings[stream_type]["resolution"] = combo_value
        update_image(is_on,stream_type)
        print(settings)

    except Exception as e:
        print(f"An error occurred: {e}")

def close_program():    
    app.destroy()  # 关闭 Tkinter 窗口

app = GUI.App(toggle_callback=toggle_switch_changed)
app.protocol("WM_DELETE_WINDOW", close_program)
red = Image.new('RGB', (160, 120), color = 'red')
black = Image.new('RGB', (160, 120), color = 'black')

red_image = ImageTk.PhotoImage(red)
black_image = ImageTk.PhotoImage(black)
app.mainloop()