import os
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGroupBox,
    QPushButton,
    QLabel,
    QLineEdit,
    QFileDialog,
)
from PySide6.QtCore import Signal, QSettings


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
        self.lab_msg = QLabel()

        self.lay_all.addWidget(self.line_path)
        self.lay_all.addWidget(self.btn_choose)
        self.lay_all.addWidget(self.lab_msg)

    def _initData(self):
        self.model_msg = "No model loaded."
        self.lab_msg.setText(self.model_msg)

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
            self.lab_msg.setText(self.model_msg)

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
        self.lab_msg.setText(self.model_msg)
