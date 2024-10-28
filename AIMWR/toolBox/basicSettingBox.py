from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QTextEdit,
    QListWidget,
)
from PySide6.QtCore import Signal
from PySide6.QtGui import QPixmap

from .._collapsible import QCollapsible
from ..infoCollector import InfoCollector


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

        self.text_class = QTextEdit()  # TODO: 修改为list类型，添加颜色
        self.btn_class = QPushButton("Reset")

        self.lab_temp_msg = QLabel()
        self.lab_temp_img = QLabel()
        self.btn_temp = QPushButton("Setup template")

        self.lay_all.addWidget(self.list_class)
        self.lay_all.addWidget(self.text_class)
        self.lay_all.addWidget(self.btn_class)
        self.lay_all.addWidget(self.lab_temp_msg)
        self.lay_all.addWidget(self.lab_temp_img)
        self.lay_all.addWidget(self.btn_temp)

    def _initData(self):
        self.is_resetting_class = False
        self.classes = []
        self.colors = []

        self.has_template = False
        self.template_path = ""

        self.text_class.setReadOnly(not self.is_resetting_class)
        self.btn_class.setText("OK" if self.is_resetting_class else "Reset class name")
        self.lab_temp_img.setVisible(self.has_template)
        self.btn_temp.setText(
            "Change template" if self.has_template else "Setup template"
        )

    def _initSignals(self):
        self.btn_temp.clicked.connect(self.start_template_setting.emit)
        self.btn_class.clicked.connect(self.resetClass)

    def setInfoCollector(self, info_c: InfoCollector):
        self.info_c = info_c
        self.renew()

    def resetClass(self):
        self.is_resetting_class = not self.is_resetting_class
        self.text_class.setReadOnly(not self.is_resetting_class)
        self.btn_class.setText("OK" if self.is_resetting_class else "Reset class name")
        if self.is_resetting_class:
            return
        text = self.text_class.toPlainText()
        class_names = text.split("\n")
        class_names = [name for name in class_names if name]  # delete empty lines
        self.info_c.resetClass(class_names)
        self.renew()

        self.update_class_setting.emit()

    def renew(self):
        # renew class names
        class_names = self.info_c.class_names
        self.text_class.setText("\n".join(class_names))
        self.text_class.setReadOnly(not self.is_resetting_class)
        # renew template messages
        self.has_template = self.info_c.hasTemplate()
        self.lab_temp_img.setVisible(self.has_template)
        self.text_class.setReadOnly(not self.is_resetting_class)
        self.btn_class.setText("OK" if self.is_resetting_class else "Reset class name")
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
