from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGroupBox,
    QPushButton,
    QCheckBox,
    QLabel,
    QComboBox,
)
from PySide6.QtCore import Signal

from .._collapsible import QCollapsible
from ..infoCollector import InfoCollector


class EditToolBox(QCollapsible):
    change_source = Signal(name="change_source")
    start_edit = Signal(name="start_edit")
    finish_edit = Signal(name="finish_edit")
    classes_rechoose = Signal(name="classes_rechoose")

    def __init__(self, parent: QWidget | None = None):
        """
        A collapsible widget to show tools for edit classification result.
        """

        super(EditToolBox, self).__init__(
            "Edit Tool", parent, expandedIcon="▼", collapsedIcon="▶"
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

        # widget: comb_source + box_filter + comb_class + btn_edit_save
        self.box_status = QGroupBox("Status")
        self.comb_source = QComboBox()
        self.box_show = QGroupBox("Filter")
        self.btn_edit_save = QPushButton("Start editing")
        self.lab_tip = QLabel("Class to assign (Double click):")
        self.comb_class = QComboBox()
        self.lay_all.addWidget(self.box_status)
        self.lay_all.addWidget(self.comb_source)
        self.lay_all.addWidget(self.box_show)
        self.lay_all.addWidget(self.btn_edit_save)
        self.lay_all.addWidget(self.lab_tip)
        self.lay_all.addWidget(self.comb_class)
        self.lab_tip.setVisible(False)
        self.comb_class.setVisible(False)

        # box_status: show status of current image
        self.lay_status = QVBoxLayout()
        self.box_status.setLayout(self.lay_status)
        self.lab_extracted = QLabel("Extracted: No")
        self.lab_classified = QLabel("Classified: No")
        self.lab_edited = QLabel("Edited: No")
        self.lay_status.addWidget(self.lab_extracted)
        self.lay_status.addWidget(self.lab_classified)
        self.lay_status.addWidget(self.lab_edited)

        # box_filter: check boxes for class names, and a button to reselect
        self.lay_filter = QVBoxLayout()
        self.box_show.setLayout(self.lay_filter)
        self.btn_reselect = QPushButton("Reselect")
        self.lay_filter.addWidget(self.btn_reselect)
        self.btn_reselect.setVisible(False)

    def _initData(self):
        self.is_editing = False
        self.class_names = []
        self.ckb_classes = []

        self.btn_text = "Save result" if self.is_editing else "Start editing"
        self.btn_edit_save.setText(self.btn_text)

    def _initSignals(self):
        self.btn_reselect.clicked.connect(self.reselect)
        self.btn_edit_save.clicked.connect(self.editOrSave)
        self.comb_source.currentIndexChanged.connect(self.changeSource)
        self.comb_class.currentIndexChanged.connect(self.assignClass)

    def setInfoCollector(self, info_c: InfoCollector):
        self.info_c = info_c
        self.resetStatus()
        self.resetCombSource()
        self.resetLayFilter()
        self.resetCombClass()

    def resetStatus(self):
        img_name = self.info_c.img_name_current
        if not img_name:
            return
        extracted, classified, edited = self.info_c.img_status[img_name]

        self.lab_extracted.setText(f"Extracted: {'Yes' if extracted else 'No'}")
        self.lab_extracted.setStyleSheet(f"color: {'green' if extracted else 'red'}")

        self.lab_classified.setText(f"Classified: {'Yes' if classified else 'No'}")
        self.lab_classified.setStyleSheet(f"color: {'green' if classified else 'red'}")

        self.lab_edited.setText(f"Edited: {'Yes' if edited else 'No'}")
        self.lab_edited.setStyleSheet(f"color: {'green' if edited else 'red'}")

    def resetCombSource(self):
        if not self.info_c:
            return

        extracted, classified, edited = self.info_c.img_status[
            self.info_c.img_name_current
        ]

        self.comb_source.clear()
        self.comb_source.addItem("[No source]")
        if extracted:
            self.comb_source.addItem("Extraction")
        if classified:
            self.comb_source.addItem("Classification")
        if edited:
            self.comb_source.addItem("Edit")

    def resetLayFilter(self):
        class_names = self.info_c.class_names
        class_names_all = class_names.copy()
        class_names_all.insert(0, "[Unclassified]")
        if self.ckb_classes == []:
            # first time to reset
            for class_name in class_names_all:
                ckb = QCheckBox(class_name)
                ckb.setChecked(True)
                self.ckb_classes.append(ckb)
                self.lay_filter.addWidget(ckb)
                ckb.stateChanged.connect(self.repaint)
            self.btn_reselect.setVisible(len(class_names))

        else:
            # when class names are reset, reassign text and check state
            for idx, ckb in enumerate(self.ckb_classes):
                ckb.setText(class_names_all[idx])
                ckb.setChecked(True)

    def resetCombClass(self):
        self.comb_class.clear()
        self.comb_class.addItem("[Unclassified]")
        self.comb_class.addItems(self.info_c.class_names)

    def atClassNamesReset(self):
        self.resetCombSource()
        self.resetLayFilter()
        self.resetCombClass()

    def atImageChanged(self):
        self.resetStatus()
        self.resetCombSource()
        self.resetLayFilter()
        self.resetCombClass()

    def reselect(self):
        is_all_checked = all([ckb.isChecked() for ckb in self.ckb_classes])
        if not is_all_checked:
            for ckb in self.ckb_classes:
                ckb.setChecked(True)
        else:
            for ckb in self.ckb_classes:
                ckb.setChecked(False)

        self.repaint()

    def repaint(self):
        checked_idx = [
            idx - 1 for idx, ckb in enumerate(self.ckb_classes) if ckb.isChecked()
        ]
        self.info_c.classes_show = checked_idx
        self.classes_rechoose.emit()

    def changeSource(self):
        source_text = self.comb_source.currentText()
        self.info_c.source_rect = source_text
        self.change_source.emit()

    def assignClass(self):
        class_idx = self.comb_class.currentIndex()
        self.info_c.class_edit = class_idx - 1

    def editOrSave(self):
        self.is_editing = not self.is_editing

        self.comb_source.setEnabled(
            not self.is_editing
        )  # disable comb_class when editing

        self.btn_text = "Save result" if self.is_editing else "Start editing"
        self.btn_edit_save.setText(self.btn_text)

        self.lab_tip.setVisible(self.is_editing)
        self.comb_class.setVisible(self.is_editing)

        if self.is_editing:
            self.repaint()
            self.start_edit.emit()
        else:
            self.finish_edit.emit()
