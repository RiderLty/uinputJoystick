from enum import Enum
import logging
import threading
from time import sleep as s_sleep


def sleep(ms):
    s_sleep(ms/1000)


def remove_non_digits(text):
    return ''.join([char for char in text if char.isdigit()])


def checkText(template, targets):
    for target in targets:
        if target in template:
            return True
    return False


class CallbackHandler(logging.Handler):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    def emit(self, record):
        msg = self.format(record)
        self.callback(msg)


class scriptType(Enum):
    nidus_single = 0
    fire_multi = 1


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
        # while self.get_value() != value:
        #     with self._condition:
        #         self._condition.wait()
        # return self._value
        self.waitForCondition(lambda x: x == value)

    def waitForCondition(self, cond):
        while not cond(self.get_value()):
            with self._condition:
                self._condition.wait()
        return self._value
