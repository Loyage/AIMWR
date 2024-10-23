import os
from ._collapsible import QCollapsible
from .infoCollector import InfoCollector
from .algorithm import Extractor, ClassifyThread, TrainThread
from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QGroupBox,
    QLabel,
    QPushButton,
    QListWidget,
    QTextEdit,
    QMessageBox,
    QButtonGroup,
    QRadioButton,
    QLineEdit,
    QComboBox,
    QCheckBox,
    QFileDialog,
    QProgressBar,
)
from PySide6.QtCore import QSettings, Signal, Qt
from PySide6.QtGui import QPixmap
from ._colors import COLORS


# ImageList + BasicSettings(class setting, template setting) + CountBox + Extraction + Classification + EditTool(set showing settings) + TrainTool + TestTool
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
        idx_now = self.list_wid.currentIndex().row()
        if idx_now > 0:
            self.list_wid.setCurrentRow(idx_now - 1)
        else:
            self.list_wid.setCurrentRow(0)
        self.select_image.emit(self.list_wid.currentItem().text())

    def moveDown(self):
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
        self.lbl_temp_img.setVisible(self.has_template)
        self.text_class.setReadOnly(not self.is_resetting_class)
        self.btn_class.setText("OK" if self.is_resetting_class else "Reset class name")
        self.btn_temp.setText(
            "Change template" if self.has_template else "Setup template"
        )
        if self.has_template:
            self.path = self.info_c.P_TEMPLATE
            self.img = QPixmap(self.path)
            self.lbl_temp_img.setPixmap(self.img)
            self.lbl_temp_img.resize(self.lbl_temp_img.pixmap().size())
            self.img_size = self.lbl_temp_img.pixmap().size()
            self.lbl_temp_msg.setText(
                f"Template image: {self.img_size.width()}x{self.img_size.height()}"
            )
        else:
            self.lbl_temp_msg.setText("No template image found.")


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


class ExtractionBox(QCollapsible):
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

    def _initSignals(self):
        self.btn_extract.clicked.connect(self.extract)

    def setInfoCollector(self, info_c: InfoCollector):
        self.info_c = info_c
        self.extractor = Extractor(self.info_c.work_dir, self.info_c.P_TEMPLATE)

    def extract(self):
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


class ModelGroupBox(QGroupBox):
    model_chosen = Signal(name="model_chosen")

    def __init__(self, title: str, parent: QWidget | None = None):
        """
        A group box to show the model path and choose model button.
        Used in ClassificationBox, TrainToolBox and TestToolBox.
        """

        super(ModelGroupBox, self).__init__(title, parent)
        self._initUI()
        self._initData()
        self._initSignals()

    def _initUI(self):
        self.lay_all = QVBoxLayout()
        self.setLayout(self.lay_all)

        self.line_path = QLineEdit()
        self.btn_choose = QPushButton("Choose model")
        self.lbl_msg = QLabel()

        self.lay_all.addWidget(self.line_path)
        self.lay_all.addWidget(self.btn_choose)
        self.lay_all.addWidget(self.lbl_msg)

    def _initData(self):
        self.model_msg = "No model loaded."
        self.lbl_msg.setText(self.model_msg)

    def _initSignals(self):
        self.btn_choose.clicked.connect(self.chooseModel)

    def chooseModel(self):
        # get current directory
        current_dir = ""
        if self.line_path.text():
            current_dir = os.path.dirname(self.line_path.text())
        if not os.path.exists(current_dir):
            current_dir = ""

        # choose model
        model_path, _ = QFileDialog.getOpenFileName(
            self, "Choose model", current_dir, "Model files (*.pt, *.pth)"
        )
        if model_path:
            self.line_path.setText(model_path)
            self.model_msg = "Model loaded."
            self.lbl_msg.setText(self.model_msg)

        self.model_chosen.emit()

    def saveSettings(self, name: str):
        settings = QSettings("AIMWR", "AIMWR")
        settings.setValue(name, self.line_path.text())

    def loadSettings(self, name: str):
        settings = QSettings("AIMWR", "AIMWR")
        model_path = settings.value(name)
        if not model_path:
            return
        elif not os.path.exists(model_path):
            settings.setValue(name, "")
            return

        self.line_path.setText(model_path)
        self.model_msg = "Model loaded."
        self.lbl_msg.setText(self.model_msg)


class ClassificationBox(QCollapsible):
    def __init__(self, parent: QWidget | None = None):
        """
        A collapsible widget to show tools for image classification.
        """

        super(ClassificationBox, self).__init__(
            "Classification", parent, expandedIcon="▼", collapsedIcon="▶"
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

        # widget: box_model + rad_current + rad_unproc + rad_all + btn_classify + bar_classify
        self.box_model = ModelGroupBox("Model")
        self.rad_current = QRadioButton("Current")
        self.rad_unproc = QRadioButton("Unprocessed")
        self.rad_all = QRadioButton("All")
        self.btn_classify = QPushButton("Classify")
        self.bar_classify = QProgressBar()
        self.lay_all.addWidget(self.box_model)
        self.lay_all.addWidget(self.rad_current)
        self.lay_all.addWidget(self.rad_unproc)
        self.lay_all.addWidget(self.rad_all)
        self.lay_all.addWidget(self.btn_classify)
        self.lay_all.addWidget(self.bar_classify)

        self.rad_current.setChecked(True)

        # set group for radio buttons
        self.btngroup = QButtonGroup()
        self.btngroup.addButton(self.rad_current)
        self.btngroup.addButton(self.rad_unproc)
        self.btngroup.addButton(self.rad_all)

    def _initData(self):
        self.model_msg = "No model loaded."
        self.box_model.lbl_msg.setText(self.model_msg)

        self.box_model.loadSettings("classification_model")

    def _initSignals(self):
        self.box_model.model_chosen.connect(self.atModelChosen)
        self.btn_classify.clicked.connect(self.classify)

    def atModelChosen(self):
        self.box_model.saveSettings("classification_model")

    def setInfoCollector(self, info_c: InfoCollector):
        self.info_c = info_c
        self.renew()

    def setAiContainer(self, ai):
        self.ai = ai

    def classify(self):
        model_path = self.box_model.line_path.text()

        # check if ai_thread is not running
        if self.ai.thread and self.ai.thread.isRunning():
            QMessageBox.warning(
                self.widget,
                "Warning",
                "Classification or training is running.",
                QMessageBox.Ok,
            )
            return

        # check if model exists
        if not self.box_model.line_path.text():
            QMessageBox.warning(
                self.widget, "Warning", "No model loaded.", QMessageBox.Ok
            )
            return

        # get image names to classify
        if not os.path.exists(model_path):
            QMessageBox.warning(
                self.widget, "Warning", "Model file not found.", QMessageBox.Ok
            )
            return

        # get image names to classify
        if self.rad_current.isChecked():
            img_names = [self.info_c.img_name_current]
        elif self.rad_unproc.isChecked():
            img_names = self.info_c.getImageNamesByFilter(
                ([True], [False], [True, False])
            )  # get unclassified images
        elif self.rad_all.isChecked():
            img_names = self.info_c.getImageNamesByFilter(
                ([True], [True, False], [True, False])
            )
        else:
            return

        # check if there are images to classify
        if not img_names:
            QMessageBox.warning(
                self.widget, "Warning", "No images to classify.", QMessageBox.Ok
            )
            return

        # start classification thread
        self.ai.thread = ClassifyThread(self.info_c, model_path, img_names, self.parent)

        # if using CPU, ask for confirmation
        if self.ai.thread.isUsingCpu():
            res = QMessageBox.question(
                self.widget,
                "Warning",
                "CUDA not found, time-consuming. Continue?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if res == QMessageBox.No:
                return

        # connect signals
        self.ai.thread.finished.connect(self.finishClassify)
        # TODO: 确认功能是否正常
        self.ai.thread.complete.connect(self.updateBar)

        # start thread
        self.ai.thread.start()
        self.bar_classify.setVisible(True)

    def updateBar(self, idx, num):
        self.bar_classify.setValue(idx / num * 100)

    def stopClassify(self):
        self.ai.thread.stop()

    def finishClassify(self):
        QMessageBox.information(
            self.widget, "Info", "Classification finished.", QMessageBox.Ok
        )
        self.bar_classify.setValue(0)
        self.bar_classify.setVisible(False)

    def renew(self):
        img_status = self.info_c.img_status
        img_classified = [img for img in img_status if img_status[img][1]]
        img_extracted = [img for img in img_status if img_status[img][0]]
        self.num_classified = len(img_classified)
        self.num_extracted = len(img_extracted)

        self.box_model.lbl_msg.setText(self.model_msg)


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
        self.lbl_tip = QLabel("Class to assign (Double click):")
        self.comb_class = QComboBox()
        self.lay_all.addWidget(self.box_status)
        self.lay_all.addWidget(self.comb_source)
        self.lay_all.addWidget(self.box_show)
        self.lay_all.addWidget(self.btn_edit_save)
        self.lay_all.addWidget(self.lbl_tip)
        self.lay_all.addWidget(self.comb_class)
        self.lbl_tip.setVisible(False)
        self.comb_class.setVisible(False)

        # box_status: show status of current image
        self.lay_status = QVBoxLayout()
        self.box_status.setLayout(self.lay_status)
        self.lbl_extracted = QLabel("Extracted: No")
        self.lbl_classified = QLabel("Classified: No")
        self.lbl_edited = QLabel("Edited: No")
        self.lay_status.addWidget(self.lbl_extracted)
        self.lay_status.addWidget(self.lbl_classified)
        self.lay_status.addWidget(self.lbl_edited)

        # box_filter: check boxes for class names, and a button to reselect
        self.lay_filter = QVBoxLayout()
        self.box_show.setLayout(self.lay_filter)
        self.btn_reselect = QPushButton("Reselect")
        self.lay_filter.addWidget(self.btn_reselect)
        self.btn_reselect.setVisible(False)

    def _initData(self):
        self.is_editing = False
        self.class_names = []

        self.btn_text = "Save result" if self.is_editing else "Start editing"
        self.btn_edit_save.setText(self.btn_text)

    def _initSignals(self):
        self.btn_reselect.clicked.connect(self.reselect)
        self.btn_edit_save.clicked.connect(self.editOrSave)
        self.comb_source.currentIndexChanged.connect(self.changeSource)
        self.comb_class.currentIndexChanged.connect(self.assignClass)

    def setInfoCollector(self, info_c: InfoCollector):
        self.info_c = info_c
        self.resetUI()
        self.renewStatus()

    def renewStatus(self):
        img_name = self.info_c.img_name_current
        extracted, classified, edited = self.info_c.img_status[img_name]

        self.lbl_extracted.setText(f"Extracted: {'Yes' if extracted else 'No'}")
        self.lbl_extracted.setStyleSheet(f"color: {'green' if extracted else 'red'}")

        self.lbl_classified.setText(f"Classified: {'Yes' if classified else 'No'}")
        self.lbl_classified.setStyleSheet(f"color: {'green' if classified else 'red'}")

        self.lbl_edited.setText(f"Edited: {'Yes' if edited else 'No'}")
        self.lbl_edited.setStyleSheet(f"color: {'green' if edited else 'red'}")

    def resetUI(self):
        class_names = self.info_c.class_names

        # renew comb_source
        self.comb_source.clear()
        # TODO: 反映是否存在结果，并统计数量
        self.comb_source.addItems(
            ["[No source]", "Extraction", "Classification", "Edit"]
        )

        # renew box_filter
        self.ckb_classes = []
        class_names_all = class_names.copy()
        class_names_all.insert(0, "[Unclassified]")
        for class_name in class_names_all:
            ckb = QCheckBox(class_name)
            ckb.setChecked(True)
            self.ckb_classes.append(ckb)
            self.lay_filter.addWidget(ckb)
            ckb.stateChanged.connect(self.repaint)
        self.btn_reselect.setVisible(len(class_names))
        self.repaint()

        # renew comb_class
        self.comb_class.clear()
        self.comb_class.addItem("[Unclassified]")
        self.comb_class.addItems(class_names)

    def resetClass(self):
        class_names = self.info_c.class_names
        # reset all widgets in box_filter
        for i in range(self.lay_filter.count()):
            self.lay_filter.itemAt(i).widget().deleteLater()
        self.lay_filter.addWidget(self.btn_reselect)
        for class_name in class_names:
            ckb = QCheckBox(class_name)
            ckb.setChecked(True)
            self.ckb_classes.append(ckb)
            self.lay_filter.addWidget(ckb)
            ckb.stateChanged.connect(self.repaint)

        # reset comb_class
        self.comb_class.clear()
        self.comb_class.addItem("[Unclassified]")
        self.comb_class.addItems(class_names)

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

        self.btn_text = "Save result" if self.is_editing else "Start editing"
        self.btn_edit_save.setText(self.btn_text)

        self.lbl_tip.setVisible(self.is_editing)
        self.comb_class.setVisible(self.is_editing)

        if self.is_editing:
            self.repaint()
            self.start_edit.emit()
        else:
            self.finish_edit.emit()


class TrainToolBox(QCollapsible):
    def __init__(self, parent: QWidget | None = None):
        """
        A collapsible widget to show tools for model training.
        """

        super(TrainToolBox, self).__init__(
            "Train Tool", parent, expandedIcon="▼", collapsedIcon="▶"
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

        # widget: box_model + box_params + btn_train + bar_train + lbl_result
        self.box_model = ModelGroupBox("Model")
        self.box_params = QGroupBox("Parameters")
        self.btn_train = QPushButton("Train")
        self.bar_train = QProgressBar()
        self.lbl_result = QLabel()
        self.lay_all.addWidget(self.box_model)
        self.lay_all.addWidget(self.box_params)
        self.lay_all.addWidget(self.btn_train)
        self.lay_all.addWidget(self.bar_train)
        self.lay_all.addWidget(self.lbl_result)

        # box_params: choose model type, and parameters
        self.lay_params = QVBoxLayout()
        self.box_params.setLayout(self.lay_params)

        self.comb_model = QComboBox()
        self.comb_model.addItems(["MobileNet", "ResNet18", "ResNet50"])
        self.lay_params.addWidget(self.comb_model)

        self.lbl_epoch = QLabel("Max epochs:")
        self.line_epoch = QLineEdit()
        self.lbl_batch = QLabel("Batch size:")
        self.line_batch = QLineEdit()
        self.lay_params.addWidget(self.lbl_epoch)
        self.lay_params.addWidget(self.line_epoch)
        self.lay_params.addWidget(self.lbl_batch)
        self.lay_params.addWidget(self.line_batch)

    def _initData(self):
        self.model_msg = "No model loaded."
        self.box_model.lbl_msg.setText(self.model_msg)
        self.line_epoch.setText("1000")
        self.line_batch.setText("32")

        self.box_model.loadSettings("train_model")

    def _initSignals(self):
        self.box_model.model_chosen.connect(self.atModelChosen)
        self.btn_train.clicked.connect(self.train)

    def setInfoCollector(self, info_c: InfoCollector):
        self.info_c = info_c

    def setAiContainer(self, ai):
        self.ai = ai

    def atModelChosen(self):
        self.box_model.saveSettings("train_model")

        model_path = self.box_model.line_path.text()
        if not model_path:
            return

        model_name = model_path.split("/")[-1]
        self.pre_model_type = model_name.split("_")[-1]
        self.comb_model.setCurrentText(self.pre_model_type)

    def train(self):
        model_path = self.box_model.line_path.text()
        if self.ai.thread and self.ai.thread.isRunning():
            QMessageBox.warning(
                self.widget,
                "Warning",
                "Classification or training is running.",
                QMessageBox.Ok,
            )
            return

        if not model_path:
            model_type = self.comb_model.currentText()
        else:
            model_type = self.pre_model_type
        max_epoch = int(self.line_epoch.text())
        batch_size = int(self.line_batch.text())

        self.ai.thread = TrainThread(
            self.info_c, model_path, model_type, max_epoch, batch_size, self.parent
        )
        if self.ai.thread.isUsingCpu():
            res = QMessageBox.question(
                self.widget,
                "Warning",
                "CUDA not found, time-consuming. Continue?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if res == QMessageBox.No:
                return

        self.ai.thread.finished.connect(self.finishTrain)
        self.ai.thread.complete.connect(self.updateBar)
        self.ai.thread.start()

    def finishTrain(self):
        QMessageBox.information(
            self.widget, "Info", "Training finished.", QMessageBox.Ok
        )
        self.lbl_result.setText("Training finished. Model saved.")
        self.bar_train.setValue(0)

    def updateBar(self, epoch, idx, loss):
        self.bar_train.setValue(epoch / self.max_epoch * 100)
        self.lbl_result.setText(f"Epoch: {epoch}, Loss: {loss:.3f}")


# TODO: TestToolBox: choose model, test, save, result
# 直接对Edit后的结果进行Classify对比
class TestToolBox(QCollapsible):
    def __init__(self, parent: QWidget | None = None):
        """
        A collapsible widget to show tools for model testing.
        """

        super(TestToolBox, self).__init__(
            "Test Tool", parent, expandedIcon="▼", collapsedIcon="▶"
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

        # widget: box_model + btn_test + lbl_result
        self.box_model = ModelGroupBox("Model")
        self.btn_test = QPushButton("Test")
        self.lbl_result = QLabel()
        self.lay_all.addWidget(self.box_model)
        self.lay_all.addWidget(self.btn_test)
        self.lay_all.addWidget(self.lbl_result)

    def _initData(self):
        self.model_msg = "No model loaded."
        self.box_model.lbl_msg.setText(self.model_msg)

        self.box_model.loadSettings("test_model")

    def _initSignals(self):
        self.btn_test.clicked.connect(self.test)
        self.box_model.model_chosen.connect(self.atModelChosen)

    def atModelChosen(self):
        self.box_model.saveSettings("test_model")

    def setInfoCollector(self, info_c: InfoCollector):
        self.info_c = info_c

    def setAiContainer(self, ai):
        self.ai = ai

    def test(self):
        model_path = self.box_model.line_path.text()
        if not model_path:
            QMessageBox.warning(
                self.widget, "Warning", "No model loaded.", QMessageBox.Ok
            )
            return

        if self.ai.thread and self.ai.thread.isRunning():
            QMessageBox.warning(
                self.widget,
                "Warning",
                "Classification or training is running.",
                QMessageBox.Ok,
            )
            return

        self.ai.thread = ClassifyThread(self.info_c, model_path, self.widget)
        if self.ai.thread.isUsingCpu():
            res = QMessageBox.question(
                self.widget,
                "Warning",
                "CUDA not found, time-consuming. Continue?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if res == QMessageBox.No:
                return

        self.ai.thread.finished.connect(self.atClassifyFinished)
        self.ai.thread.start()

    def atClassifyFinished(self):
        self.countResult()
        QMessageBox.information(self.widget, "Info", "Test finished.", QMessageBox.Ok)
        self.lbl_result.setText("Test finished.")

    def countResult(self):
        img_status = self.info_c.img_status
        img_clas_edited = [
            img for img in img_status if img_status[img][1] and img_status[img][2]
        ]
        clas_labels_all = []
        edit_labels_all = []
        for img_name in img_clas_edited:
            clas_path = self.info_c.P_CLASSIFY.format(img_name=img_name)
            edit_path = self.info_c.P_EDIT.format(img_name=img_name)
            with open(clas_path, "r") as f:
                clas_lines = f.readlines()
            with open(edit_path, "r") as f:
                edit_lines = f.readlines()
            clas_labels = [int(line.split(",")[-1]) for line in clas_lines]
            edit_labels = [int(line.split(",")[-1]) for line in edit_lines]
            clas_labels_all.extend(clas_labels)
            edit_labels_all.extend(edit_labels)

        # calculate accuracy
        correct = 0
        total = len(clas_labels_all)
        for clas_label, edit_label in zip(clas_labels_all, edit_labels_all):
            if clas_label == edit_label:
                correct += 1
        accuracy = correct / total * 100
        self.lbl_result.setText(f"Accuracy: {accuracy:.2f}%")
        return accuracy
