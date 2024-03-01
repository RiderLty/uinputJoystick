
import mss
from PIL import Image


def screenCap():
    with mss.mss() as m:
        rect = (0, 0, 1920, 1080)
        sc_img = m.grab(rect)
        return Image.frombytes("RGB", sc_img.size, sc_img.bgra, "raw", "BGRX")