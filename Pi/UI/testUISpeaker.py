from UISpeaker import UI_Speaker as Speaker
import time

__author__ = 'Pap'

test = Speaker("en-n+m2", 170, None)
while True:
    test.speak("lololololol")
    time.sleep(2)

    test.speak("lolololololololololololololololololol")
    time.sleep(0.8)
    test.stop()

