import time

class Timer:

    def __init__(self):
        self.s = 0

    def start(self):
        self.s = time.time()

    def step(self, string = ''):
        print(string, time.time() - self.s)
        self.s = time.time()

    def end(self, string = ''):
        print(string, time.time() - self.s)
        self.s = 0