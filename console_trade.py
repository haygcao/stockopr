# -*- coding: utf-8 -*-

import sys

import pandas
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from acquisition import tx, basic
from server import config as svr_config
from trade_manager import trade_manager


def fetch_close(code):
    quote = tx.get_realtime_data_sina(code)
    if not isinstance(quote, pandas.DataFrame) or quote.empty:
        return 0.0

    return quote['close'][-1]


class PlaceControlInCell(QWidget):
    def __init__(self):
        super(PlaceControlInCell, self).__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("QTable Widget演示")
        # self.resize(800, 300)
        self.setFixedWidth(700)

        layout = QHBoxLayout()

        self.table_widget = QTableWidget()

        code_list = trade_manager.query_position_ex(svr_config.ACCOUNT_ID_XY)
        self.table_widget.setRowCount(len(code_list))
        self.table_widget.setColumnCount(7)
        # for col in range(7):
        #     self.tableWidget.setColumnWidth(col, 80)
        # self.tableWidget.itemClicked.connect(self.cb_item_clicked)
        self.table_widget.cellClicked.connect(self.refresh_close)

        # 在第一行第一列添加一个字符串
        self.table_widget.setHorizontalHeaderLabels(['代码', '名称', '价格', '数量', '最新价格', '买入', '卖出'])
        # self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_widget.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

        layout.addWidget(self.table_widget)

        # stock name
        name_map = {}
        name_map_list = basic.get_stocks_name(code_list)
        for m in name_map_list:
            name_map.update({m['code']: m['name']})

        for row, code in enumerate(code_list):
            for col in range(5):
                item = QTableWidgetItem('')
                item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                # item.setTextAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
                self.table_widget.setItem(row, col, item)

        for row, code in enumerate(code_list):
            self.table_widget.item(row, 0).setText(code)
            self.table_widget.item(row, 1).setText(name_map[code])

            close = fetch_close(code)
            self.table_widget.item(row, 4).setText(str(close))

            # combox = QComboBox()
            # combox.addItems(code_list)
            # combox.setCurrentIndex(row)
            # # QSS(类似CSS样式表)
            # # 设置所有的QComboBox控件，使得它们的边距为3像素
            # combox.setStyleSheet('QComboBox{margin:3px};')
            # self.tableWidget.setCellWidget(row, 0, combox)

            #
            btn_buy = QPushButton("买入")
            # btn_buy.setDown(True)  # 默认为按下的状态
            btn_buy.setStyleSheet('QPushButton{margin:3px;background-color : red};')
            btn_buy.clicked.connect(self.cb_order)
            btn_buy.setProperty('row_col', (row, 5))
            btn_buy.setProperty('direct', 'B')
            self.table_widget.setCellWidget(row, 5, btn_buy)

            btn_sell = QPushButton("卖出")
            # btn_sell.setDown(True)  # 默认为按下的状态
            btn_sell.setStyleSheet('QPushButton{margin:3px};')
            btn_sell.clicked.connect(self.cb_order)
            btn_sell.setProperty('row_col', (row, 6))
            btn_sell.setProperty('direct', 'S')
            self.table_widget.setCellWidget(row, 6, btn_sell)

        self.setLayout(layout)
        
    def cb_order(self):
        btn = self.sender()
        row, col = btn.property('row_col')
        price_item = self.table_widget.item(row, 2)
        count_item = self.table_widget.item(row, 3)
        close_item = self.table_widget.item(row, 4)

        direct = btn.property('direct')
        code = self.table_widget.item(row, 0).text()
        name = self.table_widget.item(row, 1).text()
        price = price_item.text() if price_item else 0.0
        count = count_item.text() if count_item else 0
        close = close_item.text() if close_item else 0.0

        print('[{0}] {1}/{2} {3}x{4}'.format(direct, code, name, price, count))

        order_func = trade_manager.buy if direct == 'B' else trade_manager.sell
        order_func(svr_config.ACCOUNT_ID_XY, svr_config.OP_TYPE_DBP, code,
                   price_trade=close,
                   price_limited=price,
                   count=count,
                   period='day',
                   auto=True)

    def cb_item_clicked(self):
        print([(i.row(), i.column(), i.text()) for i in self.table_widget.selectedItems()])
        print(self.table_widget.rowCount())
        print(self.table_widget.item(0, 1).text())
        pass

    def refresh_close(self, row, col):
        code = self.table_widget.item(row, 0).text()
        close = fetch_close(code)

        self.table_widget.item(row, 4).setText(str(close))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = PlaceControlInCell()
    main.show()
    sys.exit(app.exec_())
    # sys.exit(app.exec())
