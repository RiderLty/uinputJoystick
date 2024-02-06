from queue import Queue
from time import sleep as s_sleep


class framework():
    def __init__(self) -> None:
        self.taskQueue = Queue(-1)
    
    def __del__(self) -> None:
        pass
    
    def sleep(self,ms = 0) -> None:
        pass
    
    def wait() -> None:
        #wait until task queue is empty
        pass
    
    def task(func):# 任务提交，并立即返回，按序执行 可以取消
        def newFunc(*args, **kwargs):
            return func(*args, **kwargs)
        return newFunc