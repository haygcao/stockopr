import multiprocessing
import tkinter

from PyQt5.QtWidgets import QApplication, QMessageBox

g_q_application = None
g_use_tk = True


def popup_warning_message_box(func_name, msg, callback, *args):
    if func_name == 'warning':
        func = QMessageBox.warning
        title = '警告'
    else:
        func = QMessageBox.information
        title = '提示'

    if g_use_tk:
        import tkinter.messagebox

        ws = tkinter.Tk()
        ws.withdraw()
        r = tkinter.messagebox.askokcancel(title, msg,)
        # ok = r == tkinter.messagebox.OK  # 上一版本 TK
        ok = r

        # ws.mainloop()
    else:
        global g_q_application
        if not g_q_application:
            g_q_application = QApplication([])
        # msg_box = QMessageBox(QMessageBox.Warning, '警告', msg)
        # msg_box.exec_()

        # msg_box = QMessageBox()
        # msg_box.setText(msg)
        # r = msg_box.exec()

        r = func(None, title, msg, QMessageBox.Yes | QMessageBox.No)
        ok = (r == QMessageBox.Yes)

    if callback:
        if ok:
            callback(*args)
        # elif r == QMessageBox.No:
        #     callback(*args)
        # elif r == QMessageBox.Ok:
        #     callback(*args)
    g_q_application = None


def popup_warning_message_box_mp(msg, callback=None, *args):
    # popup_warning_message_box(msg, callback, *args)
    multiprocessing.Process(
        target=popup_warning_message_box, args=('warning', msg, callback, *args)).start()


def popup_info_message_box_mp(msg, callback=None, *args):
    # popup_warning_message_box(msg, callback, *args)
    multiprocessing.Process(
        target=popup_warning_message_box, args=('info', msg, callback, *args)).start()
