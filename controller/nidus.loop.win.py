from utils.customLogger import *
import os
import cv2
import argparse
from os.path import join as path_join

from fastapi import FastAPI, Response, WebSocket
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from uvicorn import Config, Server

from utils.taskScheduler import scheduled
from utils.imgTools import *
from utils.scriptActions import *
from utils.tools import *
from utils.scriptController import *
# README
#
# 先安装依赖：
# pip install pywin32 cnocr[ort-cpu] mss vgamepad  Pillow  fastapi coloredlogs uvicorn[standard] argparse
#
# windows分辨率 1920x1080 缩放100%
# 游戏内 HUD尺寸 200%
# 关闭：辅助瞄准 动态HUD 屏幕晃动
# 手柄改键：方向左瞄准，方向右射击
#
# 手机浏览器访问  http://[电脑IP]:4443
# 准备工作做好后，ESC暂停，然后网页端点击开始

# XBOX挂机的时候记得关闭辅助瞄准

parser = argparse.ArgumentParser(usage="指定脚本类型\n", description="help info.")
parser.add_argument("--type", type=str, default="nidus",
                    help="执行的脚本 nidus/inaros ")
parser.add_argument("--screen", type=str, default="mss", help="截图获取方式 mss/url")
parser.add_argument("--match", type=str, default="ocr",
                    help="匹配方式 ocr/template")
parser.add_argument("--relic", type=int, default=-1, help="开核桃人数 -1 ~ 4")
args = parser.parse_args()

WINDOWS = sys.platform.startswith('win')
# ==============================================================================================================
wsLoggerClients = set()
ctr = scheduled(controller=controller()
                if WINDOWS else controller("127.0.0.1:8889"))
sci = scriptController(
    ctr=ctr,
    logger=logger,
    args=args
)
sci.start()

mainEventLoop = asyncio.get_event_loop()
# ==============================================================================================================


history = []


def websocketLogCallback(message):
    global wsLoggerClients, history
    history.append(message)
    if len(history) > 1000:
        del history[0]
    for ws in wsLoggerClients:
        mainEventLoop.create_task(ws.send_json(["new", f"{message}"]))


addLogCallback(websocketLogCallback)
# ==============================================================================================================
app = FastAPI()
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ==============================================================================================================


@app.get("/")
def index():
    return FileResponse(path_join("controller/html", "index.html"))


@app.get("/screen")
@app.get("/screen/{path}")
def screen_path(path: str = None):
    image = sci.getScreen()
    if path == "raw":
        return Response(
            cv2.imencode('.png', image)[1].tobytes(),
            headers={"Content-Type": "image/jpeg",
                     "Cache-Control": "max-age=0"},
        )

    if path == "draw":
        image = drawHandelScreen(image)
    if path == "mask":
        image = handelScreen(image)
    return Response(
        cv2.imencode('.png', image)[1].tobytes(),
        headers={"Content-Type": "image/jpeg",
                 "Cache-Control": "max-age=0"},
    )


@app.get("/jmp")
def jmp():
    logger.info("翻墙x1")
    sci.warframe.jump()


@app.get("/start")
def start():
    sci.resume()


@app.get("/stop")
def stop():
    sci.pause()


@app.get("/test")  # 测试函数放在这里运行
def test():
    logger.info("测试函数执行中")
    ctr.setRS(0, 1)
    ctr.sleep(300)
    ctr.setRS(0, 0)
    ctr.wait()
    logger.info("测试函数执行完毕")


@app.get("/exit")
def stop():
    logger.info("退出信号")
    os._exit(0)


@app.websocket("/wsLogger")
async def websocket_endpoint(websocket: WebSocket):
    # 连接建立时，将客户端添加到集合中
    await websocket.accept()
    wsLoggerClients.add(websocket)
    try:
        while True:
            await websocket.receive_text()
            await websocket.send_json(["sync", history ])
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


serverInstance = getServer(4443)
initUvicornLogger()
mainEventLoop.run_until_complete(serverInstance.serve())
