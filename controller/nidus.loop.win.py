import logging
import threading
import cv2
import coloredlogs
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


# TYPE = scriptType.fire_multi
TYPE = scriptType.nidus_single

WINDOWS = sys.platform.startswith('win')




#==============================================================================================================
wsLoggerClients = set()

if WINDOWS:
    ctr = scheduled(controller=controller())
else:    
    ctr = scheduled(controller=controller("127.0.0.1:8889"))
    
warframe = actions(ctr=ctr)
fsm = ThreadSafeValue(-1) #状态机
#==============================================================================================================

def mainLoop(state: ThreadSafeValue , ctr:scheduled , type  :scriptType , logger : logging.Logger):
    while True:
        if state.get_value() != 0:
            logger.info("主循环已暂停")
            state.waitFor(0)
            logger.info("主循环已启动")
        type == scriptType.nidus_single and warframe.mainLoopOnceWait_with_backRight()
        type == scriptType.fire_multi and warframe.mainLoop_shoot_and_move()




if WINDOWS:
    from cnocr import CnOcr
    def watcher(state: ThreadSafeValue , ctr:scheduled , type  :scriptType , logger : logging.Logger):
        cnocrInstance = CnOcr()
        def goto(x):
            state.set_value(x)
        def eq(x):
            return state.get_value() == x
        def breakActions():
            ctr.interrupt()
            ctr.wait()
        def autoSelectHT():
            warframe.clusterReset()
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
        while True:
            # sc_img = handelScreen(mss2np())  # 节省资源的，不用了
            sc_img = mss2np()
            out = cnocrInstance.ocr(sc_img)
            allText = "#".join([f'{x["text"].strip()}'for x in out]).strip()
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
                    type == scriptType.fire_multi and autoSelectHT()  # 单人记得注释掉
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
                    warframe.clusterReset()
                    warframe.selectHT()
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
else:
    def watcher(state: ThreadSafeValue , ctr:scheduled , type  :scriptType , logger : logging.Logger):
        def goto(x):
            state.set_value(x)
        def eq(x):
            return state.get_value() == x
        def breakActions():
            ctr.interrupt()
            ctr.wait()
        while True:
            sc_img = url2ImgNp("http://127.0.0.1:8888/screen.png")
            latestState = state.get_value()
            if eq(-1):  # 停止状态
                logger.info("观察者已暂停")
                state.waitFor(0)  # 等待0
                logger.info("观察者已启动")
            elif eq(0):  # 多数时候的状态
                logger.debug("匹配撤离与复活")
                logger.debug("匹配 报酬.png")
                if len(templateMatch(sc_img , cv2.imread("controller/assets/lfh.png"))) > 0 or len(templateMatch(sc_img , cv2.imread("controller/assets/cld.png"))) > 0:  # 停止信号
                    goto(1)  # 再次确认
                elif len(templateMatch(sc_img , cv2.imread("controller/assets/bc.png"))) > 0:  # 核桃开了
                    goto(3)  # 等待选择遗物
                    breakActions()  # 停止动作
                else:
                    pass  # 不执行任何动作
            elif eq(1):
                logger.debug("匹配撤离与复活")
                if len(templateMatch(sc_img , cv2.imread("controller/assets/lfh.png"))) > 0 or len(templateMatch(sc_img , cv2.imread("controller/assets/cld.png"))) > 0:  # 停止信号
                    goto(2)  # 再次确认
                else:
                    goto(0)  # 没了 回到主状态
            elif eq(2):
                logger.debug("匹配撤离与复活")
                if len(templateMatch(sc_img , cv2.imread("controller/assets/lfh.png"))) > 0 or len(templateMatch(sc_img , cv2.imread("controller/assets/cld.png"))) > 0:  # 停止了
                    goto(-1)  # 到停止态
                    breakActions()
                    ctr.click(BTN.BTN_START)
                else:
                    goto(0)  # 没了 回到主状态
            elif eq(3):
                logger.debug("匹配 选择遗物.png")
                if len(templateMatch(sc_img , cv2.imread("controller/assets/xzyw.png"))) > 0:  # 选择遗物了
                    goto(4)  # 到等待状态
                    warframe.dpadReset()
                    warframe.selectHT()
                else:
                    pass
            elif eq(4):
                logger.debug("匹配 生存.png")
                if len(templateMatch(sc_img , cv2.imread("controller/assets/sc.png"))) > 0:
                    ctr.sleep(500)
                    goto(0)  # 检测到关键词 回到主状态
                else:
                    pass  # 继续等待
            latestState != state.get_value() and logger.info(f"状态改变 {latestState} => {state.get_value()}")
            sleep(300)


def init_logger():
    LOGGER_NAMES = ("uvicorn", "uvicorn.access",)
    for logger_name in LOGGER_NAMES:
        logging_logger = logging.getLogger(logger_name)
        fmt = f"🌏%(asctime)s .%(levelname)s %(message)s"  # 📨
        coloredlogs.install(
            level=logging.WARN, logger=logging_logger, milliseconds=False, datefmt='%m-%d %H:%M:%S', fmt=fmt
        )

#==============================================================================================================
logger = logging.getLogger(f'{"main"}:{"loger"}')
fmt = f"🤖%(asctime)s .%(levelname)s %(message)s"
coloredlogs.install(
    level=logging.DEBUG, logger=logger, milliseconds=False, datefmt='%m-%d %H:%M:%S', fmt=fmt ,
)
formatter = logging.Formatter(fmt = f"🤖%(asctime)s .%(levelname)s \t%(message)s" , datefmt='%m-%d %H:%M:%S')
def log_callback(message):
    global wsLoggerClients
    for ws in wsLoggerClients:
        mainEventLoop.create_task(ws.send_text(f"{message}"))

handler = CallbackHandler(callback=log_callback)
handler.setFormatter(formatter)
logger.addHandler(handler)
#==============================================================================================================



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


@app.get("/screen")
@app.get("/screen/{path}")
def screen_path(path: str = None):
    if WINDOWS:
        image = mss2np()
    else:
        image = url2ImgNp("http://127.0.0.1:8888/screen.png")
    
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
        cv2.imencode('.jpg', image,[int(cv2.IMWRITE_JPEG_QUALITY), 70])[1].tobytes(),
        headers={"Content-Type": "image/jpeg",
                 "Cache-Control": "max-age=0"},
    )


@app.get("/jmp")
def jmp():
    logger.info("翻墙x1")
    warframe.jump()


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
    threading.Thread(target=mainLoop, args=(fsm,ctr,TYPE,logger)).start()
    threading.Thread(target=watcher, args=(fsm,ctr,TYPE,logger)).start()
    mainEventLoop.run_until_complete(serverInstance.serve())
