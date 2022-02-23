#!/usr/bin/python

"""
ZetCode PyQt5 tutorial

In this example, we draw text in Russian Cylliric.

Author: Jan Bodnar
Website: zetcode.com
"""

import sys
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPainter, QColor, QFont,QPalette,QPolygon,QBrush
from PyQt5.QtCore import Qt , QPoint


class Example(QWidget):

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):

        self.text = "Лев Николаевич Толстой\nАнна Каренина"

        self.setGeometry(300, 300, 350, 300)
        self.setWindowTitle('Drawing text')
        self.show()

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        self.drawText(event, qp)
        qp.end()

    def drawText(self, event, qp):
        print(event.rect())
        color =QPalette().color(QPalette().Highlight)
        # color.setHsv(color.hue(),color.saturation(),color.value(),color.alpha()-80)
        
        #border color for loading bar (progressed part)
        border_color=QColor("#5657f5")
        #base color for loading bar (progressed part)
        base_color= QColor("#434498")
        print(color.value(),base_color.value(),border_color.value())
        qp.setPen(color)
        qp.setFont(QFont('Decorative', 10))
        qp.setBrush(QBrush(color))
        qp.drawText(event.rect(), Qt.AlignCenter, self.text)
        width = event.rect().width()
        height = event.rect().height()
        ellipse_width = 200
        ellipse_height = 10
        qp.drawRect(int(width/2),event.rect().y(),200,30)
        print(width,height)
        print(QPoint(int(width/4),int(height/2-10)))
        points =QPolygon([QPoint(int(width/4),int(height/2-5)),
                          QPoint(int(3*width/4),int(height/2-5)),
                          QPoint(int(3*width/4) ,int(height/2) +5),
                          QPoint(int(width/4),int(height/2)+5)])
        qp.drawPolygon(points)


def main():

    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()