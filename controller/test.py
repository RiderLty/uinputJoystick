import threading
import time


class ThreadSafeValue:
    def __init__(self, value):
        self._value = value
        self._lock = threading.Lock()
        self._condition = threading.Condition()

    def set_value(self, new_value):
        with self._lock:
            self._value = new_value
            with self._condition:
                self._condition.notify_all()

    def get_value(self):
        with self._lock:
            return self._value

    def waitFor(self, value):
        # 等待self._value变为value 再返回
        while self._value != value:
            with self._condition:
                self._condition.wait()
        return self._value

def test_thread(thread_safe_value, value):
    print(f"Thread {threading.current_thread().name} started")
    thread_safe_value.waitFor(value)
    print(f"Thread {threading.current_thread().name} received value: {thread_safe_value.get_value()}")

value = 0
thread_safe_value = ThreadSafeValue(value)

# 创建两个线程，分别等待不同的值
thread1 = threading.Thread(target=test_thread, args=(thread_safe_value, 10), name="Thread1")
thread2 = threading.Thread(target=test_thread, args=(thread_safe_value, 20), name="Thread2")

# 启动线程
thread1.start()
thread2.start()

# 模拟延迟，确保线程1先启动
time.sleep(1)

# 更新值并通知等待线程
thread_safe_value.set_value(10)
# time.sleep(1)

thread_safe_value.set_value(20)

# 等待线程结束
thread1.join()
thread2.join()