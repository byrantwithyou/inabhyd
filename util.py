import random


class MyError(Exception):

    def __init__(self, msg=""):
        self.msg = msg
        super().__init__(self.msg)


class MyWarning(Exception):
    def __init__(self, msg=""):
        self.msg = msg
        super().__init__(self.msg)


class BiasedCoin(object):
    def flip(prob):
        if prob > 1 or prob < 0:
            raise MyError("Probability must be between 0 and 1!")
        return random.random() <= prob
