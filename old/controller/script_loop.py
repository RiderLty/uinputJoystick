import random
from controller import *
from time import sleep as s_sleep

from time import sleep



    
    
def sleep(ms):
    s_sleep(ms/1000)

SERVER_IP = "192.168.3.128"


x = xbox_controller(controller=controller(f"{SERVER_IP}:8889"))

def fanqiang():
    x.setLS(x=0, y=-1)
    sleep(10)
    x.clickBTN(BTN_A, 10)
    sleep(10)
    x.clickBTN(BTN_LB, 5)
    sleep(5)
    x.clickBTN(BTN_A, 30)
    sleep(500)
    x.setLS(x=0, y=0)


def rSleep(miniVal,maxVal):
    ms = random.randint(miniVal,maxVal)
    sleep(ms)
    return ms

def panz(time):
    x.clickBTN(BTN_B,time)#近战蓄力
    sleep(100)
    x.clickBTN(BTN_RS,100)#引爆

def v_rush():
    sleep(200)
    x.pressBTN(BTN_RB)
    sleep(50)
    x.clickBTN(BTN_LB,50)#切指挥官
    sleep(10)
    x.releaseBTN(BTN_RB)
    sleep(10)
    x.setLS(x=0,y=1)
    sleep(400)
    x.setLS(x=0,y=0)#指挥官弹出，然后向后走一段
    
    x.clickBTN(BTN_A,10)#双跳冲刺
    sleep(80)
    x.clickBTN(BTN_A,10)
    sleep(80)
    #使用表情取消僵直 鞠躬那个 提前绑定 方向键左   NO!
    # x.setDpad(DPAD_X,-1)
    # sleep(10)
    # x.setDpad(DPAD_X,0)
    
    # 蹲下虚空 防止小小黑禁技能   提前绑定 方向键 右
    x.setDpad(DPAD_X,1)
    sleep(10)
    x.setDpad(DPAD_X,0)
    

def skill():
    sleep(200)
    x.pressBTN(BTN_RB)
    sleep(10)
    x.clickBTN(BTN_X,10) #3技能
    sleep(10)
    x.clickBTN(BTN_B,10) #2技能
    sleep(550)
    x.clickBTN(BTN_Y,10) #4技能
    sleep(100)
    x.releaseBTN(BTN_RB)
    sleep(400)



def guajiLoop():#记得盘子看向地面 不要单手副武器
    count = 0
    while True:
        count += 1
        x.setLS(x=0,y=1)#向后走
        sleep(500)
        if count %3 == 0:
            panz(850)
            x.setLS(x=0,y=0)#松开向后
            panz(800)
            skill()
        else:
            panz(850)
            x.setLS(x=0,y=0)#松开向后
            panz(800)
            panz(800)
            panz(800)
        v_rush()
        
guajiLoop()
