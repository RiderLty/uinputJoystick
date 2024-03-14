import asyncio
from io import BytesIO
import time
import cv2
import mss
import numpy as np
import requests
from PIL import Image
# from cnocr.ppocr.utility import draw_ocr_box_txt

def printPerformance(func: callable) -> callable:
    if asyncio.iscoroutinefunction(func):
        async def wrapper(*args, **kwargs):
            start = time.perf_counter_ns()
            result = await func(*args, **kwargs)
            print(
                f"{func.__name__}{args[1:]}{kwargs} 耗时 {(time.perf_counter_ns() - start) / 1000000} ms")
            return result
        return wrapper
    else:
        def wrapper(*args, **kwargs):
            start = time.perf_counter_ns()
            result = func(*args, **kwargs)
            print(
                f"{func.__name__}{args[1:]}{kwargs} 耗时 {(time.perf_counter_ns() - start) / 1000000} ms")
            return result
    return wrapper




def url2ImgNp(url):
    '''从URL下载图片，返回np格式的BGR图像'''
    image_array = np.frombuffer(requests.get(url).content, np.uint8)
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    return image


def url2ImgPIL(url):
    '''从URL下载图片，返回PIL的RGB图像'''
    return Image.open(BytesIO(requests.get(url).content)).convert("RGB")


sct = mss.mss()

def mss2np(display_num=-1, zone=[(0, 0), (1920, 1080)]):
    '''display_num 显示器编号  1,2,3...    -1为主显示器

    zone 抓取区域 [(x1,y1),(x2,y2)] 左上角到右下角
    
    返回np格式的BGR图像
    '''
    assert zone[0][0] < zone[1][0]
    assert zone[0][1] < zone[1][1]
    mon = sct.monitors[display_num]
    monitor = {
        "top": mon["top"] + zone[0][1],
        "left": mon["left"] + zone[0][0],
        "width": zone[1][0] - zone[0][0],  # 手动指定区域
        "height": zone[1][1] - zone[0][1],
    }
    def getSCreen():
        screen = sct.grab(monitor)
        img = np.array(screen)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        return img
    return getSCreen

def mss2pil(display_num=-1, zone=[(0, 0), (1920, 1080)]):
    '''display_num 显示器编号  1,2,3...    -1为主显示器

    zone 抓取区域 [(x1,y1),(x2,y2)] 左上角到右下角
    
    返回PIL的RGB图像
    '''
    assert zone[0][0] < zone[1][0]
    assert zone[0][1] < zone[1][1]
    mon = sct.monitors[display_num]
    monitor = {
        "top": mon["top"] + zone[0][1],
        "left": mon["left"] + zone[0][0],
        "width": zone[1][0] - zone[0][0],  # 手动指定区域
        "height": zone[1][1] - zone[0][1],
    }
    def getSCreen():
        screen = sct.grab(monitor)
        img = Image.frombytes("RGB", screen.size, screen.bgra, "raw", "BGRX")
        return img
    return getSCreen


def pil2np(PILImg: Image):
    return cv2.cvtColor(np.array(PILImg) , cv2.COLOR_RGB2BGR)


def np2pil(npImg: np.ndarray):
    return Image.fromarray(npImg)


# def drawOCR2np(rawImg, ocrResult, font_path , asOne = False):
#     '''OCR结果绘制，输入NP，返回NP'''
#     txts = []
#     scores = []
#     boxes = []
#     boxesInt = []
    
#     for _out in ocrResult:
#         txts.append(_out['text'])
#         scores.append(_out['score'])
#         boxesInt.append(_out['position'].astype(np.int64))
#         boxes.append(_out['position'])
#     pilRaw = np2pil(rawImg)
#     pilRaw.show()
#     draw_img = draw_ocr_box_txt( pilRaw , boxes, txts, scores, drop_score=0.0, font_path=font_path)
    
#     drawImg = cv2.cvtColor(draw_img, cv2.COLOR_RGB2BGR)
#     width = pilRaw.width
#     rawDraw = drawImg[:, :width]
#     whiteDraw = drawImg[:, width:]
#     if asOne == False:
#         return rawDraw, whiteDraw
#     else:
#         cv2.fillPoly(rawDraw, boxesInt, (255, 255, 255))
#         return np.where(whiteDraw == [255,255,255] , rawDraw  , whiteDraw)
    
masks = [
    # 来复活
    [(0, 0), (0, 0), (134, 255)],
    [(949, 712), (1100, 851)],

    # 前往撤离点 & 生存 文字

    [(0, 120), (0, 23), (144, 255)],
    [(13, 280), (473, 861)],

    # # 报酬 （核桃开了  & 选择遗物
    [(16, 33), (83, 170), (118, 243)],
    [(246, 3), (742, 171)],

    # 遗物金币
    [(63, 117), (0, 30), (158, 255)],
    [(307, 436), (1585, 1033)]  # 矩形范围先放大一点
]


def imgFilter(image_hsv, hsv, zone):
    zoneMask = np.zeros_like(image_hsv, dtype=np.uint8) * 255
    assert zone[0][0] < zone[1][0]
    assert zone[0][1] < zone[1][1]
    zoneMask[zone[0][1]:zone[1][1], zone[0][0]:zone[1][0]] = 255
    result = cv2.bitwise_and(image_hsv, zoneMask)
    hsvMask = cv2.inRange(result, np.array(
        [hsv[0][0], hsv[1][0], hsv[2][0]]), np.array([hsv[0][1], hsv[1][1], hsv[2][1]]))
    return hsvMask

# @printPerformance


def handelScreen(screen):
    '''必须为np的BGA'''
    image_hsv = cv2.cvtColor(screen, cv2.COLOR_BGR2HSV)
    ored = np.array(0)
    for i in range(0, len(masks), 2):
        result = imgFilter(image_hsv, masks[i], masks[i+1])
        ored = cv2.bitwise_or(ored, result)
    return ored

# @printPerformance


def drawHandelScreen(screen):
    out = handelScreen(screen)
    out = cv2.cvtColor(out, cv2.COLOR_GRAY2BGR)
    height, width, _ = screen.shape
    red_image = np.full((height, width, 3), (0,  255, 0), dtype=np.uint8)
    img = np.where(out != [0, 0, 0], red_image, screen)
    for i in range(0, len(masks), 2):
        cv2.rectangle(img, masks[i+1][0], masks[i+1][1], (0, 255, 0), 1)
    return img


if __name__ == "__main__":
    # from cnocr import CnOcr
    # oi = CnOcr()
    npcap = mss2np(zone=[(0,1) , (500,500)])
    pilcap = mss2pil(zone=[(0,1) , (500,500)])
    while True:
        img = url2ImgNp("http://192.168.3.155:4443/screenraw")
        # img = pil2np(img)
        
        # img = pilcap()
        # img = pil2np(img)
        # img = screenCapNP()
        img = drawHandelScreen(img)
        # out = oi.ocr(img)
        # a  = drawOCR2np(img , out , r"C:\Windows\Fonts\msyhl.ttc", True )
        cv2.imshow('draw', img)
        if cv2.waitKey(1) == 27:
            break

