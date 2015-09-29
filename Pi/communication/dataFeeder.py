from serial import Serial
import Queue
import datetime

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

    def receive_data(self):
        numBytes = self.serialPort.inWaiting()
        if numBytes > 0:
            data_input = self.serialPort.read(numBytes)
            charList = list(data_input)
            for i in range(numBytes):
                self.in_queue.put(int(ord(charList[i])))

    def my_to_signed(self, num):
        if num >> 15 == 1:
            num ^= 0xFFFF
            num += 1
            return -num
        return num

    def printAll(self, dev_id, timeStamp, data_print):
        if dev_id == 2:
            print ("id: "),
            print (dev_id),
            print (", timeStamp: "),
            print (timeStamp),
            print (", data: "),
            print (data_print),
            print (datetime.datetime.now())

    def process_data(self, data):

        data_in = self.in_queue.get()

        dev_id = (data_in >> 4)

        timeStamp = ((data_in & 0xF) << 8)

        data_in = self.in_queue.get()

        timeStamp = timeStamp | data_in

        data[dev_id].append(timeStamp)

        # data_print = []

        for x in range(self.num_bytes[dev_id]):

            # First byte
            data_in = self.in_queue.get()
            dataTemp = data_in << 8

            # Second byte
            data_in = self.in_queue.get()
            dataTemp = dataTemp | data_in

            # Adds third byte for barometer reading
            if dev_id == 4:

                data_in = self.in_queue.get()
                dataTemp = (dataTemp << 8) | data_in

            # If Accelerometer and Magnetometer, check for sign
            if dev_id == 1 or dev_id == 2:
                data[dev_id].append(self.my_to_signed(dataTemp))
                # data_print.append(self.my_to_signed(dataTemp))

            # If not Accelerometer, Magnetometer, Barometer or Gyroscope,
            # take out last reading before adding new reading
            elif not (dev_id == 3 or dev_id == 4):
                data[dev_id] = dataTemp
                # if not len(data[dev_id]) == 0:
                #     data[dev_id].pop()
                # data[dev_id].append(dataTemp)
                # data_print.append(dataTemp)

            # If  Barometer or Gyroscope, add reading straight
            else:
                data[dev_id].append(dataTemp)
                # data_print.append(dataTemp)

        # self.printAll(dev_id, timeStamp, data_print)
