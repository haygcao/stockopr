import multiprocessing

from PyQt5.QtWidgets import QApplication, QMessageBox

g_q_application = None


def popup_warning_message_box(func_name, msg, callback, *args):
    global g_q_application
    if not g_q_application:
        g_q_application = QApplication([])
    # msg_box = QMessageBox(QMessageBox.Warning, '警告', msg)
    # msg_box.exec_()
    if func_name == 'warning':
        func = QMessageBox.warning
        title = '警告'
    else:
        func = QMessageBox.information
        title = '提示'

    r = func(None, title, msg, QMessageBox.Yes | QMessageBox.No)
    if callback:
        if r == QMessageBox.Yes:
            callback(*args)
        # elif r == QMessageBox.No:
        #     callback(*args)
        # elif r == QMessageBox.Ok:
        #     callback(*args)


def popup_warning_message_box_mp(msg, callback=None, *args):
    # popup_warning_message_box(msg, callback, *args)
    multiprocessing.Process(
        target=popup_warning_message_box, args=('warning', msg, callback, *args)).start()


def popup_info_message_box_mp(msg, callback=None, *args):
    # popup_warning_message_box(msg, callback, *args)
    multiprocessing.Process(
        target=popup_warning_message_box, args=('info', msg, callback, *args)).start()
