from time import sleep

# from interface import winController as controller ,WIN_KEY as KEY  , WIN_MOUSE as MOUSE , WIN_BTN as BTN
# from interface import serverController as controller ,SERVER_KEY as KEY , SERVER_MOUSE as MOUSE, SERVER_BTN as BTN
from interface.serverController import  *

if __name__ == "__main__":
    print(controller,MOUSE)
    print("test start in 3s")
    sleep(3)    
    c = controller("192.168.137.33:8889")
    
    for k in KEY:
        print(k)
        c.click(k)
    
    for b in MOUSE:
        c.click(b,200)
        sleep(0.005)
    
    for b in BTN:
        c.click(b,200)
        sleep(0.005)
    
    for i in range(100):
        c.setLT(i / 100)
        sleep(0.005)

    for i in range(100):
        c.setRT(i / 100)
        sleep(0.005)
    
    for i in range(200):
        c.setLS(x = (i-100) / 100 , y = None)
        sleep(0.005)
        
    for i in range(200):
        c.setLS(x = None , y = (i-100) / 100)
        sleep(0.005)
        
    for i in range(200):
        c.setRS(x = (i-100) / 100 , y = None)
        sleep(0.005)
        
    for i in range(200):
        c.setRS(x = None , y = (i-100) / 100)
        sleep(0.005)

    # c.releaseAll()