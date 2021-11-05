# -*- coding: utf-8 -*-

"""
ModuleNotFoundError: No module named 'gi'
sudo apt install python3-gi

ValueError: Namespace Gst not available
sudo apt install python3-gst-1.0

PYTHONPATH=/usr/lib/python3/dist-packages python toolkit/countdown.py
"""
import os
import sys

from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QPushButton, QLabel, QMainWindow, QInputDialog, QApplication, QHBoxLayout, QVBoxLayout, \
    QRadioButton, QWidget

sys.path.append('/usr/lib/python3/dist-packages')

INIT_COUNT = 25 * 60 * 10
sound_path = os.path.join(os.path.dirname(__file__), '../data/SchoolBell.ogg')  # "/usr/share/sounds/deepin/stereo/message.wav"


def count_to_time(count):
    second = count / 10
    fractional = count % 10
    h = int(second // 3600)
    m = int(second % 3600 // 60)
    s = int(second % 3600 % 60)

    return '{:02d}:{:02d}:{:02d}.{:d}'.format(h, m, s, fractional)


# QWidget::setLayout: Attempting to set QLayout "" on Window "", which already has a layout
# class Window(QMainWindow):
class Window(QWidget):
    def __init__(self):
        super().__init__()

        # setting title
        self.setWindowTitle("Python ")

        # setting geometry
        # self.setGeometry(100, 100, 400, 600)

        # calling method
        self.UiComponents()

        # showing all the widgets
        self.show()

    # method for widgets
    def UiComponents(self):

        # variables
        # count variable
        self.count = INIT_COUNT
        self.for_work = True

        # start flag
        self.start = False

        # creating push button to get time in seconds
        # button = QPushButton("Set time(s)", self)

        # setting geometry to the push button
        # button.setGeometry(125, 100, 150, 50)

        # adding action to the button
        # button.clicked.connect(self.get_seconds)

        h_layout_period1 = QHBoxLayout()
        h_layout_period2 = QHBoxLayout()
        for p in [1, 3, 5, 10, 15, 30, 45, 60]:
            rb = QRadioButton('{}min'.format(p))
            rb.toggled.connect(self.onClicked)
            if p <= 10:
                h_layout_period1.addWidget(rb)
            else:
                h_layout_period2.addWidget(rb)

        # creating label to show the seconds
        self.label = QLabel(count_to_time(INIT_COUNT), self)

        # setting geometry of label
        # self.label.setGeometry(100, 200, 200, 50)

        # setting border to the label
        self.label.setStyleSheet("border : 3px solid black")

        # setting font to the label
        self.label.setFont(QFont('Times', 15))

        # setting alignment ot the label
        self.label.setAlignment(Qt.AlignCenter)

        # creating start button
        start_button = QPushButton("Start", self)

        # setting geometry to the button
        # start_button.setGeometry(125, 350, 150, 40)

        # adding action to the button
        start_button.clicked.connect(self.start_action)

        # creating pause button
        pause_button = QPushButton("Pause", self)

        # setting geometry to the button
        # pause_button.setGeometry(125, 400, 150, 40)

        # adding action to the button
        pause_button.clicked.connect(self.pause_action)

        # creating reset button
        reset_button = QPushButton("Reset", self)

        # setting geometry to the button
        # reset_button.setGeometry(125, 450, 150, 40)

        # adding action to the button
        reset_button.clicked.connect(self.reset_action)

        h_layout_action = QHBoxLayout()

        h_layout_action.addWidget(start_button)
        h_layout_action.addWidget(pause_button)
        h_layout_action.addWidget(reset_button)

        v_layout = QVBoxLayout()
        v_layout.addLayout(h_layout_period1)
        v_layout.addLayout(h_layout_period2)
        v_layout.addWidget(self.label)
        v_layout.addLayout(h_layout_action)

        self.setLayout(v_layout)

        # creating a timer object
        timer = QTimer(self)

        # adding action to timer
        timer.timeout.connect(self.showTime)

        # update the timer every tenth second
        timer.start(100)

    def onClicked(self):
        if self.start:
            return
        radio_btn = self.sender()
        if radio_btn.isChecked():
            period = radio_btn.text()
            minute = int(period[:-3])
            self.count = minute * 60 * 10
            self.for_work = True
            self.label.setText(count_to_time(self.count))

    # method called by timer
    def showTime(self):
        # checking if flag is true
        if self.start:
            # incrementing the counter
            self.count -= 1

            # timer is completed
            if self.count == 0:
                # making flag false
                self.start = False

                # setting text to the label
                # self.label.setText("Completed !!!! ")
                if self.for_work:
                    count = 5 * 60 * 10
                    self.for_work = False
                else:
                    count = INIT_COUNT
                    self.for_work = True

                self.count = count
                self.label.setText(count_to_time(self.count))

                # url = QtCore.QUrl.fromLocalFile("/usr/share/sounds/deepin/stereo/message.wav")
                # content = QtMultimedia.QMediaContent(url)
                # player = QtMultimedia.QMediaPlayer()
                # player.setMedia(content)
                # player.setVolume(50)
                # player.play()

                from playsound import playsound
                playsound(sound_path)

        if self.start:
            text = count_to_time(self.count)

            # showing text
            self.label.setText(text)

    # method called by the push button
    def get_seconds(self):
        # making flag false
        self.start = False

        # getting seconds and flag
        second, done = QInputDialog.getInt(self, 'Seconds', 'Enter Seconds:')

        # if flag is true
        if done:
            # changing the value of count
            self.count = second * 10

            # setting text to the label
            self.label.setText(str(second))

    def start_action(self):
        # making flag true
        self.start = True

        # count = 0
        if self.count == 0:
            self.start = False

    def pause_action(self):

        # making flag false
        self.start = False

    def reset_action(self):

        # making flag false
        self.start = False

        # setting count value to 0
        self.count = INIT_COUNT
        self.for_work = True

        # setting label text
        self.label.setText(count_to_time(INIT_COUNT))



# create pyqt5 app
App = QApplication(sys.argv)

# create the instance of our Window
window = Window()

# start the app
sys.exit(App.exec())
