import multiprocessing
import sys
sys.path.append('.')
from PyQt5.QtWidgets import (QWidget, QLabel,
                             QComboBox, QApplication, QLineEdit, QGridLayout, QPushButton)

from chart.kline import open_graph


class Example(QWidget):
    def __init__(self):
        super().__init__()

        self.code = '300502'
        self.period = 'day'

        self.initUI()

    def initUI(self):
        self.lbl = QLabel("", self)

        comboCode = QComboBox(self)
        comboCode.addItem("300502")

        comboCode.activated[str].connect(self.onActivatedCode)

        comboPeriod = QComboBox(self)
        comboPeriod.addItem("m1")
        comboPeriod.addItem("m5")
        comboPeriod.addItem("m30")
        comboPeriod.addItem("day")
        comboPeriod.addItem("week")

        # comboPeriod.move(50, 50)
        # self.lbl.move(50, 150)

        comboPeriod.activated[str].connect(self.onActivatedPeriod)

        # qle = QLineEdit('300502', self)
        #
        # # qle.move(60, 100)
        # # self.lbl.move(60, 40)
        #
        # qle.textChanged[str].connect(self.onChanged)

        btn = QPushButton('show', self)
        btn.clicked.connect(self.show_chart)

        grid = QGridLayout()

        grid.setSpacing(10)
        grid.addWidget(self.lbl, 1, 0)
        grid.addWidget(comboCode, 2, 0)
        grid.addWidget(comboPeriod, 2, 1)
        grid.addWidget(btn, 2, 2)

        self.setLayout(grid)

        self.setGeometry(300, 300, 280, 170)
        self.setWindowTitle('K')
        self.show()

    def onChanged(self, text):
        self.code = text
        self.lbl.setText('open {} {}'.format(self.code, self.period))
        self.lbl.adjustSize()

    def onActivatedCode(self, text):
        self.code = text
        self.lbl.setText('open {} {}'.format(self.code, self.period))
        self.lbl.adjustSize()

    def onActivatedPeriod(self, text):
        self.period = text
        self.lbl.setText('open {} {}'.format(self.code, self.period))
        self.lbl.adjustSize()

    def show_chart(self):
        print('open {} {}'.format(self.code, self.period))
        p = multiprocessing.Process(target=open_graph, args=(self.code, self.period,))
        p.start()
        p.join(timeout=1)
        # open_graph(self.code, self.period)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())