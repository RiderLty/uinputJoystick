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
        threading.Thread(target=self.runner).start()
        self.taskRunning = threading.Lock()
        self.interruptFlag = False

        self.sleepBreakSignal = threading.Event()

    def runner(self) -> None:
        while True:
            (func, args, kwargs) = self.taskQueue.get()
            with self.taskRunning:
                if not self.interruptFlag:
                    try:
                        func(*args, **kwargs)
                    except Exception as e:
                        pass

    def __del__(self) -> None:
        pass

    def sleep(self, ms=0) -> None:
        def interruptableSleep(ms=0):
            self.sleepBreakSignal.clear()
            self.sleepBreakSignal.wait(timeout=ms / 1000)
        self.taskQueue.put((interruptableSleep, (ms,), None))

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
