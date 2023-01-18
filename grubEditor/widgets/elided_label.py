from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter,QFontMetrics
from PyQt5.QtWidgets import QLabel

class ElidedLabel(QLabel):
    def paintEvent(self, event):
        painter = QPainter(self)
        metrics = QFontMetrics(self.font())
        elided = metrics.elidedText(self.text(), Qt.ElideRight, self.width())
        painter.drawText(self.rect(), self.alignment(), elided)