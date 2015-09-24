from serial import Serial
import time
from threading import Thread
from Queue import Queue

class commu(object):
    def __init__(self):
        self.MAX_ATTEMPTS = 3;
        self.handshake1 = 0x10101010
        self.handshake2 = 0x01010101
        self.handshake3 = 0x11110000 
        self.num_id = 16
        self.num_bytes = [2, 6, 6, 2, 2, 2, 2, 2, 2]

        self.serialPort = None
        self.data = [Queue.Queue() for x in range(num_id)]

        self.in_queue = Queue.Queue()

        self.read_data_thread = None
        self.process_data_thread = None

    def init_serial(self):
        Serial(port="/dev/ttyAMA0", baudrate=9600, timeout = 0.5)

        if (self.serialPort.isOpen() == False):
            self.serialPort.open()

        self.serialPort.flushInput()
        self.serialPort.flushOutput()

    def handshake(self):
        self.serialPort.write(handshake1);
        connect_failed = False
        print ("Handshake 1 sent")
        num_tries = MAX_ATTEMPTS;

        while self.serialPort.inWaiting() <= 0:
        receive_handshake = None
        self.serialPort.read(receive_handshake)
        while(True):
            if receive_handshake == handshake2:
                print ("Handshake 2 received")
                serialPort.write(handshake3)
                print ("Handshake 3 sent")
                break
            else:
                if num_tries == 0:
                    print ("mega_conf_notreceived")
                    connect_failed = True
                    break
                
                while self.serialPort.inWaiting() <= 0:
                self.serialPort.read(receive_handshake)

                num_tries = num_tries - 1
                sleep(0.02)

        return connect_failed

    def printAll(self, dev_id, timeStamp, data):
        print ("id: "),
        print (dev_id),
        print (", timeStamp: "),
        print (timeStamp),
        print (", data: "),
        print (data)
            
    def receive_data(self):
        data_in = None
        while True:
            if self.serialPort.inWaiting() > 0:
                self.serialPort.read(data_in)
                self.in_queue.put(data_in)
                
    def process_data(self):
        data_in = None
        dev_id = None
        timeStamp = None
        data_temp = None
        
        while True:
            while self.in_queue.empty():
            self.serialPort.read(data_in)
            
            dev_id = data_in >> 4
            timeStamp = (data_in & 0xF) << 8)
            
            while self.in_queue.empty():
            self.serialPort.read(data_in)
            
            timeStamp = timeStamp | data_in

            self.data[dev_id].put(timeStamp)

            data_print = []

            for x in range(self.num_bytes[dev_id]):
                while self.in_queue.empty():
                self.serialPort.read(data_in)
                
                dataTemp = data_in << 8
                
                while self.in_queue.empty():
                self.serialPort.read(data_in)

                dataTemp = dataTemp | data_in
                self.data[dev_id].put(dataTemp)
                data_print.append(dataTemp)
                    
                self.print_all(dev_id, timeStamp, data_print)

    def run_threads(self):    
        self.read_data_thread = Thread(target=receive_data)
        self.process_data_thread = threading.Thread(target=process_data)

        self.read_data_thread.start()
        self.process_data_thread.start()

    def getData(self, id):
        if not self.data[if].empty():
            return self.data[id].get()
        return -1
    ##if handshake() == True:
    ##    print ("handshake successful");
    ##    load_data_loop();
    ##    threading.Thread(target=load_data_loop)
    ##    threading.Thread(target=process_buffer)
    ##else:
    ##    print ("handshake unsuccessful");
