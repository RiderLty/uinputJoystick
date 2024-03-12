import io
from time import sleep as s_sleep
import threading
from bottle import *
import cv2
import numpy as np
from utils.imgTools import np2pil, screenCapPIL, screenCapNP, handelScreen
from utils.taskScheduler import scheduled
from utils.interface.winController import *
import datetime
from cnocr import CnOcr
from cnocr.utils import draw_ocr_results
from nidus_action import *
from PIL import Image


ctr = scheduled(controller=controller())
nidus = actions(ctr=ctr)
ocrInstance = CnOcr()

def remove_non_digits(text): 
    return ''.join([char for char in text if char.isdigit()])

def autoSelectHT():
    for _ in range(255):
        ctr.mouseMove(-127,-127)
        ctr.sleep(1)
    ctr.click(BTN.BTN_DPAD_RIGHT)
    ctr.sleep(200)
    ctr.wait()

    rightCount = 0
    maxRightCount = -1
    maxValue = -1
    
    
    while True:
        ctr.click(BTN.BTN_DPAD_RIGHT)
        ctr.sleep(500)
        ctr.wait()
        screen = screenCapNP()
        # cv2.imwrite(rf"P:\{rightCount}.jpg" ,screen )
        ocrResult = ocrInstance.ocr(screen)
        allText = "#".join([x["text"].strip() for x in ocrResult]).strip()
        rightCount += 1
        print(allText)
        if "杜卡德" in allText:
            print("检测到关键词 ")
            value = int(remove_non_digits(allText.split("杜卡德")[0].split("#")[-1]))
            print("当前value = ",value)
            if value > maxValue:
                maxRightCount = rightCount
                maxValue = value
        if rightCount > 8:
            break
        print("\n")

    
    print("最大为",maxValue,"向右",maxRightCount)


    for _ in range(255):
        ctr.mouseMove(-127,-127)
        ctr.sleep(1)
    ctr.click(BTN.BTN_DPAD_RIGHT)
    ctr.sleep(200)
    
    for _ in range(maxRightCount):
        ctr.click(BTN.BTN_DPAD_RIGHT)
        ctr.sleep(300)
        
    ctr.click(BTN.BTN_A)
    ctr.wait()


while True:
    print("检测中")
    img = screenCapNP()
    ocrResult = ocrInstance.ocr(img)
    allText = "#".join([x["text"].strip() for x in ocrResult]).strip()
    print(allText)
    if "报酬" in allText:
        print("\n\n开始测试")
        autoSelectHT()
        exit()
    s_sleep(1)
    

