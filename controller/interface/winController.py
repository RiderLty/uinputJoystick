import ctypes
from ._controller import _controller
import vgamepad
from .winDefines import KEY, MOUSE, BTN
import win32api
import win32con
from time import sleep



_MapVirtualKey = ctypes.windll.user32.MapVirtualKeyA


class controller(_controller):

    def __init__(self) -> None:
        super().__init__()
        self.v360 = vgamepad.VX360Gamepad()
        self.downingKeys = set()
        self.LS_X = 0
        self.LS_Y = 0
        self.RS_X = 0
        self.RS_Y = 0

    def __del__(self) -> None:
        self.releaseAll()
    
    def releaseAll(self,) -> None:
        self.v360.reset()
        self.LS_X = 0
        self.LS_Y = 0
        self.RS_X = 0
        self.RS_Y = 0
        for k in self.downingKeys:
            self.release(k)

    def press(self, code) -> None:
        self.downingKeys.add(code)
        if isinstance(code, KEY):
            win32api.keybd_event(code.value, _MapVirtualKey(code.value, 0), 0, 0)
        elif isinstance(code, MOUSE):
            if code == MOUSE.MOUSE_BTN_LEFT:
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            elif code == MOUSE.MOUSE_BTN_RIGHT:
                win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
            elif code == MOUSE.MOUSE_BTN_MIDDLE:
                win32api.mouse_event(win32con.MOUSEEVENTF_MIDDLEDOWN, 0, 0, 0, 0)
        elif isinstance(code, BTN):
            self.v360.press_button(code.value)
            self.v360.update()
        else:
            raise TypeError(type(code))

    def release(self, code) -> None:
        if code in self.downingKeys:
            self.downingKeys.remove(code) 
        if isinstance(code, KEY):
            win32api.keybd_event(code.value, _MapVirtualKey(
                code.value, 0), win32con.KEYEVENTF_KEYUP, 0)
        elif isinstance(code, MOUSE):
            if code == MOUSE.MOUSE_BTN_LEFT:
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
            elif code == MOUSE.MOUSE_BTN_RIGHT:
                win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
            elif code == MOUSE.MOUSE_BTN_MIDDLE:
                win32api.mouse_event(win32con.MOUSEEVENTF_MIDDLEUP, 0, 0, 0, 0)
        elif isinstance(code, BTN):
            self.v360.release_button(code.value)
            self.v360.update()
        else:
            raise TypeError(type(code))

    def click(self,code,ms=50) -> None:
        self.press(code=code)
        sleep(ms/1000)
        self.release(code=code)

    def mouseMove(self,x,y) -> None:
        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE,x, y, 0, 0)

    def mouseWheel(self,value) -> None:
        for _ in range(abs(value)):
            if value > 0 :
                win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, 1, 0)
            else:
                win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, -1, 0)
                
    def setLS(self,x = None,y = None) -> None:# 浮点类型
        if x != None:
            self.LS_X = x
        if y != None:
            self.LS_Y = y
        self.v360.left_joystick_float(x_value_float=self.LS_X , y_value_float= self.LS_Y)
        self.v360.update()
        
    def setRS(self,x,y) -> None:
        if x != None:
            self.RS_X = x
        if y != None:
            self.RS_Y = y
        self.v360.right_joystick_float(x_value_float=self.RS_X , y_value_float= self.RS_Y)
        self.v360.update()

    def setLT(self,value) -> None:
        self.v360.left_trigger_float(value_float=value)
        self.v360.update()

    def setRT(self,value) -> None:
        self.v360.right_trigger_float(value_float=value)
        self.v360.update()


