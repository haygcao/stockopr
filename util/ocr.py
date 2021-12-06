"""
https://tesseract-ocr.github.io/tessdoc/Data-Files
"""
import os

from PIL import Image
import pytesseract

from util import util


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
    threshold = 115

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
    text = pytesseract.image_to_string(img, lang='chi_sim')
    return text
