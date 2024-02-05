from controller import *
from time import sleep as s_sleep
from cnocr import CnOcr
from time import sleep
import mss
import threading

def sleep(ms):
    s_sleep(ms/1000)

mk = mouse_keyboard_controller("192.168.3.128:8889")

def ulianfa():#中建引爆改键U 连发释放
    for i in range(3):
        mk.clickKey(KEY_U , 5)
        sleep(5)

def panz(time):
    mk.clickKey(KEY_E,time)
    sleep(100)
    mk.clickKey(KEY_U , 50)




def v_rush():
    sleep(200)
    mk.clickKey(KEY_5,5)
    sleep(50)
    mk.clickKey(KEY_S,350)
    mk.pressKey(KEY_N)
    sleep(80)
    mk.pressKey(KEY_SPACE)
    sleep(80)
    mk.clickKey(KEY_B,5)#取消硬直 指挥官的动作
    sleep(80)
    mk.releaseKey(KEY_SPACE)
    mk.releaseKey(KEY_N)
    mk.clickKey(KEY_V)


def skills():
    sleep(200)
    mk.clickKey(KEY_3,100)
    mk.clickKey(KEY_2,550)
    mk.clickKey(KEY_4,580)






flag = True
def mainLoop():
    print("main loop start !")
    count = 0
    while flag:
            count = count + 1
            mk.pressKey(KEY_S)
            sleep(500)
            panz(850)
            mk.releaseKey(KEY_S)
            if count % 3 == 0:
                panz(800)
                skills()
            else:
                panz(800)
                panz(800)
                panz(800)
            mk.wheel(y=-1)
            v_rush()

sleep(1000)
#mainLoop()
threading.Thread(target=mainLoop).start()
ocr = CnOcr()  # 所有参数都使用默认值
rect = (0, 0, 1024, 1024)
while True:
    with mss.mss() as m:
        img = m.grab(rect)
        # mss.tools.to_png( size  [img.size.width , img.height], r"/home/lty/下载/warframe_sc.png")
        mss.tools.to_png(img.rgb, img.size, output=r"/home/lty/下载/warframe_sc.png")
        out = ocr.ocr(r"/home/lty/下载/warframe_sc.png")
        print("\n=============================================")
        for res in out:
            print(res["text"], end=" | ")
            if ("来复活" in res["text"]) or ("前往撤离点" in res["text"]):
                print("STOP!")
                flag = False
                mk.clickKey(KEY_ESC)
                exit(1)
        sleep(1000)
    







