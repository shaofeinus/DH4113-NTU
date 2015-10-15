import os
import warnings

warnings.filterwarnings("ignore")

def speak(sentence) :
    os.system('sudo espeak -s 185 -a 200 -ven-n+f2 "{0}"'.format(sentence))

#sentence = raw_input("Enter sentence to speak: ")

#speak(sentence)
