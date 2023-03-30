from PyQt6.QtCore import Qt, QPoint, QPointF, QRect
from PyQt6.QtGui import QPainter, QColor, QBrush, QLinearGradient, QPen
from PyQt6.QtWidgets import QWidget

class LEDIndicator(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(15, 15)
        self.color = QColor(255,68,0)

    def set_unfinished_process_color(self):
        self.color = QColor(255,68,0)
        self.update()

    def set_in_process_color(self):
        self.color = QColor(255,230,0)
        self.update()

    def set_finished_process_color(self):
        self.color = QColor(1,88,91)
        self.update()

    def set_color(self, r,g,b):
        self.color = QColor(r,g,b)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        diameter = min(self.width(), self.height())

        # Create a gradient for the LED color
        gradient = QLinearGradient(QPointF(0, 0), QPointF(diameter, diameter))
        gradient.setColorAt(0, self.color.lighter(150))
        gradient.setColorAt(1, self.color.darker(150))

        # Paint the LED circle with the gradient
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(self.rect().center(), diameter / 2, diameter / 2)

        # Add a subtle border to the LED circle
        border_color = self.color.lighter(150)
        border_rect = QRect(0, 0, diameter, diameter)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(border_color, 1))
        painter.drawEllipse(border_rect.center(), diameter / 2, diameter / 2)


