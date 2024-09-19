import os


class InfoCollector:
    def __init__(self, work_dir: str = ""):
        self.work_dir = work_dir
        self.P_DIR = os.path.join(work_dir, "AIMWR")
        self.P_TEMPLATE = os.path.join(self.P_DIR, "template.jpg")
        self.P_CLASS = os.path.join(self.P_DIR, "class.txt")
        self.P_METADATA = os.path.join(self.P_DIR, "metadata.json")

        self.P_IMAGE = os.path.join(work_dir, "{img_name}")
        self.P_EXTARCT = os.path.join(self.P_DIR, "extraction/{img_name}.txt")
        self.P_CLASSIFY = os.path.join(self.P_DIR, "classification/{img_name}.txt")
        self.P_EDIT = os.path.join(self.P_DIR, "edit/{img_name}.txt")
        self.P_MODEL = os.path.join(self.P_DIR, "model/{model_type}_{time}.pth")

        self.class_names: list[str] = []
        self.img_name_current: str = ""
        self.img_status: dict[str, tuple[bool, bool, bool]] = {}
        # {"img_name": (extracted, classified, edited), ...}

        self._makeDirsFiles()
        self._loadClass()
        self._loadStatus()

        self.classes_show = [
            idx for idx in range(len(self.class_names))
        ]  # classes to show, bound to checkboxes in box_edit
        self.class_edit = -1  # class to assign, bound to combobox in box_edit
        self.source_rect = ""  # source for rect, bound to combobox in box_edit

    def _makeDirsFiles(self):
        if not os.path.exists(os.path.join(self.P_DIR, "extraction")):
            os.makedirs(os.path.join(self.P_DIR, "extraction"))

        if not os.path.exists(os.path.join(self.P_DIR, "classification")):
            os.makedirs(os.path.join(self.P_DIR, "classification"))

        if not os.path.exists(os.path.join(self.P_DIR, "edit")):
            os.makedirs(os.path.join(self.P_DIR, "edit"))

        if not os.path.exists(os.path.join(self.P_DIR, "model")):
            os.makedirs(os.path.join(self.P_DIR, "model"))

    def _loadClass(self):
        with open(self.P_CLASS, "r") as f:
            class_names = f.readlines()
        class_names = [name.strip() for name in class_names]
        self.class_names = class_names

    def _loadStatus(self):
        image_names = self.getImageNames()
        for img_name in image_names:
            extracted = self.hasExtracted(img_name)
            classified = self.hasClassified(img_name)
            edited = self.hasEdit(img_name)
            self.img_status[img_name] = (extracted, classified, edited)

    def hasTemplate(self):
        return os.path.exists(self.P_TEMPLATE)

    def resetClass(self, class_names: list):
        with open(self.P_CLASS, "w") as f:
            f.write("\n".join(class_names))
        self.class_names = class_names

    def getImageNames(self):
        file_names = os.listdir(self.work_dir)
        image_filter = [".jpg", ".jpeg", ".png", ".bmp"]
        image_names = [
            f for f in file_names if os.path.splitext(f)[1].lower() in image_filter
        ]
        return image_names

    def getImageNamesByFilter(
        self,
        _filter=([True, False], [True, False], [True, False]),
    ):
        result = []
        for img_name, status in self.img_status.items():
            if (
                status[0] in _filter[0]
                and status[1] in _filter[1]
                and status[2] in _filter[2]
            ):
                result.append(img_name)

        return result

    def hasExtracted(self, img_name: str):
        return os.path.exists(self.P_EXTARCT.format(img_name=img_name))

    def hasClassified(self, img_name: str):
        return os.path.exists(self.P_CLASSIFY.format(img_name=img_name))

    def hasEdit(self, img_name: str):
        return os.path.exists(self.P_EDIT.format(img_name=img_name))

    def getExtracted(self, img_name: str):
        return self._getResults(img_name, self.P_EXTARCT)

    def getClassified(self, img_name: str):
        return self._getResults(img_name, self.P_CLASSIFY)

    def getEdit(self, img_name: str):
        return self._getResults(img_name, self.P_EDIT)

    def _getResults(self, img_name: str, path: str):
        with open(path.format(img_name=img_name), "r") as f:
            lines = f.readlines()
        lines = [line.strip() for line in lines]
        poses = [tuple(map(int, line.split(","))) for line in lines]
        return poses
