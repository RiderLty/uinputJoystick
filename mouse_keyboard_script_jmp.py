from controller import *
from time import sleep as s_sleep
    
def sleep(ms):
    s_sleep(ms/1000)

mk = mouse_keyboard_controller("192.168.3.43:8889")

def ulianfa():#中建引爆改键U 连发释放
    for i in range(3):
        mk.clickKey(KEY_U , 5)
        sleep(5)

def panz(time):
    mk.clickKey(KEY_E,time)
    sleep(100)
    # mk.clickKey(KEY_U , 50)
    ulianfa()




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



def mainLoop():
    print("main loop start !")
    count = 0
    while True:
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
def jmp():
    mk.pressKey(KEY_W)
    sleep(10)
    mk.clickKey(KEY_SPACE,10)
    sleep(10)
    mk.clickKey(KEY_LEFT_SHIFT,5)
    sleep(5)
    mk.clickKey(KEY_SPACE,30)
    sleep(500)
    mk.releaseKey(KEY_W)
    
    
sleep(1000)
jmp()









# 跳跃N
# 开火滚轮下
# 次要滚轮上
# 近战U
# 表情1 b