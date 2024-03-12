

import cv2
import numpy as np

PATH = r"D:\Pictures\Screenshots\warframe\SC (6).png"

drawing = False  # 是否正在绘制矩形
x1, y1 = -1, -1  # 矩形左上角坐标
x2, y2 = -1, -1  # 矩形右下角坐标

def draw_rectangle(event, x, y, flags, param):
    global drawing, x1, y1, x2, y2
    if event == cv2.EVENT_LBUTTONDOWN:  # 鼠标左键按下，开始绘制矩形
        drawing = True
        x1, y1 = x, y
    elif event == cv2.EVENT_LBUTTONUP:  # 鼠标左键松开，结束绘制矩形并打印坐标
        drawing = False
        x2, y2 = x, y
        print(f"矩形区域:[({x1},{y1}), ({x2},{y2})]")
    elif event == cv2.EVENT_MOUSEMOVE and (flags & cv2.EVENT_FLAG_LBUTTON) :
        x2, y2 = x, y
        result = original_image.copy() 
        cv2.rectangle(result, (x1,y1), (x2, y2), (0, 255, 0), 1)
        cv2.imshow('Filtered Image', result)
        
def update_image(hue_min, hue_max, saturation_min, saturation_max, value_min, value_max):
    print(f"HSV范围:[({hue_min},{hue_max}),({saturation_min},{saturation_max}),({value_min},{value_max})]")
    lower_range = np.array([hue_min, saturation_min, value_min])
    upper_range = np.array([hue_max, saturation_max, value_max])
    filtered_image = cv2.inRange(hsv_image, lower_range, upper_range)
    result = cv2.bitwise_and(original_image, original_image, mask=filtered_image)
    cv2.imshow('Filtered Image', result)

def on_trackbar(x):
    hue_min = cv2.getTrackbarPos('Hue Min', 'Parameter Tool')
    hue_max = cv2.getTrackbarPos('Hue Max', 'Parameter Tool')
    saturation_min = cv2.getTrackbarPos('Saturation Min', 'Parameter Tool')
    saturation_max = cv2.getTrackbarPos('Saturation Max', 'Parameter Tool')
    value_min = cv2.getTrackbarPos('Value Min', 'Parameter Tool')
    value_max = cv2.getTrackbarPos('Value Max', 'Parameter Tool')
    update_image(hue_min, hue_max, saturation_min, saturation_max, value_min, value_max)

original_image = cv2.imread(PATH)
hsv_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2HSV)
update_image(0, 255, 0, 255, 0, 255)
cv2.namedWindow('Parameter Tool')
cv2.createTrackbar('Hue Min', 'Parameter Tool', 0, 255, on_trackbar)
cv2.createTrackbar('Hue Max', 'Parameter Tool', 255, 255, on_trackbar)
cv2.createTrackbar('Saturation Min', 'Parameter Tool', 0, 255, on_trackbar)
cv2.createTrackbar('Saturation Max', 'Parameter Tool', 255, 255, on_trackbar)
cv2.createTrackbar('Value Min', 'Parameter Tool', 0, 255, on_trackbar)
cv2.createTrackbar('Value Max', 'Parameter Tool', 255, 255, on_trackbar)
cv2.setMouseCallback('Filtered Image', draw_rectangle)

while True:
    if cv2.waitKey(1) == 27:
        break
cv2.destroyAllWindows()
