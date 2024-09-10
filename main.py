import os
import sys
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QFileDialog,
    QMessageBox,
    QScrollArea,
    QSpacerItem,
    QSizePolicy,
    QSplitter,
)
from PySide6.QtCore import QSettings
from AIMWR.painterLabel import PainterLabel
from AIMWR.msgBox import FolderMsgBox


class AIMWRApp(QApplication):

    def __init__(self, *args, **kwargs):
        super(AIMWRApp, self).__init__(*args, **kwargs)

        self.wgt_all = QWidget()
        self.wgt_all.setWindowTitle("AIMWR")
        self.wgt_all.showMaximized()

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
        self.spt_all.setStretchFactor(0, 6)
        self.spt_all.setStretchFactor(1, 4)

        self.lay_left = QVBoxLayout()
        self.wgt_left.setLayout(self.lay_left)
        self.lay_right = QVBoxLayout()
        self.scr_right.setLayout(self.lay_right)

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

        # lay_right: msg_box + box_folder + spacer
        self.box_folder = FolderMsgBox()
        self.spacer = QSpacerItem(20, 40, vData=QSizePolicy.Policy.Expanding)
        self.lay_right.addWidget(self.box_folder)
        self.lay_right.addItem(self.spacer)

    def _initData(self):
        self.settings = QSettings("AIMWR", "AIMWR")
        self.work_dir = self.settings.value("work_dir", "")
        self.image_name = self.settings.value("image_name", "")

        if not self.work_dir:
            self.chooseWorkspace()
        else:
            self.lin_workdir.setText(self.work_dir)
            self.box_folder.setWorkDir(self.work_dir)
            self.box_folder.update()

        if self.image_name:
            self.box_folder.setImage(self.image_name)
            self.painter.atImageChanged(os.path.join(self.work_dir, self.image_name))

    def _initSignals(self):
        self.btn_workdir.clicked.connect(self.chooseWorkspace)
        self.btn_zoom_in.clicked.connect(self.painter.zoomIn)
        self.btn_zoom_reset.clicked.connect(self.painter.zoomReset)
        self.btn_zoom_out.clicked.connect(self.painter.zoomOut)

        self.box_folder.select_image.connect(self.select_image)

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
        self.box_folder.setWorkDir(self.work_dir)
        self.box_folder.update()
        self.settings.setValue("work_dir", self.work_dir)
        self.cleanImage()

        # TODO: renew message box

    def select_image(self, image_name: str):
        self.image_name = image_name
        self.settings.setValue("image_name", self.image_name)
        self.painter.atImageChanged(os.path.join(self.work_dir, self.image_name))

    # def chooseImage(self):
    #     self.image_path, _ = QFileDialog.getOpenFileName(
    #         self.wgt_all, "Choose image", self.work_dir, "Images (*.png *.jpg)"
    #     )
    #     if self.image_path:
    #         self.image_dir, self.image_name = os.path.split(self.image_path)
    #         if self.image_dir != self.work_dir:
    #             self.warn("Image must be in the workspace")
    #             return
    #         self.lab_image.setText(self.image_name)
    #         self.settings.setValue("image_name", self.image_name)
    #         self.painter.atImageChanged(os.path.join(self.image_dir, self.image_name))
    #     else:
    #         self.warn("No image selected")
    #     # TODO: renew message box

    def cleanImage(self):
        self.image_name = ""
        self.settings.setValue("image_name", "")
        self.painter.atImageChanged("")

    def warn(self, msg):
        QMessageBox.warning(self.wgt_all, "Warning", msg, QMessageBox.Ok)


if __name__ == "__main__":
    app = AIMWRApp(sys.argv)
    sys.exit(app.exec())
