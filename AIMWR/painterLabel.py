import os
from PySide6.QtWidgets import QLabel, QWidget, QGraphicsOpacityEffect
from PySide6.QtCore import Qt, QPoint, Signal, QRect, QPoint
from PySide6.QtGui import QMouseEvent, QPainter, QPen, QPixmap
from ._colors import COLORS


def posTranImg(pos, zoom):
    return pos / zoom


def posTranScreen(pos, zoom):
    return pos * zoom


class PainterLabel(QLabel):
    """
    My custom label widget for painting circles on images.
    """

    finish_template_setting = Signal(QPixmap, name="finish_template_setting")

    NORMAL = 0
    WAITING = 1
    DRAGGING = 2
    EDITING = 3

    def __init__(self, parent=None):
        super(PainterLabel, self).__init__(parent)

        self.state = self.NORMAL
        self.zoom = 1.0
        self.img_ori = None
        self.img_show = None
        self.rect_temp = None
        self.rect_class_list = []
        self.rect_class_list_ori = []
        self.rect_class_list_edit = []
        self.painter = QPainter()
        self.info_c = None
        self.img_path = None

    def setInfoCollector(self, info_c):
        self.info_c = info_c

    def atImageChanged(self):
        if not self.info_c:
            return
        if not self.info_c.img_name_current:
            return

        self.img_path = os.path.join(self.info_c.work_dir, self.info_c.img_name_current)
        self.resetRectList()

    def resetRectList(self):
        self.rect_class_list.clear()
        if self.state == self.NORMAL:
            self.setRectNormal()
        elif self.state == self.EDITING:
            self.setRectEditing()
        else:
            return

        if not self.img_path:
            self.clear()
            self.is_paintable = False
        else:
            try:
                self.img_ori = QPixmap(self.img_path)
                self.reshowImage()
            except Exception as e:
                print(e)
                self.clear()
                self.is_paintable = False

    def setRectNormal(self):
        if self.info_c.rect_source == "Edit":
            res_clas_list = self.info_c.getEdit(self.info_c.img_name_current)
        elif self.info_c.rect_source == "Classification":
            res_clas_list = self.info_c.getClassified(self.info_c.img_name_current)
        elif self.info_c.rect_source == "Extraction":
            res_clas_list = self.info_c.getExtracted(self.info_c.img_name_current)
        else:
            res_clas_list = []

        rect_class_list_temp = []
        for x, y, w, h, clas in res_clas_list:
            rect = QRect(QPoint(x, y), QPoint(x + w, y + h))
            rect_class_list_temp.append((rect, clas))

        self.rect_class_list = self.getFilterRectList(rect_class_list_temp)

    def setRectEditing(self):
        self.rect_class_list = self.getFilterRectList(self.rect_class_list_edit)

    def getFilterRectList(self, rect_class_list):
        classes_show = self.info_c.classes_show
        return [(rect, clas) for rect, clas in rect_class_list if clas in classes_show]

    def zoomIn(self):
        if self.state == self.EDITING:
            return
        self.zoom *= 1.1
        self.reshowImage()

    def zoomOut(self):
        if self.state == self.EDITING:
            return
        self.zoom /= 1.1
        self.reshowImage()

    def zoomReset(self):
        if self.state == self.EDITING:
            return
        self.zoom = 1.0
        self.reshowImage()

    def setNormalState(self):
        self.state = self.NORMAL
        self.setCursor(Qt.ArrowCursor)

    def setDragState(self):
        self.state = self.WAITING
        self.setCursor(Qt.CrossCursor)

    def reshowImage(self):
        self.img_show = self.img_ori.scaled(
            self.img_ori.size() * self.zoom, Qt.AspectRatioMode.KeepAspectRatio
        )
        self.resize(self.img_show.size())
        self.setPixmap(self.img_show)

    def mousePressEvent(self, ev: QMouseEvent) -> None:
        if ev.button() == Qt.RightButton:
            return

        if self.state == self.NORMAL or self.state == self.EDITING:
            return

        if self.state == self.WAITING:
            self.state = self.DRAGGING
            self.pos_ori = ev.pos()

    def mouseMoveEvent(self, ev: QMouseEvent) -> None:
        if self.state == self.DRAGGING:
            self.rect_temp = QRect(self.pos_ori, ev.pos())
            self.update()

    def mouseReleaseEvent(self, ev: QMouseEvent) -> None:
        if self.state == self.DRAGGING:
            pos1 = posTranImg(self.pos_ori, self.zoom)
            pos2 = posTranImg(ev.pos(), self.zoom)
            img_temp = self.img_ori.copy(
                pos1.x(), pos1.y(), pos2.x() - pos1.x(), pos2.y() - pos1.y()
            )
            self.finish_template_setting.emit(img_temp)

            self.rect_temp = None
            self.update()

    def mouseDoubleClickEvent(self, ev: QMouseEvent) -> None:
        if self.state != self.EDITING:
            return

        pos = posTranImg(ev.pos(), self.zoom)
        new_rect_class_list = []
        for rect, clas in self.rect_class_list_edit:
            if rect.contains(pos):
                self.rect_class_list_edit.remove((rect, clas))
                new_rect_class_list.append((rect, self.info_c.class_edit))
        self.rect_class_list_edit.extend(new_rect_class_list)

        self.resetRectList()
        self.update()
        return

    def atEditStart(self):
        self.state = self.EDITING
        self.setCursor(Qt.PointingHandCursor)
        self.rect_class_list_ori = self.rect_class_list.copy()
        self.rect_class_list_edit = self.rect_class_list.copy()

    def atEditFinish(self):
        self.state = self.NORMAL
        self.saveEdit()

        self.rect_class_list = self.rect_class_list_ori.copy()
        self.rect_class_list_ori.clear()
        self.rect_class_list_edit.clear()

        self.setRectNormal()

    def saveEdit(self):
        edit_path = self.info_c.P_EDIT.format(img_name=self.info_c.img_name_current)
        with open(edit_path, "w") as f:
            for rect, clas in self.rect_class_list_edit:
                pos1 = rect.topLeft()
                pos2 = rect.bottomRight()
                x1, y1 = pos1.x(), pos1.y()
                x2, y2 = pos2.x(), pos2.y()
                f.write(f"{x1},{y1},{x2 - x1},{y2 - y1},{clas}\n")

    def paintEvent(self, event):
        super(PainterLabel, self).paintEvent(event)
        self.painter.begin(self)
        self.painter.setPen(QPen(Qt.black, 1))

        if self.rect_temp:
            self.painter.setPen(QPen(Qt.black, 1))
            self.painter.drawRect(self.rect_temp)
        for rect, clas in self.rect_class_list:
            self.drawClassifiedRect(rect, clas)

        self.painter.end()

    def drawClassifiedRect(self, rect, clas):
        self.painter.setPen(QPen(COLORS[clas + 1], 1))
        rect_show = QRect(
            QPoint(posTranScreen(rect.topLeft(), self.zoom)),
            QPoint(posTranScreen(rect.bottomRight(), self.zoom)),
        )
        self.painter.drawRect(rect_show)
