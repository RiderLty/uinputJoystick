import io
from time import sleep as s_sleep
from time import sleep
import threading
from bottle import *
from utils.screenCap import screenCap
from utils.taskScheduler import scheduled
from utils.interface.winController import *
import datetime
from cnocr import CnOcr
# README
#
# 先安装依赖：
# pip install pywin32 cnocr[ort-cpu] mss vgamepad bottle paste Pillow
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

# XBOX挂机的时候记得关闭辅助瞄准


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


ctr = scheduled(controller=controller())


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
    for i in range(10):
        ctr.click(BTN.BTN_A, 50)
        ctr.sleep(50)
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
        skill(3) #MAG 吸
        ctr.sleep(800)
        panZX4()  # 四发盘子
        # ctr.setRT(1)#女魔发射
        # ctr.sleep(50)
        # ctr.setRT(0)
        ctr.click(BTN.BTN_DPAD_RIGHT)
        skill(3)
        ctr.sleep(800)
        panZX4()  # 四发盘子
        
        ctr.setLS(0, 0)
        skill(4)  # 4技能
        ctr.sleep(1100)
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
        # ctr.setLT(0) # 瞄准触发蜘蛛赋能
        ctr.click(BTN.BTN_DPAD_LEFT, 200)
        ctr.setLS(0, 0)
        ctr.sleep(300)
        ctr.wait()
    stopFlag.set_value(True)
    print("控制线程已退出")

cnocrInstance = CnOcr()
def watcher(runningFlag: ThreadSafeValue, stopFlag: ThreadSafeValue):
    print("观察者线程已启动")
    global cnocrInstance
    while True:
        try:
            sc_img = screenCap()
            out = cnocrInstance.ocr(sc_img)
            allText = "|".join([x["text"] for x in out]).strip()
            print(datetime.datetime.now())
            # =======================================================================================
            # 检测氧气耗尽或者死亡
            detectedFlag = False
            for x in ["来复活", "前往撤离点"]:  # 死了 氧气没了（5分钟莲妈喊你可以撤了也会触发，所以检测连续出现三次）
                if x in allText:
                    detectedFlag = True
                    ensureCount += 1
                    print(f"检测到停止关键词{ensureCount}次")
                    if ensureCount >= 3:
                        print("观察者线程已停止!!!")
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
            if runningFlag.get_value() == True:# 仅执行一次
                for x in ["报酬", "无尽加成", "已经打开的"]:
                    if x in allText:
                        print("结算了，现在停止等核桃")
                        runningFlag.set_value(False)
                        ctr.interrupt()
                        break
            # =======================================================================================
            # 检测遗物并执行开启
            for x in ["选择遗物", "装备以执行任务", ]:
                if x in allText:
                    print("开核桃时间!!!")
                    selectHeTao(runningFlag, stopFlag)
                    break
            # =======================================================================================
            sleep(2000)
        except Exception as e:
            print(e)
            pass


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
    runningFlag.set_value(True)
    stopFlag.set_value(False)
    
    threading.Thread(target=mainLoop, args=(runningFlag, stopFlag)).start()


@route("/stop")
def stop():
    runningFlag.set_value(False)
    ctr.interrupt()
    ctr.click(BTN.BTN_START)
    ctr.wait()


@route("/test")  # 测试函数放在这里运行
def test():
    ctr.setRS(0, 1)
    ctr.sleep(300)
    ctr.setLS(0, 0)
    ctr.wait()


@route("/screen")
def screen():
    try:
        img = screenCap()
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
  <button onclick="performGetRequest('/test')">测试功能</button>
</div>
</body>
</html>'''


def server():
    run(
        host="0.0.0.0", port=4443, reloader=False, server="paste",quiet=True
    )


runningFlag = ThreadSafeValue(False)  # 表示正在运行
stopFlag = ThreadSafeValue(True)  # 表示已经停止

if __name__ == "__main__":
    threading.Thread(target=watcher, args=(runningFlag, stopFlag)).start()
    threading.Thread(target=server).start()
