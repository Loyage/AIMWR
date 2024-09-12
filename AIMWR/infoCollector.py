import os
import time
import json


class InfoCollector:
    def __init__(self, work_dir: str = ""):
        self.work_dir = work_dir
        self._P_DIR = os.path.join(work_dir, "AIMWR")
        self._P_TEMPLATE = os.path.join(self._P_DIR, "template.jpg")
        self._P_METADATA = os.path.join(self._P_DIR, "metadata.json")
        self._P_EXTARCTION = os.path.join(self._P_DIR, "extraction/{img_name}")

        if not os.path.exists(self._P_DIR):
            os.makedirs(self._P_DIR)

        if not os.path.exists(self._P_METADATA):
            with open(self._P_METADATA, "w") as f:
                f.write("{}")

        self.metadata = self._loadMetadata()

    def hasTemplate(self):
        return os.path.exists(self._P_TEMPLATE)

    def _loadMetadata(self):
        with open(self._P_METADATA, "r") as f:
            return json.load(f)
