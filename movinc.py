import argparse
from random import randint

import cv2
import imagehash
import numpy as np
from PIL import Image


# フレームをdhashに変換
def frame2dhash(frame):
    img = Image.fromarray(np.uint8(frame))
    return imagehash.dhash(img)


# 動画内のすべてのフレームをdhash化して配列として返す
def get_all_dhashes(mov):
    dhashes = []
    while 1:
        ret, frame = mov.read()
        if not ret: break
        dhashes.append(frame2dhash(frame))
    return dhashes


# 動画中の起点終点およびランダムなN点のフレームをdhash化して配列として返す
def get_random_points_dhashes(mov, points=1):
    # 起点フレーム
    _, frame = mov.read()
    dhashes = [frame2dhash(frame)]

    # ランダムN点フレーム
    if points > 0:
        # 最初と最後のフレームを除いたフレーム数
        num_frames = mov.get(cv2.CAP_PROP_FRAME_COUNT) - 2
        max_skip = int(num_frames / points)

        for point in range(points):
            skips = randint(1, max_skip)
            for _ in range(skips - 1):
                _ = mov.read()
            _, frame = mov.read()
            dhashes.append(frame2dhash(frame))

    # 終点フレーム
    pre_frame = None
    ret = True
    while ret:
        pre_frame = frame
        ret, frame = mov.read()
    dhashes.append(frame2dhash(pre_frame))

    return dhashes


# ターゲット動画に元動画が含まれているであろう度合い (0.0 ~ 1.0) を返す
def get_movincp(origin, target, points=1):
    origin_dhashes = get_random_points_dhashes(origin, points)
    target_dhashes = get_all_dhashes(target)
    target_index = 0
    distances = []

    for origin_dhash in origin_dhashes:
        min_distance = 64
        for i in range(target_index, len(target_dhashes)):
            target_dhash = target_dhashes[i]
            distance = origin_dhash - target_dhash
            if distance < min_distance:
                min_distance = distance
                target_index = i + 1
        distances.append(min_distance)

    return (64 - np.array(distances).mean()) / 64


# ターゲット動画に元画像が含まれているか否か (0, 1) を返す
def get_movincb(origin, target, points=1, threshold=1):
    origin_dhashes = get_random_points_dhashes(origin, points)
    origin_dhash = origin_dhashes.pop(0)
    while 1:
        ret, frame = target.read()
        if not ret:
            break
        target_dhash = frame2dhash(frame)
        if origin_dhash - target_dhash <= threshold:
            if len(origin_dhashes) > 0:
                origin_dhash = origin_dhashes.pop(0)
            else:
                return 1
    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=None)
    parser.add_argument('origin', type=str, help='path to origin movie')
    parser.add_argument('target', type=str, help='path to target movie')
    parser.add_argument('-r', '--return-value-type', type=str, default='p', help='type of return value')
    parser.add_argument('-p', '--points', type=int, default=10, help='number of random points')
    parser.add_argument('-t', '--threshold', type=int, default=3, help='threshold value')
    args = parser.parse_args()

    origin = cv2.VideoCapture(args.origin)
    target = cv2.VideoCapture(args.target)

    if args.return_value_type is 'p':
        res = get_movincp(origin, target, args.points)
    else:
        res = get_movincb(origin, target, args.points, args.threshold)
        res = "True" if res == 1 else "False"
    print(res)
