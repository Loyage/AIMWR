import os
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QMessageBox,
    QButtonGroup,
    QRadioButton,
    QProgressBar,
)

from ._modelGroupBox import ModelGroupBox
from .._collapsible import QCollapsible
from ..infoCollector import InfoCollector
from ..algorithm import ClassifyThread


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
