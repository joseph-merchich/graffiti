import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QImage, QPainter, QPen
from PyQt6.QtWidgets import QApplication, QWidget


class TransparentDrawingCanvas(QWidget):
    def __init__(self):
        super().__init__()
        self.move_offset = None
        self.frame_width = 12
        self.stroke_mode = None
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMouseTracking(True)

        self.resize(800, 600)

        self.image = QImage(
            self.size(),
            QImage.Format.Format_ARGB32_Premultiplied,
        )
        self.image.fill(Qt.GlobalColor.transparent)

        self.last_point = None

    def mousePressEvent(self, event):
        pos = event.position().toPoint()

        if event.button() == Qt.MouseButton.LeftButton:
            on_frame = (
                pos.x() < self.frame_width
                or pos.y() < self.frame_width
                or pos.x() >= self.width() - self.frame_width
                or pos.y() >= self.height() - self.frame_width
            )

            self.grabMouse()

            if on_frame:
                self.move_offset = (
                    event.globalPosition().toPoint()
                    - self.frameGeometry().topLeft()
                )
                return

            self.stroke_mode = "erase"

        elif event.button() == Qt.MouseButton.RightButton:
            self.grabMouse()
            self.stroke_mode = "draw"
        else:
            return

        self.move_offset = None
        self.last_point = pos
        self._apply_stroke(pos, pos)
        self.update()


    def mouseMoveEvent(self, event):
        if self.move_offset is not None:
            self.move(event.globalPosition().toPoint() - self.move_offset)
            return

        if self.last_point is None or self.stroke_mode is None:
            return

        current_point = event.position().toPoint()
        self._apply_stroke(self.last_point, current_point)
        self.last_point = current_point
        self.update()


    def mouseReleaseEvent(self, event):
        if event.button() in (
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.RightButton,
        ):
            self.move_offset = None
            self.last_point = None
            self.stroke_mode = None
            self.releaseMouse()


    def _apply_stroke(self, start, end):
        painter = QPainter(self.image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if self.stroke_mode == "erase":
            painter.setCompositionMode(
                QPainter.CompositionMode.CompositionMode_Clear
            )
            pen = QPen(
                QColor(0, 0, 0, 0),
                24,
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.RoundCap,
                Qt.PenJoinStyle.RoundJoin,
            )
        else:
            painter.setCompositionMode(
                QPainter.CompositionMode.CompositionMode_SourceOver
            )
            pen = QPen(
                QColor("red"),
                4,
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.RoundCap,
                Qt.PenJoinStyle.RoundJoin,
            )

        painter.setPen(pen)
        painter.drawLine(start, end)
        painter.end()
            
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        
        painter.fillRect(self.rect(), QColor(0, 0, 0, 1))

        painter.drawImage(0, 0, self.image)

        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor("white"), 2))
        painter.drawRect(self.rect().adjusted(1, 1, -2, -2))


app = QApplication(sys.argv)
canvas = TransparentDrawingCanvas()
canvas.show()
sys.exit(app.exec())

