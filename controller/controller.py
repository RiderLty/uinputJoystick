
import socket
import struct
import time

DOWN = 0x1
UP = 0x0
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
ABS_HAT0X = 0x10
ABS_HAT0Y = 0x11

DPAD_X = ABS_HAT0X
DPAD_Y = ABS_HAT0Y

KEY_ESC = 1
KEY_1 = 2
KEY_2 = 3
KEY_3 = 4
KEY_4 = 5
KEY_5 = 6
KEY_6 = 7
KEY_7 = 8
KEY_8 = 9
KEY_9 = 10
KEY_0 = 11
KEY_MINUS = 12
KEY_EQUALS = 13
KEY_BCKSPC = 14
KEY_TAB = 15
KEY_Q = 16
KEY_W = 17
KEY_E = 18
KEY_R = 19
KEY_T = 20
KEY_Y = 21
KEY_U = 22
KEY_I = 23
KEY_O = 24
KEY_P = 25
KEY_LBRACKET = 26
KEY_RBRACKET = 27
KEY_RETURN = 28
KEY_LEFT_CTRL = 29
KEY_A = 30
KEY_S = 31
KEY_D = 32
KEY_F = 33
KEY_G = 34
KEY_H = 35
KEY_J = 36
KEY_K = 37
KEY_L = 38
KEY_SEMICOLON = 39
KEY_QUOTE = 40
KEY_BACKQUOTE = 41
KEY_LEFT_SHIFT = 42
KEY_BACKSLASH = 43
KEY_Z = 44
KEY_X = 45
KEY_C = 46
KEY_V = 47
KEY_B = 48
KEY_N = 49
KEY_M = 50
KEY_COMMA = 51
KEY_PERIOD = 52
KEY_SLASH = 53
KEY_RIGHT_SHIFT = 54
KEY_KP_MULTIPLY = 55
KEY_LEFT_ALT = 56
KEY_SPACE = 57
KEY_CAPS_LOCK = 58
KEY_F1 = 59
KEY_F2 = 60
KEY_F3 = 61
KEY_F4 = 62
KEY_F5 = 63
KEY_F6 = 64
KEY_F7 = 65
KEY_F8 = 66
KEY_F9 = 67
KEY_F10 = 68
KEY_NUM_LOCK = 69
KEY_SCROLL_LOCK = 70
KEY_KP_7 = 71
KEY_KP_8 = 72
KEY_KP_9 = 73
KEY_KP_MINUS = 74
KEY_KP_4 = 75
KEY_KP_5 = 76
KEY_KP_6 = 77
KEY_KP_PLUS = 78
KEY_KP_1 = 79
KEY_KP_2 = 80
KEY_KP_3 = 81
KEY_KP_0 = 82
KEY_KP_PERIOD = 83
KEY_F11 = 87
KEY_F12 = 88
KEY_KP_ENTER = 96
KEY_RIGHT_CTRL = 97
KEY_KP_DIVIDE = 98
KEY_PRINT = 99
KEY_RIGHT_ALT = 100
KEY_HOME = 102
KEY_UP = 103
KEY_PAGEUP = 104
KEY_LEFT = 105
KEY_RIGHT = 106
KEY_END = 107
KEY_DOWN = 108
KEY_PAGEDOWN = 109
KEY_INSERT = 110
KEY_DEL = 111
KEY_PAUSE = 119
KEY_LEFT_GUI = 125
KEY_RIGHT_GUI = 126
KEY_APPLICATION = 127

MOUSE_BTN_LEFT     = 0X110
MOUSE_BTN_RIGHT    = 0X111
MOUSE_BTN_MIDDLE   = 0X112
MOUSE_BTN_SIDE     = 0X113
MOUSE_BTN_EXTRA    = 0X114
MOUSE_BTN_FORWARD  = 0X115
MOUSE_BTN_BACK     = 0X116
MOUSE_BTN_TASK     = 0X117
MOUSE_BTN_MOUSE    = 0X110




def pack_events(events):
    buffer = (len(events)).to_bytes(1, 'little', signed=False)
    for (type, code, value) in events:
        buffer += struct.pack('<HHi', type, code, value)
    return buffer


class controller():
    def __init__(self, addr) -> None:
        self.targetIp = addr.split(":")[0]
        self.targetPort = int(addr.split(":")[1])
        self.udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sendArr = (self.targetIp, self.targetPort)

    def sendBtn(self, code, downUp):
        self.udpSocket.sendto(pack_events(
            [[EV_KEY, code, downUp]]), self.sendArr)

    def sendAbs(self, code, value):
        if value == None:
            return
        if code == ABS_HAT0X or code == ABS_HAT0Y:  # 直接发
            self.udpSocket.sendto(pack_events(
                [[EV_ABS, code, value]]), self.sendArr)
        elif code == ABS_LT or code == ABS_RT:  # 0~1 转换发
            self.udpSocket.sendto(pack_events(
                [[EV_ABS, code, int(value * 1000)]]), self.sendArr)
        else:  # -1~1 转换发
            self.udpSocket.sendto(pack_events(
                [[EV_ABS, code, int(value * 1000)]]), self.sendArr)


class xbox_controller():
    def __init__(self, controller: controller) -> None:
        self.controller = controller

    def pressBTN(self, code):  # 按下
        self.controller.sendBtn(code, DOWN)

    def releaseBTN(self, code):  # 松开
        self.controller.sendBtn(code, UP)

    def clickBTN(self, code, ms=50):
        self.controller.sendBtn(code, DOWN)
        time.sleep(ms/1000)
        self.controller.sendBtn(code, UP)

    def setDpad(self, dpad, value):  # DPAD_X or DPAD_Y  value = -1,0,1 方向键，无法同时按下相反方向
        self.controller.sendAbs(dpad, value)

    def setLT(self, value):  # 0~1 float
        self.controller.sendAbs(ABS_LT, value)

    def setRT(self, value):  # 0~1 float
        self.controller.sendAbs(ABS_RT, value)

    def setLS(self, x=None, y=None):  # -1~1 float None为不修改
        self.controller.sendAbs(ABS_X, x)
        self.controller.sendAbs(ABS_Y, y)

    def setRS(self, x=None, y=None):  # -1~1 float None为不修改
        self.controller.sendAbs(ABS_Z, x)
        self.controller.sendAbs(ABS_RZ, y)


class mouse_keyboard_controller():
    def __init__(self, addr) -> None:
        self.targetIp = addr.split(":")[0]
        self.targetPort = int(addr.split(":")[1])
        self.udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sendArr = (self.targetIp, self.targetPort)

    def pressKey(self,code):
        self.udpSocket.sendto(pack_events(
                [[EV_KEY, code, 1]]), self.sendArr)
    
    def releaseKey(self,code):
        self.udpSocket.sendto(pack_events(
                [[EV_KEY, code, 0]]), self.sendArr)
    
    def clickKey(self,code,ms=50):
        self.pressKey(code)
        time.sleep(ms/1000)
        self.releaseKey(code)

    def move(self,x = None,y = None):   # x正→   y正↓ 
        if x != None:
            self.udpSocket.sendto(pack_events(
                [[EV_REL, REL_X, x]]), self.sendArr)
        if y != None:
            self.udpSocket.sendto(pack_events(
                [[EV_REL, REL_Y, y]]), self.sendArr)
    
    def wheel(self,x=None,y=None): #y=-1下滚 1 上滚
        if x != None:
            self.udpSocket.sendto(pack_events(
                [[EV_REL, REL_HWHEEL, x]]), self.sendArr)
        if y != None:
            self.udpSocket.sendto(pack_events(
                [[EV_REL, REL_WHEEL, y]]), self.sendArr)




if __name__ == "__main__":
    print("test start ")
    ct = controller("192.168.3.43:8889")
    mk = mouse_keyboard_controller("192.168.3.43:8889")

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

    # c = xbox_controller(controller=ct)

    # c.clickBTN(BTN_B, 1)
    # time.sleep(0.1)
    # c.clickBTN(BTN_RS, 0.3)


    # mk.clickKey(KEY_A,ms=1)
    # mk.clickKey(KEY_B,ms=1)
    # mk.clickKey(KEY_C,ms=1)
    # mk.clickKey(KEY_D,ms=1)
    # mk.clickKey(KEY_E,ms=1)
    
    mk.clickKey(MOUSE_BTN_RIGHT)
    
    # for i in range(100):
    #     mk.move(x=-1,y=1)
    #     time.sleep(0.01)
    
    # for i in range(10):
    #     mk.wheel(y=3)
    #     time.sleep(0.1)