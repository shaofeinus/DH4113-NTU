import RPi.GPIO as GPIO
import time

hori = [25, 8, 7]
vert = [27, 22, 23, 24]
num_map = [[1,2,3],[4,5,6],[7,8,9],[-1,0,-2]]
num_press = -3
deb_time = 0

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

print ("mode")

GPIO.setup(hori, GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(vert, GPIO.IN)
print ("setup")

def getHori(channel):
    global deb_time
    if time.time() - deb_time < 0.05 or GPIO.input(channel) == GPIO.LOW:
        return
    deb_time = time.time()
    GPIO.remove_event_detect(channel)
    for x in range(len(hori)):
        GPIO.output(hori[x], GPIO.LOW)
        if GPIO.input(channel) == GPIO.LOW:
            time.sleep(0.01)
            num_press = num_map[vert.index(channel)][x]
            print "numpress:", num_press
        GPIO.output(hori[x], GPIO.HIGH)
    GPIO.add_event_detect(channel, GPIO.RISING, callback=getHori)

for x in range(len(vert)):
     GPIO.add_event_detect(vert[x], GPIO.RISING, callback=getHori)
print ("events added")

while True:
    continue