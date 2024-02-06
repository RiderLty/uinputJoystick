import ctypes
import socket
import struct
from ._controller import _controller
from .serverDefines import KEY,MOUSE,BTN
from time import sleep

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

ABS_X = 0x00
ABS_Y = 0x01
ABS_Z = 0x02
ABS_RZ = 0x05
ABS_LT = 0x0a
ABS_RT = 0x09
ABS_HAT0X = 0x10
ABS_HAT0Y = 0x11

def pack_events(events):
    buffer = (len(events)).to_bytes(1, 'little', signed=False)
    for (type, code, value) in events:
        buffer += struct.pack('<HHi', type, code, value)
    return buffer

class controller(_controller):
    def __init__(self,addr) -> None:
        super().__init__()
        self.targetIp = addr.split(":")[0]
        self.targetPort = int(addr.split(":")[1])
        self.udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sendArr = (self.targetIp, self.targetPort)
        self.downingKeys = set()

    def __del__(self) -> None:
        self.releaseAll()
        
    def releaseAll(self,) -> None:
        for k in [x for x in self.downingKeys]:
            self.release(k)
        self.setLS(0,0)
        self.setRS(0,0)
        self.setLT(0)
        self.setRT(0)


    def press(self, code) -> None:
        self.downingKeys.add(code)
        if code in [BTN.BTN_DPAD_DOWN,BTN.BTN_DPAD_UP]:
            self.udpSocket.sendto(pack_events( [[EV_ABS, ABS_HAT0Y, code.value]]), self.sendArr)
        elif code in [BTN.BTN_DPAD_LEFT,BTN.BTN_DPAD_RIGHT]:
            self.udpSocket.sendto(pack_events( [[EV_ABS, ABS_HAT0X, code.value]]), self.sendArr)
        else:
            if isinstance(code, KEY) or isinstance(code, MOUSE) or isinstance(code, BTN):
                self.udpSocket.sendto(pack_events([[EV_KEY, code.value, DOWN]]), self.sendArr)
            else:
                raise TypeError(type(code))

    def release(self, code) -> None:
        if code in self.downingKeys:
            self.downingKeys.remove(code) 
        if code in [BTN.BTN_DPAD_DOWN,BTN.BTN_DPAD_UP]:
            self.udpSocket.sendto(pack_events( [[EV_ABS, ABS_HAT0Y, 0]]), self.sendArr)
        elif code in [BTN.BTN_DPAD_LEFT,BTN.BTN_DPAD_RIGHT]:
            self.udpSocket.sendto(pack_events( [[EV_ABS, ABS_HAT0X, 0]]), self.sendArr)
        else:
            if isinstance(code, KEY) or isinstance(code, MOUSE) or isinstance(code, BTN):
                self.udpSocket.sendto(pack_events([[EV_KEY, code.value, UP]]), self.sendArr)
            else:
                raise TypeError(type(code))

    def click(self,code,ms=50) -> None:
        self.press(code=code)
        sleep(ms/1000)
        self.release(code=code)

    def mouseMove(self,x,y) -> None:
        if x != 0:
            self.udpSocket.sendto(pack_events([[EV_REL, REL_X, x]]), self.sendArr)
        if y != 0:
            self.udpSocket.sendto(pack_events([[EV_REL, REL_Y, y]]), self.sendArr)
            
    def mouseWheel(self,value) -> None:
        self.udpSocket.sendto(pack_events([[EV_REL, REL_HWHEEL, value]]), self.sendArr)
                
    def setLS(self,x = None,y = None) -> None:# 浮点类型
        if x != None:
            self.udpSocket.sendto(pack_events([[EV_ABS, ABS_X, int(x * 1000)]]), self.sendArr)
        if y != None:
            self.udpSocket.sendto(pack_events([[EV_ABS, ABS_Y, int(y * -1000)]]), self.sendArr)
        
    def setRS(self,x = None,y = None) -> None:
        if x != None:
            self.udpSocket.sendto(pack_events([[EV_ABS, ABS_Z, int(x * 1000)]]), self.sendArr)
        if y != None:
            self.udpSocket.sendto(pack_events([[EV_ABS, ABS_RZ, int(y * -1000)]]), self.sendArr)

    def setLT(self,value) -> None:
        self.udpSocket.sendto(pack_events([[EV_ABS, ABS_LT, int(value * 1000)]]), self.sendArr)

    def setRT(self,value) -> None:
        self.udpSocket.sendto(pack_events([[EV_ABS, ABS_RT, int(value * 1000)]]), self.sendArr)



