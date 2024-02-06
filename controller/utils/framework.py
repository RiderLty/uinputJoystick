from queue import Queue
import threading
from time import sleep as s_sleep


# task 作为warper使用 将函数变为task类型
# task类型函数，执行提交任务到队列中，按序执行，立即返回
# wait 等待队列空且所有任务执行完毕
# interrupt 中断当前任务队列 阻塞直到所有无任务运行且队列为空返回



class framework():
    
    def __init__(self) -> None:
        self.taskQueue = Queue(-1)
        self.taskRunning = threading.Lock()
        self.interruptFlag = False
        self.sleepBreakSignal = threading.Event()
        threading.Thread(target=self.runner).start()
    
    
    def runner(self) -> None:
        while True:
            # print(self.interruptFlag , self.taskQueue.qsize())
            (func, args, kwargs) = self.taskQueue.get()
            if func == None and args == None and kwargs == None:
                self.taskQueue.task_done()
                return
            with self.taskRunning:
                
                if not self.interruptFlag:
                    try:
                        func(*args, **kwargs)
                    except Exception as e:
                        print("Exception when running task ",func, args, kwargs,":",e)
                else:
                    print("canceled task ",func, args, kwargs)
                self.taskQueue.task_done()
            # print(self.interruptFlag , self.taskQueue.qsize())



    
    def stop(self) -> None:
        self.interrupt()
        self.taskQueue.put((None,None,None))
    
    def interruptableSleep(self,ms):
        self.sleepBreakSignal.clear()
        if self.sleepBreakSignal.wait(timeout = ms / 1000):
            print(f"interrupted sleep {ms}ms")   
        

    def sleep(self, ms) -> None:
        self.taskQueue.put((self.interruptableSleep,(ms,), {}))
    
    def interrupt(self) -> None:
        self.sleepBreakSignal.set()
        with self.taskRunning:
            self.interruptFlag = True
        self.taskQueue.join()
        self.interruptFlag = False

    def task(self, func):  # 任务提交，并立即返回，按序执行 可以取消
        def newFunc(*args, **kwargs):
            self.taskQueue.put((func, args, kwargs))
        return newFunc
    
    def wait(self):
        self.taskQueue.join()

f = framework()


@f.task
def task_eg(name,st):
    print("task:",name)
    s_sleep(st/1000)
    print("over:",name)

    
    
if __name__ == "__main__":
    print("test start")
    def stop(ms):
        s_sleep(ms /1000)
        f.interrupt()
    threading.Thread(target=stop , args=(3000,)).start()
    task_eg("1",2000)
    f.sleep(2000)
    task_eg("5",20)
    f.wait()
    print("test over")
    f.stop()