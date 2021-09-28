import base64
import json

import cv2
import numpy as np


#
# 合成画像の生成
#

def generate(b64_left, b64_right, alpha):
    """
    教師(期待値)と検証値の合成画像を出力する
    """
    image_left = b64_to_ndarray(b64_left)
    image_right = b64_to_ndarray(b64_right)

    image_blend = cv2.addWeighted(
        src1=image_left,
        alpha=(1-alpha),
        src2=image_right,
        beta=(alpha),
        gamma=0)

    b64_blend = ndarray_to_b64(image_blend)

    return b64_blend


def b64_to_ndarray(b64_dist):
    """
    base64 -> ndarray
    """
    np_dist = np.frombuffer(base64.b64decode(b64_dist), np.uint8)
    dist = cv2.imdecode(np_dist, cv2.IMREAD_ANYCOLOR)

    return dist


def ndarray_to_b64(ndarray_dist):
    """
    ndarray -> base64
    """
    _, bytes_dist = cv2.imencode('.png', ndarray_dist)
    bytes_b64_dist = base64.b64encode(bytes_dist)
    str_b64_dist = bytes_b64_dist.decode()

    return str_b64_dist