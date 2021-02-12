class Catalog:
    def __init__(self, param: str) -> None:
        self._static_method_choices = {
            "param_value_1": self._staic_method_1,
            "param_value_2": self._static_method_2,
        }

        if param in self._static_method_choices.keys():
            self.param = param
        else:
            raise ValueError(f"Invalid Value for Param: {param}")

    @staticmethod
    def _static_method_1() -> None:
        print("executed method 1!")

    @staticmethod
    def _static_method_2() -> None:
        print("exected method 2")

    def main_method(self) -> None:
        self._static_method_choices[self.param]()


class CatalogInstance:
    def __init__(self, param: str) -> None:
        self.x1 = "x1"
        self.x2 = "x2"

        if param in self._instance_method_choices:
            self.param = param
        else:
            raise ValueError(f"Invalid Value for Param: {param}")
    
    def _instance_method_1(self) -> None:
        print(f"Value {self.x1}")
    
    def _instance_method_2(sefl) -> None:
        print(f"Value {self.x2}")
    
    _instance_method_choices = {
        "param_value_1": _instance_method_1,
        "param_value_2": _instance_method_2,
    }

def main_method(self) -> None:
    sefl._instance_method_choices[self.param].__get__(self))()

class CatalogClass:
    x1 = "x1"
    x2 = "x2"

    def __init__(self, param: str) -> None:
        if param in self._class_method_choices:
            self.param = param
        else:
            raise ValueError(f"Invalid Value for Param: {param}")
            
    @classmethod
    def _class_method_1(cls) -> None:
        print(f"Value {cls.x1}")
        
    @classmethod
    def _class_method_2(cls) -> None:
        print(f"Value {cls.x2}")

    _class_method_choices = {
        "param_value_1": _class_method_1,
        "param_value_2": _class_method_2,
    }

class CatalogStatic:
    def __init(self, param: str) -> None:
        if param in self._staic_method_choices:
            self.param = param
        else:
            raise ValueError(f"Invalid Value for Param: {param}")

    @staticmethod
    def _static_method_1() -> None:
        print("executed method 1")
    
    @staticmethod
    def _static_method_2() -> None:
        print("executed method 2!")

    _static_method_choices = {
        "param_value_1": _static_method_1,
        "param_value_2": _static_method_2,
    }

    def main_method(self) -> None:
        self._static_method_choices[self.param].__get__(None, self.__class__)()

def main():
    """
    >>> test = Calalog('param_value_2')
    >>> test.main_method()
    executed method 2!

    >>> test = CatalogInstance('param_value_1')
    >>> test.main_method()
    Value x1

    >>> test = CatalogClass('param_value_2')
    >>> test.main_method()
    Value x2

    >>> test = CatalogStatic('param_value_1')
    >>> test.main_method()
    executed method 1!
    """

if __name__ == "__main__":
    import doctest

    doctest.testmod()