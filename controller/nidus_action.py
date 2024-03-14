import sys
from utils.taskScheduler import scheduled

from utils.interface.winController import *
if not sys.platform.startswith('win'):
    from utils.interface.serverController import *


class actions():
    def __init__(self, ctr: scheduled) -> None:
        self.ctr = ctr
        self.mainCount = 0

    def clusterReset(self):
        '''移动光标到左上角头像为止,完成后返回'''
        for _ in range(255):
            self.ctr.mouseMove(-127, -127)
            self.ctr.sleep(1)
        self.ctr.click(BTN.BTN_DPAD_RIGHT)
        self.ctr.sleep(200)
        self.ctr.wait()

    def selectHT(self,):  # 开核桃 使用方向键导航 ，先到坐上然后用手柄确认
        '''使用方向键导航到左上角，然后选择第一个核桃，完成后返回'''
        
        self.clusterReset()
        self.ctr.click(BTN.BTN_DPAD_RIGHT)
        self.ctr.sleep(100)
        self.ctr.click(BTN.BTN_DPAD_DOWN)
        self.ctr.sleep(100)
        self.ctr.click(BTN.BTN_DPAD_RIGHT)
        self.ctr.sleep(100)
        for _ in range(6):
            self.ctr.click(BTN.BTN_A, 50)
            self.ctr.sleep(50)
        self.ctr.wait()

    def skill(self, num: int):
        '''使用手柄释放技能'''
        skillList = [BTN.BTN_A, BTN.BTN_A, BTN.BTN_X,
                     BTN.BTN_B, BTN.BTN_Y, BTN.BTN_LB]
        self.ctr.press(BTN.BTN_RB)
        self.ctr.sleep(50)
        self.ctr.click(skillList[num])
        self.ctr.release(BTN.BTN_RB)

    def jump(self,):
        self.ctr.setLS(0, 1)
        self.ctr.sleep(10)
        self.ctr.click(BTN.BTN_A)
        self.ctr.sleep(10)
        self.ctr.click(BTN.BTN_LB)
        self.ctr.sleep(5)
        self.ctr.click(BTN.BTN_A, 30)
        self.ctr.sleep(500)
        self.ctr.setLS(0, 0)
        self.ctr.wait()

    def panZ(self, time: int):
        self.ctr.click(BTN.BTN_B, time)
        self.ctr.sleep(100)
        self.ctr.click(BTN.BTN_RS, 50)

    def panZX4(self,):  # 耗时 3.95
        self.ctr.sleep(100)
        self.panZ(850)
        self.panZ(800)
        self.panZ(800)
        self.panZ(800)

    def mainLoopOnceWait_with_backRight(self,):  # 右下角翻滚是可以解除挂机的，然而直前直后不行
        '''执行一次主循环，完成全部动作后返回'''
        self.ctr.setLS(-1, -1)  # 左后方走
        self.ctr.click(BTN.BTN_DPAD_LEFT)  # 女魔发射
        self.skill(3)  # MAG 吸
        self.ctr.sleep(800)
        self.panZX4()  # 四发盘子
        self.ctr.click(BTN.BTN_DPAD_LEFT)  # 女魔发射
        self.skill(3)
        self.ctr.sleep(800)
        self.panZX4()  # 四发盘子
        self.ctr.setLS(0, 0)
        self.skill(4)  # 4技能
        self.ctr.sleep(1100)
        self.ctr.setLS(0, 1)  # 向前
        self.ctr.sleep(50)
        self.ctr.click(BTN.BTN_LB)  # 向前翻滚
        self.ctr.setLS(0, 0)
        self.ctr.sleep(1000)
        self.skill(2)  # 2技能
        for _ in range(10):
            self.skill(1)
            self.ctr.sleep(100)
        self.ctr.sleep(600)
        self.ctr.setLS(1, -1)
        self.ctr.sleep(50)
        self.ctr.click(BTN.BTN_LB, 100)  # 向右后翻滚
        self.ctr.setLS(0, -1)
        self.ctr.sleep(1000)
        self.ctr.click(BTN.BTN_A)  # 跳跃
        self.ctr.sleep(200)
        self.ctr.click(BTN.BTN_DPAD_RIGHT, 200)  # 瞄准触发蜘蛛赋能
        self.ctr.setLS(0, 0)
        self.ctr.sleep(300)
        self.ctr.wait()

    def mainLoop_shoot_and_move(self):
        self.ctr.setLS(0,-1)
        self.ctr.sleep(1500)
        self.ctr.setLS(0,1)
        self.ctr.sleep(2000)
        self.ctr.setLS(0,0)
       
        for _ in range(30):  # 循环 开启时候执行一次，随后按住左键
            self.ctr.press(BTN.BTN_DPAD_LEFT)
            self.ctr.sleep(1000)
            self.ctr.release(BTN.BTN_DPAD_LEFT)
            self.ctr.sleep(10)
        self.ctr.wait()
