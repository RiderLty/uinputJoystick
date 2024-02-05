import ctypes
from time import sleep as s_sleep
from time import sleep
import threading
import requests
from controller import *


def sleep(ms):
    s_sleep(ms/1000)


flag = True

SERVER_IP = "192.168.3.43"
x = xbox_controller(controller=controller(f"{SERVER_IP}:8889"))


def panZ(time):
    x.clickBTN(BTN_B, time)
    sleep(100)
    x.clickBTN(BTN_RS, 50)


def panZX4():  # 耗时 3.95
    sleep(100)
    panZ(850)
    panZ(800)
    panZ(800)
    panZ(800)


def shoot():
    x.setRT(1)
    sleep(50)
    x.setRT(0)  # 来一发


skillMap = [BTN_A, BTN_A, BTN_X, BTN_B, BTN_Y, BTN_LB]


def skill(num):
    x.pressBTN(BTN_RB)
    sleep(50)
    x.clickBTN(skillMap[num])
    x.releaseBTN(BTN_RB)  # 4技能


def mainLoop():
    print("main loop start !")
    global flag
    while flag:

        x.setLS(-1, 1)

        panZX4()
        shoot()
        sleep(500)
        panZX4()
        shoot()
        
        x.setLS(0, 0)
        
        skill(4)  # 4技能
        sleep(1100)
        
        x.setLS(0, -1)
        sleep(100)
        x.clickBTN(BTN_LB)  # 向前翻滚
        x.setLS(0, 0)
        sleep(950)

        skill(2)  # 2技能
        sleep(800)

        x.setLS(1, 0.5)
        sleep(50)
        x.clickBTN(BTN_LB)  # 向右后翻滚
        x.setLS(0, 1)
        sleep(1000)

        x.clickBTN(BTN_A)  # 跳跃
        sleep(150)
        x.setLT(1)  # 瞄准
        sleep(150)
        x.setLT(0)
        x.setLS(0, 0)
        sleep(350)
    print("over!")

# def watcher():
#     ocr = CnOcr()  # 所有参数都使用默认值
#     global flag
#     rect = (0, 0, 1920, 1080)
#     with mss.mss() as m:
#         while True:
#             try:
#                 # resp = requests.get("http://192.168.3.43:8888/screen.png")
#                 # with open(r"P:\screen.png",'wb') as f:
#                 #     f.write(resp.content)
#                 img = m.grab(rect)
#                 mss.tools.to_png(img.rgb, img.size, output=r"P:\screen.png")
#                 out = ocr.ocr(r"P:\screen.png")
#                 print("\n=============================================")
#                 for res in out:
#                     print(res["text"], end=" | ")
#                     if ("来复活" in res["text"]) or ("前往撤离点" in res["text"]):
#                         print("STOP!!!")
#                         flag = False
#                         clickKey(KEY_ESC)
#                         luzhi()#非正常
#                         return
#                 key_state = win32api.GetKeyState(win32con.VK_NUMLOCK)
#                 num_lock_state = key_state & 1
#                 print("numLock",num_lock_state == 0)
#                 if num_lock_state == 0:
#                     print("STOP!!!")
#                     flag = False
#                     clickKey(KEY_ESC)
#                     return
#                 sleep(1000)
#             except Exception as e:
#                 print(e)
#                 pass


if __name__ == "__main__":
    # sleep(3000)
    # clickKey(KEY_ESC)
    # threading.Thread(target=watcher).start()
    x.pressBTN(BTN_START)
    mainLoop()


# 跳跃N
# 开火滚轮下
# 次要滚轮上
# 近战U
# 表情1 b
