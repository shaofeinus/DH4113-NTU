import os
import subprocess

__author__ = 'Pap'

class UI_Speaker(object):
    def __init__(self, voice="en-n+m2" , amplitude=200, speed=170):
        self.args = ["sudo", "espeak", "-a", str(amplitude), "-s", str(speed), "-v", str(voice)]
        self.sub_proc = subprocess.Popen(self.args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def speak(self, sentence):
        # wait for previous instance to close
        # try:
        #     self.sub_proc.communicate()
        #     self.sub_proc.terminate()
        # except:
        #     pass
        # self.sub_proc = subprocess.Popen(self.args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # write to console as input
        try:
            self.sub_proc.stdin.write("\""+str(sentence).strip() + "\"\n")
            self.sub_proc.stdin.flush()
        except:
            self.sub_proc = subprocess.Popen(self.args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.sub_proc.stdin.write("\""+str(sentence).strip() + "\"\n")
            self.sub_proc.stdin.flush()
    def stop(self):
        # stops speech by immediately terminating the process
        try:
            self.sub_proc.terminate()
        except:
            pass

    def wait(self):
        try:
            self.sub_proc.communicate()
            self.sub_proc.terminate()
        except:
            pass
        self.sub_proc = subprocess.Popen(self.args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def __del__(self):
        try:
            self.sub_proc.communicate()
            self.sub_proc.terminate()
        except:
            pass