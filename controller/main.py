import platform
import threading
from utils.taskScheduler import scheduled
from utils.interface.winController import * #windows用
ctr = scheduled(controller=controller() , DEBUG = True)


# from utils.interface.serverController import * #其他平台用
# ctr = scheduled(controller=controller("127.0.0.1:8889"))



def helloWorld():
    ctr.click(KEY.KEY_H)
    ctr.click(KEY.KEY_E)
    ctr.click(KEY.KEY_L)
    ctr.click(KEY.KEY_L)
    ctr.click(KEY.KEY_O)
    ctr.sleep(500)
    ctr.click(KEY.KEY_SPACE)
    ctr.sleep(500)
    ctr.click(KEY.KEY_W)
    ctr.click(KEY.KEY_O)
    ctr.click(KEY.KEY_R)
    ctr.click(KEY.KEY_L)
    ctr.click(KEY.KEY_D)
    ctr.wait() 
    

def testJoyStick():
    for k in BTN:
        ctr.click(k,500)
        ctr.sleep(100)
    for i in range(100):
        ctr.setLT(i / 100)
        ctr.sleep(5)
    for i in range(100):
        ctr.setRT(i / 100)
        ctr.sleep(5)
    for i in range(200):
        ctr.setLS(x = (i-100) / 100 , y = None)
        ctr.sleep(5)
    for i in range(200):
        ctr.setLS(x = None , y = (i-100) / 100)
        ctr.sleep(5)
    for i in range(200):
        ctr.setRS(x = (i-100) / 100 , y = None)
        ctr.sleep(5)
    for i in range(200):
        ctr.setRS(x = None , y = (i-100) / 100)
        ctr.sleep(5)
    ctr.wait()
    
def testMouse():
    ctr.press(MOUSE.MOUSE_BTN_LEFT)
    for _ in range(100):
        ctr.mouseMove(-5,-5)
        ctr.sleep(10)
    for _ in range(100):
        ctr.mouseMove(5,5)
        ctr.sleep(10)
    ctr.release(MOUSE.MOUSE_BTN_LEFT)
    ctr.click(MOUSE.MOUSE_BTN_RIGHT)
    ctr.wait()

def testBreak():
    def breaker():
        print("三秒后中断执行")
        sleep(3) #这里是time.sleep 秒为单位 运行在其他线程
        ctr.interrupt()
    threading.Thread(target = breaker).start()
    ctr.click(KEY.KEY_1,10)
    ctr.sleep(1000)
    ctr.click(KEY.KEY_2,10)
    ctr.sleep(1000)
    ctr.click(KEY.KEY_3,10)
    ctr.sleep(1000)
    ctr.click(KEY.KEY_4,10)
    ctr.sleep(1000)
    ctr.click(KEY.KEY_5,10)
    ctr.sleep(1000)
    ctr.wait()
# testMouse()
# testJoyStick()
# helloWorld()1
testBreak()
ctr.stop()