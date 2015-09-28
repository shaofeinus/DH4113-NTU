from serial import Serial
import threading
import Queue
import datetime

serialPort = Serial(port="/dev/ttyAMA0", baudrate=115200, timeout=2)

if not serialPort.isOpen():
    serialPort.open()

serialPort.flushInput()
serialPort.flushOutput()

#CONSTANTS
MAX_ATTEMPTS = 3
handshake1 = 0x10101010
handshake2 = 0x01010101
handshake3 = 0x11110000
num_id = 16
num_bytes = [1, 3, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]

#GLOBALS
data = [Queue.Queue() for x in range(num_id)]
in_queue = Queue.Queue()

def handshake():
    serialPort.write(handshake1);
    connect_failed = False
    num_tries = MAX_ATTEMPTS;

    receive_handshake = receive_data()
    while True :
        if receive_handshake == handshake2:
            serialPort.write(handshake3)
            break
        else:
            if num_tries == 0:
                print ("mega_conf_notreceived")
                connect_failed = True
                break

            receive_handshake = receive_data()
            num_tries = num_tries - 1
            #sleep(0.02)

    return connect_failed

def printAll(dev_id, timeStamp, data_print):

    if dev_id == 2:
        print ("id: "),
        print (dev_id),
        print (", timeStamp: "),
        print (timeStamp),
        print (", data: "),
        print (data_print),
        print datetime.datetime.now()

def receive_data():
    data_input = 0
    while True:
        numBytes = serialPort.inWaiting()
        #print numBytes
        if numBytes > 0:
            data_input = serialPort.read(numBytes)
            charList = list(data_input)
            for i in range(numBytes):
                in_queue.put(int(ord(charList[i])))

def my_to_signed(num):
    if num >> 15 == 1:
        num = num ^ 0xFFFF
        num = num + 1
        return -num
    return num

def process_data():
    while True:
        while in_queue.empty():
            continue

        data_in = in_queue.get()
        dev_id = (data_in >> 4)
        timeStamp = ((data_in & 0xF) << 8)
        while in_queue.empty():
            continue
        data_in = in_queue.get()
        timeStamp = timeStamp | data_in
        data[dev_id].put(timeStamp)

        data_print = []
        for x in range(num_bytes[dev_id]):
            while in_queue.empty():
                continue
            data_in = in_queue.get()
            dataTemp = data_in << 8

            while in_queue.empty():
                continue
            data_in = in_queue.get()
            dataTemp = dataTemp | data_in

            if dev_id == 4:
                while in_queue.empty():
                    continue
                data_in = in_queue.get()
                dataTemp = dataTemp << 8
                dataTemp = dataTemp | data_in

            if dev_id == 1 or dev_id == 2:
                data[dev_id].put(my_to_signed(dataTemp))
                data_print.append(my_to_signed(dataTemp))
            else:
                data[dev_id].put(dataTemp)
                data_print.append(dataTemp)

        printAll(dev_id, timeStamp, data_print)


n = 10
#data_input = ""#[0]

read_data_thread = threading.Thread(target=receive_data)
process_data_thread = threading.Thread(target=process_data)

read_data_thread.start()
process_data_thread.start()
