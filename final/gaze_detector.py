import os

os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

import numpy as np
from tensorflow.keras.models import load_model
import cv2

lc_model = load_model("../gaze-models/model_lc.h5")
rc_model = load_model("../gaze-models/model_rc.h5")
lr_model = load_model("../gaze-models/model_lr.h5")
rr_model = load_model("../gaze-models/model_rr.h5")


def get_eye_region_boundaries(face_keypoints):
    eyes = face_keypoints[36:48]
    xmin = np.min(eyes[:, 0])
    xmax = np.max(eyes[:, 0])
    ymin = np.min(eyes[:, 1])
    ymax = np.max(eyes[:, 1])
    return xmin, xmax, ymin, ymax


def get_eye_region(frame, face_keypoints):
    l, r, t, b = get_eye_region_boundaries(face_keypoints)
    eyes_image = frame[t - 20:b + 10, l - 20:r + 20, :]
    return eyes_image


def prep_eye_image(eye_image):
    eye_image = cv2.resize(eye_image, (72, 40))[:, :, ::-1].astype(np.float32) / 255.
    return eye_image


def predict_all(frame, face_keypoints):
    eyes_image = get_eye_region(frame, face_keypoints)
    left_eye = prep_eye_image(eyes_image[:, :int(eyes_image.shape[1] / 2), :])
    right_eye = prep_eye_image(eyes_image[:, int(eyes_image.shape[1] / 2):, :])
    probs_lc = lc_model.predict(np.asarray([left_eye]))[0]
    probs_rc = lc_model.predict(np.asarray([right_eye]))[0]
    probs_lr = lr_model.predict(np.asarray([left_eye]))[0]
    probs_rr = rr_model.predict(np.asarray([right_eye]))[0]
    return (np.argmax(probs_lc + probs_rc), np.argmax(probs_lr + probs_rr))
