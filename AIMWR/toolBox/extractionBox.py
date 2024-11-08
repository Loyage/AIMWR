from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QPushButton,
    QRadioButton,
    QButtonGroup,
    QMessageBox,
)
from PySide6.QtCore import Signal
from PySide6.QtGui import QPixmap

from .._collapsible import QCollapsible
from ..infoCollector import InfoCollector
from ..algorithm import Extractor


class ExtractionBox(QCollapsible):
    start_template_setting = Signal(name="start_template_setting")
    finish_extraction = Signal(name="finish_extraction")

    def __init__(self, parent: QWidget | None = None):
        """
        A collapsible widget to show tools for image extraction.
        """

        super(ExtractionBox, self).__init__(
            "Extraction", parent, expandedIcon="▼", collapsedIcon="▶"
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

        self.lab_temp_msg = QLabel()
        self.lab_temp_img = QLabel()
        self.btn_temp = QPushButton("Setup template")
        self.lay_all.addWidget(self.lab_temp_msg)
        self.lay_all.addWidget(self.lab_temp_img)
        self.lay_all.addWidget(self.btn_temp)

        self.rad_current = QRadioButton("Current")
        self.rad_unproc = QRadioButton("Unprocessed")
        self.rad_all = QRadioButton("All")
        self.lay_all.addWidget(self.rad_current)
        self.lay_all.addWidget(self.rad_unproc)
        self.lay_all.addWidget(self.rad_all)

        self.btn_extract = QPushButton("Extract")
        self.lay_all.addWidget(self.btn_extract)

        self.btngroup = QButtonGroup()
        self.btngroup.addButton(self.rad_current)
        self.btngroup.addButton(self.rad_unproc)
        self.btngroup.addButton(self.rad_all)

        self.rad_current.setChecked(True)

    def _initData(self):
        self.extractor = None
        self.has_template = False
        self.template_path = ""
        self.lab_temp_img.setVisible(self.has_template)
        self.btn_temp.setText(
            "Change template" if self.has_template else "Setup template"
        )

    def _initSignals(self):
        self.btn_extract.clicked.connect(self.doExtract)
        self.btn_temp.clicked.connect(self.start_template_setting.emit)

    def setInfoCollector(self, info_c: InfoCollector):
        self.info_c = info_c
        self.extractor = Extractor(self.info_c.work_dir, self.info_c.P_TEMPLATE)
        self.renewTemplate()

    def renewTemplate(self):
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
                f"Template size: {self.img_size.width()}x{self.img_size.height()}"
            )
        else:
            self.lab_temp_msg.setText("No template image found.")

    def doExtract(self):
        # check if template image exists
        if not self.info_c.hasTemplate():
            QMessageBox.warning(
                self.widget, "Warning", "No template image found.", QMessageBox.Ok
            )
            return

        # get image names to process
        if self.rad_current.isChecked():
            img_names = [self.info_c.img_name_current]
        elif self.rad_unproc.isChecked():
            img_names = self.info_c.getImageNamesByFilter(
                ([False], [True, False], [True, False])
            )
        elif self.rad_all.isChecked():
            img_names = self.info_c.getImageNames()
        else:
            return

        # start extraction
        wells_locs = []
        for img_name in img_names:
            wells_locs = self.extractor.wellExtract(img_name)
            self.writeResult(img_name, wells_locs)

        # show message box
        if len(img_names) > 1:
            QMessageBox.information(
                self.widget,
                "Info",
                f"Extraction finished. {len(img_names)} images processed.",
                QMessageBox.Ok,
            )

        self.finish_extraction.emit()

    def writeResult(self, img_name, wells_loc):
        with open(self.info_c.P_EXTARCT.format(img_name=img_name), "w") as f:
            for loc in wells_loc:
                x = loc[0]
                y = loc[1]
                w = self.extractor.t.shape[1]
                h = self.extractor.t.shape[0]
                f.write(f"{x},{y},{w},{h},{-1}\n")
