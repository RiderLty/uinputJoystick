import cv2
from utils.imgTools import url2ImgNp
import time

while True:
    img = url2ImgNp("http://192.168.3.155:4443/screen/mask")
    cv2.imshow("img",img)
    cv2.imwrite(rf"controller/assets/saveTmp/{time.time()}.png" , img)
    if cv2.waitKey(1) == 27:
        break


# from utils.imgTools import handelScreen
# import cv2


# cv2.imshow("p", handelScreen(cv2.imread(r"C:\Users\lty65\projects\uinputJoystick\controller\assets\saveTmp\1710860279.1734593.png")))
# cv2.waitKey(-1)