import os
import warnings

warnings.filterwarnings("ignore")

def speak(sentence) :
    os.system('espeak -ven+f2 "{0}"'.format(sentence))

#sentence = raw_input("Enter sentence to speak: ")

#speak(sentence)
