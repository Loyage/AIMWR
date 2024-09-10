import os
from ._collapsible import QCollapsible
from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QGroupBox,
    QLabel,
    QPushButton,
    QListView,
)
from PySide6.QtCore import QStringListModel, Signal


class FolderMsgBox(QCollapsible):
    select_image = Signal(str, name="select_image")

    def __init__(self, parent: QWidget | None = None):
        """
        A collapsible widget to show a list of images in the workspace.
        """

        super(FolderMsgBox, self).__init__(
            "Folder", parent, expandedIcon="▼", collapsedIcon="▶"
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

        # widget: status + image_list + lay_move + btn_update
        self.box_status = QGroupBox("Status")
        self.listview = QListView()
        self.lay_move = QHBoxLayout()
        self.btn_update = QPushButton("Update list")
        self.lay_all.addWidget(self.box_status)
        self.lay_all.addWidget(self.listview)
        self.lay_all.addLayout(self.lay_move)
        self.lay_all.addWidget(self.btn_update)

        # box_status
        self.lay_status = QVBoxLayout()
        self.box_status.setLayout(self.lay_status)
        self.lbl_status = QLabel("")

        # image_list
        self.list_model = QStringListModel()
        self.listview.setModel(self.list_model)

        # lay_move: btn_up + btn_down
        self.btn_up = QPushButton("▲")
        self.btn_down = QPushButton("▼")
        self.lay_move.addWidget(self.btn_up)
        self.lay_move.addWidget(self.btn_down)

    def _initData(self):
        self.work_dir = ""

    def _initSignals(self):
        self.btn_update.clicked.connect(self.update)
        self.listview.clicked.connect(self.atListClicked)
        self.btn_up.clicked.connect(self.moveUp)
        self.btn_down.clicked.connect(self.moveDown)

    def atListClicked(self, index):
        image_name = self.list_model.stringList()[index.row()]
        self.select_image.emit(image_name)

    def moveUp(self):
        idx_now = self.listview.currentIndex().row()
        if idx_now > 0:
            self.listview.setCurrentIndex(self.list_model.index(idx_now - 1, 0))
        else:
            self.listview.setCurrentIndex(self.list_model.index(0, 0))
        self.select_image.emit(
            self.list_model.stringList()[self.listview.currentIndex().row()]
        )

    def moveDown(self):
        idx_now = self.listview.currentIndex().row()
        if idx_now < len(self.list_model.stringList()) - 1:
            self.listview.setCurrentIndex(self.list_model.index(idx_now + 1, 0))
        else:
            self.listview.setCurrentIndex(
                self.list_model.index(len(self.list_model.stringList()) - 1, 0)
            )
        self.select_image.emit(
            self.list_model.stringList()[self.listview.currentIndex().row()]
        )

    def update(self):
        self._updateList()
        self._updateStatus()

    def _updateList(self):
        self.list_model.setStringList([])
        files = os.listdir(self.work_dir)
        image_filter = [".jpg", ".jpeg", ".png", ".bmp"]
        images = [f for f in files if os.path.splitext(f)[1].lower() in image_filter]
        self.list_model.setStringList(images)
        self.listview.setModel(self.list_model)

    def _updateStatus(self):
        self.num_images = len(self.list_model.stringList())
        self.text_status = f"Images: {self.num_images}"
        self.lbl_status.setText(f"Workspace: {self.work_dir}")
        self.lay_status.addWidget(self.lbl_status)

    def setWorkDir(self, work_dir: str):
        self.work_dir = work_dir
        self.update()

    def setImage(self, image_name: str):
        # fixme: when the list is empty, how to handle this?
        if image_name not in self.list_model.stringList():
            idx = 0
        else:
            idx = self.list_model.stringList().index(image_name)
        self.listview.setCurrentIndex(self.list_model.index(idx, 0))
        self.select_image.emit(image_name)
