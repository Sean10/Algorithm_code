import threading
class ZeroEvenOdd:
    def __init__(self, n):
        self.n = n
        self.semaphore_zero = threading.Semaphore(0)
        self.semaphore_even = threading.Semaphore(0)
        self.semaphore_odd = threading.Semaphore(0)
        self.semaphore_zero.release()
        
        
	# printNumber(x) outputs "x", where x is an integer.
    def zero(self, printNumber: 'Callable[[int], None]') -> None:
        for i in range(self.n):
            self.semaphore_zero.acquire()
            printNumber(0)
            # start from 1
            if (i+1) % 2 == 0:
                self.semaphore_even.release()
            else:
                self.semaphore_odd.release()
        
        
    def even(self, printNumber: 'Callable[[int], None]') -> None:
        for i in range(self.n):
            if (i+1) % 2 != 0:
                continue
            self.semaphore_even.acquire()
            printNumber(i+1)
            if i + 1 < self.n:
                self.semaphore_zero.release()
        
        
    def odd(self, printNumber: 'Callable[[int], None]') -> None:
        for i in range(self.n):
            if (i+1) % 2 == 0:
                continue
            self.semaphore_odd.acquire()
            printNumber(i+1)
            if i + 1 < self.n:
                self.semaphore_zero.release()
