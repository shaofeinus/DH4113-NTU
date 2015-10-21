from collections import deque

__author__ = 'Pap'


class test_class():
    def __init__(self, my_deq):
        self.my_deq = my_deq

    def run(self):
        my_deq.append(1)
        my_deq.append(2)
        my_deq.append(3)

my_deq = deque()

my_deq.append(0)

print my_deq

test = test_class(my_deq)

print test.my_deq

test.run()

print test.my_deq

print my_deq