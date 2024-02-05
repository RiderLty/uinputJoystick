from controller import *
from time import sleep as s_sleep
from controller import *
from time import sleep as s_sleep
from cnocr import CnOcr
from time import sleep
import mss
import threading
import requests

    
def sleep(ms):
    s_sleep(ms/1000)

mk = mouse_keyboard_controller("192.168.3.128:8889")


flag = True

def panz(time):
    mk.clickKey(KEY_E,time)
    sleep(100)
    mk.clickKey(KEY_U , 50)

def panzX4():#耗时 3.95
    sleep(100)
    panz(850)
    panz(800)
    panz(800)
    panz(800)


def mainLoop():
    print("main loop start !")
    count = 0
    global flag
    while flag:
        mk.pressKey(KEY_S)#左后方
        mk.pressKey(KEY_A)
        
        panzX4()    
        mk.wheel(y=-1)#来一发
        sleep(800)
        
        panzX4()
        mk.wheel(y=-1)#来一发
        
        mk.clickKey(KEY_4,50)#4技能
        sleep(1100)  
          
        mk.releaseKey(KEY_S)
        mk.releaseKey(KEY_A)
        sleep(500)
        
        
        mk.pressKey(KEY_W)
        sleep(50)
        mk.clickKey(KEY_LEFT_SHIFT,50)#向前翻滚
        mk.releaseKey(KEY_W)
        sleep(1000)
        
        
        mk.clickKey(KEY_2,50)#2技能
        sleep(800)
        
        
        mk.pressKey(KEY_S)
        mk.pressKey(KEY_D)
        mk.clickKey(KEY_LEFT_SHIFT,50)#向右后翻滚
        mk.releaseKey(KEY_D)
        sleep(1000)
        
        mk.clickKey(KEY_N)#跳跃
        sleep(200)
        mk.clickKey(KEY_J,200)#瞄准
        mk.releaseKey(KEY_S)
        sleep(300)
        
        
def watcher():
    ocr = CnOcr()  # 所有参数都使用默认值
    global flag
    while True:
        try:
            resp = requests.get("http://192.168.3.43:8888/screen.png")        
            with open(r"P:\screen.png",'wb') as f:
                f.write(resp.content)
            out = ocr.ocr(r"P:\screen.png")
            print("\n=============================================")
            for res in out:
                print(res["text"], end=" | ")
                if ("来复活" in res["text"]) or ("前往撤离点" in res["text"]):
                    print("STOP!")
                    flag = False
                    mk.clickKey(KEY_ESC)
                    exit(1)
        except Exception as e:
            print(e)
            pass    

if __name__ =="__main__":
    sleep(3000)
    mk.clickKey(KEY_ESC)
    threading.Thread(target=watcher).start()
    mainLoop()
    






# 跳跃N
# 开火滚轮下
# 次要滚轮上
# 近战U
# 表情1 b
