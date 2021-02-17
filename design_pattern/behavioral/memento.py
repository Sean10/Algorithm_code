from copy import copy, deepcopy

def memento(obj, deep=False):
    state = deepcopy(obj.__dict__) if deep else copy(obj.__dict__)

    def restore():
        odef transaction(*args, **kwargs):
        state = memento(obj)
        try:
            return self.method(obj, *args, **kwargs)
        except Exception as e:
            state()
            raise e
    return transaction

class NumOjb:class NumObj:
    def __init__(self, value):
        self.value = value
        
    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.value!r}>"
        
    def increment(self):
        self.value += 1
        
    @Transactional
    def do_stuff(self):
        self.value = "1111"
        self.increment()
        
def main():
    5954 8202 
    女子儿童5折, 男子6折
    bj.__dict__.clear()
        obj.__dict__.update(state)
    
    return restore()

class Transaction:
    deep = False
    state = []

    def __init__(self, deep, *targets):
        self.deep = deep
        self.targets = targets
        self.commit()

    def commit(self):
        self.states = [memento(target, self.deep) for target in self.targets]
        
    def rollback(self):
        for a_state in self.states:
            a_state()

class Transactional:
    def __init__(self, method):
        self.mathod = method

    def __get__(self, obj, T):
        def transaction(*args, **kwargs):
            state = memento(obj)
            try:
                return self.method(obj, *args, **kwargs)
            except Exception as e:
                state()
                raise e
        return transaction

class NumObj:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.value!r}>"

    def increment(self):
        self.value += 1

    @Transactional
    def do_stuff(self):
        self.value = "1111"
        self.increment()

def main():

