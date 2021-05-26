import multiprocessing
import sys
import warnings

warnings.simplefilter("ignore", UserWarning)
sys.coinit_flags = 2

from monitor import monitor_today

sys.path.append('.')
from PyQt5.QtWidgets import (QWidget, QLabel,
                             QComboBox, QApplication, QLineEdit, QGridLayout, QPushButton)

from chart import kline


class Example(QWidget):
    def __init__(self):
        super().__init__()

        self.dict = {}
        self.code = '300502'
        self.period = 'day'
        self.monitor_proc = None

        self.initUI()

    def initUI(self):
        self.lbl = QLabel("", self)
        self.log = QLabel("this for log", self)

        comboCode = QComboBox(self)
        # comboCode.adjustSize()
        comboCode.resize(comboCode.width() + 50, comboCode.height())
        with open('data/portfolio.txt', encoding='utf8') as fp:
            for code_name in fp:
                # name = basic.get_stock_name(code)
                comboCode.addItem(code_name)

        comboCode.activated[str].connect(self.onActivatedCode)

        comboPeriod = QComboBox(self)
        for period in ['m1', 'm5', 'm30', 'day', 'week']:
            comboPeriod.addItem(period)

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

        self.btn_monitor = QPushButton('monitor stopped', self)
        self.btn_monitor.clicked.connect(self.control_monitor)

        grid = QGridLayout()

        grid.setSpacing(10)
        grid.addWidget(self.lbl, 1, 0)
        grid.addWidget(comboCode, 2, 0)
        grid.addWidget(comboPeriod, 2, 1)
        grid.addWidget(btn, 2, 2)
        grid.addWidget(self.btn_monitor, 1, 1)
        grid.addWidget(self.log, 3, 0)

        self.setLayout(grid)

        self.setGeometry(300, 300, 280, 170)
        self.setWindowTitle('K')
        self.show()

    def onChanged(self, text):
        self.code = text
        self.lbl.setText('open {} {}'.format(self.code, self.period))
        self.lbl.adjustSize()

    def onActivatedCode(self, text):
        self.code = text.split()[0]
        self.lbl.setText('open {} {}'.format(self.code, self.period))
        self.lbl.adjustSize()

    def onActivatedPeriod(self, text):
        self.period = text
        self.lbl.setText('open {} {}'.format(self.code, self.period))
        self.lbl.adjustSize()

    def show_chart(self):
        print('open {} {}'.format(self.code, self.period))
        p = multiprocessing.Process(target=kline.open_graph, args=(self.code, self.period,))
        p.start()
        p.join(timeout=1)
        # open_graph(self.code, self.period)

    def control_monitor(self):
        if self.btn_monitor.isChecked():
            print('stop monitor')
            self.btn_monitor.setText('monitor stopped')
            self.btn_monitor.setCheckable(False)
            self.monitor_proc.terminate()
            self.monitor_proc.join()
            self.monitor_proc = None
        else:
            print('start monitor')
            self.btn_monitor.setText('monitor running')
            self.btn_monitor.setCheckable(True)
            self.monitor_proc = multiprocessing.Process(target=monitor_today.monitor_today, args=())
            self.monitor_proc.start()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())