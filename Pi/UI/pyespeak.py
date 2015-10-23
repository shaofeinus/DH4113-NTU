import os

class Speaker(object):

	def speak(self, sentence) :
		if sentence == ".":
			os.system('sudo espeak -s 185 -a 200 -ven-n+m2 "dot"')
		else:
			os.system('sudo espeak -s 170 -a 200 -ven-n+m2 "{0}"'.format(str(sentence)))


