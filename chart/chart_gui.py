import multiprocessing
import sys
import warnings

from PyQt5 import QtCore

from acquisition import acquire
from trade_manager import trade_manager

warnings.simplefilter("ignore", UserWarning)
sys.coinit_flags = 2

from monitor import monitor_today

sys.path.append('.')
from PyQt5.QtWidgets import (QWidget, QLabel,
                             QComboBox, QApplication, QLineEdit, QGridLayout, QPushButton, QMainWindow)

from chart import kline


class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.initUI()
        self.show()

    def initUI(self):
        self.alertWidget = Panel()
        self.setCentralWidget(self.alertWidget)


class Panel(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

        self.dict = {}
        self.code = '300502'
        self.period = 'day'
        self.monitor_proc = None
        self.count = '0'

        self.initUI()

    def initUI(self):
        self.lbl = QLabel("", self)
        self.log = QLabel("this for log", self)

        self.combo_code = QComboBox(self)
        # comboCode.adjustSize()
        self.combo_code.resize(self.combo_code.width() + 50, self.combo_code.height())
        self.load()

        self.combo_code.activated[str].connect(self.on_activated_code)

        btn_load = QPushButton('load', self)
        btn_load.clicked.connect(self.load)

        combo_period = QComboBox(self)
        for period in ['m1', 'm5', 'm30', 'day', 'week']:
            combo_period.addItem(period)

        # comboPeriod.move(50, 50)
        # self.lbl.move(50, 150)

        combo_period.activated[str].connect(self.on_activated_period)

        qle_code = QLineEdit('300502', self)

        # qle.move(60, 100)
        # self.lbl.move(60, 40)

        qle_code.textChanged[str].connect(self.on_code_changed)

        btn = QPushButton('show', self)
        btn.clicked.connect(self.show_chart)

        self.btn_monitor = QPushButton('monitor stopped', self)
        self.btn_monitor.clicked.connect(self.control_monitor)

        btn_update_quote = QPushButton('update quote', self)
        btn_update_quote.clicked.connect(self.update_quote)

        qle_count = QLineEdit(self.count, self)
        qle_count.textChanged[str].connect(self.on_count_changed)

        btn_buy = QPushButton('Buy', self)
        btn_buy.clicked.connect(self.buy)

        btn_sell = QPushButton('Sell', self)
        btn_sell.clicked.connect(self.sell)

        grid = QGridLayout()

        grid.setSpacing(10)
        grid.addWidget(self.lbl, 1, 0)
        grid.addWidget(self.combo_code, 2, 0)
        grid.addWidget(combo_period, 2, 2)
        grid.addWidget(btn, 2, 3)
        grid.addWidget(btn_load, 2, 4)
        grid.addWidget(self.btn_monitor, 1, 1)
        grid.addWidget(btn_update_quote, 1, 2)

        grid.addWidget(qle_code, 3, 0)
        grid.addWidget(qle_count, 3, 1)
        grid.addWidget(btn_buy, 3, 2)
        grid.addWidget(btn_sell, 3, 3)

        grid.addWidget(self.log, 4, 0)

        self.setLayout(grid)

        self.setGeometry(300, 300, 280, 170)
        self.setWindowTitle('K')
        self.show()

    def on_code_changed(self, text):
        self.code = text
        self.lbl.setText('open {} {}'.format(self.code, self.period))
        self.lbl.adjustSize()

    def on_count_changed(self, text):
        self.count = text
        self.lbl.setText('order {} {}'.format(self.code, self.count))
        self.lbl.adjustSize()

    def on_activated_code(self, text):
        self.code = text.split()[0]
        self.lbl.setText('open {} {}'.format(self.code, self.period))
        self.lbl.adjustSize()

    def load(self):
        self.combo_code.clear()
        with open('data/portfolio.txt', encoding='utf8') as fp:
            for code_name in fp:
                # name = basic.get_stock_name(code)
                self.combo_code.addItem(code_name)

    def on_activated_period(self, text):
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

    def update_quote(self):
        p = multiprocessing.Process(target=acquire.save_quote, args=())
        p.start()

    def buy(self):
        trade_manager.buy(self.code, int(self.count))

    def sell(self):
        trade_manager.sell(self.code, int(self.count))


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # ex = Main()
    ex = Panel()
    sys.exit(app.exec_())
