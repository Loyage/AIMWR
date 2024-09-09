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

        self.initData()
        self.initUI()
        self.initSignals()

    def initData(self):
        self.settings = QSettings("AIMWR", "AIMWR")
        self.work_dir = self.settings.value("work_dir", "")
        self.image_name = self.settings.value("image_name", "")

        if not self.work_dir:
            self.chooseWorkspace()

    def initUI(self):
        self.lay_all = QHBoxLayout()
        self.spt_all = QSplitter()
        self.wgt_all.setLayout(self.lay_all)
        self.lay_all.addWidget(self.spt_all)

        # wgt_all: QWidget + QScrollArea
        self.wgt_left = QWidget()
        self.scr_right = QScrollArea()
        self.spt_all.addWidget(self.wgt_left)
        self.spt_all.addWidget(self.scr_right)
        self.lay_right = QVBoxLayout()
        self.scr_right.setLayout(self.lay_right)

        # wgt_left: QVBoxLayout + layout_left_workdir + layout_image_name + scroll_area + layout_left_controls
        self.lay_left = QVBoxLayout()
        self.wgt_left.setLayout(self.lay_left)
        self.layout_left_workdir = QHBoxLayout()
        self.layout_image_name = QHBoxLayout()
        self.scroll_area = QScrollArea()
        self.layout_left_controls = QHBoxLayout()
        self.lay_left.addLayout(self.layout_left_workdir)
        self.lay_left.addLayout(self.layout_image_name)
        self.lay_left.addWidget(self.scroll_area)
        self.lay_left.addLayout(self.layout_left_controls)
        self.lay_left.setStretch(0, 1)
        self.lay_left.setStretch(1, 1)
        self.lay_left.setStretch(2, 8)
        self.lay_left.setStretch(3, 1)

        # scroll_area: painter
        self.painter = PainterLabel()
        self.scroll_area.setWidget(self.painter)

        # layout_left_workdir: btn_workdir, lab_workdir
        self.btn_workdir = QPushButton("Choose workspace")
        self.lab_workdir = QLineEdit(self.work_dir)
        self.lab_workdir.setReadOnly(True)
        self.layout_left_workdir.addWidget(self.btn_workdir)
        self.layout_left_workdir.addWidget(self.lab_workdir)
        self.layout_left_workdir.setStretch(0, 2)
        self.layout_left_workdir.setStretch(1, 8)

        # layout_image_name: btn_image, lab_image
        self.btn_image = QPushButton("Choose image")
        self.lab_image = QLineEdit(self.image_name)
        self.lab_image.setReadOnly(True)
        self.layout_image_name.addWidget(self.btn_image)
        self.layout_image_name.addWidget(self.lab_image)
        self.layout_image_name.setStretch(0, 2)
        self.layout_image_name.setStretch(1, 8)

        # layout_left_controls:
        self.layout_left_controls.addWidget(QPushButton("Previous"))
        self.layout_left_controls.addWidget(QPushButton("Next"))

        # lay_right: msg_box, btn_save
        self.test_box = FolderMsgBox()
        self.spacer = QSpacerItem(20, 40, vData=QSizePolicy.Policy.Expanding)
        self.lay_right.addWidget(self.test_box)
        self.lay_right.addWidget(QPushButton("Save"))
        self.lay_right.addItem(self.spacer)

    def initSignals(self):
        self.btn_workdir.clicked.connect(self.chooseWorkspace)
        self.btn_image.clicked.connect(self.chooseImage)

    def chooseWorkspace(self):
        self.work_dir = QFileDialog.getExistingDirectory(
            self.wgt_all, "Choose workspace", self.work_dir
        )
        if self.work_dir:
            self.lab_workdir.setText(self.work_dir)
            self.settings.setValue("work_dir", self.work_dir)
            self.cleanImage()
        else:
            self.warn("No workspace selected")
        # TODO: renew message box

    def chooseImage(self):
        self.image_path, _ = QFileDialog.getOpenFileName(
            self.wgt_all, "Choose image", self.work_dir, "Images (*.png *.jpg)"
        )
        if self.image_path:
            self.image_dir, self.image_name = os.path.split(self.image_path)
            if self.image_dir != self.work_dir:
                self.warn("Image must be in the workspace")
                return
            self.lab_image.setText(self.image_name)
            self.settings.setValue("image_name", self.image_name)
            self.painter.atImageChanged(os.path.join(self.image_dir, self.image_name))
        else:
            self.warn("No image selected")
        # TODO: renew message box

    def cleanImage(self):
        self.image_name = ""
        self.settings.setValue("image_name", "")
        self.lab_image.setText(self.image_name)
        self.painter.atImageChanged("")

    def warn(self, msg):
        QMessageBox.warning(self.wgt_all, "Warning", msg, QMessageBox.Ok)


if __name__ == "__main__":
    app = AIMWRApp(sys.argv)
    sys.exit(app.exec())
