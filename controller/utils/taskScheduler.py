from queue import Queue
import threading

from .interface._controller import _controller


# task 作为warper使用 将函数变为task类型
# task类型函数，执行提交任务到队列中，按序执行，立即返回
# wait 等待队列空且所有任务执行完毕
# interrupt 中断当前任务队列 阻塞直到所有无任务运行且队列为空返回


class taskScheduler ():
    def __init__(self, DEBUG=False) -> None:
        self.DEBUG = DEBUG
        self.taskQueue = Queue(-1)
        self.taskRunning = threading.Lock()
        self.interruptFlag = False
        self.sleepBreakSignal = threading.Event()
        threading.Thread(target=self.runner).start()

    def __call__(self, func):  # 任务提交，并立即返回，按序执行 可以取消
        def newFunc(*args, **kwargs):
            self.taskQueue.put((func, args, kwargs))
        return newFunc

    def runner(self) -> None:
        while True:
            (func, args, kwargs) = self.taskQueue.get()
            if func == None and args == None and kwargs == None:
                self.taskQueue.task_done()
                return
            with self.taskRunning:
                if not self.interruptFlag:
                    try:
                        func(*args, **kwargs)
                    except Exception as e:
                        self.DEBUG and print(
                            "Exception when running task ", func, args, kwargs, ":", e)
                else:
                    self.DEBUG and print("canceled task ", func, args, kwargs)
                self.taskQueue.task_done()

    def stop(self) -> None:
        self.interrupt()
        self.taskQueue.put((None, None, None))

    def interruptableSleep(self, ms):
        self.sleepBreakSignal.clear()
        if self.sleepBreakSignal.wait(timeout=ms / 1000):
            self.DEBUG and print(f"interrupted sleep {ms}ms")

    def sleep(self, ms) -> None:
        self.taskQueue.put((self.interruptableSleep, (ms,), {}))

    def interrupt(self) -> None:
        self.sleepBreakSignal.set()
        with self.taskRunning:
            self.interruptFlag = True
        self.taskQueue.join()
        self.interruptFlag = False

    def wait(self):
        if not self.taskQueue.empty():
            self.taskQueue.join()


class scheduled():
    def __init__(self, controller: _controller , DEBUG = False) -> None:
        '''创建一个scheduled的controller
        
        使其具有可以随时中断并取消后续动作的特性
        
        但是只能单线程运行
        
        scheduled的controller执行指令后会立即返回，需要使用wait方法等待指令执行完毕
    '''
        self.controller = controller
        self.scheduler = taskScheduler()
        self.DEBUG = DEBUG

    def interrupt(self,):
        '''中断当前指令序列
        
        释放全部按键 摇杆恢复初始状态'''
        self.DEBUG and print("[DEBUG]:正在中断当前序列")
        self.scheduler.interrupt()
        self.controller.releaseAll()
        self.DEBUG and print("[DEBUG]:当前序列已中断")
        
    
    def wait(self,):
        '''等待当前提交的指令执行完毕'''
        self.DEBUG and print("[DEBUG]:等待当前队列指令执行中")
        self.scheduler.wait()
        self.DEBUG and print("[DEBUG]:队列指令执行完毕")
        
    
    def stop(self,):
        '''结束运行
        应当仅在程序结束运行时调用'''
        self.DEBUG and print("[DEBUG]:正在停止")
        self.scheduler.stop()
        self.DEBUG and print("[DEBUG]:程序已停止")
    
    
    def sleep(self,ms):
        '''等待 (ms)'''
        self.DEBUG and print(f"[DEBUG]:等待{ms}ms")
        return self.scheduler.sleep(ms=ms)

    def press(self, code) -> None:
        '''按下按键'''
        self.DEBUG and print(f"[DEBUG]:按下{code.name}")
        return self.scheduler(self.controller.press)(code)

    def release(self, code) -> None:
        '''释放按键'''
        self.DEBUG and print(f"[DEBUG]:释放{code.name}")
        return self.scheduler(self.controller.release)(code)

    def click(self, code, ms=50) -> None:
        '''点击一次按键 默认50ms'''
        self.press(code=code)
        self.sleep(ms=ms)
        self.release(code=code)

    def mouseMove(self, x, y) -> None:
        '''鼠标移动 相对量'''
        self.DEBUG and print(f"[DEBUG]:鼠标移动({x},{y})")
        return self.scheduler(self.controller.mouseMove)(x, y)

    def mouseWheel(self, value) -> None:
        '''鼠标滚轮'''
        self.DEBUG and print(f"[DEBUG]:鼠标滚轮({value})")
        return self.scheduler(self.controller.mouseWheel)(value)

    def setLS(self, x=None, y=None) -> None:  # 浮点类型
        '''左摇杆xy (-1 ~ 1)'''
        self.DEBUG and print(f"[DEBUG]:手柄左摇杆({x},{y})")
        return self.scheduler(self.controller.setLS)(x,y)

    def setRS(self, x, y) -> None:
        '''右摇杆xy (-1 ~ 1)'''
        self.DEBUG and print(f"[DEBUG]:手柄右摇杆({x},{y})")
        return self.scheduler(self.controller.setRS)(x,y)

    def setLT(self, value) -> None:
        '''左扳机 (0 ~ 1)'''
        self.DEBUG and print(f"[DEBUG]:手柄左扳机({value})")
        return self.scheduler(self.controller.setLT)(value)

    def setRT(self, value) -> None:
        '''右扳机 (0 ~ 1)'''
        self.DEBUG and print(f"[DEBUG]:手柄右扳机({value})")
        return self.scheduler(self.controller.setRT)(value)
