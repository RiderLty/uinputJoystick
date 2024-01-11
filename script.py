from controller import *
from time import sleep as s_sleep


def sleep(ms):
    s_sleep(ms/1000)


x = xbox_controller(controller=controller("192.168.3.43:8889"))

# x.clickBTN(BTN_A)

# x.setRS(x=0 ,y=0)

# x.setRS(x=-0.01 ,y=0)

x.setLS(x=0, y=-1)
sleep(10)
x.clickBTN(BTN_A, 10)
sleep(10)
x.clickBTN(BTN_LB, 5)
sleep(5)
x.clickBTN(BTN_A, 30)
sleep(500)
x.setLS(x=0, y=0)
