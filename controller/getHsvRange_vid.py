
import cv2
import mss
import numpy as np
from PIL import Image

from cnocr import CnOcr

from utils.imgTools import *


hue_min = 0
hue_max = 255
saturation_min = 0
saturation_max = 255
value_min = 0
value_max = 255


def on_trackbar(x):
    global hue_min, hue_max, saturation_min, saturation_max, value_min, value_max
    hue_min = cv2.getTrackbarPos('Hue Min', 'Parameter Tool')
    hue_max = cv2.getTrackbarPos('Hue Max', 'Parameter Tool')
    saturation_min = cv2.getTrackbarPos('Saturation Min', 'Parameter Tool')
    saturation_max = cv2.getTrackbarPos('Saturation Max', 'Parameter Tool')
    value_min = cv2.getTrackbarPos('Value Min', 'Parameter Tool')
    value_max = cv2.getTrackbarPos('Value Max', 'Parameter Tool')
    print(
        f"HSV范围:[({hue_min},{hue_max}),({saturation_min},{saturation_max}),({value_min},{value_max})]")


drawing = False  # 是否正在绘制矩形
x1, y1 = -1, -1  # 矩形左上角坐标
x2, y2 = -1, -1  # 矩形右下角坐标


def draw_rectangle(event, x, y, flags, param):
    global drawing, x1, y1, x2, y2
    if event == cv2.EVENT_LBUTTONDOWN:  # 鼠标左键按下，开始绘制矩形
        drawing = True
        x1, y1 = x, y
        x2, y2 = x, y
    elif event == cv2.EVENT_LBUTTONUP:  # 鼠标左键松开，结束绘制矩形并打印坐标
        drawing = False
        x2, y2 = x, y
        print(f"矩形区域:[({x1},{y1}), ({x2},{y2})]")
    elif event == cv2.EVENT_MOUSEMOVE and (flags & cv2.EVENT_FLAG_LBUTTON):
        x2, y2 = x, y


cv2.namedWindow('Display')
cv2.namedWindow('Parameter Tool')
cv2.createTrackbar('Hue Min', 'Parameter Tool', 0, 255, on_trackbar)
cv2.createTrackbar('Hue Max', 'Parameter Tool', 255, 255, on_trackbar)
cv2.createTrackbar('Saturation Min', 'Parameter Tool', 0, 255, on_trackbar)
cv2.createTrackbar('Saturation Max', 'Parameter Tool', 255, 255, on_trackbar)
cv2.createTrackbar('Value Min', 'Parameter Tool', 0, 255, on_trackbar)
cv2.createTrackbar('Value Max', 'Parameter Tool', 255, 255, on_trackbar)
cv2.createTrackbar('show ocr', 'Parameter Tool', 0, 1, on_trackbar)
# def button_callback(x):
#     print("button click")
# cv2.createButton('Button', button_callback, None, cv2.WINDOW_NORMAL)
cv2.setMouseCallback('Display', draw_rectangle)


def update_image(original_image):
    hsv_image = original_image.copy()
    hsv_image = cv2.cvtColor(hsv_image, cv2.COLOR_BGR2HSV)
    lower_range = np.array([hue_min, saturation_min, value_min])
    upper_range = np.array([hue_max, saturation_max, value_max])
    filtered_image = cv2.inRange(hsv_image, lower_range, upper_range)
    result = cv2.bitwise_and(original_image, original_image, mask=filtered_image)
    cv2.rectangle(result, (x1, y1), (x2, y2), (0, 255, 0), 1)
    return result


oi = CnOcr()
# img = cv2.imread("") #读取文件
# while True:
# img = screenCapturer()  # 获取BGR格式图像

while True:
    # img = url2ImgNp("http://192.168.3.155:4443/screenocr")
    img = mss2np()
    img = update_image(img )
    
    if cv2.getTrackbarPos('show ocr', 'Parameter Tool') == 1:
        out = oi.ocr(img)
        img = drawOCR2np(    img   , out,   r"C:\Windows\Fonts\msyhl.ttc", True)
    cv2.imshow('Display', img)
    if cv2.waitKey(1) == 27:
        break
