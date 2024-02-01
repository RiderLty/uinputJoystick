import cv2
import numpy as np

red1=np.array([0,0,0])
red2=np.array([128,128,128])

image = cv2.imread(r"P:\screen.png")
cv2.imshow("input", image)
hsv=cv2.cvtColor(image,cv2.COLOR_BGR2HSV)
mask=cv2.inRange(hsv,red1,red2)
cv2.imshow("output", mask)
cv2.waitKey(0)