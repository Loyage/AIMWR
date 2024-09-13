import os
from ._collapsible import QCollapsible
from .infoCollector import InfoCollector
from .algorithm import Extractor
from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QGroupBox,
    QLabel,
    QPushButton,
    QListView,
    QTextEdit,
    QMessageBox,
    QButtonGroup,
    QRadioButton,
)
from PySide6.QtCore import QStringListModel, Signal
from PySide6.QtGui import QPixmap


# CountBox(folder, image) + ImageList + BasicSettings(class setting, template setting) + Extraction + Classification + EditTool(set showing color) + TrainTool
class CountBox(QCollapsible):
    def __init__(self, parent: QWidget | None = None):
        """
        A collapsible widget to show the count result.
        """

        super(CountBox, self).__init__(
            "Count", parent, expandedIcon="▼", collapsedIcon="▶"
        )
        self._initUI()
        self._initData()
        self._initSignals()

    def _initUI(self):
        self.widget = QWidget()
        self.setContent(self.widget)
        self.lay_all = QVBoxLayout()
        self.widget.setLayout(self.lay_all)
        self.collapse()

        self.box_image = QGroupBox("Image")
        self.box_class = QGroupBox


class ImageListBox(QCollapsible):
    select_image = Signal(str, name="select_image")

    def __init__(self, parent: QWidget | None = None):
        """
        A collapsible widget to show a list of images in the workspace.
        """

        super(ImageListBox, self).__init__(
            "Image List", parent, expandedIcon="▼", collapsedIcon="▶"
        )
        self._initUI()
        self._initData()
        self._initSignals()

    def _initUI(self):
        self.widget = QWidget()
        self.setContent(self.widget)
        self.lay_all = QVBoxLayout()
        self.widget.setLayout(self.lay_all)
        self.collapse()

        # widget: image_list + lay_move + btn_update
        self.listview = QListView()
        self.lay_move = QHBoxLayout()
        self.btn_update = QPushButton("Update list")
        self.lay_all.addWidget(self.listview)
        self.lay_all.addLayout(self.lay_move)
        self.lay_all.addWidget(self.btn_update)

        # image_list
        self.list_model = QStringListModel()
        self.listview.setModel(self.list_model)

        # lay_move: btn_up + btn_down
        self.btn_up = QPushButton("▲")
        self.btn_down = QPushButton("▼")
        self.lay_move.addWidget(self.btn_up)
        self.lay_move.addWidget(self.btn_down)

    def _initData(self):
        self.work_dir = ""

    def _initSignals(self):
        self.listview.clicked.connect(self.atListClicked)
        self.btn_up.clicked.connect(self.moveUp)
        self.btn_down.clicked.connect(self.moveDown)
        self.btn_update.clicked.connect(self.renew)

    def setInfoCollector(self, info_c: InfoCollector):
        self.info_c = info_c
        self.work_dir = self.info_c.work_dir
        self.renew()

    def atListClicked(self, index):
        image_name = self.list_model.stringList()[index.row()]
        self.select_image.emit(image_name)

    def moveUp(self):
        idx_now = self.listview.currentIndex().row()
        if idx_now > 0:
            self.listview.setCurrentIndex(self.list_model.index(idx_now - 1, 0))
        else:
            self.listview.setCurrentIndex(self.list_model.index(0, 0))
        self.select_image.emit(
            self.list_model.stringList()[self.listview.currentIndex().row()]
        )

    def moveDown(self):
        idx_now = self.listview.currentIndex().row()
        if idx_now < len(self.list_model.stringList()) - 1:
            self.listview.setCurrentIndex(self.list_model.index(idx_now + 1, 0))
        else:
            self.listview.setCurrentIndex(
                self.list_model.index(len(self.list_model.stringList()) - 1, 0)
            )
        self.select_image.emit(
            self.list_model.stringList()[self.listview.currentIndex().row()]
        )

    def renew(self):
        self.list_model.setStringList([])
        files = os.listdir(self.work_dir)
        image_filter = [".jpg", ".jpeg", ".png", ".bmp"]
        images = [f for f in files if os.path.splitext(f)[1].lower() in image_filter]
        self.list_model.setStringList(images)
        self.listview.setModel(self.list_model)

    def setImage(self, image_name: str):
        # fixme: when the list is empty, how to handle this?
        if image_name not in self.list_model.stringList():
            idx = 0
        else:
            idx = self.list_model.stringList().index(image_name)
        self.listview.setCurrentIndex(self.list_model.index(idx, 0))
        self.select_image.emit(image_name)


class BasicSettingBox(QCollapsible):
    setup_template = Signal(name="setup_template")

    def __init__(self, parent: QWidget | None = None):
        """
        A collapsible widget to show basic settings for classification.
        """

        super(BasicSettingBox, self).__init__(
            "Basic Settings", parent, expandedIcon="▼", collapsedIcon="▶"
        )
        self._initUI()
        self._initData()
        self._initSignals()

    def _initUI(self):
        self.widget = QWidget()
        self.setContent(self.widget)
        self.lay_all = QVBoxLayout()
        self.widget.setLayout(self.lay_all)
        self.collapse()

        self.text_class = QTextEdit()
        self.btn_class = QPushButton("Reset")

        self.lbl_temp_msg = QLabel()
        self.lbl_temp_img = QLabel()
        self.btn_temp = QPushButton("Setup template")

        self.lay_all.addWidget(self.text_class)
        self.lay_all.addWidget(self.btn_class)
        self.lay_all.addWidget(self.lbl_temp_msg)
        self.lay_all.addWidget(self.lbl_temp_img)
        self.lay_all.addWidget(self.btn_temp)

    def _initData(self):
        self.is_resetting_class = False
        self.classes = []
        self.colors = []

        self.has_template = False
        self.template_path = ""

        self.text_class.setReadOnly(not self.is_resetting_class)
        self.btn_class.setText("OK" if self.is_resetting_class else "Reset class name")
        self.lbl_temp_img.setVisible(self.has_template)
        self.btn_temp.setText(
            "Change template" if self.has_template else "Setup template"
        )

    def _initSignals(self):
        self.btn_temp.clicked.connect(self.setup_template.emit)
        self.btn_class.clicked.connect(self.resetClass)

    def setInfoCollector(self, info_c: InfoCollector):
        self.info_c = info_c
        self.renew()

    def resetClass(self):
        self.is_resetting_class = not self.is_resetting_class
        self.renew()

        text = self.text_class.toPlainText()
        class_names = text.split("\n")
        self.info_c.resetClass(class_names)

    def renew(self):
        self.has_template = self.info_c.hasTemplate()
        self.lbl_temp_img.setVisible(self.has_template)
        self.text_class.setReadOnly(not self.is_resetting_class)
        self.btn_class.setText("OK" if self.is_resetting_class else "Reset class name")
        self.btn_temp.setText(
            "Change template" if self.has_template else "Setup template"
        )
        if self.has_template:
            self.path = self.info_c._P_TEMPLATE
            self.img = QPixmap(self.path)
            self.lbl_temp_img.setPixmap(self.img)
            self.lbl_temp_img.resize(self.lbl_temp_img.pixmap().size())
            self.expand()
            self.img_size = self.lbl_temp_img.pixmap().size()
            self.lbl_temp_msg.setText(
                f"Template image: {self.img_size.width()}x{self.img_size.height()}"
            )
        else:
            self.lbl_temp_msg.setText("No template image found.")
        self.expand()


class ExtractionBox(QCollapsible):
    def __init__(self, parent: QWidget | None = None):
        """
        A collapsible widget to show tools for image extraction.
        """

        super(ExtractionBox, self).__init__(
            "Extraction", parent, expandedIcon="▼", collapsedIcon="▶"
        )
        self.parent = parent
        self._initUI()
        self._initData()
        self._initSignals()

    def _initUI(self):
        self.widget = QWidget()
        self.setContent(self.widget)
        self.lay_all = QVBoxLayout()
        self.widget.setLayout(self.lay_all)
        self.collapse()

        self.group = QButtonGroup()
        self.btn_single = QRadioButton("Single image")
        self.btn_all = QRadioButton("Whole folder")
        self.group.addButton(self.btn_single)
        self.group.addButton(self.btn_all)

        self.btn_extract = QPushButton("Extract")

    def _initData(self):
        self.extractor = None
        pass

    def _initSignals(self):
        self.btn_extract.clicked.connect(self.extract)

    def setInfoCollector(self, info_c: InfoCollector):
        self.info_c = info_c
        self.extractor = Extractor(self.info_c.work_dir, self.info_c._P_TEMPLATE)

    def extract(self):
        if not self.info_c.hasTemplate():
            QMessageBox.warning(
                self.wgt_all, "Warning", "No template image found.", QMessageBox.Ok
            )
            return

        if self.btn_single.isChecked():
            img_names = [self.parent.image_name]
            wells_locs = [self.extractor.wellExtract(self.parent.image_name)]
        elif self.btn_all.isChecked():
            img_names = self.parent.img_list.stringList()
            wells_locs = []
            for img_name in img_names:
                wells_locs.append(self.extractor.wellExtract(img_name))
        else:
            return

        self.writeResult(img_names, wells_locs)

    def writeResult(self, img_names: list, wells_locs: list):
        pass


class FolderInfoBox(QCollapsible):
    select_image = Signal(str, name="select_image")

    def __init__(self, parent: QWidget | None = None):
        """
        A collapsible widget to show a list of images in the workspace.
        """

        super(FolderInfoBox, self).__init__(
            "Folder Info", parent, expandedIcon="▼", collapsedIcon="▶"
        )
        self._initUI()
        self._initData()
        self._initSignals()

    def _initUI(self):
        self.widget = QWidget()
        self.setContent(self.widget)
        self.lay_all = QVBoxLayout()
        self.widget.setLayout(self.lay_all)
        self.collapse()

        # widget: Count + image_list + lay_move + btn_update
        self.box_count = QGroupBox("Count")
        self.listview = QListView()
        self.lay_move = QHBoxLayout()
        self.btn_update = QPushButton("Update list")
        self.lay_all.addWidget(self.box_count)
        self.lay_all.addWidget(self.listview)
        self.lay_all.addLayout(self.lay_move)
        self.lay_all.addWidget(self.btn_update)

        # box_count
        self.lay_status = QVBoxLayout()
        self.box_count.setLayout(self.lay_status)
        self.lbl_status = QLabel("")

        # image_list
        self.list_model = QStringListModel()
        self.listview.setModel(self.list_model)

        # lay_move: btn_up + btn_down
        self.btn_up = QPushButton("▲")
        self.btn_down = QPushButton("▼")
        self.lay_move.addWidget(self.btn_up)
        self.lay_move.addWidget(self.btn_down)

    def _initData(self):
        self.work_dir = ""

    def _initSignals(self):
        self.btn_update.clicked.connect(self.update)
        self.listview.clicked.connect(self.atListClicked)
        self.btn_up.clicked.connect(self.moveUp)
        self.btn_down.clicked.connect(self.moveDown)

    def setInfoCollector(self, info_c: InfoCollector):
        self.info_c = info_c
        self.work_dir = self.info_c.work_dir
        self.update()

    def atListClicked(self, index):
        image_name = self.list_model.stringList()[index.row()]
        self.select_image.emit(image_name)

    def moveUp(self):
        idx_now = self.listview.currentIndex().row()
        if idx_now > 0:
            self.listview.setCurrentIndex(self.list_model.index(idx_now - 1, 0))
        else:
            self.listview.setCurrentIndex(self.list_model.index(0, 0))
        self.select_image.emit(
            self.list_model.stringList()[self.listview.currentIndex().row()]
        )

    def moveDown(self):
        idx_now = self.listview.currentIndex().row()
        if idx_now < len(self.list_model.stringList()) - 1:
            self.listview.setCurrentIndex(self.list_model.index(idx_now + 1, 0))
        else:
            self.listview.setCurrentIndex(
                self.list_model.index(len(self.list_model.stringList()) - 1, 0)
            )
        self.select_image.emit(
            self.list_model.stringList()[self.listview.currentIndex().row()]
        )

    def update(self):
        self._updateList()
        self._updateStatus()

    def _updateList(self):
        self.list_model.setStringList([])
        files = os.listdir(self.work_dir)
        image_filter = [".jpg", ".jpeg", ".png", ".bmp"]
        images = [f for f in files if os.path.splitext(f)[1].lower() in image_filter]
        self.list_model.setStringList(images)
        self.listview.setModel(self.list_model)

    def _updateStatus(self):
        self.num_images = len(self.list_model.stringList())
        self.text_status = f"Images: {self.num_images}"
        self.lbl_status.setText(f"Workspace: {self.work_dir}")
        self.lay_status.addWidget(self.lbl_status)

    def setImage(self, image_name: str):
        # fixme: when the list is empty, how to handle this?
        if image_name not in self.list_model.stringList():
            idx = 0
        else:
            idx = self.list_model.stringList().index(image_name)
        self.listview.setCurrentIndex(self.list_model.index(idx, 0))
        self.select_image.emit(image_name)


# TODO: img_info_box: count, label to show class name and the color, choose class file to load(auto or manual)
class ImageInfoBox(QCollapsible):
    def __init__(self, parent: QWidget | None = None):
        """
        A collapsible widget to show information about the selected image.
        """

        super(ImageInfoBox, self).__init__(
            "Image Info", parent, expandedIcon="▼", collapsedIcon="▶"
        )
        self._initUI()
        self._initData()
        self._initSignals()

    def _initUI(self):
        self.widget = QWidget()
        self.setContent(self.widget)
        self.lay_all = QVBoxLayout()
        self.widget.setLayout(self.lay_all)
        self.collapse()

        self.box_count = QGroupBox("Count")

    def _initData(self):
        self.img_size = None

    def _initSignals(self):
        pass

    def setInfoCollector(self, info_c: InfoCollector):
        self.info_c = info_c
        self.renew()

    def renew(self):
        pass


# TODO: folder_tool_box: extract, classify
# TODO: TrainToolBox: choose model, train, test, save


class ImageToolBox(QCollapsible):
    # TODO: btn- extraction, classification(choose model)
    # TODO: edit & save
    def __init__(self, parent: QWidget | None = None):
        """
        A collapsible widget to show tools for image processing.
        """

        super(ImageToolBox, self).__init__(
            "Image Tools", parent, expandedIcon="▼", collapsedIcon="▶"
        )
        self._initUI()
        self._initData()
        self._initSignals()

    def _initUI(self):
        self.widget = QWidget()
        self.setContent(self.widget)
        self.lay_all = QVBoxLayout()
        self.widget.setLayout(self.lay_all)
        self.collapse()

        self.btn_zoom_in = QPushButton("Zoom In")
        self.btn_zoom_out = QPushButton("Zoom Out")
        self.btn_zoom_reset = QPushButton("Zoom Reset")
        self.lay_all.addWidget(self.btn_zoom_in)
        self.lay_all.addWidget(self.btn_zoom_out)
        self.lay_all.addWidget(self.btn_zoom_reset)

    def _initData(self):
        pass

    def _initSignals(self):
        self.btn_zoom_in.clicked.connect(self.zoomIn)
        self.btn_zoom_out.clicked.connect(self.zoomOut)
        self.btn_zoom_reset.clicked.connect(self.zoomReset)

    def zoomIn(self):
        pass

    def zoomOut(self):
        pass

    def zoomReset(self):
        pass
