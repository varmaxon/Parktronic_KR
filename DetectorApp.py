from tkinter import *
from tkinter import messagebox
import customtkinter as ctk
from tkinter import filedialog
from PIL import Image, ImageTk

from Detector import Detector
from DefaultParams import DefaultParams


class DetectorApp:
    def __init__(self):
        self.epsilon_to_find_rect = 20
        self.__buffer = []

        self.app = ctk.CTk()
        self.app.title("Parktronic (Admin)")
        self.app.geometry(str(int(self.app.winfo_screenwidth() * 0.7)) + "x" +
                          str(int(self.app.winfo_screenheight() * 0.63)))

        self.detector = Detector()

        # Main Menu

        main_menu = Menu(self.app)
        self.app.config(menu=main_menu)
        self.__make_menu(main_menu)

        # LOGO

        self.canvas_logo = Canvas(self.app, width=451, height=145, background='#ebebeb', highlightthickness=0)
        image = Image.open("Images/parktronic_logo_transformed.png")
        photo = ImageTk.PhotoImage(image)
        self.canvas_logo.create_image(0, 0, anchor='nw', image=photo)
        self.canvas_logo.grid(row=0, column=0, pady=20, columnspan=3, rowspan=3)

        # PARAMS

        text_settings = ctk.StringVar(value="НАСТРОЙКИ")
        text_yolo_path = ctk.StringVar(value="📌 Укажите путь к папке yolo:                              ")

        text_nearby_boxes = ctk.StringVar(value="⚙ Число смежных боксов")
        text_e_cleaning_similar = ctk.StringVar(value="⚙ Степень смещения при чистке")
        text_dif_points = ctk.StringVar(value="⚙ Мин. расстояние для добавления бокса")
        text_e_iou = ctk.StringVar(value="⚙ Порог пересечения площадей (IoU)")
        text_size_block_frames = ctk.StringVar(value="⚙ Число кадров в блоке обработки")

        self.yolo_path = ctk.StringVar(value=DefaultParams.params['yolo_path'])

        label0 = ctk.CTkLabel(master=self.app, textvariable=text_settings, width=120, height=25, corner_radius=8, font=("Courier", 24))
        label0.grid(row=3, column=0, padx=10, pady=(20, 5), columnspan=3)

        label1 = ctk.CTkLabel(master=self.app, textvariable=text_yolo_path, width=200, height=25, corner_radius=8, font=("Courser", 16))
        label1.grid(row=4, column=0, columnspan=1, padx=(10, 0), pady=5)
        self.label_yolo_path = ctk.CTkLabel(master=self.app, textvariable=self.yolo_path, width=350, height=25,
                                            fg_color=("white", "gray75"), corner_radius=8)
        self.label_yolo_path.grid(row=5, column=0, padx=(20, 0), columnspan=2, pady=(5, 10))

        btn_open_path = ctk.CTkButton(master=self.app, text="Выбрать 📂", width=60, height=25, command=self.__open_dir)
        btn_open_path.grid(row=5, column=2, padx=10, pady=(5, 10))

        label_size_block_frames = ctk.CTkLabel(master=self.app, textvariable=text_size_block_frames, width=200, height=25, corner_radius=8, font=("Courser", 16))
        label_size_block_frames.grid(row=10, column=0, sticky=W, padx=(10, 0), pady=5)
        self.spinbox_size_block_frames = Spinbox(master=self.app, from_=0, to=1000, increment=1, font=("Courser", 14), width=10, textvariable=DoubleVar(value=DefaultParams.params['size_block_frames']))
        self.spinbox_size_block_frames.grid(row=10, column=2, columnspan=1, sticky=NW, padx=(10, 0), pady=5)

        label_nearby_boxes = ctk.CTkLabel(master=self.app, textvariable=text_nearby_boxes, width=200, height=25, corner_radius=8, font=("Courser", 16))
        label_nearby_boxes.grid(row=6, column=0, sticky=NW, padx=(10, 0), pady=5)

        self.spinbox_nearby_boxes = Spinbox(master=self.app, from_=1, to=int(self.spinbox_size_block_frames.get()), increment=1, font=("Courser", 14), width=10, textvariable=DoubleVar(value=DefaultParams.params['len_nearby_boxes']))
        self.spinbox_nearby_boxes.grid(row=6, column=2, columnspan=1, sticky=NW, padx=(10, 0), pady=5)

        label_e_cleaning_similar = ctk.CTkLabel(master=self.app, textvariable=text_e_cleaning_similar, width=200, height=25, corner_radius=8, font=("Courser", 16))
        label_e_cleaning_similar.grid(row=7, column=0, sticky=NW, padx=(10, 0), pady=5)
        self.spinbox_e_cleaning_similar = Spinbox(master=self.app, from_=0, to=100, increment=1, font=("Courser", 14), width=10, textvariable=DoubleVar(value=DefaultParams.params['e_cleaning_similar']))
        self.spinbox_e_cleaning_similar.grid(row=7, column=2, columnspan=1, sticky=NW, padx=(10, 0), pady=5)

        label_dif_points = ctk.CTkLabel(master=self.app, textvariable=text_dif_points, width=200, height=25, corner_radius=8, font=("Courser", 16))
        label_dif_points.grid(row=8, column=0, sticky=NW, padx=(10, 0), pady=5)
        self.spinbox_dif_points = Spinbox(master=self.app, from_=0, to=10, increment=1, font=("Courser", 14), width=10, textvariable=DoubleVar(value=DefaultParams.params['e_dif_points']))
        self.spinbox_dif_points.grid(row=8, column=2, columnspan=1, sticky=NW, padx=(10, 0), pady=5)

        label_iou = ctk.CTkLabel(master=self.app, textvariable=text_e_iou, width=200, height=25, corner_radius=8, font=("Courser", 16))
        label_iou.grid(row=9, column=0, sticky=W, padx=(10, 0), pady=5)
        self.spinbox_iou = Spinbox(master=self.app, from_=0, to=1, increment=0.001, font=("Courser", 14), width=10, textvariable=DoubleVar(value=DefaultParams.params['e_iou']))
        self.spinbox_iou.grid(row=9, column=2, columnspan=1, sticky=NW, padx=(10, 0), pady=5)

        btn_default_settings = ctk.CTkButton(master=self.app, width=50, height=32, border_width=0, corner_radius=8, text="Сброс параметров", command=self.__set_default_settings)
        btn_default_settings.grid(row=21, column=0, padx=(10, 100), pady=10)

        # RECOGNITION BUTTON

        run_btn = ctk.CTkButton(master=self.app, width=30, height=32, border_width=0, corner_radius=8,
                                text=" ▶ ", command=self.__run_detect)
        run_btn.grid(row=21, column=11, padx=(10, 0), pady=10)

        # Canvas & Image

        self.canvas = Canvas(self.app, width=640, height=480, highlightthickness=1, highlightbackground="black")
        self.canvas.grid(row=1, column=3, padx=10, pady=10, rowspan=20, columnspan=11)
        self.canvas.create_text(640//2, 480//2, font="Verdana 20 normal roman",
                                text="🎬\n\nВыберите или добавьте камеру", justify='center')

        # Combobox CAMERAS

        self.cameras_list = []
        camera_default = ctk.StringVar(value="Выберите камеру")

        self.combobox_camera = ctk.CTkComboBox(master=self.app, values=self.cameras_list,
                                               command=self.__choose_camera,
                                               variable=camera_default, state='readonly',
                                               width=(int(self.canvas.winfo_reqwidth() * 0.67)))

        self.combobox_camera.grid(row=0, column=3, padx=(0, 0), pady=(20, 10), columnspan=9)
        self.combobox_camera.bind("<<ComboboxSelected>>", self.__choose_camera)

        # ADD CAMERA & DEL CAMERA

        add_button = ctk.CTkButton(master=self.app, width=30, height=32, border_width=0, corner_radius=8,
                                   text="➕", command=self.__button_add)
        add_button.grid(row=0, column=11, padx=2, pady=(20, 10))
        del_button = ctk.CTkButton(master=self.app, width=30, height=32, border_width=0, corner_radius=8,
                                   text="➖", command=self.__button_del)
        del_button.grid(row=0, column=12, padx=2, pady=(20, 10))

        # RUN BUTTON

        back_button = ctk.CTkButton(master=self.app, width=100, height=32, border_width=0, corner_radius=8,
                                    text="Назад", command=self.__backward)
        back_button.grid(row=21, column=3, padx=(40, 0), pady=10)

        save_button = ctk.CTkButton(master=self.app, width=200, height=32, border_width=0, corner_radius=8,
                                    text="Сохранить", command=self.__save_state)
        save_button.grid(row=21, column=4, padx=(20, 20), pady=10)

        clear_button = ctk.CTkButton(master=self.app, width=100, height=32, border_width=0, corner_radius=8,
                                     text="Сброс", command=self.__clear_buffer)
        clear_button.grid(row=21, column=5, pady=10)

        self.canvas.bind("<Button-1>", self.__on_wasd)

        self.app.mainloop()

    def __make_menu(self, main_menu):
        main_menu.add_command(label=" Запуск", command=self.__run)

    def __run(self):
        try:
            self.detector.run()
            self.app.withdraw()
            print("\nRunning...\n")
        except:
            messagebox.showwarning("Предупреждение", "Отсутствуют добавленные камеры")

    def __choose_camera(self, choice=None, flag=True):
        if flag and (choice is None):
            raise Exception("Неизвестная ошибка в __choose_camera")

        if choice is None:
            choice = self.combobox_camera.get()

        choice = choice.split(' | ')
        choice_parking = choice[0].split()[-1]
        choice_camera = choice[1].split()[-1]

        required_parking = self.detector.parking_list[choice_parking]
        required_view = required_parking.parking_views[choice_camera]
        frame = required_view.get_current_frame()

        if flag:
            self.image = self.__photo_image(frame)
            self.canvas = Canvas(self.app, width=self.image.width(), height=self.image.height(), highlightthickness=1, highlightbackground="black")
            self.canvas.grid(row=1, column=3, padx=10, pady=10, rowspan=20, columnspan=11)
            self.canvas.create_image(self.image.width() // 2, self.image.height() // 2, image=self.image, anchor="center")
            self.canvas.bind("<Button-1>", self.__on_wasd)

            self.__buffer = required_view.places_coordinates
            self.__redraw()

            if not required_view.hyperparams.params_is_none():
                self.yolo_path.set(required_view.hyperparams.get_yolo_path())
                self.spinbox_nearby_boxes.config(textvariable=DoubleVar(value=required_view.hyperparams.get_len_nearby_boxes()))
                self.spinbox_e_cleaning_similar.config(textvariable=DoubleVar(value=required_view.hyperparams.get_e_cleaning_similar()))
                self.spinbox_dif_points.config(textvariable=DoubleVar(value=required_view.hyperparams.get_e_dif_points()))
                self.spinbox_iou.config(textvariable=DoubleVar(value=required_view.hyperparams.get_e_iou()))
                self.spinbox_size_block_frames.config(textvariable=DoubleVar(value=required_view.hyperparams.get_size_block_frames()))

        if not flag:
            required_view.places_coordinates = self.__buffer

    def __button_add(self):
        def save_new_camera():
            parking_num = entry_add_1.get()
            camera_num = entry_add_2.get()
            camera_url = entry_add_3.get()
            if len(parking_num) > 0 and len(camera_num) > 0 and len(camera_url) > 0:
                self.detector.cmd_add_camera([parking_num, camera_num, camera_url])
                str_set_new_camera = f"Parking {parking_num} | " \
                                     f"Camera {camera_num} | " \
                                     f"URL {camera_url}"
                flag_len = len(self.cameras_list)
                self.cameras_list = []
                for key, value in self.detector.parking_list.items():
                    new_camera_lst = self.detector.parking_list[key].print_list_cameras(key)
                    for item in new_camera_lst:
                        new_camera_str = f"Parking {item[0]} | "\
                                         f"Camera {item[1]} | "\
                                         f"URL {item[4]}"
                        self.cameras_list.append(new_camera_str)
                        self.combobox_camera.configure(values=self.cameras_list, variable="Выберите камеру")
                    if len(self.cameras_list) - flag_len == 1:
                        messagebox.showinfo("Успешно", "Камера добавлена успешно")
                        add_window.destroy()
                        self.combobox_camera.set(str_set_new_camera)
                        self.__choose_camera(choice=str_set_new_camera)
                    elif len(self.cameras_list) - flag_len == 0:
                        messagebox.showwarning("Предупреждение", "Камера с такими параметрами уже существует")
                    else:
                        messagebox.showerror("Ошибка", "Неизвестная ошибка при добавлении камеры")
            else:
                messagebox.showwarning("Предупреждение", "Заполните все поля")

        add_window = ctk.CTk()
        add_window.title("Новая камера")
        add_window.geometry("250x250")

        label_add_1 = ctk.CTkLabel(master=add_window, text="Параметры камеры", width=120, height=25,
                                   fg_color=("white", "gray75"), corner_radius=8)
        label_add_1.grid(padx=10, pady=10, row=0, column=0)
        add_window.grid_columnconfigure(0, weight=1)

        val1 = StringVar(add_window, value=str(DefaultParams.params['parking_number']))
        val2 = StringVar(add_window, value=str(DefaultParams.params['camera_number']))
        val3 = StringVar(add_window, value=DefaultParams.params['camera_url'])

        entry_add_1 = ctk.CTkEntry(master=add_window, placeholder_text="Введите номер парковки", width=200, height=25,
                                   border_width=2, corner_radius=10, textvariable=val1)
        entry_add_1.grid(padx=10, pady=10, row=1, column=0)

        entry_add_2 = ctk.CTkEntry(master=add_window, placeholder_text="Введите номер камеры", width=200, height=25,
                                   border_width=2, corner_radius=10, textvariable=val2)
        entry_add_2.grid(padx=10, pady=10, row=2, column=0)

        entry_add_3 = ctk.CTkEntry(master=add_window, placeholder_text="Введите URL камеры", width=200, height=25,
                                   border_width=2, corner_radius=10, textvariable=val3)
        entry_add_3.grid(padx=10, pady=10, row=3, column=0)

        button = ctk.CTkButton(master=add_window, width=120, height=32, border_width=0, corner_radius=8,
                               text="Добавить", command=save_new_camera)
        button.grid(padx=10, pady=10, row=4, column=0)

        add_window.mainloop()

    def __button_del(self):
        def delete_camera():
            parking_num = entry_add_1.get()
            camera_num = entry_add_2.get()
            if len(parking_num) > 0 and len(camera_num) > 0:
                self.detector.cmd_del_camera([parking_num, camera_num])
                flag_len = len(self.cameras_list)
                self.cameras_list = []
                for key, value in self.detector.parking_list.items():
                    new_camera_lst = self.detector.parking_list[key].print_list_cameras(key)
                    if len(new_camera_lst) == 0:
                        camera_default = ctk.StringVar(value="Добавьте или выберите камеру")
                        self.combobox_camera.configure(values=[], variable=camera_default)
                    else:
                        for item in new_camera_lst:
                            new_camera_str = f"Parking {item[0]} | "\
                                             f"Camera {item[1]} | "\
                                             f"URL {item[4]}"
                            self.cameras_list.append(new_camera_str)
                            self.combobox_camera.configure(values=self.cameras_list)

                    if len(self.cameras_list) - flag_len == -1:
                        messagebox.showinfo("Успешно", "Камера удалена успешно")
                        add_window.destroy()
                    elif len(self.cameras_list) - flag_len == 0:
                        messagebox.showwarning("Предупреждение", "Камера с такими параметрами не найдена")
                    else:
                        messagebox.showerror("Ошибка", "Неизвестная ошибка при удалении камеры")

            else:
                messagebox.showwarning("Предупреждение", "Заполните все поля")

        add_window = ctk.CTk()
        add_window.title("Удаление камеры")
        add_window.geometry("250x250")

        label_add_1 = ctk.CTkLabel(master=add_window, text="Параметры камеры", width=120, height=25,
                                   fg_color=("white", "gray75"), corner_radius=8)
        label_add_1.grid(padx=10, pady=10, row=0, column=0)
        add_window.grid_columnconfigure(0, weight=1)

        val1 = StringVar(add_window, value="1")
        val2 = StringVar(add_window, value="5")

        entry_add_1 = ctk.CTkEntry(master=add_window, placeholder_text="Введите номер парковки", width=200, height=25,
                                   border_width=2, corner_radius=10)  # textvariable=val1
        entry_add_1.grid(padx=10, pady=10, row=1, column=0)

        entry_add_2 = ctk.CTkEntry(master=add_window, placeholder_text="Введите номер камеры", width=200, height=25,
                                   border_width=2, corner_radius=10)  # textvariable=val2
        entry_add_2.grid(padx=10, pady=10, row=2, column=0)

        button = ctk.CTkButton(master=add_window, width=120, height=32, border_width=0, corner_radius=8,
                               text="Удалить", command=delete_camera)
        button.grid(padx=10, pady=10, row=4, column=0)

        add_window.mainloop()

    def __run_detect(self):
        if self.combobox_camera.get() != "Выберите камеру":
            camera_str = self.combobox_camera.get().split(' | ')
            parking_num = camera_str[0].split()[-1]
            parking_view = camera_str[1].split()[-1]
            required_parking = self.detector.parking_list[parking_num]
            required_view = required_parking.parking_views[parking_view]
            if required_view.hyperparams.params_is_none():
                messagebox.showwarning("Предупреждение", "Установите и сохраните параметры")
            else:
                self.app.withdraw()
                print(required_view.run_view_recognition(fl_show=True)[0])
                self.app.deiconify()

        else:
            messagebox.showwarning("Предупреждение", "Выберите настраиваемую камеру")
        # self.app.destroy()

    def __redraw(self):
        self.canvas.create_image(self.image.width() // 2, self.image.height() // 2, image=self.image, anchor="center")
        for point in self.__buffer:
            self.canvas.create_rectangle(point[0] - 5, point[1] - 5, point[0] + 5, point[1] + 5, fill='green')

    def __backward(self):
        if len(self.__buffer) > 0:
            self.__buffer.pop()
            self.__redraw()

    def __save_state(self):
        if self.combobox_camera.get() != "Выберите камеру" and len(self.cameras_list) > 0:
            camera_str = self.combobox_camera.get().split(' | ')
            parking_num = camera_str[0].split()[-1]
            parking_view = camera_str[1].split()[-1]
            required_parking = self.detector.parking_list[parking_num]
            required_view = required_parking.parking_views[parking_view]

            required_view.hyperparams.set_params(self.yolo_path.get(),
                                                 int(float(self.spinbox_nearby_boxes.get())),
                                                 int(float(self.spinbox_e_cleaning_similar.get())),
                                                 int(float(self.spinbox_dif_points.get())),
                                                 float(self.spinbox_iou.get()),
                                                 int(float(self.spinbox_size_block_frames.get())))

            if len(self.__buffer) == 0:
                required_view.places_coordinates = []
            self.__clear_buffer()

        else:
            messagebox.showwarning("Предупреждение", "Выберите настраиваемую камеру")

    def __clear_buffer(self):
        if len(self.cameras_list) > 0:
            self.__buffer = []
            self.__redraw()
        else:
            messagebox.showwarning("Предупреждение", "Выберите настраиваемую камеру")

    def __save_coordinates(self):
        self.__choose_camera(flag=False)

    def __set_default_settings(self):
        self.yolo_path.set(DefaultParams.params['yolo_path'])
        self.spinbox_nearby_boxes.config(textvariable=DoubleVar(value=DefaultParams.params['len_nearby_boxes']))
        self.spinbox_e_cleaning_similar.config(textvariable=DoubleVar(value=DefaultParams.params['e_cleaning_similar']))
        self.spinbox_dif_points.config(textvariable=DoubleVar(value=DefaultParams.params['e_dif_points']))
        self.spinbox_iou.config(textvariable=DoubleVar(value=DefaultParams.params['e_iou']))
        self.spinbox_size_block_frames.config(textvariable=DoubleVar(value=DefaultParams.params['size_block_frames']))

    @staticmethod
    def __photo_image(img):
        h, w = img.shape[:2]
        data = f'P6 {w} {h} 255 '.encode() + img[..., ::-1].tobytes()
        return PhotoImage(width=w, height=h, data=data, format='PPM')

    def __on_wasd(self, event):
        if len(self.cameras_list) > 0:
            fl = True
            for item in self.__buffer:
                if abs(item[0] - event.x) < self.epsilon_to_find_rect and \
                   abs(item[1] - event.y) < self.epsilon_to_find_rect:
                    fl = False
                    break
            if fl:
                self.canvas.create_rectangle(event.x - 5, event.y - 5, event.x + 5, event.y + 5, fill='green')
                self.__buffer.append([event.x, event.y])

    def __open_dir(self):
        self.app.yolo_path = filedialog.askdirectory(initialdir="C:/", title='Выбрать')
        self.yolo_path.set(self.app.yolo_path)
