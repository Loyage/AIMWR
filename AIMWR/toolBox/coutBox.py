from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
)

from .._collapsible import QCollapsible
from ..infoCollector import InfoCollector


class CountBox(QCollapsible):
    def __init__(self, parent: QWidget | None = None):
        """
        A collapsible widget to show the count of images in the workspace.
        """

        super(CountBox, self).__init__(
            "Folder Count", parent, expandedIcon="▼", collapsedIcon="▶"
        )
        self._initUI()
        self._initData()

    def _initUI(self):
        self.widget = QWidget()
        self.setContent(self.widget)
        self.lay_all = QVBoxLayout()
        self.widget.setLayout(self.lay_all)
        self.collapse()

        self.lbl_img = QLabel("Images: 0")
        self.lbl_extracted = QLabel("Extracted: 0")
        self.lbl_classified = QLabel("Classified: 0")
        self.lbl_edited = QLabel("Edited: 0")

        self.lay_all.addWidget(self.lbl_img)
        self.lay_all.addWidget(self.lbl_extracted)
        self.lay_all.addWidget(self.lbl_classified)
        self.lay_all.addWidget(self.lbl_edited)

    def _initData(self):
        self.num_img = 0
        self.num_extracted = 0
        self.num_classified = 0
        self.num_edited = 0

    def setInfoCollector(self, info_c: InfoCollector):
        self.info_c = info_c
        self.renew()

    def renew(self):
        img_status = self.info_c.img_status
        img_extracted = [img for img in img_status if img_status[img][0]]
        img_classified = [img for img in img_status if img_status[img][1]]
        img_edited = [img for img in img_status if img_status[img][2]]
        self.num_img = len(img_status)
        self.num_extracted = len(img_extracted)
        self.num_classified = len(img_classified)
        self.num_edited = len(img_edited)

        self.lbl_img.setText(f"Images: {self.num_img}")
        self.lbl_extracted.setText(f"Extracted: {self.num_extracted}")
        self.lbl_classified.setText(f"Classified: {self.num_classified}")
        self.lbl_edited.setText(f"Edited: {self.num_edited}")
