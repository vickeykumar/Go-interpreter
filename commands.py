#!/usr/bin/python env
import os,re,subprocess,sys
import platform

#config
import logging
logging.basicConfig(
   level=logging.DEBUG,
   format='%(asctime)s:%(levelname)s:%(lineno)d:%(message)s',
   filename="/tmp/out.log",
   filemode='w'
)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

EDITOR = "vim"	#default editor
CLEAR = "cls"	#clear command on ur system
if not (platform.system() in ('Windows', 'Microsoft')):
        import readline
        CLEAR = 'clear'
packageName = "package main"
filename = "/tmp/test.go"

importset = ['"fmt"']
cgo = []
variableSet = []
importstring = ""
bodylist = ["func main() {","/*body*/"]
bodystring = ""
headerstring = ""
footerstring = ""
CommandHelpStr = {  ":h CommandName" : "Print Help Menu.",
		":e <EditorName, line no>" : "Edit the Source File(in editor or single line).",
		":d <line no, range>" : "Display a line or a Range of lines (given as L1:L2) or comma separated lines.",
		":r, :x" : "Run as Go File.",
		":q" : "Quit the session.",
		":c, :cls" : "Clear the session,and Restart.",
		":doc <packageName> <functionName>" : "Display the documentation.",
		":save <filename>" : "Save the current session in to a file.",
		":CGO" : "Cgo input (use KeyboardInterrupt to save)."
		}
CommandArg = ''

Command2FuncMap = {
	":h":"PrintHelp",
	":e":"editSourceFile",
	":r":"run",
	":x":"run",
	":d":"display",
	":save":"SaveSessionIntoFile",
	":CGO":"GetCgoInput"
}

# utility functions
def GetInput(inputstring = ''):
	global headerstring,footerstring,bodystring,bodylist,importset,importstring,CommandArg,variableSet,filename
	if inputstring == '':
		return
	elif inputstring.startswith(":doc"):
		inputstring = inputstring.split(" ",1)
		CommandArg = inputstring[1] if len(inputstring)>1 else ''
		displayDoc()
		return
	elif inputstring.startswith(":c") or inputstring.startswith(":cls") :
		os.system(CLEAR)
		init()
		return
	elif inputstring.startswith(":q"):
		if os.path.exists(filename):
			os.remove(filename)
		sys.exit()
	for k,fun in Command2FuncMap.iteritems():
		if inputstring.startswith(k):
			inputstring = inputstring.split(" ",1)
			CommandArg = inputstring[1] if len(inputstring)>1 else ''
			if callable(globals()[fun]):
				globals()[fun]()
			return
	if inputstring.startswith("import "):
		pkg = inputstring.split()[-1]
		if pkg not in importset:
			importset.append(pkg)
	elif (len(re.split(' |=|:=|\(|\)',inputstring)) == 1) or inputstring.startswith('"') :	#input is value or string
		err = run("fmt.Println(" + inputstring + ")")
		if err != '':
			print err,
	elif isListinStartofString(["fmt.println(","fmt.print(","fmt.printf("], inputstring.lower()):		
		err = run(inputstring)
		if err != '':
			print err,
	elif inputstring[-1] == "{":
		GetBlockInput(inputstring)
	elif re.compile("[a-zA-Z0-9\.]+\([^\)]*\)(\.[^\)]*\))?").match(inputstring):		#caught a function call
		flag = inputstring[-1]
		if flag == ';':
			inputstring = inputstring[0:-1]
			err = run("fmt.Println(" + inputstring + ")")
			if err != '':
				err = run(inputstring)
				if err != '':
					print err,
		else:
			bodylist.append(inputstring)
			headerstring += '\n\t' + inputstring
	elif inputstring != '':
		if updateVariableSet(inputstring):
			createFooterString()
		bodylist.append(inputstring)
		headerstring += '\n\t' + inputstring

def updateVariableSet(inputstring=''):
	global variableSet
	flag = False
	v = ''
	if inputstring.startswith("var"):
		v = inputstring.split()[1]
	elif len(inputstring.split(':=',1)) > 1:
		v = inputstring.split(':=',1)[0]
	if v != '' :		#variable caught
		var1 =[i.strip() for i in v.split(",")]
		for v in var1:
			if v != "_" and v not in variableSet :
				variableSet.append(v)
				flag = True
	return flag

def displayDoc():
	global CommandArg
	commandstr = 'godoc ' + CommandArg
	os.system(commandstr)

def display():
	global CommandArg,bodylist,importset,cgo
	try:
		lines = CommandArg.strip().split(":")
		if len(lines) < 3 and len(lines)>0:
			lines = [int(i) for i in lines]
			if len(lines)==2:
				lines = range(lines[0],lines[1])
			offset = len(importset) + len(cgo) + 3
			for i in lines:
				if (i>offset) and (i < (len(bodylist) + offset)):
					print "line ",i,": ",bodylist[i - offset].strip()
				else:
					print "invalid line no. ",i
		else:
			print "invalid no of arguments"
	except Exception,e:
			print "ERROR: invalid argument ",str(e)

def createHeaderString():
	global headerstring
	headerstring = "\n\t".join(bodylist)

def createFooterString():
	global footerstring,variableSet
	tempstr = ("\tvar " + ",".join(["_" for v in variableSet]) + " = " + ",".join([v for v in variableSet])) if len(variableSet)>0 else '' 
	footerstring = "\t/*!body*/\n" + tempstr + "\n}"

def init():			#initialize again
	global importset,variableSet,importstring,bodylist,bodystring,headerstring,footerstring,cgo
	importset = ['"fmt"']
	variableSet = []
	cgo = []
	importstring = ""
	bodylist = ["func main() {","/*body*/"]
	bodystring = ""
	headerstring = ""
	footerstring = ""
	createHeaderString()
	createFooterString()
	if not os.path.exists("/tmp/"):
		os.makedirs("/tmp/")

def GetBodyString(tempstr = ''):
	global bodystring,headerstring,footerstring
	bodystring = (headerstring + "\n\t" + tempstr + "\n" + footerstring) if tempstr !='' else (headerstring + "\n" + footerstring)
	return bodystring

def GetImportString():
	global importstring,importset,bodystring
	importstring = "import (\n\t" + "\n\t".join([pkg if pkg.split("/")[-1].strip('"')+'.' in bodystring else '_ '+pkg for pkg in importset]) + "\n)\n"
	return importstring

def GetBodyString(tempstr = ''):
	global headerstring,footerstring
	return headerstring + "\n\t" + tempstr + "\n" + footerstring

def isListinStartofString(list1=[],str1=''):
	for l in list1:
		if str1.startswith( l ):
			return True
def isStringinStartofList(str1,list1=[]):
	for l in list1:
		if l.strip().startswith(str1):
			return True

def GetCgoInput(startstring=''):
	global cgo
	try:
		while(1):
			inp = raw_input()
			if inp.strip() == 'import "C"':
				if inp.strip() in cgo:
					del cgo[cgo.index(inp)]
				cgo.append(inp)
				break
			if inp.strip() != '':
				cgo.append(inp)
	except KeyboardInterrupt:
		print "OK"
		pass

def GetCgoString():
	global cgo
	return '\n'.join(cgo)

def GetBlockInput(startstring=''):
	global bodylist,headerstring
	tempbodylist = []
	tempstr = ""
	try:
		notabs = 1
		tempbodylist.append(startstring)
		while notabs > 0 :
			inp = raw_input().strip()
			if inp != '' :
				if inp[-1] == '}' or inp[-3:] == '}()':
					notabs -= 1
				inp = ''.join(["\t" for i in range(notabs)]) + inp
				tempbodylist.append(inp)
				if inp[-1] == '{' and inp.strip()[0] != '}':
					notabs += 1
				
		if isStringinStartofList("import",tempbodylist):
			raise SyntaxError("wrong import inside a block")
		tempstr = '\n\t'.join(tempbodylist)

		if startstring.startswith("func "):
			bodylist = tempbodylist + bodylist
			headerstring = tempstr + '\n' +headerstring
		else:
			bodylist += tempbodylist
			headerstring += '\n\t' + tempstr
	except Exception,e:
		print "Error: ",str(e)

def run(tempstr = ''):
	global packageName,filename,headerstring,bodystring
	bodystring = GetBodyString(tempstr)
	progstr = packageName + "\n" + GetCgoString() + "\n" + GetImportString() + bodystring
	f = open(filename,"w")
	f.write(progstr)
	f.close()
	out,err = subprocess.Popen("go run " + filename,stderr=subprocess.PIPE, shell=True).communicate()
	return err

def SaveSessionIntoFile():
	global CommandArg,packageName,headerstring,bodystring
	if CommandArg != '':
		dir = os.path.dirname(CommandArg)
        	if dir != '' and not os.path.exists(dir):
			if raw_input("Path does not exists: want to create.. ?(y/n) ").strip().lower() == 'y':
				os.makedirs(dir)
			else:
				return
		bodystring = GetBodyString()
		progstr = packageName + "\n" + GetCgoString() + "\n" + GetImportString() + bodystring
		f = open(CommandArg,"w")
		f.write(progstr)
		f.close()
		print "file saved successfully..."
	else:
		print "Insufficient Arguments, Check Help"

def PrintHelp():
	print "\n  COMMANDS:\n"
	width = max([len(word) for word in CommandHelpStr.keys()])
	for key,val in CommandHelpStr.iteritems():
		print "\t",key.ljust(width),"\t",val

def editSourceFile():
	global CommandArg,bodylist,cgo
	try:
		i = int(CommandArg.strip())
		offset = len(importset) + len(cgo) + 3
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
			createHeaderString()
		else:
			print "invalid argument"
	except Exception,e:
		if (CommandArg.strip() == "vim") or (CommandArg.strip() == ""):
			os.system(EDITOR + " " + filename)
		else:
			print "ERROR: invalid argument ",str(e)
#def UpdateFromFile():

