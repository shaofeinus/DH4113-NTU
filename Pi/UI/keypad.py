import RPi.GPIO as GPIO
import time
import Queue

hori = [25, 8, 7]
vert = [27, 22, 23, 24]
num_map = [[0,1,2],[3,4,5],[6,7,8],[9,10,11]]
deb_time = 0
#press_time = 0


key_map = [['.',',','?','!'],['a','b','c'],['d','e','f'],['g','h','i'],['j','k','l'],['m','n','o'],['p','q','r','s'],['t','u','v'],['w','x','y','z'],[''],[' '],['']]
num_count = 0
prev_num = -3
num_queue = Queue.Queue()
out_str = ""

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

print ("mode")

GPIO.setup(hori, GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(vert, GPIO.IN)
print ("setup")

def debounce(channel):
    global deb_time
    if time.time() - deb_time < 0.05 or GPIO.input(channel) == GPIO.LOW:
        return False
    deb_time = time.time()
    return True

def getHori(channel):
    if not debounce(channel):
        return
    global press_time
    press_time = time.time()
    GPIO.remove_event_detect(channel)
    for x in range(len(hori)):
        GPIO.output(hori[x], GPIO.LOW)
        if GPIO.input(channel) == GPIO.LOW:
            time.sleep(0.01)
            num_queue.put(num_map[vert.index(channel)][x])
        GPIO.output(hori[x], GPIO.HIGH)
    GPIO.add_event_detect(channel, GPIO.RISING, callback=getHori)

for x in range(len(vert)):
     GPIO.add_event_detect(vert[x], GPIO.RISING, callback=getHori)
print ("events added")

while True:
    while num_queue.empty():
        continue
    num = num_queue.get()
    print num
    if num == 11:
        print "del"
        if len(out_str)>0:
            out_str = out_str[:len(out_str)-1]
        num_count = 0
        prev_num = 11
    elif num == 9:
        print "next"
        out_str += key_map[prev_num][num_count]
        num_count = 0
        prev_num = 9
    else:
        if num != prev_num:
            print "diff"
            if prev_num != -3:
                out_str += key_map[prev_num][num_count]
            num_count = 0
            prev_num = num
        else:
            print "same"
            num_count = (num_count + 1) % len(key_map[num])

    print "out str:", out_str



    continue