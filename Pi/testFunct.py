__author__ = 'Pap'

class test(object):
    def __init__(self):
        self.a = 3

    def out(self):
        print self.a

def times(self):
    self.a *= 2

my_test = test()
my_test.out()
test.times = times
my_test.times()
my_test.out()