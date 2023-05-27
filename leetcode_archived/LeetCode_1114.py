import threading

class Foo:
    def __init__(self):
        self._value_lock1 = threading.Lock()
        self._value_lock2 = threading.Lock()
        self._value_lock3 = threading.Lock()
        self._value_lock2.acquire()
        self._value_lock3.acquire()



    def first(self, printFirst: 'Callable[[], None]') -> None:
        self._value_lock1.acquire()
        # printFirst() outputs "first". Do not change or remove this line.
        printFirst()
        self._value_lock2.release()


    def second(self, printSecond: 'Callable[[], None]') -> None:
        self._value_lock2.acquire()
        # printSecond() outputs "second". Do not change or remove this line.
        printSecond()
        self._value_lock3.release()



    def third(self, printThird: 'Callable[[], None]') -> None:
        self._value_lock3.acquire()
        # printThird() outputs "third". Do not change or remove this line.
        printThird()
        self._value_lock1.release()

