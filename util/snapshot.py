"""
sudo apt install scrot
"""

from PIL import ImageGrab

import pyautogui

# pos = pyautogui.locateOnScreen(os.path.join(root_dir, "关键数据.png"))
# print(pos)


def snapshot(img_file):
    # ths (1520, 480, 345, 265))
    # tdx (1686, 271, 234, 176)
    img_file = 'my_screenshot1.png'
    if img_file:
        pic_3 = pyautogui.screenshot(img_file, region=(1686, 271, 234, 176))
    else:
        pic_3 = pyautogui.screenshot(region=(1686, 271, 234, 176))

    return pic_3


def snapshot2(img_file):
    rangle = (1686, 271, 1920, 447)

    # import pyscreenshot as ImageGrab
    im = ImageGrab.grab(rangle)

    if img_file:
        im.save(img_file)

    return im
