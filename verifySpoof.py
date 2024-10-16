# -*- coding: utf-8 -*-
# @Time : 20-6-9 下午3:06
# @Author : zhuying
# @Company : Minivision
# @File : test.py
# @Software : PyCharm

import os
import cv2
import numpy as np
import argparse
import warnings
import time

from silentFaceAntiSpoofing.src.anti_spoof_predict import AntiSpoofPredict
from silentFaceAntiSpoofing.src.generate_patches import CropImage
from silentFaceAntiSpoofing.src.utility import parse_model_name
warnings.filterwarnings('ignore')




# 因为安卓端APK获取的视频流宽高比为3:4,为了与之一致，所以将宽高比限制为3:4
def check_image(image):
    height, width, channel = image.shape
    if width/height != 3/4:
        print("Image is not appropriate!!!\nHeight/Width should be 4/3.")
        return False
    else:
        return True


def verify_spoof(image_path, model_dir, device_id):
    try:
        model = AntiSpoofPredict(device_id)
        image_cropper = CropImage()
        image = cv2.imread(image_path)
        image = cv2.resize(image, (int(image.shape[0] * 3 / 4), image.shape[0]))
        result = check_image(image)
        if result is False:
            return 255, "No image"
        image_bbox = model.get_bbox(image)
        prediction = np.zeros((1, 3))
        test_speed = 0
        # sum the prediction from single model's result
        for model_name in os.listdir(model_dir):
            h_input, w_input, model_type, scale = parse_model_name(model_name)
            param = {
                "org_img": image,
                "bbox": image_bbox,
                "scale": scale,
                "out_w": w_input,
                "out_h": h_input,
                "crop": True,
            }
            if scale is None:
                param["crop"] = False
            img = image_cropper.crop(**param)
            start = time.time()
            prediction += model.predict(img, os.path.join(model_dir, model_name))
            test_speed += time.time()-start

        # draw result of prediction
        label = np.argmax(prediction)
        value = prediction[0][label]/2

        return label, value
    except Exception as e:
        return 255, f"Error detecting spoof: {e}"


if __name__ == "__main__":
    desc = "test"
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument(
        "--device_id",
        type=int,
        default=0,
        help="which gpu id, [0/1/2/3]")
    parser.add_argument(
        "--model_dir",
        type=str,
        default="./silentFaceAntiSpoofing/resources/anti_spoof_models",
        help="model_lib used to test")
    parser.add_argument(
        "--image_name",
        type=str,
        default="/workspaces/Silent-Face-Anti-Spoofing/captured_image.png",
        help="image used to test")
    args = parser.parse_args()
    verify_spoof(args.image_name, args.model_dir, args.device_id)
