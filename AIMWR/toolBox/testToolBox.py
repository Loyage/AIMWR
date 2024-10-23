from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QPushButton,
    QMessageBox,
)

from ._modelGroupBox import ModelGroupBox
from .._collapsible import QCollapsible
from ..infoCollector import InfoCollector
from ..algorithm import ClassifyThread


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
