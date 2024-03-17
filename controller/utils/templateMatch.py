import datetime
import time
import cv2
import numpy as np
from imgTools import url2ImgNp , handelScreen




def templateMatch(img, target , threshold = 0.8):
    w, h = target.shape[1], target.shape[0]
    res = cv2.matchTemplate(img, target, cv2.TM_CCOEFF_NORMED )
    _, max_val, _, max_loc = cv2.minMaxLoc(res)
    if max_val > 1 or max_val < threshold:
        return None
    else:
        rectangle = [(max_loc[0], max_loc[1]), (max_loc[0]+w, max_loc[1] + h)]
        return [max_val ,rectangle ]

if __name__ == "__main__":
    # while True:
    #     img = handelScreen(url2ImgNp(r"http://192.168.3.155:4443/screenraw"))
    #     img = handelScreen(cv2.imread(r"E:\WRREC\20240315230635.png"))
    #     cv2.imwrite(r"P:\out.png" , img)
        
    #     list = [r"P:\target.png",r"P:\bc.png",r"P:\xzyw.png" , r"P:\lfh.png" , r"P:\cld.png"  ,  r"P:\25.png" , r"P:\100.png" , r"P:\0.png" ,r"P:\45.png"]  #65
    #     result = []
    #     for file in list:
    #         target = cv2.imread(file)
    #         res = templateMatch(img , target , 0.8)
    #         result.append(res)
        
    #     flag = False
    #     for res in result:
    #         if res:
    #             flag = True
    #             img = cv2.rectangle(img, res[1][0], res[1][1], [0, 255, 0], 1)
    #             cv2.imshow("img",img )
    #             if cv2.waitKey(1) == 27:
    #                 exit()
    #     if flag == False:
    #         print("no result matched")
    #         cv2.imshow("img",img )
    #         if cv2.waitKey(1) == 27:
    #             exit()
    
    img = handelScreen(url2ImgNp(r"http://192.168.3.155:4443/screenraw"))
    cv2.imwrite(r"P:\out.png" , img)
        
    
    
    while True:
        img = handelScreen(url2ImgNp(r"http://192.168.3.155:4443/screenraw"))
        target = cv2.imread(r"P:\bc.png")
        res = templateMatch(img , target , 0.8)
        if res != None:
            time.sleep(1)
            cv2.imwrite(rf'E:\WRREC\{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}.png' , url2ImgNp(r"http://192.168.3.155:4443/screenraw"))
            print("sleep 5 min ",datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            time.sleep(60 * 5)
        time.sleep(2)
        print("scanning ",datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))