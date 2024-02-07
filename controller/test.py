import threading
from time import sleep
from utils.taskScheduler import scheduled
# from utils.interface.winController import *
from utils.interface.serverController import *

if __name__ == "__main__":

    c = scheduled(controller=controller("192.168.137.33:8889"))
    c.sleep(1000)
    c.click(BTN.BTN_DPAD_DOWN,500)
    c.sleep(500)
    c.click(BTN.BTN_DPAD_RIGHT,500)
    c.sleep(500)
    c.click(BTN.BTN_DPAD_UP,500)
    c.sleep(500)
    c.click(BTN.BTN_DPAD_LEFT,500 )
    c.wait()
    # c.stop()
    
    def breaker():
        sleep(5)
        c.interrupt()
    # threading.Thread(target = breaker).start()
    
    
    print("test start in 3s")
    # c.sleep(3000)
    
    # c = controller("192.168.137.33:8889")
    # for k in KEY:
    #     print(k)
    #     c.click(k)

    # for b in MOUSE:
    #     c.click(b,200)
    #     c.sleep(5)

    for b in BTN:
        c.click(b,200)
        c.sleep(5)

    for i in range(100):
        c.setLT(i / 100)
        c.sleep(5)

    for i in range(100):
        c.setRT(i / 100)
        c.sleep(5)

    for i in range(200):
        c.setLS(x = (i-100) / 100 , y = None)
        c.sleep(5)

    for i in range(200):
        c.setLS(x = None , y = (i-100) / 100)
        c.sleep(5)

    for i in range(200):
        c.setRS(x = (i-100) / 100 , y = None)
        c.sleep(5)

    for i in range(200):
        c.setRS(x = None , y = (i-100) / 100)
        c.sleep(5)

    c.wait()
    c.stop()
    
