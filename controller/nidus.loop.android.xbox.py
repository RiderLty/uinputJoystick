import io
from time import sleep as s_sleep
from time import sleep
import threading
from bottle import *
import requests
# from utils.screenCap import screenCap
from utils.taskScheduler import scheduled
# from utils.interface.winController import *
from utils.interface.serverController import *
from PIL import Image
import aircv as ac
import numpy as np
import socket

# README
#
# 先安装依赖：
# pip install pywin32 cnocr[ort-cpu] mss vgamepad bottle paste Pillow
#
# windows分辨率 1920x1080 缩放100%
# 推荐游戏内 UI 200%
#
# 改键
# xbox里 
# 方向左 瞄准
# 方向右 射击（防止弹出聊天框）



#
# 手机浏览器访问  http://[电脑IP]:4443
# 准备工作做好后，ESC暂停，然后网页端点击开始

# XBOX挂机的时候记得关闭辅助瞄准

IP = "192.168.3.43"
SCRIPT_PATH = os.path.abspath(__file__)


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


# ctr = scheduled(controller=controller())
ctr = scheduled(controller=controller(IP+":8889"))


def openHT():  # 开核桃 使用方向键导航 ，先到坐上然后用手柄确认
    for _ in range(10):
        ctr.click(BTN.BTN_DPAD_LEFT)
        ctr.sleep(70)
    for _ in range(5):
        ctr.click(BTN.BTN_DPAD_UP)
        sleep(70)
    for _ in range(3):
        ctr.click(BTN.BTN_DPAD_LEFT)
        sleep(70)
    for _ in range(3):
        ctr.click(BTN.BTN_DPAD_UP)
        sleep(70)
    ctr.click(BTN.BTN_DPAD_RIGHT)
    ctr.sleep(100)
    ctr.click(BTN.BTN_DPAD_DOWN)
    ctr.sleep(100)
    ctr.click(BTN.BTN_DPAD_RIGHT)
    ctr.sleep(100)
    ctr.click(BTN.BTN_A, 10)
    ctr.sleep(300)
    ctr.click(BTN.BTN_A, 10)
    ctr.sleep(300)
    ctr.click(BTN.BTN_A, 10)
    ctr.sleep(300)
    ctr.wait()


def selectHeTao(runningFlag: ThreadSafeValue, stopFlag: ThreadSafeValue):
    runningFlag.set_value(False)
    ctr.interrupt()
    openHT()
    sleep(1000 * 5)
    threading.Thread(target=mainLoop, args=(runningFlag, stopFlag)).start()


def nvidiaVideoSave():  # 快捷键  英伟达的即时重放 没有就注释掉
    # pressKey(18)
    # sleep(50)
    # clickKey(121)
    # sleep(50)
    # releaseKey(18)
    return


def panZ(time):  # 扔盘子 + 引爆
    ctr.click(BTN.BTN_B, time)
    ctr.sleep(100)
    ctr.click(BTN.BTN_RS, 50)


def panZX4():  # 耗时 3.95
    ctr.sleep(100)
    panZ(850)
    panZ(800)
    panZ(800)
    panZ(800)


def skill(num):
    skillList = [BTN.BTN_A, BTN.BTN_A, BTN.BTN_X,
                 BTN.BTN_B, BTN.BTN_Y, BTN.BTN_LB]
    ctr.press(BTN.BTN_RB)
    ctr.sleep(50)
    ctr.click(skillList[num])
    ctr.release(BTN.BTN_RB)


def mainLoop(runningFlag: ThreadSafeValue, stopFlag: ThreadSafeValue):
    print("控制线程已启动")
    runningFlag.set_value(True)
    stopFlag.set_value(False)
    while runningFlag.get_value() == True:
        ctr.setLS(-1, -1)  # 左后方走
        # ctr.setRT(1)  # 女魔发射
        # ctr.sleep(50)
        # ctr.setRT(0)
        ctr.click(BTN.BTN_DPAD_RIGHT)
        ctr.sleep(800)
        panZX4()  # 四发盘子
        # ctr.setRT(1)  # 女魔发射
        # ctr.sleep(50)
        # ctr.setRT(0)
        ctr.click(BTN.BTN_DPAD_RIGHT)
        ctr.sleep(800)
        panZX4()  # 四发盘子
        skill(4)  # 4技能
        ctr.sleep(1100)
        ctr.setLS(0, 0)
        ctr.sleep(500)

        ctr.setLS(0, 1)  # 向前
        ctr.sleep(50)
        ctr.click(BTN.BTN_LB)  # 向前翻滚
        ctr.setLS(0, 0)

        ctr.sleep(1000)
        skill(2)  # 2技能
        ctr.sleep(800)

        ctr.setLS(1, -1)
        ctr.sleep(50)
        ctr.click(BTN.BTN_LB, 100)  # 向右后翻滚
        ctr.setLS(0, -1)
        ctr.sleep(1000)
        ctr.click(BTN.BTN_A)  # 跳跃
        ctr.sleep(200)
        # ctr.setLT(1)
        # ctr.sleep(200)
        # ctr.setLT(0)  # 瞄准触发蜘蛛赋能
        ctr.click(BTN.BTN_DPAD_LEFT,200)
        ctr.setLS(0, 0)
        ctr.sleep(300)
        ctr.wait()
    stopFlag.set_value(True)
    print("控制线程已退出")


def loadImage(directory):
    image_list = []
    supported_extensions = ['.jpg', '.jpeg', '.png', '.gif']  # 支持的图片文件扩展名
    # 遍历指定目录下的所有文件
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        # 检查文件是否是图片文件
        if os.path.isfile(file_path) and any(filename.lower().endswith(ext) for ext in supported_extensions):
            try:
                # 加载图片为PIL的Image对象
                image = Image.open(file_path)
                image_list.append(np.array(image))
            except Exception as e:
                print(f"无法加载图像文件: {file_path}. 错误: {str(e)}")

    return image_list


def findImg(bigImg, smallImgList):
    maxConfidence = 0
    for smallImg in smallImgList:
        result = ac.find_template(bigImg, smallImg)
        if result != None:
            maxConfidence = max(maxConfidence, result["confidence"])
    return maxConfidence


def watcher(runningFlag: ThreadSafeValue, stopFlag: ThreadSafeValue):
    global SCRIPT_PATH
    script_dir = os.path.dirname(SCRIPT_PATH)
    assets_dir = os.path.join(script_dir, 'assets')
    stopImgList = loadImage(os.path.join(assets_dir, 'stop'))
    hetaoImgList = loadImage(os.path.join(assets_dir, 'hetao'))
    while runningFlag.get_value() == True:
        # try:
        response = requests.get(f"http://{IP}:8888/screen.png")
        sc_img = np.array(Image.open(BytesIO(response.content)))
        stopConf = findImg(sc_img, stopImgList)
        hetaoConf = findImg(sc_img, hetaoImgList)
        print("conf:",stopConf,hetaoConf)
        # =======================================================================================
        # 检测氧气耗尽或者死亡
        detectedFlag = False
        if stopConf > 0.9:  # 死了 氧气没了（5分钟莲妈喊你可以撤了也会触发，所以检测连续出现三次）
            detectedFlag = True
            ensureCount += 1
            print(f"检测到停止图片{ensureCount}次")
            if ensureCount >= 3:
                print("已停止!!!")
                runningFlag.set_value(False)
                ctr.interrupt()
                ctr.click(BTN.BTN_START)
                ctr.wait()
                nvidiaVideoSave()  # 非正常
                return
            continue
        if detectedFlag == False:
            ensureCount = 0
        # =======================================================================================
        # 检测遗物并执行开启
        if hetaoConf > 0.9:
            print("开核桃时间!!!")
            selectHeTao(runningFlag, stopFlag)
            continue
        # =======================================================================================
        sleep(1000)
        # except Exception as e:
        #     print("ERR:",e)
        #     pass


@route("/jmp", method="GET")
def jmp():
    ctr.setLS(0, 1)
    ctr.sleep(10)
    ctr.click(BTN.BTN_A)
    ctr.sleep(10)
    ctr.click(BTN.BTN_LB)
    ctr.sleep(5)
    ctr.click(BTN.BTN_A, 30)
    ctr.sleep(500)
    ctr.setLS(0, 0)
    ctr.wait()


@route("/start")
def start():
    if runningFlag.get_value() == True:
        return
    print("start")
    ctr.click(BTN.BTN_LS)
    ctr.sleep(100)
    ctr.click(BTN.BTN_START)
    ctr.sleep(1000)
    ctr.wait()
    threading.Thread(target=watcher, args=(runningFlag, stopFlag)).start()
    threading.Thread(target=mainLoop, args=(runningFlag, stopFlag)).start()


@route("/stop")
def stop():
    runningFlag.set_value(False)
    ctr.interrupt()
    ctr.click(BTN.BTN_START)
    ctr.wait()


@route("/test")  # 测试函数放在这里运行
def test():
    # ctr.click(BTN.BTN_DPAD_DOWN)
    # ctr.sleep(100)
    # ctr.click(BTN.BTN_DPAD_RIGHT)
    # ctr.sleep(100)
    # ctr.click(BTN.BTN_DPAD_UP)
    # ctr.sleep(100)
    # ctr.click(BTN.BTN_DPAD_LEFT)
    # ctr.sleep(100)
    # ctr.wait()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    sock.sendto(b'\x01\x00\x00\x00\x00\x00\x00', ('192.168.3.104', 5644))
    s_sleep(0.2)
    sock.sendto(b'\x00\x00\x00\x00\x00\x00\x00' ,('192.168.3.104', 5644))
    s_sleep(0.3)
    sock.sendto(b'\x00\x00\x1a\x00\x00\x00\x00\x00', ("192.168.3.104", 5643))
    s_sleep(0.01)
    sock.sendto(b'\x00\x00,\x1a\x00\x00\x00\x00', ("192.168.3.104", 5643))
    s_sleep(0.02)
    sock.sendto(b'\x00\x00\x1a\x00\x00\x00\x00\x00', ("192.168.3.104", 5643))
    s_sleep(0.02)
    sock.sendto(b'\x02\x00\x1a\x00\x00\x00\x00\x00', ("192.168.3.104", 5643))
    s_sleep(0.01)
    sock.sendto(b'\x00\x00\x1a\x00\x00\x00\x00\x00', ("192.168.3.104", 5643))
    s_sleep(0.01)
    sock.sendto(b'\x00\x00,\x1a\x00\x00\x00\x00', ("192.168.3.104", 5643))
    s_sleep(0.06)
    sock.sendto(b'\x00\x00\x1a\x00\x00\x00\x00\x00', ("192.168.3.104", 5643))
    s_sleep(0.5)
    sock.sendto(b'\x00\x00\x00\x00\x00\x00\x00\x00', ("192.168.3.104", 5643))
    sock.close()

@route("/screen")
def screen():
    redirect(f"http://{IP}:8888/screen.png")


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
        setInterval( () => { document.querySelector("#img").src = `/screen?t=${Date.now()}`   } , 4000)
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
    run(
        host="0.0.0.0", port=4443, reloader=False, server="paste", quiet=True
    )


runningFlag = ThreadSafeValue(False)  # 表示正在运行
stopFlag = ThreadSafeValue(True)  # 表示已经停止

if __name__ == "__main__":
    threading.Thread(target=server).start()
    # print(__file__)
    # script_path = os.path.abspath(__file__)
    # script_dir = os.path.dirname(script_path)
    # assets_dir = os.path.join(script_dir, 'assets')
    # stopImg = loadImage(os.path.join(assets_dir, 'stop'))
    # hetaoImg = loadImage(os.path.join(assets_dir, 'hetao'))
    # response  = requests.get(f"http://{IP}:8888/screen.png")
    # sc_img = Image.open(BytesIO(response.content))
    # bigImg = np.array(sc_img)
    # print(findImg(bigImg , stopImg))
    # ctr.stop()
