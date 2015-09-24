from serial import Serial
import time
from threading import Thread
from Queue import Queue

#CONSTANTS
MAX_ATTEMPTS = 3;
handshake1 = 0x10101010
handshake2 = 0x01010101
handshake3 = 0x11110000 
num_id = 16
num_bytes = [2, 6, 6, 2, 2, 2, 2, 2, 2]

#GLOBALS
serialPort = None
data = [Queue.Queue() for x in range(num_id)]
in_queue = Queue.Queue()
read_data_thread = None
process_data_thread = None

def init_serial():
    Serial(port="/dev/ttyAMA0", baudrate=9600, timeout = 0.5)

    if (serialPort.isOpen() == False):
        serialPort.open()

    serialPort.flushInput()
    serialPort.flushOutput()

def handshake():
    serialPort.write(handshake1);
    connect_failed = False
    num_tries = MAX_ATTEMPTS;

    receive_handshake = receive_data()
    while(True):
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
            sleep(0.02)

    return connect_failed

def printAll(dev_id, timeStamp, data):
    print ("id: "),
    print (dev_id),
    print (", timeStamp: "),
    print (timeStamp),
    print (", data: "),
    print (data)
        
def receive_data():
    data_in = None
    while True:
        if serialPort.inWaiting() > 0:
            serialPort.read(data_in)
            in_queue.put(data_in)
            
def process_data():
    data_in = None
    dev_id = None
    timeStamp = None
    data_temp = None
    
    while True:
        while in_queue.empty():
        dev_id = data_in >> 4
        timeStamp = (data_in & 0xF) << 8)
        
        while in_queue.empty():
        serialPort.read(data_in)
        
        timeStamp = timeStamp | data_in

        data[dev_id].put(timeStamp)

        data_print = []

        for x in range(num_bytes[dev_id]):
            while in_queue.empty():
            serialPort.read(data_in)
            
            dataTemp = data_in << 8
            
            while in_queue.empty():
            serialPort.read(data_in)

            dataTemp = dataTemp | data_in
            data[dev_id].put(dataTemp)
            data_print.append(dataTemp)
                
            print_all(dev_id, timeStamp, data_print)

def run_threads():    
    read_data_thread = Thread(target=receive_data)
    process_data_thread = threading.Thread(target=process_data)

    read_data_thread.start()
    process_data_thread.start()

        
##if handshake() == True:
##    print ("handshake successful");
##    load_data_loop();
##    threading.Thread(target=load_data_loop)
##    threading.Thread(target=process_buffer)
##else:
##    print ("handshake unsuccessful");
