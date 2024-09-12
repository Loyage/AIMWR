import math
from PySide6.QtWidgets import QLabel, QWidget, QGraphicsOpacityEffect
from PySide6.QtCore import Qt, QPoint, Signal, QRect, QPoint
from PySide6.QtGui import QMouseEvent, QPainter, QPen, QPixmap


def posTranImg(pos, zoom):
    return pos / zoom


def posTranScreen(pos, zoom):
    return pos * zoom


class PainterLabel(QLabel):
    """
    My custom label widget for painting circles on images.
    """

    get_template = Signal(QPixmap, name="get_template")
    doLabel = Signal(int, int, int, name="doLabel")
    beginDrag = Signal(int, int, name="beginDrag")
    endEdit = Signal(name="endEdit")

    NORMAL = 0
    WAITING = 1
    DRAGGING = 2
    EDITING = 3

    def __init__(self, parent=None):
        super(PainterLabel, self).__init__(parent)
        # self.is_label_mode = False
        # self.is_paintable = False
        # self.drop_state = 0
        # self.x1 = -1.0
        # self.y1 = -1.0
        # self.button_bef = Qt.NoButton
        # self.dragging_objs_ori = []
        # self.editing_objs = []

        self.state = self.NORMAL
        self.zoom = 1.0
        self.img_ori = None
        self.img_show = None
        self.rect_temp = None
        self.painter = QPainter()

    def atImageChanged(self, image_path):
        if not image_path:
            self.clear()
            self.is_paintable = False
        else:
            try:
                self.img_ori = QPixmap(image_path)
                self.reshow()
                self.resize(self.img_show.size())
            except Exception as e:
                self.clear()
                self.is_paintable = False

    def zoomIn(self):
        self.zoom *= 1.1
        self.reshow()

    def zoomOut(self):
        self.zoom /= 1.1
        self.reshow()

    def zoomReset(self):
        self.zoom = 1.0
        self.reshow()

    def setDragState(self):
        self.state = self.WAITING
        self.setCursor(Qt.CrossCursor)

    def reshow(self):
        self.img_show = self.img_ori.scaled(
            self.img_ori.size() * self.zoom, Qt.AspectRatioMode.KeepAspectRatio
        )
        self.setPixmap(self.img_show)
        self.resize(self.img_show.size())

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
            self.state = self.EDITING
            pos1 = posTranImg(self.pos_ori, self.zoom)
            pos2 = posTranImg(ev.pos(), self.zoom)
            img_temp = self.img_ori.copy(
                pos1.x(), pos1.y(), pos2.x() - pos1.x(), pos2.y() - pos1.y()
            )
            self.get_template.emit(img_temp)

            self.rect_temp = None
            self.update()

    def paintEvent(self, event):
        super(PainterLabel, self).paintEvent(event)
        self.painter.begin(self)
        self.painter.setPen(QPen(Qt.black, 1))
        if self.rect_temp:
            self.painter.drawRect(self.rect_temp)
        self.painter.end()

    # def setIsPaintable(self, value):
    #     self.is_paintable = value
    #     self.updateCursor()

    # def setIsLabelMode(self, value):
    #     self.is_label_mode = value
    #     self.updateCursor()

    # def setDropState(self, drop_state):
    #     self.drop_state = drop_state

    # def setDraggingObjects(self, dragging_objects):
    #     self.dragging_objs_ori = dragging_objects

    # def updateCursor(self):
    #     if self.is_label_mode:
    #         self.setCursor(Qt.PointingHandCursor)
    #     elif self.is_paintable:
    #         self.setCursor(Qt.CrossCursor)
    #     else:
    #         self.setCursor(Qt.ArrowCursor)

    # def getEditingObjs(self):
    #     return self.editing_objs

    # def paintEvent(self, event):
    #     super(PainterLabel, self).paintEvent(event)  # 绘制背景的图片

    #     if not self.is_paintable:
    #         return

    #     painter = QPainter(self)
    #     pen = QPen()
    #     for obj in self.editing_objs:
    #         if obj.obj_state == 0:  # 空包
    #             pen = QPen(Qt.red, 1)
    #         elif obj.obj_state == 1:  # 单包
    #             pen = QPen(Qt.blue, 1)
    #         elif obj.obj_state == 2:  # 多包
    #             pen = QPen(Qt.green, 1)
    #         painter.setPen(pen)
    #         if not self.is_micro_well:
    #             painter.drawEllipse(QPoint(obj.x, obj.y), int(obj.r), int(obj.r))
    #         else:
    #             painter.drawTemplate(QRect(obj.x, obj.y, int(2 * obj.r), int(2 * obj.r)))

    # def mousePressEvent(self, event):
    #     if not self.is_paintable:
    #         return

    #     if self.button_bef != Qt.NoButton:
    #         return

    #     if self.is_label_mode:
    #         if event.button() == Qt.LeftButton:
    #             x = event.pos().x()
    #             y = event.pos().y()
    #             self.doLabel.emit(x, y, self.drop_state)
    #             return

    #     if event.button() == Qt.LeftButton:  # 左键按下，开始画圆
    #         self.x1 = event.pos().x()
    #         self.y1 = event.pos().y()
    #         self.button_bef = Qt.LeftButton
    #     elif event.button() == Qt.RightButton:  # 右键按下，开始拖动
    #         self.x1 = event.pos().x()
    #         self.y1 = event.pos().y()
    #         self.beginDrag.emit(self.x1, self.y1)
    #         self.button_bef = Qt.RightButton
    #     else:
    #         return
    #     self.update()

    # def mouseMoveEvent(self, event):
    #     if not self.is_paintable:
    #         return

    #     if (not self.is_micro_well and self.drop_state == 3) or (
    #         self.is_micro_well and self.drop_state == 6
    #     ):
    #         return

    #     if event.buttons() & Qt.LeftButton and self.button_bef == Qt.LeftButton:
    #         x2 = event.pos().x()
    #         y2 = event.pos().y()

    #         self.editing_objs.clear()
    #         if not self.is_micro_well:
    #             radius = math.sqrt((self.x1 - x2) ** 2 + (self.y1 - y2) ** 2)
    #             self.editing_objs.append(
    #                 PainterLabel.Object(self.x1, self.y1, radius, self.drop_state)
    #             )
    #         else:
    #             length = (x2 - self.x1) / 2.0
    #             self.editing_objs.append(
    #                 PainterLabel.Object(self.x1, self.y1, length, self.drop_state)
    #             )

    #     elif event.buttons() & Qt.RightButton and self.button_bef == Qt.RightButton:
    #         x2 = event.pos().x()
    #         y2 = event.pos().y()

    #         self.editing_objs.clear()
    #         for obj in self.dragging_objs_ori:
    #             x = obj.x + x2 - self.x1
    #             y = obj.y + y2 - self.y1
    #             self.editing_objs.append(
    #                 PainterLabel.Object(x, y, obj.r, obj.obj_state)
    #             )

    #     else:
    #         return
    #     self.update()

    # def mouseReleaseEvent(self, event):
    #     if not self.is_paintable:
    #         return

    #     if self.is_label_mode:
    #         return

    #     if self.button_bef == Qt.LeftButton and event.button() == Qt.LeftButton:
    #         self.button_bef = Qt.NoButton
    #         x2 = event.pos().x()
    #         y2 = event.pos().y()
    #         radius = math.sqrt((self.x1 - x2) ** 2 + (self.y1 - y2) ** 2)

    #         self.editing_objs.clear()
    #         if not self.is_micro_well:
    #             self.editing_objs.append(
    #                 PainterLabel.Object(self.x1, self.y1, radius, self.drop_state)
    #             )
    #         else:
    #             self.editing_objs.append(
    #                 PainterLabel.Object(self.x1, self.y1, radius, self.drop_state)
    #             )
    #         self.endEdit.emit()
    #         self.editing_objs.clear()

    #         self.update()
    #     elif self.button_bef == Qt.RightButton and event.button() == Qt.RightButton:
    #         self.button_bef = Qt.NoButton
    #         x2 = event.pos().x()
    #         y2 = event.pos().y()

    #         self.editing_objs.clear()
    #         for obj in self.dragging_objs_ori:
    #             x = obj.x + x2 - self.x1
    #             y = obj.y + y2 - self.y1
    #             self.editing_objs.append(
    #                 PainterLabel.Object(x, y, obj.r, obj.obj_state)
    #             )
    #         self.endEdit.emit()
    #         self.dragging_objs_ori.clear()
    #         self.editing_objs.clear()

    #         self.update()
    #     else:
    #         return

    # def mouseDoubleClickEvent(self, event):
    #     if not self.is_paintable:
    #         return
    #     x2 = event.pos().x()  # 鼠标相对于所在控件的位置
    #     y2 = event.pos().y()
