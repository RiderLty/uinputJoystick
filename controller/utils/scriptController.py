import argparse
import logging
import threading

import cv2
from .imgTools import handelScreen, mss2np, templateMatch, url2ImgNp
from .scriptActions import *
from .taskScheduler import scheduled
from .tools import ThreadSafeValue, checkText , sleep


class scriptController():
    def __init__(self, ctr: scheduled,   logger: logging.Logger, args: argparse.Namespace) -> None:
        self.ctr = ctr
        self.state = ThreadSafeValue(-1)
        self.args = args
        self.logger = logger
        self.runningFlag = True
        self.ocrInstance = None
        if self.args.match == "ocr":
            from cnocr import CnOcr
            self.ocrInstance = CnOcr()
        self.warframe = actions(self.ctr)
        self.totalRelicValue = 0
        self.totalRelicCount = 0


    def start(self,):
        threading.Thread(target=self.watcher).start()
        threading.Thread(target=self.mainExecuter).start()

    def stop(self,):
        self.runningFlag = False
        self.breakActions()
        self.goto(0)

    def resume(self):
        self.totalRelicValue = 0
        self.totalRelicCount = 0 
        if self.state.get_value() == -1:
            self.ctr.click(BTN.BTN_LS)
            self.ctr.sleep(100)
            self.ctr.click(BTN.BTN_B)
            self.ctr.sleep(1000)
            self.ctr.wait()
            self.goto(0)
            self.logger.info("已发送开始信号")
        else:
            self.logger.info("已在运行，无需开始")

    def pause(self,):
        self.goto(-1)
        self.breakActions()
        self.ctr.click(BTN.BTN_START)
        if self.state.get_value() != -1:
            self.logger.info("已发送停止指令")
            self.goto(-1)
            self.ctr.interrupt()
            self.ctr.wait()
            self.ctr.click(BTN.BTN_START)
        else:
            self.logger.info("已停止，无需停止")

    def eq(self, x):
        return self.state.get_value() == x

    def goto(self, x):
        return self.state.set_value(x)

    def breakActions(self,):
        self.ctr.interrupt()
        self.ctr.wait()

    def getScreen(self,):
        if self.args.screen == "mss":
            return mss2np()
        elif self.args.screen == "url":
            return url2ImgNp("http://127.0.0.1:8888/screen.png")
        else:
            self.logger.error(f"错误的参数 args.screen:{self.args.screen}")
            return None

    def autoSelectHT(self,):
        self.warframe.clusterReset()
        maxValue = 0
        self.ctr.sleep(100)
        self.ctr.click(BTN.BTN_DPAD_DOWN)
        self.ctr.sleep(200)
        self.ctr.click(BTN.BTN_DPAD_DOWN)
        self.ctr.sleep(700)
        self.ctr.click(BTN.BTN_DPAD_UP)
        self.ctr.sleep(500)
        for i in range(self.args.relic):
            if i != 0:
                self.ctr.click(BTN.BTN_DPAD_RIGHT)  # 两次下就是第一个了
                self.ctr.sleep(700)
                self.ctr.wait()
            img = handelScreen(self.getScreen())
            text = None
            if self.args.match == "ocr":
                ocrResult = self.ocrInstance.ocr(img)
                text = "#".join([x["text"].strip() for x in ocrResult]).strip()
                self.logger.debug(text)
            elif self.args.match == "template":
                pass
            else:
                pass
            value = self.getRelicValue(img , text)
            self.logger.info(f"index = {i + 1} value = { value}")
            if value >= maxValue:
                maxValue = value
                self.ctr.click(BTN.BTN_A)
                self.ctr.wait()
        self.totalRelicValue += maxValue
        self.totalRelicCount += 1
        self.logger.info(f"杜卡德总价值{self.totalRelicValue},遗物均值{(self.totalRelicValue / self.totalRelicCount):.4f}")
    
    def watcher(self,):
        '''观察者 截图 识别 执行部分动作 控制状态机'''
        text = None
        img = None
        while self.runningFlag:
            img = self.getScreen()
            if self.args.match == "ocr":
                ocrResult = self.ocrInstance.ocr(img) 
                text = "#".join([x["text"].strip() for x in ocrResult]).strip()
            latestState = self.state.get_value()
            if self.eq(-1):  # 停止状态
                self.logger.info("观察者已暂停")
                self.state.waitFor(0)  # 等待0
                self.logger.info("观察者已启动")
            elif self.eq(0):  # 多数时候的状态
                if not self.runningFlag:
                    return
                if self.args.relic == -1 and self.checkIfStop(img, text):  # 停止信号 多人的时候没啥用了 而且沙甲还会被检测
                     self.goto(1)  # 再次确认
                elif self.checkIsReward(img, text):  # 核桃开了
                    self.goto(3)  # 等待选择遗物
                    self.breakActions()  # 停止动作
                    self.autoSelectHT()
                else:
                    pass  # 不执行任何动作
            elif self.eq(1):
                if self.checkIfStop(img, text):  # 停止信号
                    self.goto(2)  # 再次确认
                else:
                    self.goto(0)  # 没了 回到主状态
            elif self.eq(2):
                if self.checkIfStop(img, text):  # 停止了
                    self.goto(-1)  # 到停止态
                    self.breakActions()
                    self.ctr.click(BTN.BTN_START)
                else:
                    self.goto(0)  # 没了 回到主状态
            elif self.eq(3):
                if self.checkSelectRelic(img, text):  # 选择遗物了
                    self.goto(4)  # 到等待状态
                    self.warframe.dpadReset()
                    self.warframe.selectHT()
                else:
                    pass
            elif self.eq(4):
                if self.checkIfStart(img, text):
                    self.ctr.sleep(500)
                    self.goto(0)  # 检测到关键词 回到主状态
                else:
                    pass  # 继续等待
            latestState != self.state.get_value() and self.logger.info(
                f"状态改变 {latestState} => {self.state.get_value()}")
            sleep(1000)

    def mainExecuter(self,):
        '''主要执行者 默认状态时 循环执行'''
        while self.runningFlag:
            if self.state.get_value() != 0:
                self.logger.info("主循环已暂停")
                self.state.waitFor(0)
                self.logger.info("主循环已启动")
            if not self.runningFlag:
                return
            if self.args.type == "nidus":
                self.warframe.mainLoopOnceWait_with_backRight()
            elif self.args.type == "inaros":
                self.warframe.mainLoop_shoot_and_move_inaros()
            else:
                self.logger.warn(f"错误的参数 self.args.type:{self.args.type}")

    def checkIfStop(self, img=None, text=None):
        if self.args.match == "ocr":
            return checkText(text, ["来复活", "前往撤离点"])
        elif self.args.match == "template":
            return len(templateMatch(img, cv2.imread("controller/assets/lfh.png"))) > 0 or len(templateMatch(img, cv2.imread("controller/assets/cld.png"))) > 0
        else:
            self.logger.error(f"错误的参数 args.match:{self.args.match}")
            return False

    def checkIsReward(self, img=None, text=None):
        if self.args.match == "ocr":
            return checkText(text, ["报酬"])
        elif self.args.match == "template":
            return len(templateMatch(img, cv2.imread("controller/assets/bc.png"))) > 0
        else:
            self.logger.error(f"错误的参数 args.match:{self.args.match}")
            return False

    def checkSelectRelic(self, img=None, text=None):
        if self.args.match == "ocr":
            return checkText(text, ["选择遗物"])
        elif self.args.match == "template":
            return len(templateMatch(img, cv2.imread("controller/assets/xzyw.png"))) > 0
        else:
            self.logger.error(f"错误的参数 args.match:{self.args.match}")
            return False

    def checkIfStart(self, img=None, text=None):
        if self.args.match == "ocr":
            return checkText(text, ["生存"])
        elif self.args.match == "template":
            return len(templateMatch(img, cv2.imread("controller/assets/sc.png"))) > 0
        else:
            self.logger.error(f"错误的参数 args.match:{self.args.match}")
        return False

    def getRelicValue(self, img=None, text=None):
        if self.args.match == "ocr":
            for price in [15, 25, 45, 65, 100]:
                if f"{price}杜卡德" in text or f"{price}社卡德" in text:
                    return price
            return 0
        elif self.args.match == "template":
            for value in [0, 15, 25, 45, 65, 100]:
                if len(templateMatch(img, cv2.imread(f"controller/assets/dukade/{value}.png"))) > 0:
                    return value
            return 0
        else:
            self.logger.error(f"错误的参数 args.match:{self.args.match}")
            return 0


