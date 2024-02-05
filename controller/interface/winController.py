import ctypes
from .controller import controller
import vgamepad
from .winDefines import KEY, MOUSE, BTN
import win32api
import win32con
from time import sleep



_MapVirtualKey = ctypes.windll.user32.MapVirtualKeyA


class winController(controller):

    def __init__(self) -> None:
        super().__init__()
        self.v360 = vgamepad.VX360Gamepad()

    def releaseAll(self,) -> None:
        self.v360.reset()
        for k in KEY:
            self.release(k)
        for k in MOUSE:
            self.release(k)

    def press(self, code) -> None:
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

    def mouseMove(self,x=0,y=0) -> None:
        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE,x, y, 0, 0)

    def mouseWheel(self,value=0) -> None:#win api 只有方向
        win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, value, 0)

    def setLS(self,x,y) -> None:# 浮点类型
        self.v360.left_joystick_float(x_value_float=x,y_value_float=y)
        self.v360.update()
        
    def setRS(self,x,y) -> None:
        self.v360.right_joystick_float(x_value_float=x,y_value_float=y)
        self.v360.update()

    def setLT(self,value) -> None:
        self.v360.left_trigger_float(value_float=value)
        self.v360.update()

    def setRT(self,value) -> None:
        self.v360.right_trigger_float(value_float=value)
        self.v360.update()


