

def max_window(window):
    """
    最大化窗口
    """
    if window.get_show_state() != 3:
        window.maximize()
    window.set_focus()
