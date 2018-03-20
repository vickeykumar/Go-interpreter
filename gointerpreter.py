#!/usr/bin/python
import os
from commands import *
import platform
if not (platform.system() in ('Windows', 'Microsoft')):
        import readline
	CLEAR = 'clear'

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
			print "\nError: ",str(e)
			pass

if __name__ == "__main__":
	main()
