"""Class with hyperparams"""


class DefaultParams:
    params = dict(detect_object='car',
                  key_press_exit=27,
                  yolo_path="C:/Users/user/PycharmProjects/Parktronic/Detector/yolo",
                  len_nearby_boxes=2,
                  e_cleaning_similar=20,
                  e_dif_points=10,
                  e_iou=0.97,
                  size_block_frames=50,
                  parking_number=1,
                  camera_number=1,
                  camera_url="http://192.168.1.78:8080/video",
                  increase=5)
