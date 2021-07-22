

def max_window(window):
    """
    最大化窗口
    """
    try:
        if window.get_show_state() != 3:
            window.maximize()
        window.set_focus()
    except Exception as e:
        print(e)
