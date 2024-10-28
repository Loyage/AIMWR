from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGroupBox,
    QPushButton,
    QLabel,
    QProgressBar,
    QComboBox,
    QLineEdit,
    QMessageBox,
)

from ._modelGroupBox import ModelGroupBox
from .._collapsible import QCollapsible
from ..infoCollector import InfoCollector
from ..algorithm import TrainThread


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

        # widget: box_model + box_params + btn_train + bar_train + lab_result
        self.box_model = ModelGroupBox("Model")
        self.box_params = QGroupBox("Parameters")
        self.btn_train = QPushButton("Train")
        self.bar_train = QProgressBar()
        self.lab_result = QLabel()
        self.lay_all.addWidget(self.box_model)
        self.lay_all.addWidget(self.box_params)
        self.lay_all.addWidget(self.btn_train)
        self.lay_all.addWidget(self.bar_train)
        self.lay_all.addWidget(self.lab_result)

        # box_params: choose model type, and parameters
        self.lay_params = QVBoxLayout()
        self.box_params.setLayout(self.lay_params)

        self.comb_model = QComboBox()
        self.comb_model.addItems(["MobileNet", "ResNet18", "ResNet50"])
        self.lay_params.addWidget(self.comb_model)

        self.lab_epoch = QLabel("Max epochs:")
        self.line_epoch = QLineEdit()
        self.lab_batch = QLabel("Batch size:")
        self.line_batch = QLineEdit()
        self.lay_params.addWidget(self.lab_epoch)
        self.lay_params.addWidget(self.line_epoch)
        self.lay_params.addWidget(self.lab_batch)
        self.lay_params.addWidget(self.line_batch)

    def _initData(self):
        self.model_msg = "No model loaded."
        self.box_model.lab_msg.setText(self.model_msg)
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
        self.lab_result.setText("Training finished. Model saved.")
        self.bar_train.setValue(0)

    def updateBar(self, epoch, idx, loss):
        self.bar_train.setValue(epoch / self.max_epoch * 100)
        self.lab_result.setText(f"Epoch: {epoch}, Loss: {loss:.3f}")
