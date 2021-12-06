"""
sudo apt install scrot
https://tesseract-ocr.github.io/tessdoc/Data-Files
"""

import time

from PIL import Image
import pytesseract

from PIL import ImageGrab

import pyautogui
import pywinauto

# pos = pyautogui.locateOnScreen(os.path.join(root_dir, "关键数据.png"))
# print(pos)
from server.component import helper


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
    # rangle = (1686, 271, 1920, 447)  # 1920 x 1080
    rangle = (825, 265, 1024, 442)  # 1024 x 768

    # import pyscreenshot as ImageGrab
    im = ImageGrab.grab(rangle)

    if img_file:
        im.save(img_file)

    return im


def resize_img(im):
    (x, y) = im.size  # read image size
    x_s = int(x * 3)  # define standard width
    y_s = int(y * x_s / x)  # calc height based on standard width
    out = im.resize((x_s, y_s), Image.ANTIALIAS)  # resize image with high-quality
    return out


def two(img):
    from PIL import Image

    # 模式L”为灰色图像，它的每个像素用8个bit表示，0表示黑，255表示白，其他数字表示不同的灰度。
    img_grey = img.convert('L')
    # return img_grey
    # img_grey.save("test1.png")

    # 自定义灰度界限，大于这个值为黑色，小于这个值为白色
    threshold = 135

    table = []
    for i in range(256):
        if i < threshold:
            table.append(0)
        else:
            table.append(1)

    # 图片二值化
    photo = img_grey.point(table, '1')
    return photo


def reg(img):
    if isinstance(img, str):
        img = Image.open(img)
    img = resize_img(img)
    img = two(img)
    # img.show()

    # /usr/share/tesseract-ocr/4.00/tessdata/chi_sim.traineddata
    text = pytesseract.image_to_string(img)  # , lang='chi_sim')
    return text


def get_rt_quote_tdx(code):
    pid = helper.get_pid_by_exec('C:\\new_jyplug\\tdxw.exe')
    if pid < 0:
        app = pywinauto.Application().start('C:\\new_jyplug\\tdxw.exe')
    else:
        app = pywinauto.Application().connect(process=pid)

    main_window = app.window(class_name='TdxW_MainFrame_Class')
    helper.max_window(main_window)

    main_window.TypeKeys(code)
    # main_window.TypeKeys('{ENTER}')
    pywinauto.keyboard.send_keys('{ENTER}')

    img = snapshot2('')
    text = reg(img)

    d = [
        ('close', 'open'),
        ('change', 'high'),
        ('percent', 'low'),
        ('volume', 'qrr'),

    ]

    quote = {}

    rows = text.split('\n')
    for row in rows:
        if not row.strip():
            continue

        cols = row.split()

        key = d[len(quote) // 2][0]
        try:
            if key == 'percent':
                val1 = float(cols[0][:-1])
            elif key == 'volume':
                val1 = int(cols[0])
            else:
                val1 = float(cols[0])
        except:
            val1 = None

        try:
            val2 = float(cols[-1])
        except:
            val2 = None
        quote.update({d[len(quote) // 2][0]: val1})
        quote.update({d[len(quote) // 2][1]: val2})

        if len(quote) == 8:
            break
    return quote


if __name__ == '__main__':
    text = get_rt_quote_tdx()
    print(text)
