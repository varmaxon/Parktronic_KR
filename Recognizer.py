import cv2
import numpy as np
from ultralytics import YOLO
import torch
from PIL import Image

from DefaultParams import DefaultParams


class Recognizer:
    def __init__(self, url, video_shape, marked_coordinates, hyperparams, fl_show):
        if video_shape is None:
            raise Exception("Connection failed")

        if None in (hyperparams.get_yolo_path(), hyperparams.get_len_nearby_boxes(),
                    hyperparams.get_e_cleaning_similar(), hyperparams.get_e_dif_points(),
                    hyperparams.get_e_iou(), hyperparams.get_size_block_frames()):
            raise TypeError("HyperParam type is None")

        self.hyperparams = hyperparams

        self.nearby_boxes = []
        self.cleaning_1 = []
        self.matrix_counters = np.zeros((video_shape['y'], video_shape['x']))
        self.parking_places = []
        self.parking_places_points = marked_coordinates
        self.main_points = marked_coordinates
        self.status_place = []
        self.fl_show = fl_show

        self.net = cv2.dnn.readNetFromDarknet(self.hyperparams.get_yolo_path() + "/yolov4-tiny.cfg",
                                              self.hyperparams.get_yolo_path() + "/yolov4-tiny.weights")

        self.seg_model = YOLO("yolo/yolov8x-seg.pt")  # load a pretrained model (recommended for training)
        self.device = torch.device('cpu')
        self.seg_model.to(self.device)

        layer_names = self.net.getLayerNames()
        out_layers_indexes = self.net.getUnconnectedOutLayers()
        self.out_layers = [layer_names[index - 1] for index in out_layers_indexes]

        # Loading from a file of object classes that YOLO can detect
        with open(self.hyperparams.get_yolo_path() + "/coco.names.txt") as file:
            self.classes = file.read().split("\n")

        self.video = url
        look_for = [self.hyperparams.detect_object]

        # Delete spaces
        list_look_for = []
        for look in look_for:
            list_look_for.append(look.strip())

        self.classes_to_look_for = list_look_for

    def __draw_object_bounding_box(self, image_to_process, index, box):
        """
        Drawing object borders with captions
        :param image_to_process: original image
        :param index: index of object class defined with YOLO
        :param box: coordinates of the area around the object
        :return: image with marked objects
        """
        x, y, w, h = box
        start = (x, y)
        end = (x + w, y + h)
        color = (0, 255, 0)
        width = 2
        final_image = cv2.rectangle(image_to_process, start, end, color, width)

        start = (x, y - 10)
        font_size = 1
        font = cv2.FONT_HERSHEY_SIMPLEX
        width = 2
        text = self.classes[index]
        final_image = cv2.putText(final_image, text, start, font,
                                  font_size, color, width, cv2.LINE_AA)

        return final_image

    def __calc_s(self, i, j):
        max_x1 = max(self.nearby_boxes[0][i][0], self.nearby_boxes[1][j][0])
        max_y1 = max(self.nearby_boxes[0][i][1], self.nearby_boxes[1][j][1])
        min_x2 = min(self.nearby_boxes[0][i][0] + self.nearby_boxes[0][i][2],
                     self.nearby_boxes[1][j][0] + self.nearby_boxes[1][j][2])
        min_y2 = min(self.nearby_boxes[0][i][1] + self.nearby_boxes[0][i][3],
                     self.nearby_boxes[1][j][1] + self.nearby_boxes[1][j][3])

        if (max_x1 > min_x2) or (max_y1 > min_y2):
            s_cross = 0
        else:
            s_cross = (min_x2 - max_x1) * (min_y2 - max_y1)

        s1 = self.nearby_boxes[0][i][2] * self.nearby_boxes[0][i][3]
        s2 = self.nearby_boxes[1][j][2] * self.nearby_boxes[1][j][3]

        return s_cross / (s1 + s2 - s_cross)

    def __compare_squares(self, rect1, rect2):
        s1 = rect1[2] * rect1[3]
        s2 = rect2[2] * rect2[3]
        if s1 < s2:
            return False
        else:
            del self.cleaning_1[self.cleaning_1.index(rect2)]
            return True

    def cleaning_similar(self, rect1, rect2, epsilon):  # (new, old)
        if (rect1[0] > rect2[0]) and (rect1[1] > rect2[1]) and (rect1[0] + rect1[2] < rect2[0] + rect2[2]) and (
                rect1[1] + rect1[3] < rect2[1] + rect2[3]):
            return False
        elif (abs(rect1[0] - rect2[0]) < epsilon) and (abs(rect1[1] - rect2[1]) < epsilon):
            return self.__compare_squares(rect1, rect2)
        elif (abs((rect1[0] + rect1[2]) - (rect2[0] + rect2[2])) < epsilon) and (abs(rect1[1] - rect2[1]) < epsilon):
            return self.__compare_squares(rect1, rect2)
        elif (abs(rect1[0] - rect2[0]) < epsilon) and (abs((rect1[1] + rect1[3]) - (rect2[1] + rect2[3])) < epsilon):
            return self.__compare_squares(rect1, rect2)
        elif (abs((rect1[0] + rect1[2]) - (rect2[0] + rect2[2])) < epsilon) and (
                abs((rect1[1] + rect1[3]) - (rect2[1] + rect2[3])) < epsilon):
            return self.__compare_squares(rect1, rect2)
        else:
            return True

    def __box_crossing(self, epsilon_dif_points, epsilon_dif_square, len_nearby_boxes):
        if len(self.nearby_boxes) != len_nearby_boxes:
            raise ValueError(f"ERROR: len(nearby_boxes) != {len_nearby_boxes}")

        box_crossing_arr = []
        for i in range(len(self.nearby_boxes[0])):
            if (i < len(self.nearby_boxes[1])) and (
                    abs(self.nearby_boxes[0][i][0] - self.nearby_boxes[1][i][0]) <= epsilon_dif_points) and (
                    abs(self.nearby_boxes[0][i][1] - self.nearby_boxes[1][i][1]) <= epsilon_dif_points):
                s = self.__calc_s(i, i)
                if (s > 0) and (s > epsilon_dif_square):
                    box_crossing_arr.append(self.nearby_boxes[1][i])
            else:
                for j in range(len(self.nearby_boxes[1])):
                    if (abs(self.nearby_boxes[0][i][0] - self.nearby_boxes[1][j][0]) <= epsilon_dif_points) and (
                            abs(self.nearby_boxes[0][i][1] - self.nearby_boxes[1][j][1]) <= epsilon_dif_points):
                        s = self.__calc_s(i, j)
                        if (s > 0) and (s > epsilon_dif_square):
                            box_crossing_arr.append(self.nearby_boxes[1][j])
                            break

        for new in box_crossing_arr:
            flag = True
            for old in self.cleaning_1:
                if not self.cleaning_similar(new, old, self.hyperparams.get_e_cleaning_similar()):
                    flag = False
            if flag:
                self.cleaning_1.append(new)

    def __apply_yolo_object_detection(self, image_to_process):
        height, width, _ = image_to_process.shape

        # blobFromImage(image, scalefactor, size, mean, swapRB)
        blob = cv2.dnn.blobFromImage(image_to_process, 1 / 255, (608, 608), (0, 0, 0), swapRB=True, crop=False)
        self.net.setInput(blob)
        outs = self.net.forward(self.out_layers)
        class_indexes, class_scores, boxes = ([] for _ in range(3))
        objects_count = 0

        # Starting a search for objects in an image
        for out in outs:
            for obj in out:
                scores = obj[5:]
                class_index = np.argmax(scores)
                class_score = scores[class_index]
                if class_score > 0:
                    center_x = int(obj[0] * width)
                    center_y = int(obj[1] * height)
                    obj_width = int(obj[2] * width)
                    obj_height = int(obj[3] * height)
                    box = [center_x - obj_width // 2, center_y - obj_height // 2,
                           obj_width, obj_height]
                    boxes.append(box)
                    class_indexes.append(class_index)
                    class_scores.append(float(class_score))

        # Selection
        chosen_boxes = cv2.dnn.NMSBoxes(boxes, class_scores, 0.0, 0.4)
        new_box = []
        for box_index in chosen_boxes:
            box_index = box_index
            box = boxes[box_index]
            class_index = class_indexes[box_index]

            # For debugging, we draw objects included in the desired classes
            if self.classes[class_index] in self.classes_to_look_for:
                objects_count += 1

                new_box.append(box)

                image_to_process = self.__draw_object_bounding_box(image_to_process, class_index, box)

        if len(self.nearby_boxes) < self.hyperparams.get_len_nearby_boxes():
            self.nearby_boxes.append(new_box)
        else:
            del self.nearby_boxes[0]
            self.nearby_boxes.append(new_box)
            self.__box_crossing(self.hyperparams.get_e_dif_points(),
                                self.hyperparams.get_e_iou(),
                                self.hyperparams.get_len_nearby_boxes())

        final_image = image_to_process
        return final_image

    @staticmethod
    def __is_point_inside_circle(bbox, point) -> bool:
        x, y, w, h = 0, 0, bbox[1], bbox[0]
        x_center, y_center = x + int(w / 2), y + int(h / 2)

        r = int(h / 2)
        r -= 0.1 * r
        d = np.sqrt((point[0] - x_center) ** 2 + (point[1] - y_center) ** 2)  # расстояние от центра до точки

        return d < r

    def __find_contours(self, img, point, bbox) -> bool:
        w, h = bbox[2], bbox[3]
        increase = DefaultParams.params["increase"]

        bbox[0] -= increase if bbox[0] >= increase else bbox[0]
        bbox[1] -= increase if bbox[1] >= increase else bbox[1]

        if bbox[0] + bbox[2] <= img.shape[0] + increase:
            bbox[2] += increase
        else:
            bbox[2] = img.shape[0] - bbox[0]

        if bbox[1] + bbox[3] <= img.shape[1] + increase:
            bbox[3] += increase
        else:
            bbox[3] = img.shape[1] - bbox[1]

        w_new, h_new = bbox[2], bbox[3]
        point_new = point[0] - bbox[0] + int((w_new - w) / 2), point[1] - bbox[1] + int((h_new - h) / 2)

        box_img = img[bbox[1]:bbox[1] + bbox[3], bbox[0]:bbox[0] + bbox[2]]

        try:
            box_img = cv2.cvtColor(box_img, cv2.COLOR_BGR2RGB)
            img_pil = Image.fromarray(box_img)
            results = self.seg_model(img_pil, device=self.device, verbose=False)
        except:
            print("BOX_IMG is empty")
            return True

        try:
            segmentation_mask = results[0].masks.data[0].numpy()
            segmentation_mask = cv2.resize(segmentation_mask, (box_img.shape[1], box_img.shape[0]))
            # mask_img = Image.fromarray(segmentation_mask, "I")
            # mask_img.show()5
            if len(results[0].boxes.cls) == 0:
                raise Exception

            return not bool(segmentation_mask[point_new[1]][point_new[0]])

        except:
            print("Сегментация не найдена -> алгоритм окружностей")
            return not self.__is_point_inside_circle(box_img.shape, point_new)  # если накладывается => False

    def __update_parking_places(self, img):
        self.status_place = []
        for point in self.main_points:
            self.status_place.append([False, point])
            fl = True
            for bbox in self.cleaning_1:
                if (bbox[0] < point[0] < bbox[0] + bbox[2]) and (bbox[1] < point[1] < bbox[1] + bbox[3]):
                    fl = self.__find_contours(img, point, bbox.copy())
            if fl:
                self.status_place[self.status_place.index([False, point])][0] = True

    # def cleaning_counters(self, max_frames_block):
    #     """Magic-numbers: 0.2(20% от максимума)"""
    #
    #     counters = []
    #
    #     for item in self.parking_places_points:
    #         if self.matrix_counters[item[0]][item[1]] > 0:
    #             counters.append([self.matrix_counters[item[0]][item[1]], [item[0], item[1]]])
    #
    #     print(self.parking_places)
    #     print(counters)
    #
    #     mas_zip = zip(counters, self.parking_places)
    #     mas_zip_sort = sorted(mas_zip, key=lambda tup: tup[0])
    #     counters_sort = [x[0] for x in mas_zip_sort]
    #     parking_places_sort = [x[1] for x in mas_zip_sort]
    #
    #     # Или же убираем всё, что не входит в 20% от максимального счетчика за блок (1000 / 50 = 20.0)
    #
    #     min_counter = 0.2 * max_frames_block
    #     jump_idx = 0
    #     for i in range(len(counters_sort)):
    #         if counters_sort[i][0] > min_counter:
    #             jump_idx = i
    #             break
    #
    #     del counters_sort[:jump_idx]
    #     del parking_places_sort[:jump_idx]
    #
    #     print("'Counters' after cleaning #2:", counters_sort)
    #     print("'Parking_places' after cleaning #2:", parking_places_sort)
    #     print()
    #
    #     for item in counters_sort:
    #         if item[1] not in self.main_points:
    #             self.main_points.append(item[1])
    #     print("MAIN_POINTS:", self.main_points)
    #
    #     А вообще можно по правилу 3-х СИГМ убирать малоиспользуемые места
    #

    def start_video_object_detection(self, size_block_frames):
        cap = cv2.VideoCapture(self.video)
        if not cap.isOpened():
            raise Exception("Failed open")

        frame = 0
        img_without_box = 0
        while frame < size_block_frames:
            frame += 1

            cap.set(cv2.CAP_PROP_POS_FRAMES, frame)
            _, img = cap.read()
            img_without_box = img.copy()
            # формируем cleaning_1 - стоящие авто в данный момент

            if frame % 5 != 0:
                continue

            #img = cv2.imread("Images/3.jpeg")
            img = self.__apply_yolo_object_detection(img)

            # img = cv2.resize(img, (1920 // 2, 1080 // 2))
            if self.fl_show:
                cv2.imshow('Detecting', img)

            key_press = cv2.waitKey(1)

            if key_press == self.hyperparams.key_press_exit:
                break
        else:
            self.__update_parking_places(img_without_box)
            self.cleaning_1 = []

        cap.release()
        cv2.destroyAllWindows()
