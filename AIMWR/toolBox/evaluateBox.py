from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QPushButton,
    QMessageBox,
)

from .._collapsible import QCollapsible
from ..infoCollector import InfoCollector
from ..algorithm import ClassifyThread


class EvaluateBox(QCollapsible):
    def __init__(self, parent: QWidget | None = None):
        """
        A collapsible widget to show tools for model testing.
        """

        super(EvaluateBox, self).__init__(
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

    def _initData(self):
        pass

    def _initSignals(self):
        pass

    def setInfoCollector(self, info_c: InfoCollector):
        self.info_c = info_c

    def evaluate(self):
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
        self.lab_result.setText(f"Accuracy: {accuracy:.2f}%")
        return accuracy
