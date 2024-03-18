import cv2
from utils.imgTools import url2ImgNp
import time

while True:
    img = url2ImgNp("http://192.168.3.43:8888/screen.png")
    cv2.imshow("img",img)
    cv2.imwrite(rf"controller/assets/saveTmp/{time.time()}.png" , img)
    if cv2.waitKey(1) == 27:
        break