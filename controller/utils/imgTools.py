import asyncio
from io import BytesIO
import math
import time
import cv2
import mss
import numpy as np
import requests
from PIL import Image, ImageDraw, ImageFont


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


def mss2np(display_num=-1, wh=None):
    '''display_num 显示器编号  1,2,3...    -1为主显示器

    zone 抓取区域 [(x1,y1),(x2,y2)] 左上角到右下角

    返回np格式的BGR图像
    '''
    with mss.mss() as sct:
        mon = sct.monitors[display_num]
        if wh == None:
            monitor = {
                "top": mon["top"],
                "left": mon["left"] ,
                "width": mon["width"], 
                "height": mon["height"],
            }
        else:
            monitor = {
                "top": wh[0],
                "left": wh[1],
                "width": wh[2],  # 手动指定区域
                "height": wh[3],
            }
        screen = sct.grab(monitor)
        img = np.array(screen)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        return img


def mss2pil(display_num=-1, wh=None):
    '''display_num 显示器编号  1,2,3...    -1为主显示器

    zone 抓取区域 [(x1,y1),(x2,y2)] 左上角到右下角

    返回PIL的RGB图像
    '''
    with mss.mss() as sct:
        mon = sct.monitors[display_num]
        if wh == None:
            monitor = {
                "top": mon["top"],
                "left": mon["left"] ,
                "width": mon["width"],
                "height": mon["height"],
            }
        else:
            monitor = {
                "top": wh[0],
                "left": wh[1],
                "width": wh[2],  # 手动指定区域
                "height": wh[3],
            }
        screen = sct.grab(monitor)
        img = Image.frombytes("RGB", screen.size, screen.bgra, "raw", "BGRX")
        return img


def mss2BytesImg(display_num=-1, wh=None):
    '''display_num 显示器编号  1,2,3...    -1为主显示器

    zone 抓取区域 [(x1,y1),(x2,y2)] 左上角到右下角

    返回PIL的RGB图像
    '''
    with mss.mss() as sct:
        mon = sct.monitors[display_num]
        if wh == None:
            monitor = {
                "top": mon["top"],
                "left": mon["left"] ,
                "width": mon["width"],
                "height": mon["height"],
            }
        else:
            monitor = {
                "top": wh[0],
                "left": wh[1],
                "width": wh[2],  # 手动指定区域
                "height": wh[3],
            }
        screen = sct.grab(monitor)
        img_bytes = mss.tools.to_png(screen.rgb, screen.size)
        return img_bytes

def pil2np(PILImg: Image):
    return cv2.cvtColor(np.array(PILImg), cv2.COLOR_RGB2BGR)


def np2pil(npImg: np.ndarray):
    return Image.fromarray(cv2.cvtColor(np.array(npImg), cv2.COLOR_BGR2RGB))


def drawOCR2np(rawImg, ocrResult, font_path, asOne=False, miniScore=0.6):
    '''OCR结果绘制，输入NP，返回NP'''
    txts = []
    scores = []
    boxes = []
    boxesInt = []

    for _out in ocrResult:
        if miniScore >= _out['score']:
            continue
        txts.append(_out['text'])
        scores.append(_out['score'])
        boxesInt.append(_out['position'].astype(np.int64))
        boxes.append(_out['position'])
    cv2.fillPoly(rawImg, boxesInt, (255, 255, 255))
    draw_img = np2pil(rawImg)
    draw_right = ImageDraw.Draw(draw_img)
    for idx, (box, txt, score) in enumerate(zip(boxes, txts, scores)):
        draw_right.polygon(
            [
                box[0][0], box[0][1], box[1][0], box[1][1], box[2][0],
                box[2][1], box[3][0], box[3][1]
            ],
            outline=None)
        box_height = math.sqrt((box[0][0] - box[3][0])**2 + (box[0][1] - box[3][
            1])**2)
        box_width = math.sqrt((box[0][0] - box[1][0])**2 + (box[0][1] - box[1][
            1])**2)
        if box_height > 2 * box_width:
            font_size = max(int(box_width * 0.9), 10)
            font = ImageFont.truetype(font_path, font_size, encoding="utf-8")
            cur_y = box[0][1]
            for c in txt:
                try:
                    char_size = font.getsize(c)
                    draw_right.text((box[0][0] + 3, cur_y),
                                    c, fill=(0, 0, 0), font=font)
                    cur_y += char_size[1]
                except Exception as e:
                    print(f"processing [{c}] error:{str(e)}")
        else:
            font_size = max(int(box_height * 0.8), 10)
            font = ImageFont.truetype(font_path, font_size, encoding="utf-8")
            draw_right.text(
                [box[0][0], box[0][1]], txt, fill=(0, 0, 0), font=font)
    # return pil2np(draw_right.im)

    return pil2np(draw_img)

    # drawImg = cv2.cvtColor(draw_right, cv2.COLOR_RGB2BGR)
    # width = pilRaw.width
    # rawDraw = drawImg[:, :width]
    # whiteDraw = drawImg[:, width:]
    # if asOne == False:
    #     return rawDraw, whiteDraw
    # else:
    #     cv2.fillPoly(rawDraw, boxesInt, (255, 255, 255))
    #     return np.where(whiteDraw == [255,255,255] , rawDraw  , whiteDraw)


masks = [
    # 来复活
    [(0, 0), (0, 0), (134, 255)],
    [(949, 712), (1100, 851)],

    # 前往撤离点 & 生存 文字

    [(0, 255), (0, 71), (132, 255)],
    [(13, 280), (473, 861)],

    # # 报酬 （核桃开了  & 选择遗物
    [(16, 33), (83, 170), (118, 243)],
    [(246, 3), (742, 171)],

    # 遗物金币
    [(0,255),(0,37),(164,255)],
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
    raw = screen.copy()
    image_hsv = cv2.cvtColor(screen, cv2.COLOR_BGR2HSV)
    ored = np.array(0)
    for i in range(0, len(masks), 2):
        ored = cv2.bitwise_or(ored, imgFilter(image_hsv, masks[i], masks[i+1]))
    masked = cv2.bitwise_and(raw, raw, mask=ored)
    return masked

# @printPerformance


def drawHandelScreen(screen):

    out = handelScreen(screen)
    height, width, _ = screen.shape
    green_image = np.full((height, width, 3), (0,  255, 0), dtype=np.uint8)
    img = np.where(out != [0, 0, 0], green_image, screen)
    for i in range(0, len(masks), 2):
        cv2.rectangle(img, masks[i+1][0], masks[i+1][1], (0, 255, 0), 1)
    return img


def template2Mask(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresholded = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)
    return  cv2.bitwise_not(thresholded)


def templateMatch(search, target, threshold=0.8):
    img = search.copy()
    w, h = target.shape[1], target.shape[0]
    results = []
    while True:
        res = cv2.matchTemplate(img, target, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(res)
        print(max_val,max_loc)
        if max_val > 1 or max_val < threshold:
            break
        else:
            rectangle = [(max_loc[0], max_loc[1]),(max_loc[0]+w, max_loc[1] + h)]
            cv2.rectangle(img ,rectangle[0] ,rectangle[1] , [0,0,0,0] , -1 )
            results.append((max_val, rectangle))
    return results


if __name__ == "__main__":
    from cnocr import CnOcr
    oi = CnOcr()
    npcap = mss2np(zone=[(0, 1), (500, 500)])
    pilcap = mss2pil(zone=[(0, 1), (500, 500)])
    while True:
        # img = url2ImgPIL("http://192.168.3.155:4443/screenraw")
        img = handelScreen(mss2np())
        # img = pil2np(img)
        # out = oi.ocr(img)
        # img = drawOCR2np(img, out, r"C:\Windows\Fonts\msyhl.ttc", True)
        cv2.imshow('draw', img)
        if cv2.waitKey(1) == 27:
            break
