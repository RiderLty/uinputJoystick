
import socket
import struct
import time

DOWN = 0x1
UP = 0x0
DEV_NAME = "rm_kbm"
EV_SYN = 0x00
EV_KEY = 0x01
EV_REL = 0x02
EV_ABS = 0x03

REL_X = 0x00
REL_Y = 0x01
REL_WHEEL = 0x08
REL_HWHEEL = 0x06
SYN_REPORT = 0x00


BTN_A = 0x130
BTN_B = 0x131
BTN_X = 0x133
BTN_Y = 0x134
BTN_LS = 0x13D
BTN_RS = 0x13E
BTN_LB = 0x136
BTN_RB = 0x137
BTN_SELECT = 0x13A
BTN_START = 0x13B
BTN_MODE = 0x13C


ABS_X = 0x00
ABS_Y = 0x01
ABS_Z = 0x02
ABS_RZ = 0x05
ABS_LT = 0x0a
ABS_RT = 0x09
ABS_HAT0X = 0x11
ABS_HAT0Y = 0x10

DPAD_X = ABS_HAT0X
DPAD_Y = ABS_HAT0Y


def pack_events(events):
    buffer = (len(events)).to_bytes(1, 'little', signed=False)
    for (type, code, value) in events:
        buffer += struct.pack('<HHi', type, code, value)
    return buffer


class controller():
    def __init__(self, addr) -> None:
        print("send all events to :", addr)
        self.targetIp = addr.split(":")[0]
        self.targetPort = int(addr.split(":")[1])
        self.udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sendArr = (self.targetIp, self.targetPort)

    def sendBtn(self, code, downUp):
        self.udpSocket.sendto(pack_events(
            [[EV_KEY, code, downUp]]), self.sendArr)

    def sendAbs(self, code, value):
        if code == ABS_HAT0X or code == ABS_HAT0Y:  # 直接发
            self.udpSocket.sendto(pack_events(
                [[EV_ABS, code, value]]), self.sendArr)
        elif code == ABS_LT or code == ABS_RT:  # 0~1 转换发
            self.udpSocket.sendto(pack_events(
                [[EV_ABS, code, int(value * 1023)]]), self.sendArr)
        else:  # -1~1 转换发
            self.udpSocket.sendto(pack_events(
                [[EV_ABS, code, int(value*32767 + 32767)]]), self.sendArr)


class xbox_controller():
    def __init__(self, controller: controller) -> None:
        self.controller = controller

    def pressBTN(self, code):  # 按下
        self.controller.sendBtn(code, DOWN)

    def releaseBTN(self, code):  # 松开
        self.controller.sendBtn(code, UP)

    def clickBTN(self,code,downTime = 0.05):
        self.controller.sendBtn(code, DOWN)
        time.sleep(downTime)
        self.controller.sendBtn(code, UP)


    def setDpad(self, dpad, value):  # DPAD_X or DPAD_Y  value = -1,0,1 方向键，无法同时按下相反方向
        self.controller.sendAbs(DPAD_X, value)

    def setLT(self, value):  # 0~1 float
        self.controller.sendAbs(ABS_LT, value)

    def setRT(self, value):  # 0~1 float
        self.controller.sendAbs(ABS_RT, value)

    def setLS(self, x=None, y=None):  # -1~1 float None为不修改
        if x:
            self.controller.sendAbs(ABS_X, x)
        if y:
            self.controller.sendAbs(ABS_Y, y)

    def setRS(self, x=None, y=None):  # -1~1 float None为不修改
        if x:
            self.controller.sendAbs(ABS_Z, x)
        if y:
            self.controller.sendAbs(ABS_RZ, y)


if __name__ == "__main__":
    print("test start ")
    ct = controller("192.168.3.43:8889")

    # def testButton(BTN, name):
    #     print("click ", name)
    #     ct.sendBtn(BTN, DOWN)
    #     time.sleep(0.2)
    #     ct.sendBtn(BTN, UP)
    #     time.sleep(0.2)

    # for (code, name) in [
    #     (BTN_A, "BTN_A"),
    #     (BTN_B, "BTN_B"),
    #     (BTN_X, "BTN_X"),
    #     (BTN_Y, "BTN_Y"),
    #     (BTN_LS, "BTN_LS"),
    #     (BTN_RS, "BTN_RS"),
    #     (BTN_LB, "BTN_LB"),
    #     (BTN_RB, "BTN_RB"),
    #     # (BTN_SELECT, "BTN_SELECT"),
    #     # (BTN_START, "BTN_START"),
    #     # (BTN_MODE, "BTN_MODE"),
    # ]:
    #     testButton(code, name)

    # for i in range(64):
    #     ct.sendAbs(ABS_LT, i/64)
    #     time.sleep(0.01)
    # ct.sendAbs(ABS_LT, 0)

    # for i in range(128):
    #     ct.sendAbs(ABS_RT, i/64)
    #     time.sleep(0.01)
    # ct.sendAbs(ABS_RT, 0)

    # ct.sendAbs(ABS_HAT0X, -1)
    # time.sleep(0.3)

    # ct.sendAbs(ABS_HAT0X, 1)
    # time.sleep(0.3)

    # ct.sendAbs(ABS_HAT0X, 0)
    # ct.sendAbs(ABS_HAT0Y, -1)
    # time.sleep(0.3)

    # ct.sendAbs(ABS_HAT0Y, 1)
    # time.sleep(0.3)

    # ct.sendAbs(ABS_HAT0Y, 0)
    # time.sleep(0.05)

    # for i in range(128):
    #     ct.sendAbs(ABS_X, (i - 64)/64)
    #     time.sleep(0.005)
    # ct.sendAbs(ABS_X, 0)

    # for i in range(128):
    #     ct.sendAbs(ABS_Y, (i - 64)/64)
    #     time.sleep(0.005)
    # ct.sendAbs(ABS_Y, 0)

    # for i in range(128):
    #     ct.sendAbs(ABS_Z, (i - 64)/64)
    #     time.sleep(0.005)
    # ct.sendAbs(ABS_Z, 0)

    # for i in range(128):
    #     ct.sendAbs(ABS_RZ, (i - 64)/64)
    #     time.sleep(0.005)
    # ct.sendAbs(ABS_RZ, 0)

    
    c=xbox_controller(controller=ct)
    
    c.clickBTN(BTN_B,1)
    time.sleep(0.1)
    c.clickBTN(BTN_RS,0.3)