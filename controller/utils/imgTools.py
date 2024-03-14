import asyncio
from io import BytesIO
import time
import cv2
import mss
import numpy as np
import requests
from PIL import Image
from cnocr.ppocr.utility import draw_ocr_box_txt


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
    response = requests.get(url)
    image_data = response.content
    image_array = np.frombuffer(image_data, np.uint8)
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    return image


def url2ImgPIL(url):
    response = requests.get(url)
    image_data = response.content
    img = Image.open(BytesIO(image_data)).convert("RGB")
    return img


def screenCapPIL():
    with mss.mss() as m:
        rect = (0, 0, 1920, 1080)
        sc_img = m.grab(rect)
        return Image.frombytes("RGB", sc_img.size, sc_img.bgra, "raw", "BGRX")


def screenCapNP():
    with mss.mss() as m:
        rect = (0, 0, 1920, 1080)
        sc_img = m.grab(rect)
        npImg = np.array(sc_img)
        npImg = cv2.cvtColor(npImg, cv2.COLOR_BGRA2BGR)
        return npImg
        # result = np.frombuffer(sc_img.bgra, dtype=np.uint8)
        # width = sc_img.size.width  # 宽度
        # height = sc_img.size.height  # 高度
        # result = cv2.cvtColor(result.reshape(
        #     (height, width, 4)), cv2.COLOR_BGRA2BGR)
        # return result


def pil2np(PILImg: Image):
    npImg = np.array(PILImg)
    return npImg


def np2pil(npImg: np.ndarray):
    pilImg = Image.fromarray(npImg)
    return pilImg


def drawOCR2np(rawImg, ocrResult, font_path , asOne = False):
    '''OCR结果绘制，输入NP，返回NP'''
    txts = []
    scores = []
    boxes = []
    boxesInt = []
    
    for _out in ocrResult:
        txts.append(_out['text'])
        scores.append(_out['score'])
        boxesInt.append(_out['position'].astype(np.int64))
        boxes.append(_out['position'])
    pilRaw = np2pil(rawImg)
    pilRaw.show()
    draw_img = draw_ocr_box_txt( pilRaw , boxes, txts, scores, drop_score=0.0, font_path=font_path)
    
    drawImg = cv2.cvtColor(draw_img, cv2.COLOR_RGB2BGR)
    width = pilRaw.width
    rawDraw = drawImg[:, :width]
    whiteDraw = drawImg[:, width:]
    if asOne == False:
        return rawDraw, whiteDraw
    else:
        cv2.fillPoly(rawDraw, boxesInt, (255, 255, 255))
        return np.where(whiteDraw == [255,255,255] , rawDraw  , whiteDraw)
    
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
    from cnocr import CnOcr
    oi = CnOcr()
    while True:
        img = url2ImgNp("http://192.168.3.155:4443/screenraw")
        # img = screenCapNP()
        img = drawHandelScreen(img)
        out = oi.ocr(img)
        a  = drawOCR2np(img , out , r"C:\Windows\Fonts\msyhl.ttc", True )
        cv2.imshow('draw', a)
        if cv2.waitKey(1) == 27:
            break
