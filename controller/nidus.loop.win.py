import io
from time import sleep as s_sleep
from time import sleep
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


class imgFac():
    def __init__(self) -> None:
        self.screen = None
        self.inRangeScreen = None

    def setScreen(self, recapture=True):
        '获取原始屏幕'
        if recapture == True or self.screen == None:
            screen = screenCapNP()
            self.screen = screen
            return screen
        else:
            return self.screen

    def getInRangeScreen(self, recapture=True):
        '获取在指定范围内的屏幕的灰度图像'
        if recapture == True or self.inRangeScreen == None:
            inRangeScreen = handelScreen(self.setScreen(True))
            self.inRangeScreen = inRangeScreen
            return inRangeScreen
        else:
            return self.inRangeScreen

    def getOCRResult(self, recapture=False):
        '获取OCR结果图像'
        pass

    def setOCRout(self, out):
        '记录OCR结果'
        pass


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


mainLoopPaused = ThreadSafeValue(True)
watchPaused = ThreadSafeValue(True)


def sleep(ms):
    s_sleep(ms/1000)


ctr = scheduled(controller=controller())
nidus = actions(ctr=ctr)


def mainLoop(mainLoopPaused: ThreadSafeValue):
    while True:
        if mainLoopPaused.get_value() == True:
            print("主循环已暂停")
            mainLoopPaused.waitFor(False)
            print("主循环已启动")
        nidus.mainLoopOnceWait_with_backRight()
        # nidus.mainLoopOnceWait_juts_run()


def watcher(watchPaused: ThreadSafeValue, mainLoopPaused: ThreadSafeValue):  # 是否检测 false则暂停检测
    cnocrInstance = CnOcr()
    ensureCount = 0
    while True:
        if watchPaused.get_value() == True:
            print("观察者已暂停")
            watchPaused.waitFor(False)
            print("观察者已启动")
        try:
            sc_img = handelScreen(screenCapNP())
            # sc_img =  screenCapNP()
            out = cnocrInstance.ocr(sc_img)
            # draw_ocr_results(sc_img, out, r"P:\out.png", r"C:\Users\lty65\AppData\Local\Microsoft\Windows\Fonts\仿宋_GB2312.ttf")
            allText = "|".join(
                [f'{x["text"]}({x["score"]})'for x in out]).strip()
            print(datetime.datetime.now(), allText)
            # =======================================================================================
            # 检测氧气耗尽或者死亡
            detectedFlag = False
            for x in ["来复活", "前往撤离点"]:  # 死了 氧气没了（5分钟莲妈喊你可以撤了也会触发，所以检测连续出现三次）
                if x in allText:
                    detectedFlag = True
                    ensureCount += 1
                    print(f"检测到停止关键词{ensureCount}次")
                    if ensureCount >= 3:
                        watchPaused.set_value(True)
                        mainLoopPaused.set_value(True)
                        ctr.interrupt()
                        ctr.click(BTN.BTN_START)
                        ctr.wait()
                        # nvidiaVideoSave()  # 非正常
                    continue
            if detectedFlag == False:
                ensureCount = 0
            # =======================================================================================
            for x in ["报酬", "无尽加成", "已经打开的"]:
                if x in allText:
                    mainLoopPaused.set_value(True)
                    print("结算等核桃")
                    ctr.interrupt()
                    ctr.wait()
                    break
            # =======================================================================================
            # 检测遗物并执行开启
            for x in ["选择遗物", "装备以执行任务", ]:
                if x in allText:
                    print("开核桃时间!!!")
                    mainLoopPaused.set_value(True)
                    nidus.openHT()
                    sleep(1000 * 5)
                    mainLoopPaused.set_value(False)
                    break
            # =======================================================================================
            sleep(2000)
        except Exception as e:
            print(e)
            pass


@route("/jmp", method="GET")
def jmp():
    nidus.jump()


@route("/start")
def start():
    print("start")
    ctr.click(BTN.BTN_LS)
    ctr.sleep(100)
    ctr.click(BTN.BTN_B)
    ctr.sleep(1000)
    ctr.wait()
    mainLoopPaused.set_value(False)
    watchPaused.set_value(False)


@route("/stop")
def stop():
    mainLoopPaused.set_value(True)
    watchPaused.set_value(True)
    ctr.interrupt()
    ctr.click(BTN.BTN_START)
    ctr.wait()


@route("/test")  # 测试函数放在这里运行
def test():
    ctr.setRS(0, 1)
    ctr.sleep(300)
    ctr.setRS(0, 0)
    ctr.wait()


@route("/screenmask")
def screen():
    try:
        img = handelScreen(screenCapNP())
        img = np2pil(cv2.cvtColor(img, cv2.COLOR_GRAY2BGR))  # mask是灰度图像
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
        img = screenCapPIL()
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
    run(host="0.0.0.0", port=4443, reloader=False, server="paste",)


if __name__ == "__main__":
    threading.Thread(target=mainLoop, args=(mainLoopPaused,)).start()
    threading.Thread(target=watcher, args=(
        watchPaused,  mainLoopPaused,)).start()
    threading.Thread(target=server).start()

    # print("helllo")
    # # img = cv2.imread(r"D:\Pictures\Screenshots\warframe\SC (16).png")
    # img = screenCapNP()

    # img = handelScreen(img)

    # cv2.imshow('Filtered Image', img)

    # while True:
    #     if cv2.waitKey(1) == 27:
    #         break
    # cv2.destroyAllWindows()
