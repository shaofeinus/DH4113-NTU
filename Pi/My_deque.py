from collections import deque
__author__ = 'Pap'

class my_deque(object):
    def __init__(self):
        self.queue = deque()
        self.flush_queue = False

    def appendleft(self, item):
        if self.flush_queue:
            self.queue.clear()
            self.flush_queue = False
        self.queue.appendleft(item)

    def pop(self):
        item = self.queue.pop()
        if self.flush_queue:
            self.queue.clear()
            self.flush_queue = False
        return item

    def popleft(self):
        item = self.queue.popleft()
        if self.flush_queue:
            self.queue.clear()
            self.flush_queue = False
        return item

    def append(self, item):
        if self.flush_queue:
            self.queue.clear()
            self.flush_queue = False
        self.queue.append(item)

    def clear(self):
        self.queue.clear()

    def flush(self):
        self.flush_queue = True

    def empty(self):
        return len(self.queue) is 0
