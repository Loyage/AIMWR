from ._collapsible import QCollapsible
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGroupBox,
    QLabel,
    QPushButton,
    QGridLayout,
)


class FolderMsgBox(QCollapsible):
    def __init__(self, parent: QWidget | None = None):
        super(FolderMsgBox, self).__init__(
            "Folder messages", parent, expandedIcon="▼", collapsedIcon="▶"
        )

        self.widget = QWidget()
        self.setContent(self.widget)
        self.collapse()

        self.vl = QVBoxLayout()
        self.widget.setLayout(self.vl)

        self.status_box = QGroupBox("Status")

        self.status_box.setLayout(QVBoxLayout())
        self.status_box.layout().addWidget(QLabel("No workspace selected"))
        self.vl.addWidget(self.status_box)
        self.vl.addWidget(QPushButton("Choose workspace"))
