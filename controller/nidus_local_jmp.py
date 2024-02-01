import ctypes
import os
from time import sleep as s_sleep
from cnocr import CnOcr
from cnocr.utils import draw_ocr_results
from time import sleep
import mss
import threading
import requests
import win32api
import win32con
import vgamepad as vg
from vgamepad import XUSB_BUTTON



# README !
# 电脑分辨率 1920*1080 缩放100%
# 游戏内 UI 200% 
# 改键

# 跳跃N
# 开火滚轮下
# 次要滚轮上
# 近战U
# 表情1 b




def sleep(ms):
    s_sleep(ms/1000)


_MapVirtualKey = ctypes.windll.user32.MapVirtualKeyA


MOUSE_BTN_LEFT = 1
MOUSE_BTN_RIGHT = 2
MOUSE_BTN_MIDDLE = 3
KEY_E = 69
KEY_U = 85
KEY_S = 83
KEY_A = 65
KEY_3 = 51
KEY_4 = 52
KEY_W = 87
KEY_LEFT_SHIFT = 0x10
KEY_D = 68
KEY_N = 78
KEY_J = 74
KEY_ESC = 0x1b
KEY_2 = 50
KEY_L = 76

def pressKey(num):
    win32api.keybd_event(num, _MapVirtualKey(num, 0), 0, 0)


def releaseKey(num):
    win32api.keybd_event(num, _MapVirtualKey(
        num, 0), win32con.KEYEVENTF_KEYUP, 0)


def clickKey(num, ms=50):
    pressKey(num=num)
    sleep(ms)
    releaseKey(num=num)

def jmp():
    pressKey(KEY_W)
    sleep(10)
    clickKey(KEY_N,10)
    sleep(10)
    clickKey(KEY_LEFT_SHIFT,5)
    sleep(5)
    clickKey(KEY_N,30)
    sleep(500)
    releaseKey(KEY_W)
    

if __name__ == "__main__":
    sleep(1000)
    clickKey(KEY_ESC,50)
    sleep(1500)
    jmp()