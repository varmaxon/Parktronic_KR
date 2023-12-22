import cv2
from Recognizer import Recognizer
# import requests
import json
import base64
import time
from abc import ABC, abstractmethod


class ISpaceInfo(ABC):
    @abstractmethod
    def set(self, status_place, image):
        pass

    @abstractmethod
    def get_image(self):
        pass

    @abstractmethod
    def get_old_status_place(self):
        pass

    @abstractmethod
    def get_new_status_place(self):
        pass


class SpaceInfo(ISpaceInfo):
    def __init__(self):
        self.__old_status_place = []
        self.__new_status_place = []
        self.__image = None

    def set(self, status_place, image):
        self.__old_status_place.clear()
        for item in self.__new_status_place:
            self.__old_status_place.append(item)

        self.__new_status_place.clear()
        self.__new_status_place = status_place
        self.__image = image

    def get_image(self):
        return self.__image

    def get_old_status_place(self):
        return self.__old_status_place

    def get_new_status_place(self):
        return self.__new_status_place


class ICamera(ABC):
    @abstractmethod
    def get_url(self):
        pass

    @abstractmethod
    def get_frame(self):
        pass


class Camera(ICamera):
    def __init__(self, url):
        self.__url = url
        self.capture = cv2.VideoCapture(self.__url)
        self.fl_connection = self.capture.isOpened()
        self.video_shape = {"x": None, "y": None}
        if self.fl_connection:
            self.video_shape["x"] = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.video_shape["y"] = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

    def get_url(self):
        return self.__url

    def get_frame(self):
        if self.fl_connection:
            self.capture = cv2.VideoCapture(self.__url)
            _, img = self.capture.read()
            return img


class IHyperParams(ABC):
    @abstractmethod
    def params_is_none(self):
        pass

    @abstractmethod
    def set_params(self, yolo_path, len_nearby_boxes, e_cleaning_similar, e_dif_points, e_iou, size_block_frames):
        pass

    @abstractmethod
    def get_yolo_path(self):
        pass

    @abstractmethod
    def get_len_nearby_boxes(self):
        pass

    @abstractmethod
    def get_e_cleaning_similar(self):
        pass

    @abstractmethod
    def get_e_dif_points(self):
        pass

    @abstractmethod
    def get_e_iou(self):
        pass

    @abstractmethod
    def get_size_block_frames(self):
        pass


class HyperParams(IHyperParams):
    detect_object = 'car'
    key_press_exit = 27

    def __init__(self):
        self.__yolo_path = None
        self.__len_nearby_boxes = None
        self.__e_cleaning_similar = None
        self.__e_dif_points = None
        self.__e_iou = None
        self.__size_block_frames = None

    def params_is_none(self):
        return None in (self.__yolo_path, self.__len_nearby_boxes, self.__e_cleaning_similar,
                        self.__e_dif_points, self.__e_iou, self.__size_block_frames)

    def set_params(self, yolo_path, len_nearby_boxes, e_cleaning_similar, e_dif_points, e_iou, size_block_frames):
        self.__yolo_path = yolo_path
        self.__len_nearby_boxes = len_nearby_boxes
        self.__e_cleaning_similar = e_cleaning_similar
        self.__e_dif_points = e_dif_points
        self.__e_iou = e_iou
        self.__size_block_frames = size_block_frames

    def get_yolo_path(self):
        return self.__yolo_path

    def get_len_nearby_boxes(self):
        return self.__len_nearby_boxes

    def get_e_cleaning_similar(self):
        return self.__e_cleaning_similar

    def get_e_dif_points(self):
        return self.__e_dif_points

    def get_e_iou(self):
        return self.__e_iou

    def get_size_block_frames(self):
        return self.__size_block_frames


class IParkingView(ABC):
    @abstractmethod
    def get_camera_url(self):
        pass

    @abstractmethod
    def get_current_frame(self):
        pass

    @abstractmethod
    def get_camera_shape(self):
        pass

    @abstractmethod
    def get_connection(self) -> bool:
        pass


class ParkingView(IParkingView):
    def __init__(self, url):
        self.space_info = SpaceInfo()
        self.hyperparams = HyperParams()
        self.camera = Camera(url)
        self.places_coordinates = []
        if self.camera.fl_connection:
            _, frame = self.camera.capture.read()
            # obj = SettingPlaces(frame, [1])
            # self.places_coordinates = obj.places_coordinates

    def get_camera_url(self):
        return self.camera.get_url()

    def get_current_frame(self):
        if self.camera.fl_connection:
            _, frame = self.camera.capture.read()
            return frame

        else:
            return -1

    def __make_result_image(self, arr_points):
        img = self.camera.get_frame()
        # cv2.imshow('Last_frame', img)

        for coordinates in arr_points:
            color = (0, 255, 0)
            if not coordinates[0]:
                color = (0, 0, 255)

            # cv2.circle(img, coordinates[1], 10, color, -1)
            cv2.rectangle(img,
                          [coordinates[1][0] - 10, coordinates[1][1] - 10],
                          [coordinates[1][0] + 10, coordinates[1][1] + 10],
                          color,
                          -1)

        return img

    def run_view_recognition(self, fl_show=False):
        if self.get_connection():
            recognition = Recognizer(url=self.get_camera_url(),
                                     video_shape=self.get_camera_shape(),
                                     marked_coordinates=self.get_camera_places_coordinates(),
                                     hyperparams=self.hyperparams,
                                     fl_show=fl_show)
            if self.hyperparams.get_size_block_frames() is not None:
                recognition.start_video_object_detection(self.hyperparams.get_size_block_frames())
                result_img = self.__make_result_image(recognition.status_place)
                self.space_info.set(recognition.status_place, result_img)
                return recognition.status_place, result_img

            else:
                raise Exception("HyperParams.size_block_frames is NONE")

    def get_camera_shape(self):
        return self.camera.video_shape if self.camera.fl_connection else None

    def get_camera_places_coordinates(self):
        return self.places_coordinates

    def get_connection(self) -> bool:
        return self.camera.fl_connection

    def is_changed_view(self) -> bool:
        return not self.space_info.get_new_status_place() == self.space_info.get_old_status_place()


class Sender:
    @staticmethod
    def send(url, data) -> int:
        # headers = {'content-type': 'application/json'}
        # resp = requests.post(url, headers=headers, data=data)
        # return resp.status_code
        return 200


class IParking(ABC):
    @abstractmethod
    def add_camera(self, camera_args):
        pass

    @abstractmethod
    def delete_camera(self, id_camera):
        pass

    @abstractmethod
    def print_list_cameras(self, parking_key):
        pass

    @abstractmethod
    def run_parking(self):
        pass


class Parking(IParking):
    def __init__(self, parking_args):
        self.mas_space_info = []
        self.parking_views = dict()

        self.add_camera(parking_args)

    def add_camera(self, camera_args):
        id_camera, url = camera_args
        self.parking_views[id_camera] = ParkingView(url)

    def delete_camera(self, id_camera):
        if id_camera in self.parking_views:
            self.parking_views.pop(id_camera)

    def print_list_cameras(self, parking_key):
        result = []
        for key, value in self.parking_views.items():
            result.append([parking_key, key, str(value.get_connection()).upper(),
                           str(value.get_camera_shape()['x']) + "x" + str(value.get_camera_shape()['y']),
                           value.get_camera_url()])
        return result

    def is_changed(self) -> bool:
        for _, value in self.parking_views.items():
            if value.is_changed_view():
                return True
        return False

    @staticmethod
    def __send_results(parking_view):
        cnt_free = 0
        for item in parking_view.space_info.get_new_status_place():
            if item[0]:
                cnt_free += 1

        cv2.imwrite("Images/last_img.jpg", parking_view.space_info.get_image())

        cv2.imshow('Detecting', parking_view.space_info.get_image())
        key_press = cv2.waitKey(1)
        while key_press != 27:
            key_press = cv2.waitKey(1)

        coded_image = base64.b64encode(parking_view.space_info.get_image()).decode('utf-8')

        url = 'http://127.0.0.1:8000/view'
        json_data = json.dumps({
            "id": None,
            "parking_lot_id": 1,
            "image": coded_image,
            "free_places": cnt_free,
            "capacity": len(parking_view.space_info.get_new_status_place())
        })
        send_status = Sender.send(url, json_data)
        if send_status == 200:
            print(f"Изменения отправлены | {time.ctime()}")
        else:
            raise Exception(f"ERROR: send status is {send_status} | {time.ctime()}")

    def run_parking(self):
        for _, value in self.parking_views.items():
            if value.get_connection():
                value.run_view_recognition(fl_show=True)
                if self.is_changed():
                    self.__send_results(value)


class Detector:
    def __init__(self):
        self.parking_list = dict()

    def cmd_add_camera(self, command):
        parking_key = command[0]
        if parking_key in self.parking_list:
            self.parking_list[parking_key].add_camera(command[1:])
        else:
            new_parking = Parking(command[1:])
            self.parking_list[parking_key] = new_parking

    def cmd_del_camera(self, command):
        parking_key = command[0]
        if parking_key in self.parking_list:
            self.parking_list[parking_key].delete_camera(command[1])

    def run(self):
        for i in range(10):
            if len(self.parking_list) > 0:
                for _, value in self.parking_list.items():
                    value.run_parking()
            else:
                raise Exception("No cameras are connected")
