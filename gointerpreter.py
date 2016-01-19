#!/usr/bin/python env
import os

EDITOR = "vim"	#default editor
filename = "test.go"
importSet = ['"fmt"']
variableSet = []

packageName = "package main"
importstring = ""
bodylist = ["func main() {","/*body*/"]
bodystring = ""
CommandHelpStr = {  ":help, :h CommandName" : "Print Help Menu",
		":e <EditorName, line no>" : "Edit the Source File(in editor or single line)",
		":d <line no, range>" : "Display a line or a Range of lines (given as L1:L2) or comma separated lines",
		":r, :x" : "Run as Go File",
		":q" : "Quit the session",
		":c" : "Clear the session,and Restart"
		}
CommandArg = ''

# utility functions
def createImportStringAndBodyString(importSet, bodylist):
	bodystring = "\t".join(bodylist) + "\t/*!body*/" + "\tvar " + ",".join(["_" for v in variableSet]) + " = " + ",".join([v for v in variableSet]) + "\n}"
	importstring = "import (\n\t" + "\n\t".join([pkg if pkg.strip('"')+'.' in bodystring else '_ '+pkg for pkg in importset]) + "\n)"

def PrintHelp():
	print "\n  COMMANDS:\n"
	width = max([len(word) for word in CommandHelpStr.keys()])
	for key,val in CommandHelpStr.iteritems():
		print "\t",key.ljust(width),"\t",val

def editSourceFile():
	try:
		i = int(CommandArg.strip())
		offset = len(importset) + 3
		if (i>offset) and (i < (len(bodylist) + offset)):
			notabs = 0
			for c in bodylist[i - offset] :
				if c != "\t":
					break
				else:
					notabs += 1
			print "line ",i,": ",bodylist[i - offset].strip()
			inp = raw_input("enter new line: ").strip()
			if inp != "":
				bodylist[i - offset] = "".join(["\t" for i in xrange(notabs)]) + inp
			else:
				del(bodylist[i - offset])
		else:
			print "invalid argument"
	except:
		if (i.strip() == "vim") or (i.strip() == ""):
			os.system(EDITOR + " " + filename)
		else:
			print "invalid argument"


