import io
from time import sleep as s_sleep
from time import sleep
import threading
from bottle import *
import cv2
import numpy as np
from utils.imgTools import *
from utils.taskScheduler import scheduled
from utils.interface.winController import *
import datetime
from cnocr import CnOcr
from cnocr.utils import draw_ocr_results
from nidus_action import *
from PIL import Image

# README
#
# 先安装依赖：
# pip install pywin32 cnocr[ort-cpu] mss vgamepad bottle paste Pillow
#
# windows分辨率 1920x1080 缩放100%
# 游戏内 HUD尺寸 200%
# 关闭：辅助瞄准 动态HUD 屏幕晃动
# 手柄改键：方向左瞄准，方向右射击
#
# 手机浏览器访问  http://[电脑IP]:4443
# 准备工作做好后，ESC暂停，然后网页端点击开始

# XBOX挂机的时候记得关闭辅助瞄准

cnocrInstance = CnOcr()


class ThreadSafeValue:
    def __init__(self, value):
        self._value = value
        self._lock = threading.Lock()
        self._condition = threading.Condition()

    def set_value(self, new_value):
        with self._lock:
            self._value = new_value
            with self._condition:
                self._condition.notify_all()

    def get_value(self):
        with self._lock:
            return self._value

    def waitFor(self, value):
        # 等待self._value变为value 再返回
        while self.get_value() != value:
            with self._condition:
                self._condition.wait()
        return self._value


def sleep(ms):
    s_sleep(ms/1000)


ctr = scheduled(controller=controller())
nidus = actions(ctr=ctr)

fsm = ThreadSafeValue(-1)


def mainLoop(state: ThreadSafeValue):
    while True:
        if state.get_value() != 0:
            print("主循环已暂停")
            state.waitFor(0)
            print("主循环已启动")
        nidus.mainLoopOnceWait_with_backRight()
        # nidus.mainLoop_shoot_and_move()


def remove_non_digits(text):
    return ''.join([char for char in text if char.isdigit()])


def autoSelectHT():
    nidus.clusterReset()
    maxRightCount = -1
    maxValue = -1
    ctr.sleep(100)
    for i in range(8):
        ctr.click(BTN.BTN_DPAD_RIGHT)
        ctr.sleep(500)
        ctr.wait()
        screen = handelScreen(mss2np())
        ocrResult = cnocrInstance.ocr(screen)
        allText = "#".join([x["text"].strip() for x in ocrResult]).strip()
        print(allText)
        if "杜卡德" in allText:
            print("检测到关键词 ")
            value = int(remove_non_digits(
                allText.split("杜卡德")[0].split("#")[-1]))
            print("当前value = ", value)
            if value >= maxValue:
                maxRightCount = i
                maxValue = value
        print("\n")
    nidus.clusterReset()
    for _ in range(maxRightCount + 1):
        ctr.click(BTN.BTN_DPAD_RIGHT)
        ctr.sleep(300)
    ctr.click(BTN.BTN_A)
    ctr.wait()


def checkText(template, targets):
    for target in targets:
        if target in template:
            return True
    return False


def watcher(state: ThreadSafeValue):
    
    def goto(x):
        state.set_value(x)
    
    def eq(x):
        return state.get_value() == x

    def breakActions():
        ctr.interrupt()
        ctr.wait()

    while True:
        sc_img = handelScreen(mss2np()) # 节省资源的，不用了
        # sc_img = mss2np()
        out = cnocrInstance.ocr(sc_img)
        allText = "#".join([f'{x["text"].strip()}'for x in out]).strip()
        latestState = state.get_value()
        if eq(-1):#停止状态
            print("观察者已暂停")
            state.waitFor(0)#等待0
            print("观察者已启动")
        elif eq(0):#多数时候的状态
            if checkText(allText, ["来复活", "前往撤离点"]):#停止信号
                goto(1)#再次确认
            elif checkText(allText, ["报酬"]):#核桃开了
                goto(3)#等待选择遗物
                breakActions()#停止动作
                # autoSelectHT() #单人记得注释掉
            else:
                pass#不执行任何动作
        elif eq(1):
            if checkText(allText, ["来复活", "前往撤离点"]):#停止信号
                goto(2)#再次确认
            else:
                goto(0)#没了 回到主状态
        elif eq(2):
            if checkText(allText, ["来复活", "前往撤离点"]):#停止了
                goto(-1)#到停止态
                breakActions()
                ctr.click(BTN.BTN_START)
            else:
                goto(0)#没了 回到主状态
        elif eq(3):
            if checkText(allText, ["选择遗物"]):#选择遗物了
                goto(4) # 到等待状态
                nidus.selectHT()
            else:
                pass
        elif eq(4):
            if checkText(allText, ["生存"]):
                goto(0) #检测到关键词 回到主状态
            else:
                pass #继续等待
        latestState != state.get_value() and print(datetime.datetime.now(),f"{latestState} => {state.get_value()}")
        sleep(1000)

@route("/jmp", method="GET")
def jmp():
    nidus.jump()


@route("/start")
def start():
    print("开始")
    ctr.click(BTN.BTN_LS)
    ctr.sleep(100)
    ctr.click(BTN.BTN_B)
    ctr.sleep(1000)
    ctr.wait()
    fsm.set_value(0)


@route("/stop")
def stop():
    print("停止")
    fsm.set_value(-1)
    ctr.interrupt()
    ctr.wait()
    ctr.click(BTN.BTN_START)


@route("/test")  # 测试函数放在这里运行
def test():
    ctr.setRS(0, 1)
    ctr.sleep(300)
    ctr.setRS(0, 0)
    ctr.wait()


@route("/screenmask")
def screen():
    try:
        img = handelScreen(mss2np())
        img = np2pil(img)  # mask是灰度图像
        save_options = {
            'format': 'JPEG',
            'quality': 72  # 设置图片质量，范围为0-100
        }
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, **save_options)
        img_byte_arr = img_byte_arr.getvalue()
        response.headers['Content-Type'] = 'image/jpg'
        response.headers['Content-Length'] = len(img_byte_arr)
        return img_byte_arr
    except Exception as e:
        return str(e)


@route("/screen")
def screen():
    try:
        img = drawHandelScreen(mss2np())
        img = np2pil(img)  # mask是灰度图像
        save_options = {
            'format': 'JPEG',
            'quality': 72  # 设置图片质量，范围为0-100
        }
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, **save_options)
        img_byte_arr = img_byte_arr.getvalue()
        response.headers['Content-Type'] = 'image/jpg'
        response.headers['Content-Length'] = len(img_byte_arr)
        return img_byte_arr
    except Exception as e:
        return str(e)


@route("/screenraw")
def screen():
    try:
        img = mss2pil()
        save_options = {
            'format': 'JPEG',
            'quality': 100  # 设置图片质量，范围为0-100
        }
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, **save_options)
        img_byte_arr = img_byte_arr.getvalue()
        response.headers['Content-Type'] = 'image/jpg'
        response.headers['Content-Length'] = len(img_byte_arr)
        return img_byte_arr
    except Exception as e:
        return str(e)


@route("/screenocr")
def screen():
    try:
        screen = mss2np()
        draw = drawHandelScreen(mss2np())
        img = handelScreen(screen)
        out = cnocrInstance.ocr(img)
        rawDraw = drawOCR2np(draw, out, r"C:\Windows\Fonts\msyhl.ttc", True)
        img = np2pil(rawDraw)
        save_options = {
            'format': 'JPEG',
            'quality': 72  # 设置图片质量，范围为0-100
        }
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, **save_options)
        img_byte_arr = img_byte_arr.getvalue()
        response.headers['Content-Type'] = 'image/jpg'
        response.headers['Content-Length'] = len(img_byte_arr)
        return img_byte_arr
    except Exception as e:
        return str(e)


@route("/")
def index():
    return '''<!DOCTYPE html>
<html>
<head>
<style>
    html, body {
      height: 100%;
      margin: 0;
      padding: 0;
    }

    .container {
      display: flex;
      flex-direction: column;
      height: 100%;
    }

    .container button {
      flex: 1;
      font-size: 50px;
    }
    
    .container img {
      flex: 1;
      width: 100%
    }
  </style>
  <title>GET请求示例</title>
  <script>
    const performGetRequest = (url) => {
      fetch(url)
        .then(response => response.text())
        .then(data => {
          console.log(data);
          // 在这里可以添加处理响应数据的逻辑
        })
        .catch(error => {
          console.error('发生错误:', error);
        });
    }
    (() => {
        setInterval( () => { document.querySelector("#img").src = `/screen?t=${Date.now()}`   } , 1000)
    })()
    
  </script>
</head>
<body>
<div class="container">
  <img src="/screen" id="img" >
  <button onclick="performGetRequest('/jmp')">指挥官翻墙</button>
  <button onclick="performGetRequest('/start')">开始</button>
  <button onclick="performGetRequest('/stop')">停止</button>
  <button onclick="performGetRequest('/test')">测试功能</button>
</div>
</body>
</html>'''


def server():
    run(host="0.0.0.0", port=4443, reloader=False,   quiet=True)


if __name__ == "__main__":
    threading.Thread(target=mainLoop, args=(fsm,)).start()
    threading.Thread(target=watcher, args=(fsm,)).start()
    threading.Thread(target=server).start()

    # print("helllo")
    # # img = cv2.imread(r"D:\Pictures\Screenshots\warframe\SC (16).png")
    # img = mss2np()

    # img = handelScreen(img)

    # cv2.imshow('Filtered Image', img)

    # while True:
    #     if cv2.waitKey(1) == 27:
    #         break
    # cv2.destroyAllWindows()
