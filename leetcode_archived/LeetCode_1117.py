import threading
from enum import Enum

class State(Enum):
    INIT = 0
    H = 1
    O = 2
    HO = 3
    HH = 4


class H2O:
    def __init__(self):
        self.semaphore_hydrogen = threading.Semaphore(2)
        self.semaphore_oxygen = threading.Semaphore(1)
        self.state = State.INIT
        self.state_lock = threading.Lock()
        


    def hydrogen(self, releaseHydrogen: 'Callable[[], None]') -> None:
        self.semaphore_hydrogen.acquire()
        # releaseHydrogen() outputs "H". Do not change or remove this line.
        releaseHydrogen()
        with self.state_lock:
            if State.INIT == self.state:
                self.state = State.H
            elif State.H == self.state:
                self.state = State.HH
            elif State.O == self.state:
                self.state = State.HO
            elif State.HO == self.state:
                self.state = State.INIT
            else:
                print(f'error: current_state:{self.state}')
            if State.INIT == self.state:
                self.semaphore_hydrogen.release()
                self.semaphore_hydrogen.release()
                self.semaphore_oxygen.release()


    def oxygen(self, releaseOxygen: 'Callable[[], None]') -> None:
        self.semaphore_oxygen.acquire()
        # releaseOxygen() outputs "O". Do not change or remove this line.
        releaseOxygen()
        with self.state_lock:
            if State.INIT == self.state:
                self.state = State.O
            elif State.H == self.state:
                self.state = State.HO
            elif State.HH == self.state:
                self.state = State.INIT
            else:
                print(f'error: current_state:{self.state}')
            if State.INIT == self.state:
                self.semaphore_hydrogen.release()
                self.semaphore_hydrogen.release()
                self.semaphore_oxygen.release()

