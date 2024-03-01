import ctypes
import io
import os
from time import sleep as s_sleep
from cnocr import CnOcr
from cnocr.utils import draw_ocr_results
from time import sleep
import mss
import threading
import win32api
import win32con
import vgamepad as vg
from vgamepad import XUSB_BUTTON
from bottle import *
from PIL import Image
import requests
# README
#
# 先安装依赖：
# pip install pywin32 cnocr[ort-cpu] mss vgamepad bottle Pillow
#
# windows分辨率 1920x1080 缩放100%
# 推荐游戏内 UI 200%
#
# 改键
# 跳跃N
# 开火L
# 瞄准J
# 重击U
#
# 手机浏览器访问  http://[电脑IP]:4443
# 准备工作做好后，ESC暂停，然后网页端点击开始

vx360 = vg.VX360Gamepad()


class ThreadSafeValue:
    def __init__(self, value):
        self._value = value
        self._lock = threading.Lock()

    def set_value(self, new_value):
        with self._lock:
            self._value = new_value

    def get_value(self):
        with self._lock:
            return self._value


def sleep(ms):
    s_sleep(ms/1000)


_MapVirtualKey = ctypes.windll.user32.MapVirtualKeyA


MOUSE_BTN_LEFT = 1
MOUSE_BTN_RIGHT = 2
MOUSE_BTN_MIDDLE = 3
KEY_E = 69
KEY_U = 85
KEY_S = 83
KEY_A = 65
KEY_3 = 51
KEY_4 = 52
KEY_W = 87
KEY_LEFT_SHIFT = 0x10
KEY_D = 68
KEY_N = 78
KEY_J = 74
KEY_ESC = 0x1b
KEY_1 = 49
KEY_2 = 50
KEY_L = 76


def pressKey(num):
    win32api.keybd_event(num, _MapVirtualKey(num, 0), 0, 0)


def releaseKey(num):
    win32api.keybd_event(num, _MapVirtualKey(
        num, 0), win32con.KEYEVENTF_KEYUP, 0)


def clickKey(num, ms=50):
    pressKey(num=num)
    sleep(ms)
    releaseKey(num=num)


def mouse_press(btn):
    if btn == MOUSE_BTN_LEFT:
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    elif btn == MOUSE_BTN_RIGHT:
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
    elif btn == MOUSE_BTN_MIDDLE:
        win32api.mouse_event(win32con.MOUSEEVENTF_MIDDLEDOWN, 0, 0, 0, 0)


def mouse_release(btn):
    if btn == MOUSE_BTN_LEFT:
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    elif btn == MOUSE_BTN_RIGHT:
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
    elif btn == MOUSE_BTN_MIDDLE:
        win32api.mouse_event(win32con.MOUSEEVENTF_MIDDLEUP, 0, 0, 0, 0)


def moveWheel(x=0, y=0):
    if y == -1:
        win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, 1, 0)


def mouse_move(offset_x, offset_y):
    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE,
                         offset_x*2, offset_y*2, 0, 0)


def openHT():  # 开核桃 使用方向键导航 ，先到坐上然后用手柄确认
    for _ in range(10):
        clickKey(KEY_A, 50)
        sleep(70)
    for _ in range(5):
        clickKey(KEY_W, 50)
        sleep(70)
    for _ in range(3):
        clickKey(KEY_A, 50)
        sleep(70)
    for _ in range(3):
        clickKey(KEY_W, 50)
        sleep(70)
    clickKey(KEY_D)
    sleep(100)
    clickKey(KEY_S)
    sleep(100)
    clickKey(KEY_D)
    sleep(100)
    for _ in range(10):  # 鼠标点击不生效 用手柄A确认
        vx360.press_button(XUSB_BUTTON.XUSB_GAMEPAD_A)
        vx360.update()
        sleep(10)
        vx360.release_button(XUSB_BUTTON.XUSB_GAMEPAD_A)
        vx360.update()
        sleep(100)


def selectHeTao(runningFlag: ThreadSafeValue, stopFlag: ThreadSafeValue):
    global vx360
    runningFlag.set_value(False)
    print("等待控制线程退出")
    while True:
        if stopFlag.get_value() == True:
            break
        else:
            sleep(100)
    openHT()
    sleep(1000 * 5)
    threading.Thread(target=mainLoop, args=(runningFlag, stopFlag)).start()


def nvidiaVideoSave():  # 快捷键  英伟达的即时重放 没有就注释掉
    pressKey(18)
    sleep(50)
    clickKey(121)
    sleep(50)
    releaseKey(18)
    return

def notify():
    requests.get(f"https://trigger.macrodroid.com/87782f44-7a7b-418d-a23a-4702ddc28783/drlintriger-jv55u5hb6b?tag=important&text={'寄了'}&title={'AutoBot通知'}")


def panZ(time):  # 扔盘子 + 引爆
    clickKey(KEY_E, time)
    sleep(100)
    clickKey(KEY_U, 50)


def panZX4():  # 耗时 3.95
    sleep(100)
    panZ(850)
    panZ(800)
    panZ(800)
    panZ(800)


def mainLoop(runningFlag: ThreadSafeValue, stopFlag: ThreadSafeValue):
    print("控制线程已启动")
    runningFlag.set_value(True)
    stopFlag.set_value(False)
    while runningFlag.get_value() == True:
        if runningFlag.get_value() == False:
            break

        pressKey(KEY_S)  # 左后方走
        pressKey(KEY_A)

        clickKey(KEY_L)  # 女魔发射
        sleep(800)
        panZX4()  # 四发盘子
        clickKey(KEY_L)  # 女魔发射
        sleep(800)
        panZX4()  # 四发盘子
        releaseKey(KEY_S)
        releaseKey(KEY_A)

        clickKey(KEY_3, 50)  # 2技能
        sleep(250)
        
        clickKey(KEY_4, 50)  # 4技能
        
        if runningFlag.get_value() == False:
            break
        sleep(800)
        if runningFlag.get_value() == False:
            break

        pressKey(KEY_W)
        sleep(50)
        clickKey(KEY_LEFT_SHIFT, 50)  # 向前翻滚
        releaseKey(KEY_W)

        if runningFlag.get_value() == False:
            break
        sleep(1100)
        if runningFlag.get_value() == False:
            break
        
        clickKey(KEY_2, 50) 
        sleep(500)
        
        for _ in range(15):
            clickKey(KEY_1, 10)  
            sleep(100)
        sleep(500)
        pressKey(KEY_S)
        pressKey(KEY_D)
        clickKey(KEY_LEFT_SHIFT, 50)  # 向右后翻滚
        releaseKey(KEY_D)
        if runningFlag.get_value() == False:
            break
        sleep(1000)
        clickKey(KEY_N)  # 跳跃
        sleep(200)
        clickKey(KEY_J, 200)  # 瞄准触发蜘蛛赋能
        releaseKey(KEY_S)
        if runningFlag.get_value() == False:
            break
        sleep(300)
    stopFlag.set_value(True)
    print("控制线程已退出")


def watcher(runningFlag: ThreadSafeValue, stopFlag: ThreadSafeValue):
    ocr = CnOcr()  # 所有参数都使用默认值
    rect = (0, 0, 1920, 1080)
    ensureCount = 0
    with mss.mss() as m:
        while runningFlag.get_value() == True:
            try:
                sc_img = m.grab(rect)
                img = Image.frombytes("RGB", sc_img.size,sc_img.bgra, "raw", "BGRX")
                out = ocr.ocr(img)
                print("\n=============================================")
                allText = "".join([x["text"] for x in out]).strip()
                # =======================================================================================
                # 检测氧气耗尽或者死亡
                detectedFlag = False
                for x in ["来复活", "前往撤离点"]:  # 死了 氧气没了（5分钟莲妈喊你可以撤了也会触发，所以检测连续出现三次）
                    if x in allText:
                        detectedFlag = True
                        ensureCount += 1
                        print(f"检测到停止关键词{ensureCount}次")
                        if ensureCount >= 3:
                            print("已停止!!!")
                            runningFlag.set_value(False)
                            clickKey(KEY_ESC)
                            nvidiaVideoSave()  # 非正常
                            notify()
                            return
                        continue
                if detectedFlag == False:
                    ensureCount = 0
                # =======================================================================================
                # 检测遗物并执行开启
                for x in ["选择遗物", "装备以执行任务", ]:
                    if x in allText:
                        print("开核桃时间!!!")
                        selectHeTao(runningFlag, stopFlag)
                        break
                # =======================================================================================
                sleep(1000)
            except Exception as e:
                print(e)
                pass


@route("/jmp", method="GET")
def jmp():
    pressKey(KEY_W)
    sleep(10)
    clickKey(KEY_N, 10)
    sleep(10)
    clickKey(KEY_LEFT_SHIFT, 5)
    sleep(5)
    clickKey(KEY_N, 30)
    sleep(500)
    releaseKey(KEY_W)


@route("/start")
def start():
    if runningFlag.get_value() == True:
        return
    print("start")

    vx360.press_button(XUSB_BUTTON.XUSB_GAMEPAD_A)
    vx360.update()
    sleep(100)
    vx360.release_button(XUSB_BUTTON.XUSB_GAMEPAD_A)
    vx360.update()
    sleep(100)
    vx360.press_button(XUSB_BUTTON.XUSB_GAMEPAD_START)
    vx360.update()
    sleep(100)
    vx360.release_button(XUSB_BUTTON.XUSB_GAMEPAD_START)
    vx360.update()
    sleep(1000)
    threading.Thread(target=watcher, args=(runningFlag, stopFlag)).start()
    threading.Thread(target=mainLoop, args=(runningFlag, stopFlag)).start()


@route("/stop")
def stop():
    runningFlag.set_value(False)
    clickKey(KEY_ESC)


@route("/tht")
def testHeTao():
    openHT()


@route("/screen")
def screen():
    # start = time.time()
    rect = (0, 0, 1920, 1080)
    with mss.mss() as m:
        try:
            sc_img = m.grab(rect)
            img = Image.frombytes("RGB", sc_img.size,
                                  sc_img.bgra, "raw", "BGRX")
            img_byte_arr = io.BytesIO()
            # img = img.resize((1280, 720))
            save_options = {
                'format': 'JPEG',
                'quality': 72  # 设置图片质量，范围为0-100
            }
            img.save(img_byte_arr, **save_options)
            img_byte_arr = img_byte_arr.getvalue()
            response.headers['Content-Type'] = 'image/jpg'
            response.headers['Content-Length'] = len(img_byte_arr)
            # print("finish in ",time.time() - start)
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
  <button onclick="performGetRequest('/tht')">测试核桃</button>
</div>
</body>
</html>'''


def server():
    run(
        host="0.0.0.0", port=4443, reloader=False, server="paste"
    )


runningFlag = ThreadSafeValue(False)  # 表示正在运行
stopFlag = ThreadSafeValue(True)  # 表示已经停止

if __name__ == "__main__":
    threading.Thread(target=server).start()
    