import os
import sys
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLineEdit,
    QFileDialog,
    QMessageBox,
    QScrollArea,
    QSpacerItem,
    QSizePolicy,
    QSplitter,
)
from PySide6.QtCore import QSettings, Qt
from PySide6.QtGui import QPixmap
from AIMWR.painterLabel import PainterLabel
from AIMWR.toolBox import (
    ImageListBox,
    BasicSettingBox,
    CountBox,
    ExtractionBox,
    ClassificationBox,
    EditToolBox,
    TrainToolBox,
)
from AIMWR.infoCollector import InfoCollector
from AIMWR.algorithm import AiContainer


class AIMWRApp(QApplication):

    def __init__(self, *args, **kwargs):
        super(AIMWRApp, self).__init__(*args, **kwargs)

        self.wgt_all = QWidget()
        self.wgt_all.setWindowTitle("AIMWR")

        self._initUI()
        self._initData()
        self._initSignals()

    def _initUI(self):
        self.lay_all = QHBoxLayout()
        self.spt_all = QSplitter()
        self.wgt_all.setLayout(self.lay_all)
        self.lay_all.addWidget(self.spt_all)

        # wgt_all: wgt_left | scr_right
        self.wgt_left = QWidget()
        self.scr_right = QScrollArea()
        self.spt_all.addWidget(self.wgt_left)
        self.spt_all.addWidget(self.scr_right)
        self.spt_all.setStretchFactor(0, 3)
        self.spt_all.setStretchFactor(1, 7)

        self.lay_left = QVBoxLayout()
        self.wgt_left.setLayout(self.lay_left)
        self.wgt_right = QWidget()
        self.lay_right = QVBoxLayout()
        self.scr_right.setWidget(self.wgt_right)
        self.wgt_right.setLayout(self.lay_right)
        self.scr_right.setWidgetResizable(True)

        # wgt_left: work_dir + painter + control
        self.lay_work_dir = QHBoxLayout()
        self.scr_painter = QScrollArea()
        self.lay_control = QHBoxLayout()
        self.lay_left.addLayout(self.lay_work_dir)
        self.lay_left.addWidget(self.scr_painter)
        self.lay_left.addLayout(self.lay_control)
        self.lay_left.setStretch(0, 1)
        self.lay_left.setStretch(1, 1)
        self.lay_left.setStretch(2, 8)
        self.lay_left.setStretch(3, 1)

        # work_dir: button | line_edit
        self.btn_workdir = QPushButton("Choose workspace")
        self.lin_workdir = QLineEdit("")
        self.lin_workdir.setReadOnly(True)
        self.lay_work_dir.addWidget(self.btn_workdir)
        self.lay_work_dir.addWidget(self.lin_workdir)
        self.lay_work_dir.setStretch(0, 2)
        self.lay_work_dir.setStretch(1, 8)

        # painter: painter_label
        self.painter = PainterLabel()
        self.scr_painter.setWidget(self.painter)

        # control: zoom_in | zoom_reset | zoom_out
        self.btn_zoom_in = QPushButton("Zoom in")
        self.btn_zoom_reset = QPushButton("Zoom reset")
        self.btn_zoom_out = QPushButton("Zoom out")
        self.lay_control.addWidget(self.btn_zoom_in)
        self.lay_control.addWidget(self.btn_zoom_reset)
        self.lay_control.addWidget(self.btn_zoom_out)

        # lay_right: img_list + basic_setting + extraction + spacer
        self.box_img_list = ImageListBox(self.wgt_all)
        self.box_setting = BasicSettingBox(self.wgt_all)
        self.box_count = CountBox(self.wgt_all)
        self.box_extraction = ExtractionBox(self.wgt_all)
        self.box_classification = ClassificationBox(self.wgt_all)
        self.box_edit = EditToolBox(self.wgt_all)
        self.box_train = TrainToolBox(self.wgt_all)
        self.spacer = QSpacerItem(20, 40, vData=QSizePolicy.Policy.Expanding)
        self.lay_right.addWidget(self.box_img_list)
        self.lay_right.addWidget(self.box_setting)
        self.lay_right.addWidget(self.box_count)
        self.lay_right.addWidget(self.box_extraction)
        self.lay_right.addWidget(self.box_classification)
        self.lay_right.addWidget(self.box_edit)
        self.lay_right.addWidget(self.box_train)
        self.lay_right.addItem(self.spacer)

        self.box_img_list.setVisible(False)
        self.box_setting.setVisible(False)
        self.box_count.setVisible(False)
        self.box_extraction.setVisible(False)
        self.box_classification.setVisible(False)
        self.box_edit.setVisible(False)
        self.box_train.setVisible(False)

        # show maximized
        self.wgt_all.showMaximized()

    def _initData(self):
        self.info_c = None
        self.settings = QSettings("AIMWR", "AIMWR")
        self.work_dir = self.settings.value("work_dir", "")
        self.image_name = self.settings.value("image_name", "")
        self.model_dir = self.settings.value("model_dir", "")

        self._initAiContainer()
        self._initWorkDir()
        self._initImageName()
        self._initModelDir()

    def _initAiContainer(self):
        self.ai = AiContainer()
        self.box_classification.setAiContainer(self.ai)
        self.box_train.setAiContainer(self.ai)

    def _initWorkDir(self):
        if not self.work_dir:
            return
        elif not os.path.exists(self.work_dir):
            self.warn("Workspace not exists")
            self.work_dir = ""
            self.settings.setValue("work_dir", "")
        else:
            self.lin_workdir.setText(self.work_dir)
            self.setupInfoCollector(InfoCollector(self.work_dir))

    def _initImageName(self):
        is_image_name_exist = os.path.exists(
            os.path.join(self.work_dir, self.image_name)
        )
        if not is_image_name_exist:
            self.warn("Image not exists")
            self.image_name = ""
            self.settings.setValue("image_name", "")
        elif self.image_name:
            self.box_img_list.setImage(self.image_name)
            if self.info_c:
                self.info_c.img_name_current = self.image_name
            self.painter.atImageChanged()
        else:
            self.box_img_list.renew()

    def _initModelDir(self):
        if not self.model_dir:
            return
        elif not os.path.exists(self.model_dir):
            self.model_dir = ""
            self.settings.setValue("model_dir", "")
        else:
            if self.info_c:
                self.info_c.model_dir = self.model_dir

    def _initSignals(self):
        self.btn_workdir.clicked.connect(self.chooseWorkspace)
        self.btn_zoom_in.clicked.connect(self.painter.zoomIn)
        self.btn_zoom_reset.clicked.connect(self.painter.zoomReset)
        self.btn_zoom_out.clicked.connect(self.painter.zoomOut)

        self.box_img_list.select_image.connect(self.select_image)
        self.box_setting.start_template_setting.connect(self.start_template_setting)
        self.box_setting.update_class_setting.connect(self.box_edit.resetClass)
        self.box_extraction.finish_extraction.connect(self.finish_extraction)
        self.box_edit.change_source.connect(self.painter.resetRectList)
        self.box_edit.start_edit.connect(self.start_edit)
        self.box_edit.finish_edit.connect(self.finish_edit)
        self.box_edit.classes_rechoose.connect(self.classes_rechoose)

        self.painter.finish_template_setting.connect(self.finish_template_setting)

    def chooseWorkspace(self):
        self.work_dir = QFileDialog.getExistingDirectory(
            self.wgt_all, "Choose workspace", self.work_dir
        )
        if not self.work_dir:
            self.warn("No workspace selected")
            return

        if not os.path.exists(os.path.join(self.work_dir, "AIMWR")):
            # 弹出提示框，询问是否创建文件夹
            result = QMessageBox.question(
                self.wgt_all,
                "Create folder",
                "For the first time, you need to create a folder named 'AIMWR' in the workspace.",
            )
            if result == QMessageBox.Yes:
                os.makedirs(os.path.join(self.work_dir, "AIMWR"))
            else:
                return

        self.lin_workdir.setText(self.work_dir)
        self.settings.setValue("work_dir", self.work_dir)
        self.cleanImage()
        self.setupInfoCollector(InfoCollector(self.work_dir))
        self.box_img_list.renew()

    def setupInfoCollector(self, info_c: InfoCollector):
        self.info_c = info_c
        self.info_c.img_name_current = self.image_name

        self.box_img_list.setInfoCollector(info_c)
        self.box_setting.setInfoCollector(info_c)
        self.box_count.setInfoCollector(info_c)
        self.box_extraction.setInfoCollector(info_c)
        self.box_classification.setInfoCollector(info_c)
        self.box_edit.setInfoCollector(info_c)
        self.box_train.setInfoCollector(info_c)
        self.painter.setInfoCollector(info_c)

        self.box_img_list.setVisible(True)
        self.box_setting.setVisible(True)
        self.box_count.setVisible(True)
        self.box_extraction.setVisible(True)
        self.box_classification.setVisible(True)
        self.box_train.setVisible(True)
        self.box_edit.setVisible(True)

    def select_image(self, image_name: str):
        self.image_name = image_name
        self.info_c.img_name_current = image_name
        self.settings.setValue("image_name", self.image_name)
        self.painter.atImageChanged()

    def start_template_setting(self):
        self.painter.setDragState()
        # disable other buttons
        self.lay_right.setEnabled(False)

    def finish_template_setting(self, pixmap: QPixmap):
        self.painter.setNormalState()
        # enable other buttons
        self.lay_right.setEnabled(True)

        if not self.image_name:
            self.warn("No image selected")
            return

        result = QMessageBox.question(
            self.wgt_all,
            "Confirm",
            "Are you sure to set this image as the template?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if result == QMessageBox.No:
            return

        # save template img
        pixmap.save(self.info_c.P_TEMPLATE)
        self.box_setting.renew()

        # reset template image in extractor
        self.box_extraction.extractor.resetTemplate(self.info_c.P_TEMPLATE)

    def finish_extraction(self):
        self.painter.resetRectList()
        self.renew()

    def start_edit(self):
        self.painter.setEditState()

    def finish_edit(self):
        self.painter.setNormalState()
        self.painter.atEditFinish()
        self.renew()

    def classes_rechoose(self):
        self.painter.resetRectList()

    def cleanImage(self):
        self.image_name = ""
        self.settings.setValue("image_name", "")
        if self.info_c:
            self.info_c.img_name_current = None
        self.painter.atImageChanged()

    def renew(self):
        self.box_img_list.renew()
        self.box_setting.renew()
        self.box_classification.renew()
        self.painter.atImageChanged()

    def warn(self, msg):
        QMessageBox.warning(self.wgt_all, "Warning", msg, QMessageBox.Ok)


if __name__ == "__main__":
    app = AIMWRApp(sys.argv)
    sys.exit(app.exec())
