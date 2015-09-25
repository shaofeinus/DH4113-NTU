from serial import Serial
from Queue import Queue

__author__ = 'Shao Fei'


class DataFeeder:

    # CONSTANTS
    BAUD_RATE = 115200
    num_bytes = [1, 3, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]

    def __init__(self):
        self.in_queue = Queue.Queue()
        self.serialPort = Serial(port="/dev/ttyAMA0", baudrate=self.BAUD_RATE, timeout=2)
        if not self.serialPort.isOpen():
            self.serialPort.open()
        self.serialPort.flushInput()
        self.serialPort.flushOutput()

    def receive_data(self, inQueueLock):
        data_input = [0]
        if self.serialPort.inWaiting() > 0:
            self.serialPort.readinto(data_input)
            inQueueLock.acquire()
            self.in_queue.put(int(ord(data_input[0])))
            inQueueLock.release()

    def my_to_signed(self, num):
        if num >> 15 == 1:
            num ^= 0xFFFF
            num += 1
            return -num
        return num

    def process_data(self, data, inQueueLock, dataLock):

        while self.in_queue.empty():
            continue

        inQueueLock.acquire()
        data_in = self.in_queue.get()
        inQueueLock.release()

        dev_id = (data_in >> 4)
        timeStamp = ((data_in & 0xF) << 8)

        while self.in_queue.empty():
            continue

        inQueueLock.acquire()
        data_in = self.in_queue.get()
        inQueueLock.release()

        timeStamp = timeStamp | data_in

        dataLock.acquire()
        data[dev_id].put(timeStamp)
        dataLock.release()

        for x in range(self.num_bytes[dev_id]):
            while self.in_queue.empty():
                continue

            inQueueLock.acquire()
            data_in = self.in_queue.get()
            inQueueLock.release()

            dataTemp = data_in << 8

            while self.in_queue.empty():
                continue

            inQueueLock.acquire()
            data_in = self.in_queue.get()
            inQueueLock.release()

            dataTemp = dataTemp | data_in

            if dev_id == 4: #adds third byte for barometer reading
                while self.in_queue.empty():
                    continue

                inQueueLock.acquire()
                data_in = self.in_queue.get()
                inQueueLock.release()

                dataTemp = (dataTemp << 8) | data_in

            if dev_id == 1 or dev_id == 2:
                dataLock.acquire()
                data[dev_id].put(self.my_to_signed(dataTemp))
                dataLock.release()

            else:
                dataLock.acquire()
                data[dev_id].put(dataTemp)
                dataLock.release()
