import os
import cv2
import numpy as np


class Extractor:
    def __init__(self, dir, template_path):
        self.dir = dir
        self.t = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)

    def wellExtract(self, img_name: str):
        match_thre = 0.15

        img_path = os.path.join(self.dir, img_name)
        src_color = cv2.imread(img_path)
        src_gray = cv2.cvtColor(src_color, cv2.COLOR_BGR2GRAY)

        img_binary = cv2.adaptiveThreshold(
            src_gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 25, 10
        )

        result = cv2.matchTemplate(img_binary, self.t, cv2.TM_CCOEFF_NORMED)

        wells_loc = []
        while True:
            minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(result)
            if maxVal < match_thre:
                break

            wells_loc.append(maxLoc)
            # 创建矩形区域并确保它在图像边界内
            rect = (
                maxLoc[0] - 100,
                maxLoc[1] - 100,
                self.t.shape[1],
                self.t.shape[0],
            )
            rect = (
                rect[0],
                rect[1],
                min(rect[0] + rect[2], img_binary.shape[1]),
                min(rect[1] + rect[3], img_binary.shape[0]),
            )

        with open(self.info_c._P_EXTARCTION.format(img_name=img_name), "w") as f:
            for i, loc in enumerate(wells_loc):

                f.write(f"{loc[0]},{loc[1]},{self.t.shape[1]},{self.t.shape[0]}\n")
                img_cut = src_color[
                    loc[1] : loc[1] + self.t.shape[0],
                    loc[0] : loc[0] + self.t.shape[1],
                ]
                cv2.imwrite(
                    os.path.join(self.info_c._P_DIR, str(i) + img_name), img_cut
                )

        return wells_loc
