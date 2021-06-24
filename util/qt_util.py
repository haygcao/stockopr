import multiprocessing

from PyQt5.QtWidgets import QApplication, QMessageBox

g_q_application = None


def popup_warning_message_box(msg, callback, *args):
    global g_q_application
    if not g_q_application:
        g_q_application = QApplication([])
    # msg_box = QMessageBox(QMessageBox.Warning, '警告', msg)
    # msg_box.exec_()
    r = QMessageBox.warning(None, '警告', msg, QMessageBox.Yes | QMessageBox.No)
    if callback:
        if r == QMessageBox.Yes:
            callback(*args)
        # elif r == QMessageBox.No:
        #     callback(*args)
        # elif r == QMessageBox.Ok:
        #     callback(*args)


def popup_warning_message_box_mp(msg, callback=None, *args):
    # popup_warning_message_box(msg, callback, *args)
    multiprocessing.Process(target=popup_warning_message_box, args=(msg, callback, *args)).start()
