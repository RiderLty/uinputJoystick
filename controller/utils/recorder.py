
import queue
import threading

from screenCap import screenCap
import time

class recorder():
    def __init__(self,interval = 1000 , length = 60 * 5) -> None:
        self.scs = queue.Queue()
        self.flag = False
        self.condition = threading.Condition()
        def recThread():
            while True:

                while self.flag == False:
                    self.scs =queue.Queue()
                    with self.condition:
                        self.condition.wait()
                
                img = screenCap( resize= (1280,720))
                if self.scs.qsize() > length:
                    self.scs.get()
                self.scs.put(img)
                
                time.sleep( interval / 1000)
                #  REC
                
        threading.Thread(target=recThread).start()
    
    def start(self,):
        self.scs = queue.Queue()
        self.flag = True
        with self.condition:
            self.condition.notify_all()
    
    
    def stop(self,):
        self.flag = False
    
    
    def save(self,output_path = None):
        # 保存为WebP动态图并指定质量
        print(f"保存中，总长度{self.scs.qsize()}")
        img = []
        while not self.scs.empty():
            img.append(self.scs.get())
        img[0].save(output_path, format='WebP', save_all=True, append_images=img[1:], duration=200, loop=0, quality=90)
        print(f"已保存到{output_path}")
        self.stop()
        
if __name__ == "__main__":
    print("test start")
    rec = recorder()
    rec.start()
    time.sleep(60 * 10 )
    rec.save("save.webp")