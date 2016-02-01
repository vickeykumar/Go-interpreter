#!/usr/bin/python env
import os
from commands import *

def main():
	print "*************************************************************************"
	print "*                  WELCOME TO GO INTERPRETER                            *"
	print "*************************************************************************\n"
	PrintHelp()
	init()
	while (1):
		try:
			GetInput(raw_input("go>>").strip())
		except KeyboardInterrupt:
			print "\nKeyboardInterrupt"
			pass
		except Exception,e:
			print "Error: ",str(e)
			pass

if __name__ == "__main__":
	main()


