from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QListWidgetItem,
    QTextEdit,
    QListWidget,
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QPixmap

from .._collapsible import QCollapsible
from ..infoCollector import InfoCollector
from .._colors import COLORS


class BasicSettingBox(QCollapsible):
    start_template_setting = Signal(name="start_template_setting")
    update_class_setting = Signal(name="update_class_setting")

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

        self.lab_class = QLabel("Class names:")
        self.list_class = QListWidget()
        self.btn_class = QPushButton("Reset")

        self.lab_temp_msg = QLabel()
        self.lab_temp_img = QLabel()
        self.btn_temp = QPushButton("Setup template")

        self.lay_all.addWidget(self.lab_class)
        self.lay_all.addWidget(self.list_class)
        self.lay_all.addWidget(self.btn_class)
        self.lay_all.addWidget(self.lab_temp_msg)
        self.lay_all.addWidget(self.lab_temp_img)
        self.lay_all.addWidget(self.btn_temp)

    def _initData(self):
        self.classes = []
        self.colors = []

        self.has_template = False
        self.template_path = ""

        self.btn_class.setText("Save changes")
        self.lab_temp_img.setVisible(self.has_template)
        self.btn_temp.setText(
            "Change template" if self.has_template else "Setup template"
        )

    def _initSignals(self):
        self.btn_temp.clicked.connect(self.start_template_setting.emit)
        self.btn_class.clicked.connect(self.resetClass)

    def setInfoCollector(self, info_c: InfoCollector):
        self.info_c = info_c
        # renew class names
        self.list_class.clear()
        class_names = self.info_c.class_names
        for idx, name in enumerate(class_names):
            item = QListWidgetItem(name)
            item.setFlags(item.flags() | Qt.ItemIsEditable)
            item.setForeground(COLORS[idx + 1])
            self.list_class.addItem(item)

        self.renew()

    def resetClass(self):
        class_names = []
        item_num = self.list_class.count()
        for idx in range(item_num):
            item = self.list_class.item(idx)
            class_names.append(item.text())

        self.info_c.resetClass(class_names)
        self.renew()

        self.update_class_setting.emit()

    def renew(self):
        # renew class names
        self.class_names = self.info_c.class_names
        # renew template messages
        self.has_template = self.info_c.hasTemplate()
        self.lab_temp_img.setVisible(self.has_template)
        self.btn_temp.setText(
            "Change template" if self.has_template else "Setup template"
        )
        if self.has_template:
            self.path = self.info_c.P_TEMPLATE
            self.img = QPixmap(self.path)
            self.lab_temp_img.setPixmap(self.img)
            self.lab_temp_img.resize(self.lab_temp_img.pixmap().size())
            self.img_size = self.lab_temp_img.pixmap().size()
            self.lab_temp_msg.setText(
                f"Template image: {self.img_size.width()}x{self.img_size.height()}"
            )
        else:
            self.lab_temp_msg.setText("No template image found.")
