import ctypes
import struct
from time import sleep, time, time_ns
from defines import *
import win32api
import win32con
import socket

_MapVirtualKey = ctypes.windll.user32.MapVirtualKeyA

MOUSE_BTN_LEFT = 1
MOUSE_BTN_RIGHT = 2
MOUSE_BTN_MIDDLE = 3

DOWN = 1
UP = 0


def key_press(num):
    win32api.keybd_event(num, _MapVirtualKey(num, 0), 0, 0)


def key_release(num):
    win32api.keybd_event(num, _MapVirtualKey(
        num, 0), win32con.KEYEVENTF_KEYUP, 0)


def key_event(num, down):
    if down:
        key_press(num)
    else:
        key_release(num)


def mouse_press(btn):
    if btn == MOUSE_BTN_LEFT:
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    elif btn == MOUSE_BTN_RIGHT:
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
    elif btn == MOUSE_BTN_MIDDLE:
        win32api.mouse_event(win32con.MOUSEEVENTF_MIDDLEDOWN, 0, 0, 0, 0)


def mouse_release(btn):
    if btn == MOUSE_BTN_LEFT:
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    elif btn == MOUSE_BTN_RIGHT:
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
    elif btn == MOUSE_BTN_MIDDLE:
        win32api.mouse_event(win32con.MOUSEEVENTF_MIDDLEUP, 0, 0, 0, 0)


def mouse_wheel(delta):
    win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, delta, 0)


def mouse_move(offset_x, offset_y):
    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, offset_x, offset_y, 0, 0)


if __name__ == "__main__":
    print("start server")
    
    UDP_IP = "0.0.0.0"  # 监听所有可用的网络接口
    UDP_PORT = 8889     # 接收数据的端口号
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    while True:
        pack, addr = sock.recvfrom(1024)  # 1024表示一次最多接收的字节数
        for i in range(pack[0]):
            type = struct.unpack('<H', pack[8*i+1: 8*i+3])[0]
            code = struct.unpack('<H', pack[8*i+3: 8*i+5])[0]
            value = struct.unpack('<i', pack[8*i+5: 8*i+9])[0]
            if type == 1:#keyEvent
                print(type, linuxCode_scanCode[code], value)
                
                code = linuxCode_scanCode[code]
                if value == DOWN:
                    key_press(code)
                elif value == UP:
                    key_release(code)
            elif type == 2:#rel_event   
                pass