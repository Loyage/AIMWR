import os
import time
import json


class InfoCollector:
    def __init__(self, work_dir: str = ""):
        self.work_dir = work_dir
        self._P_DIR = os.path.join(work_dir, "AIMWR")
        self._P_TEMPLATE = os.path.join(self._P_DIR, "template.jpg")
        self._P_CLASS = os.path.join(self._P_DIR, "class.txt")
        self._P_METADATA = os.path.join(self._P_DIR, "metadata.json")
        self._P_EXTARCTION = os.path.join(self._P_DIR, "extraction/{img_name}.txt")

        if not os.path.exists(self._P_DIR):
            os.makedirs(self._P_DIR)

        if not os.path.exists(self._P_CLASS):
            with open(self._P_CLASS, "w") as f:
                f.write("{}")

        self.class_setting = self._loadClass()

    def hasTemplate(self):
        return os.path.exists(self._P_TEMPLATE)

    def _loadClass(self):
        with open(self._P_CLASS, "r") as f:
            class_names = f.readlines()
        class_names = [name.strip() for name in class_names]
        self.class_names = class_names

    def resetClass(self, class_names: list):
        with open(self._P_CLASS, "w") as f:
            f.write("\n".join(class_names))
        self.class_names = class_names
