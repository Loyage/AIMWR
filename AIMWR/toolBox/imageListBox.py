from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGroupBox,
    QPushButton,
    QListWidget,
    QHBoxLayout,
    QCheckBox,
    QLabel,
)
from PySide6.QtCore import Signal

from .._collapsible import QCollapsible
from ..infoCollector import InfoCollector


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

        # widget: btn_reset_filter + box_filter + image_list + lay_move + btn_update
        self.box_filter = QGroupBox("Filter")
        self.btn_reset_filter = QPushButton("Reset filter")
        self.list_wid = QListWidget()
        self.lay_move = QHBoxLayout()
        self.btn_update = QPushButton("Update list")
        self.lay_all.addWidget(self.btn_reset_filter)
        self.lay_all.addWidget(self.box_filter)
        self.lay_all.addWidget(self.list_wid)
        self.lay_all.addLayout(self.lay_move)
        # self.lay_all.addWidget(self.btn_update)

        # box_filter
        self._initUIFilter()

        # lay_move: btn_up + btn_down
        self.btn_up = QPushButton("▲")
        self.btn_down = QPushButton("▼")
        self.lay_move.addWidget(self.btn_up)
        self.lay_move.addWidget(self.btn_down)

    def _initUIFilter(self):
        self.lay_filter = QVBoxLayout()
        self.box_filter.setLayout(self.lay_filter)

        # Extracted
        self.lbl_flt_extract = QLabel("Extracted:")
        self.lay_flt_extract = QHBoxLayout()
        self.lay_filter.addWidget(self.lbl_flt_extract)
        self.lay_filter.addLayout(self.lay_flt_extract)

        self.ckb_flt_extract_yes = QCheckBox("Yes")
        self.ckb_flt_extract_no = QCheckBox("No")
        self.lay_flt_extract.addWidget(self.ckb_flt_extract_yes)
        self.lay_flt_extract.addWidget(self.ckb_flt_extract_no)

        # Classified
        self.lbl_flt_classify = QLabel("Classified:")
        self.lay_flt_classify = QHBoxLayout()
        self.lay_filter.addWidget(self.lbl_flt_classify)
        self.lay_filter.addLayout(self.lay_flt_classify)

        self.ckb_flt_classify_yes = QCheckBox("Yes")
        self.ckb_flt_classify_no = QCheckBox("No")
        self.lay_flt_classify.addWidget(self.ckb_flt_classify_yes)
        self.lay_flt_classify.addWidget(self.ckb_flt_classify_no)

        # Edited
        self.lbl_flt_edit = QLabel("Edited:")
        self.lay_flt_edit = QHBoxLayout()
        self.lay_filter.addWidget(self.lbl_flt_edit)
        self.lay_filter.addLayout(self.lay_flt_edit)

        self.ckb_flt_edit_yes = QCheckBox("Yes")
        self.ckb_flt_edit_no = QCheckBox("No")
        self.lay_flt_edit.addWidget(self.ckb_flt_edit_yes)
        self.lay_flt_edit.addWidget(self.ckb_flt_edit_no)

        # set all checkboxes to checked
        self.ckb_flt_extract_yes.setChecked(True)
        self.ckb_flt_extract_no.setChecked(True)
        self.ckb_flt_classify_yes.setChecked(True)
        self.ckb_flt_classify_no.setChecked(True)
        self.ckb_flt_edit_yes.setChecked(True)
        self.ckb_flt_edit_no.setChecked(True)

    def _initData(self):
        self.work_dir = ""

    def _initSignals(self):
        self.list_wid.clicked.connect(self.atListClicked)
        self.btn_up.clicked.connect(self.moveUp)
        self.btn_down.clicked.connect(self.moveDown)
        self.btn_update.clicked.connect(self.renew)

        self.ckb_flt_extract_yes.stateChanged.connect(self.renew)
        self.ckb_flt_extract_no.stateChanged.connect(self.renew)
        self.ckb_flt_classify_yes.stateChanged.connect(self.renew)
        self.ckb_flt_classify_no.stateChanged.connect(self.renew)
        self.ckb_flt_edit_yes.stateChanged.connect(self.renew)
        self.ckb_flt_edit_no.stateChanged.connect(self.renew)

        self.btn_reset_filter.clicked.connect(self.resetFilter)

    def setInfoCollector(self, info_c: InfoCollector):
        self.info_c = info_c
        self.work_dir = self.info_c.work_dir
        self.renew()

    def atListClicked(self, index):
        image_name = self.list_wid.currentItem().text()
        self.select_image.emit(image_name)

    def moveUp(self):
        if self.list_wid.count() == 0:
            return
        idx_now = self.list_wid.currentIndex().row()
        if idx_now > 0:
            self.list_wid.setCurrentRow(idx_now - 1)
        else:
            self.list_wid.setCurrentRow(0)
        self.select_image.emit(self.list_wid.currentItem().text())

    def moveDown(self):
        if self.list_wid.count() == 0:
            return
        idx_now = self.list_wid.currentIndex().row()
        if idx_now < self.list_wid.count() - 1:
            self.list_wid.setCurrentRow(idx_now + 1)
        else:
            self.list_wid.setCurrentRow(self.list_wid.count() - 1)
        self.select_image.emit(self.list_wid.currentItem().text())

    def resetFilter(self):
        self.ckb_flt_extract_yes.setChecked(True)
        self.ckb_flt_extract_no.setChecked(True)
        self.ckb_flt_classify_yes.setChecked(True)
        self.ckb_flt_classify_no.setChecked(True)
        self.ckb_flt_edit_yes.setChecked(True)
        self.ckb_flt_edit_no.setChecked(True)
        self.renew()

    def renew(self):
        # # renew checkbox to display
        # extract_yes = self.ckb_flt_extract_yes.isChecked()
        # self.ckb_flt_classify_yes.setEnabled(extract_yes)
        # self.ckb_flt_classify_no.setEnabled(extract_yes)
        # self.ckb_flt_edit_yes.setEnabled(extract_yes)
        # self.ckb_flt_edit_no.setEnabled(extract_yes)

        # renew list
        self.list_wid.clear()
        _filter = ([], [], [])
        if self.ckb_flt_extract_yes.isChecked():
            _filter[0].append(True)
        if self.ckb_flt_extract_no.isChecked():
            _filter[0].append(False)
        if self.ckb_flt_classify_yes.isChecked():
            _filter[1].append(True)
        if self.ckb_flt_classify_no.isChecked():
            _filter[1].append(False)
        if self.ckb_flt_edit_yes.isChecked():
            _filter[2].append(True)
        if self.ckb_flt_edit_no.isChecked():
            _filter[2].append(False)

        image_names = self.info_c.getImageNamesByFilter(_filter)
        self.list_wid.addItems(image_names)

        # choose image if it is in the list
        if self.info_c.img_name_current in image_names:
            idx = image_names.index(self.info_c.img_name_current)
            self.list_wid.setCurrentRow(idx)
            self.select_image.emit(self.info_c.img_name_current)

    def setImage(self, image_name: str):
        # FIXME: when the list is empty, how to handle this?
        string_list = [
            self.list_wid.item(i).text() for i in range(self.list_wid.count())
        ]
        if image_name not in string_list:
            idx = 0
        else:
            idx = string_list.index(image_name)
        self.list_wid.setCurrentRow(idx)
        self.select_image.emit(image_name)
