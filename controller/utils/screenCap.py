
import mss
from PIL import Image


def screenCap():
    m = mss.mss()
    rect = (0, 0, 1920, 1080)
    def inner():
        sc_img = m.grab(rect)
        return Image.frombytes("RGB", sc_img.size, sc_img.bgra, "raw", "BGRX")
    return inner
    