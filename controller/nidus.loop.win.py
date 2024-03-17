from enum import Enum
import io
import logging
from time import sleep as s_sleep
from time import sleep
import threading
from bottle import *
import cv2
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import numpy as np
from utils.imgTools import *
from utils.taskScheduler import scheduled
from utils.interface.winController import *
import datetime
from cnocr import CnOcr
from cnocr.utils import draw_ocr_results
from nidus_action import *
from PIL import Image
from fastapi import FastAPI, HTTPException, Request, Response, WebSocket, WebSocketDisconnect
import coloredlogs
from uvicorn import Config, Server
from os.path import join as path_join
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
# README
#
# 先安装依赖：
# pip install pywin32 cnocr[ort-cpu] mss vgamepad  Pillow  fastapi coloredlogs uvicorn[standard]
#
# windows分辨率 1920x1080 缩放100%
# 游戏内 HUD尺寸 200%
# 关闭：辅助瞄准 动态HUD 屏幕晃动
# 手柄改键：方向左瞄准，方向右射击
#
# 手机浏览器访问  http://[电脑IP]:4443
# 准备工作做好后，ESC暂停，然后网页端点击开始

# XBOX挂机的时候记得关闭辅助瞄准



wsLoggerClients = set()

def log_callback(message):
    for ws in wsLoggerClients:
        mainEventLoop.create_task(ws.send_text(f"{message}"))
    
logger = logging.getLogger(f'{"main"}:{"loger"}')
fmt = f"🤖%(asctime)s .%(levelname)s %(message)s"
coloredlogs.install(
    level=logging.INFO, logger=logger, milliseconds=False, datefmt='%m-%d %H:%M:%S', fmt=fmt ,
)
formatter = logging.Formatter(fmt = f"🤖%(asctime)s .%(levelname)s \t%(message)s" , datefmt='%m-%d %H:%M:%S')
class CallbackHandler(logging.Handler):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    def emit(self, record):
        msg = self.format(record)
        self.callback(msg)

handler = CallbackHandler(callback=log_callback)
handler.setFormatter(formatter)
logger.addHandler(handler)

last_ocr_text = ""
class scriptType(Enum):
    nidus_single = 0
    fire_multi = 1


# TYPE = scriptType.fire_multi
TYPE = scriptType.nidus_single


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
    global TYPE
    while True:
        if state.get_value() != 0:
            logger.info("主循环已暂停")
            state.waitFor(0)
            logger.info("主循环已启动")
        TYPE == scriptType.nidus_single and nidus.mainLoopOnceWait_with_backRight()
        TYPE == scriptType.fire_multi and nidus.mainLoop_shoot_and_move()


def remove_non_digits(text):
    return ''.join([char for char in text if char.isdigit()])


def autoSelectHT():
    nidus.clusterReset()
    maxValue = -1
    ctr.sleep(100)
    ctr.click(BTN.BTN_DPAD_DOWN)
    ctr.sleep(50)
    ctr.click(BTN.BTN_DPAD_DOWN)
    ctr.sleep(50)
    for i in range(4):
        if i != 0:
            ctr.click(BTN.BTN_DPAD_RIGHT)  # 两次下就是第一个了
        ctr.sleep(700)
        ctr.wait()
        screen = handelScreen(mss2np())
        ocrResult = cnocrInstance.ocr(screen)
        allText = "#".join([x["text"].strip() for x in ocrResult]).strip()
        logger.debug(allText)
        for keyword in ["杜卡德", "社卡德"]:
            if keyword in allText:
                logger.info(f"检测到关键词 {keyword}")
                value = int(remove_non_digits(
                    allText.split(keyword)[0].split("#")[-1]))
                logger.info(f"当前金币值为{value}")
                if value >= maxValue:
                    maxValue = value
                    ctr.click(BTN.BTN_A)
                    ctr.wait()
                break
    ctr.wait()


def checkText(template, targets):
    for target in targets:
        if target in template:
            return True
    return False


def watcher(state: ThreadSafeValue):
    global TYPE, last_ocr_text

    def goto(x):
        state.set_value(x)

    def eq(x):
        return state.get_value() == x

    def breakActions():
        ctr.interrupt()
        ctr.wait()

    while True:
        # sc_img = handelScreen(mss2np())  # 节省资源的，不用了
        sc_img = mss2np()
        out = cnocrInstance.ocr(sc_img)
        allText = "#".join([f'{x["text"].strip()}'for x in out]).strip()
        last_ocr_text = allText
        latestState = state.get_value()
        if eq(-1):  # 停止状态
            logger.info("观察者已暂停")
            state.waitFor(0)  # 等待0
            logger.info("观察者已启动")
        elif eq(0):  # 多数时候的状态
            if checkText(allText, ["来复活", "前往撤离点"]):  # 停止信号
                goto(1)  # 再次确认
            elif checkText(allText, ["报酬"]):  # 核桃开了
                goto(3)  # 等待选择遗物
                breakActions()  # 停止动作
                TYPE == scriptType.fire_multi and autoSelectHT()  # 单人记得注释掉
            else:
                pass  # 不执行任何动作
        elif eq(1):
            if checkText(allText, ["来复活", "前往撤离点"]):  # 停止信号
                goto(2)  # 再次确认
            else:
                goto(0)  # 没了 回到主状态
        elif eq(2):
            if checkText(allText, ["来复活", "前往撤离点"]):  # 停止了
                goto(-1)  # 到停止态
                breakActions()
                ctr.click(BTN.BTN_START)
            else:
                goto(0)  # 没了 回到主状态
        elif eq(3):
            if checkText(allText, ["选择遗物"]):  # 选择遗物了
                goto(4)  # 到等待状态
                nidus.selectHT()
            else:
                pass
        elif eq(4):
            if checkText(allText, ["生存"]):
                ctr.sleep(500)
                goto(0)  # 检测到关键词 回到主状态
            else:
                pass  # 继续等待
        latestState != state.get_value() and logger.info(f"状态改变 {latestState} => {state.get_value()}")
        sleep(1000)


def init_logger():
    LOGGER_NAMES = ("uvicorn", "uvicorn.access",)
    for logger_name in LOGGER_NAMES:
        logging_logger = logging.getLogger(logger_name)
        fmt = f"🌏%(asctime)s .%(levelname)s %(message)s"  # 📨
        coloredlogs.install(
            level=logging.WARN, logger=logging_logger, milliseconds=False, datefmt='%m-%d %H:%M:%S', fmt=fmt
        )


app = FastAPI()
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

mainEventLoop = asyncio.get_event_loop()


@app.get("/")
def index():
    return FileResponse(path_join("controller/html", "index.html"))


@app.get("/ocr")
def last_ocr_result():
    global last_ocr_text
    return last_ocr_text


@app.get("/screen")
@app.get("/screen/{path}")
def screen_path(path: str = None):
    image = mss2np()
    if path == "raw":
        return Response(
        cv2.imencode('.png', image)[1].tobytes(),
        headers={"Content-Type": "image/jpeg",
                 "Cache-Control": "max-age=31536000"},
    )
    if path == "ocr":
        screen = image.copy()
        img = handelScreen(screen)
        out = cnocrInstance.ocr(img)
        draw = drawHandelScreen(image)
        image = drawOCR2np(draw, out, r"NotoSansHans-Regular-2.ttf", True)
    if path == "draw":
        image = drawHandelScreen(image)
    if path == "mask":
        image = handelScreen(image)
    return Response(
        cv2.imencode('.jpg', image,[int(cv2.IMWRITE_JPEG_QUALITY), 70])[1].tobytes(),
        headers={"Content-Type": "image/jpeg",
                 "Cache-Control": "max-age=31536000"},
    )


@app.get("/jmp")
def jmp():
    logger.info("翻墙x1")
    nidus.jump()


@app.get("/start")
def start():
    global fsm
    if fsm.get_value() == -1:
        logger.info("已发送开始指令")
        ctr.click(BTN.BTN_LS)
        ctr.sleep(100)
        ctr.click(BTN.BTN_B)
        ctr.sleep(1000)
        ctr.wait()
        fsm.set_value(0)
    else:
        logger.info("已在运行")

@app.get("/stop")
def stop():
    if fsm.get_value() != -1:
        logger.info("已发送停止指令")
        fsm.set_value(-1)
        ctr.interrupt()
        ctr.wait()
        ctr.click(BTN.BTN_START)
    else:
        logger.info("已停止")

@app.get("/test")  # 测试函数放在这里运行
def test():
    logger.info("测试函数执行中")
    ctr.setRS(0, 1)
    ctr.sleep(300)
    ctr.setRS(0, 0)
    ctr.wait()
    logger.info("测试函数执行完毕")
    


@app.websocket("/wsLogger")
async def websocket_endpoint(websocket: WebSocket):
    # 连接建立时，将客户端添加到集合中
    await websocket.accept()
    wsLoggerClients.add(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            pass
    except Exception as e:
        wsLoggerClients.remove(websocket)
        pass

app.mount("/", StaticFiles(directory="controller/html"), name="static")

def getServer(port):
    serverConfig = Config(
        app=app,
        # host="::",
        host="0.0.0.0",
        port=port,
        log_level="info",
        ws_max_size=1024*1024*1024*1024,
    )
    return Server(serverConfig)


if __name__ == "__main__":
    serverInstance = getServer(4443)
    init_logger()
    threading.Thread(target=mainLoop, args=(fsm,)).start()
    threading.Thread(target=watcher, args=(fsm,)).start()
    mainEventLoop.run_until_complete(serverInstance.serve())
