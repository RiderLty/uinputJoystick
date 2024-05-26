import sys
from utils.taskScheduler import scheduled
import pyperclip

if sys.platform.startswith('win'):
    from utils.interface.winController import *
else:
    from utils.interface.serverController import *


class actions():
    def __init__(self, ctr: scheduled) -> None:
        self.ctr = ctr
        self.mainCount = 0

    def clusterReset(self):
        '''移动光标到左上角头像为止,完成后返回'''
        self.ctr.mouseMove(-65535, -65535)
        self.ctr.sleep(100)
        self.ctr.click(BTN.BTN_DPAD_RIGHT)
        self.ctr.sleep(200)
        self.ctr.wait()

    def dpadReset(self):
        '''方向键重置 功能与clusterReset相同，但适用于无鼠标情况'''
        for _ in range(8):
            self.ctr.click(BTN.BTN_DPAD_LEFT)
            self.ctr.sleep(50)
        for _ in range(5):
            self.ctr.click(BTN.BTN_DPAD_UP)
            self.ctr.sleep(50)
        for _ in range(3):
            self.ctr.click(BTN.BTN_DPAD_LEFT)
            self.ctr.sleep(50)
        for _ in range(3):
            self.ctr.click(BTN.BTN_DPAD_UP)
            self.ctr.sleep(50)
        self.ctr.wait()

    def selectHT(self,):  # 开核桃
        'Y Y left[xN] A X A'
        self.ctr.click(BTN.BTN_Y)
        self.ctr.sleep(300)
        self.ctr.click(BTN.BTN_Y)
        self.ctr.sleep(300)
        for _ in range(1):
            self.ctr.click(BTN.BTN_DPAD_LEFT)
            self.ctr.sleep(300)
        self.ctr.click(BTN.BTN_A)
        self.ctr.sleep(300)
        self.ctr.click(BTN.BTN_X)
        self.ctr.sleep(300)
        self.ctr.click(BTN.BTN_A)
        self.ctr.wait()

    def selectHT_count_by_number(self,):  # 选数量最多的核桃
        'Y Y left[xN] A X A'
        self.ctr.click(BTN.BTN_Y)
        self.ctr.sleep(900)
        self.ctr.click(BTN.BTN_DPAD_DOWN)
        self.ctr.sleep(300)
        self.ctr.click(BTN.BTN_DPAD_DOWN)
        self.ctr.sleep(300)
        self.ctr.click(BTN.BTN_DPAD_DOWN)
        self.ctr.sleep(300)
        self.ctr.click(BTN.BTN_A)
        self.ctr.sleep(300)
        self.selectHT()

    def selectHT_count_by_level(self,):  # 选一个精炼的核桃
        'Y Y left[xN] A X A'
        self.ctr.click(BTN.BTN_Y)
        self.ctr.sleep(900)
        self.ctr.click(BTN.BTN_DPAD_DOWN)
        self.ctr.sleep(300)
        self.ctr.click(BTN.BTN_DPAD_DOWN)
        self.ctr.sleep(300)
        self.ctr.click(BTN.BTN_A)
        self.ctr.sleep(300)
        self.selectHT()

    def selectHT_by_search(self, search=""):  # 选择特定核桃 搜索然后选择第一个
        'Y Y left[xN] A X A'
        pyperclip.copy(search)
        self.ctr.click(BTN.BTN_LS)
        self.ctr.sleep(300)

        self.ctr.click(KEY.KEY_BACKSPACE, 10)
        self.ctr.sleep(10)
        self.ctr.click(KEY.KEY_BACKSPACE, 10)
        self.ctr.sleep(10)
        self.ctr.click(KEY.KEY_BACKSPACE, 10)
        self.ctr.sleep(10)
        self.ctr.press(KEY.KEY_LEFT_CTRL)
        self.ctr.sleep(50)
        self.ctr.click(KEY.KEY_V)
        self.ctr.release(KEY.KEY_LEFT_CTRL)
        self.ctr.sleep(300)

        self.ctr.click(BTN.BTN_Y)
        self.ctr.sleep(300)
        self.ctr.click(BTN.BTN_Y)
        self.ctr.sleep(300)

        self.ctr.click(BTN.BTN_Y)
        self.ctr.sleep(300)
        self.ctr.click(BTN.BTN_Y)
        self.ctr.sleep(300)
        self.ctr.click(BTN.BTN_DPAD_DOWN)
        self.ctr.sleep(300)
        self.ctr.click(BTN.BTN_A)
        self.ctr.sleep(300)
        self.ctr.click(BTN.BTN_RS)
        self.ctr.sleep(300)
        self.ctr.click(BTN.BTN_X)
        self.ctr.sleep(300)
        self.ctr.click(BTN.BTN_A)
        self.ctr.sleep(2000)
        self.ctr.click(BTN.BTN_A)
        self.ctr.wait()

    # def selectSpecificHT(self,keyWord):
    #     pass

    def skill(self, num: int):
        '''使用手柄释放技能'''
        skillList = [BTN.BTN_A, BTN.BTN_A, BTN.BTN_X,
                     BTN.BTN_B, BTN.BTN_Y, BTN.BTN_LB]
        self.ctr.press(BTN.BTN_RB)
        self.ctr.sleep(50)
        self.ctr.click(skillList[num])
        self.ctr.release(BTN.BTN_RB)

    def jump(self,):
        # self.ctr.setLS(0, 1)
        # self.ctr.sleep(10)
        # self.ctr.click(BTN.BTN_A)
        # self.ctr.sleep(10)
        # self.ctr.click(BTN.BTN_LB)
        # self.ctr.sleep(5)
        # self.ctr.click(BTN.BTN_A, 30)
        # self.ctr.sleep(500)
        # self.ctr.setLS(0, 0)
        # self.ctr.wait()
        self.ctr.press(KEY.KEY_W)
        self.ctr.sleep(10)
        self.ctr.press(KEY.KEY_SPACE)
        self.ctr.sleep(10)
        self.ctr.release(KEY.KEY_SPACE)
        self.ctr.sleep(10)
        self.ctr.press(KEY.KEY_LEFT_SHIFT)
        self.ctr.sleep(16)
        self.ctr.release(KEY.KEY_LEFT_SHIFT)
        self.ctr.sleep(16)
        self.ctr.press(KEY.KEY_SPACE)
        self.ctr.sleep(50)
        self.ctr.release(KEY.KEY_SPACE)
        self.ctr.sleep(700)
        self.ctr.release(KEY.KEY_W)
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

    def mainLoop_nidus_old(self,):  # 右下角翻滚是可以解除挂机的，然而直前直后不行
        '''执行一次主循环，完成全部动作后返回'''
        self.ctr.sleep(300)
        self.ctr.click(BTN.BTN_B)
        self.ctr.sleep(300)
        for _ in range(4):
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

    def mainLoop_nidus(self,):  # 右下角翻滚是可以解除挂机的，然而直前直后不行
        '''执行一次主循环，完成全部动作后返回'''
        self.ctr.press(KEY.KEY_X)  # 四次秒复活机会
        self.ctr.setLS(-1, -1)  # 左后方走
        
        for i in range(3):
            self.ctr.click(BTN.BTN_DPAD_LEFT)  # 女魔发射
            self.ctr.sleep(800)
            self.panZX4()  # 四发盘子
            self.ctr.sleep(30)
            
        self.ctr.setLS(0, 0)
        self.skill(4)  # 4技能
        self.ctr.sleep(800)
        self.ctr.setLS(0, 1)  # 向前
        self.ctr.sleep(50)
        self.ctr.click(BTN.BTN_LB)  # 向前翻滚
        self.ctr.setLS(0, 0)
        self.ctr.sleep(900)
        self.ctr.press(BTN.BTN_RB)
        self.ctr.sleep(50)
        self.ctr.click(BTN.BTN_X, 50)
        self.ctr.sleep(700)
        for _ in range(4):  # axby
            self.ctr.click(BTN.BTN_A, 50)
            self.ctr.sleep(600)
        self.ctr.release(BTN.BTN_RB)
        # self.ctr.sleep(500)
        self.ctr.setLS(1, -1)
        self.ctr.sleep(50)
        self.ctr.click(BTN.BTN_LB, 100)  # 向右后翻滚
        self.ctr.sleep(800)
        self.ctr.setLS(0, 0)
        self.ctr.release(KEY.KEY_X)
        self.ctr.wait()

    def mainLoop_shoot_and_move(self):
        self.ctr.setLS(0, -1)
        self.ctr.sleep(1500)
        self.ctr.setLS(0, 1)
        self.ctr.sleep(2000)
        self.ctr.setLS(0, 0)

        for _ in range(30):  # 循环 开启时候执行一次，随后按住左键
            self.ctr.press(BTN.BTN_DPAD_LEFT)
            self.ctr.sleep(1000)
            self.ctr.release(BTN.BTN_DPAD_LEFT)
            self.ctr.sleep(10)
        self.ctr.wait()

    def mainLoop_inaros(self):
        for _ in range(4):
            self.ctr.setLS(0, 1)  # 向前
            self.ctr.sleep(50)
            self.ctr.click(BTN.BTN_LB)  # 向前翻滚
            self.ctr.setLS(0, 0)
            self.ctr.sleep(800)

            self.ctr.setLS(1, -1)
            self.ctr.sleep(50)
            self.ctr.click(BTN.BTN_LB)  # 向右后翻滚
            self.ctr.setLS(0, 0)
            self.ctr.sleep(800)

            self.ctr.setLS(-1, -1)  #
            self.ctr.sleep(1200)
            self.ctr.setLS(0, 0)
            self.ctr.press(BTN.BTN_DPAD_LEFT)
            self.ctr.sleep(1000 * 0.5)
            self.ctr.setLS(0, 0)
            self.ctr.sleep(1000 * 7.5)

            self.ctr.release(BTN.BTN_DPAD_LEFT)

        self.ctr.wait()

    def mainLoop_khora(self):
        self.ctr.click(BTN.BTN_B)

        self.ctr.setLS(0, 1)  # 向前
        self.ctr.sleep(50)
        self.ctr.click(BTN.BTN_LB)  # 向前翻滚
        self.ctr.setLS(0, 0)
        self.ctr.sleep(800)

        self.ctr.setLS(1, -1)
        self.ctr.sleep(50)
        self.ctr.click(BTN.BTN_LB)  # 向右后翻滚
        self.ctr.setLS(0, 0)
        self.ctr.sleep(800)

        self.ctr.setLS(-1, -1)  #
        self.ctr.sleep(200)
        self.ctr.click(BTN.BTN_LB)  # 向右后翻滚
        self.ctr.sleep(400)
        self.ctr.setLS(0, 0)
        self.ctr.sleep(500)

        self.ctr.press(BTN.BTN_DPAD_RIGHT)
        self.ctr.click(BTN.BTN_B)
        self.ctr.sleep(200)
        self.skill(4)
        self.ctr.sleep(200)
        for j in range(7):
            self.ctr.sleep(800)
            self.skill(3)
        self.ctr.release(BTN.BTN_DPAD_RIGHT)
        self.ctr.wait()

    def mainLoop_nekros(self):
        self.ctr.click(BTN.BTN_B)

        self.ctr.setLS(0, 1)  # 向前
        self.ctr.sleep(50)
        self.ctr.click(BTN.BTN_LB)  # 向前翻滚
        self.ctr.setLS(0, 0)
        self.ctr.sleep(800)

        self.ctr.setLS(1, -1)
        self.ctr.sleep(50)
        self.ctr.click(BTN.BTN_LB)  # 向右后翻滚
        self.ctr.setLS(0, 0)
        self.ctr.sleep(800)

        self.ctr.setLS(-1, -1)  #
        self.ctr.sleep(200)
        self.ctr.click(BTN.BTN_LB)  # 向右后翻滚
        self.ctr.sleep(400)
        self.ctr.setLS(0, 0)
        self.ctr.sleep(500)

        self.ctr.press(BTN.BTN_DPAD_RIGHT)
        self.ctr.click(BTN.BTN_B)
        self.ctr.sleep(450)  # 亵渎
        self.skill(3)
        self.ctr.sleep(300)
        self.skill(3)
        self.ctr.sleep(1000)
        for i in range(10):  # 集团1 复活队友
            self.skill(1)
            self.ctr.sleep(400)
        self.ctr.release(BTN.BTN_DPAD_RIGHT)
        self.ctr.wait()

    def mainLoop_dante_blm(self):
        self.ctr.click(KEY.KEY_5, 400)
        self.ctr.click(KEY.KEY_E, 100)
        for i in range(9):
            self.ctr.click(KEY.KEY_1, 10)

            self.ctr.sleep(700)
            for j in range(7):
                self.ctr.click(KEY.KEY_L, 200)
                self.ctr.click(KEY.KEY_2, 10)
                self.ctr.click(KEY.KEY_E, 500)
                # self.ctr.sleep(500)
        self.ctr.wait()

    def mainLoop_dante(self):
        self.ctr.sleep(400)
        self.ctr.press(KEY.KEY_X)
        self.ctr.setLS(0, 1)  # 向前
        self.ctr.sleep(50)
        self.ctr.click(BTN.BTN_LB)  # 向前翻滚
        self.ctr.setLS(0, 0)
        self.ctr.sleep(1200)
        self.ctr.setLS(1, -1)
        self.ctr.sleep(50)
        self.ctr.click(BTN.BTN_LB)  # 向右后翻滚
        self.ctr.setLS(0, 0)
        self.ctr.sleep(800)
        self.ctr.setLS(-1, -1)
        for _ in range(7):
            for i in range(10):
                self.ctr.click(KEY.KEY_2, 10)
                self.ctr.sleep(350)
            self.ctr.setLS(-1, -1)
            self.ctr.sleep(400)
            self.ctr.click(BTN.BTN_DPAD_LEFT) 
            self.ctr.sleep(800)
            self.panZX4()
            self.ctr.setLS(0, 0)
            self.ctr.sleep(200)
        self.ctr.release(KEY.KEY_X)
        self.ctr.wait()
    

    def mainLoop_titania(self,):
        
        self.ctr.setLS(-1, -1)  # 左后方走
        for i in range(3):
            self.skill(3)
            self.ctr.press(BTN.BTN_X)  # 四次秒复活机会
            self.ctr.click(BTN.BTN_DPAD_LEFT)  # 女魔发射
            self.ctr.sleep(800)
            self.panZX4()  # 四发盘子
            self.ctr.sleep(30)
            self.ctr.release(BTN.BTN_X)
            
        self.ctr.press(BTN.BTN_X)  # 四次秒复活机会
        self.ctr.sleep(300)
        self.ctr.setLS(0, 1)  # 向前
        self.ctr.sleep(50)
        self.ctr.click(BTN.BTN_LB)  # 向前翻滚
        self.ctr.setLS(0, 0)
        self.ctr.sleep(900)
        self.ctr.setLS(1, -1)
        self.ctr.sleep(50)
        self.ctr.click(BTN.BTN_LB, 100)  # 向右后翻滚
        self.ctr.sleep(800)
        self.ctr.setLS(0, 0)
        self.ctr.release(BTN.BTN_X)
        self.ctr.wait()