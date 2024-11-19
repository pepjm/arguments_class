#!python3
#VERSION=0.7
import sys, json
import os
import io, re
from datetime import datetime
import time
from pprint import pprint

myoutputs=None
NORMAL = 1
VERBOSE = 2
DEBUG = 4
SILENT = 0

class outputs:
    global NORMAL
    global VERBOSE
    global DEBUG
    global SILENT
    def __init__(self,level=NORMAL,printout=True,debugFileName='',outputFileName='',logFileName=''):
        self.NORMAL = 1
        self.VERBOSE = 2
        self.DEBUG = 4
        self.SILENT = 0
        self.printout=printout
        self.debugFileName=debugFileName
        self.outputFileName=outputFileName
        self.logFileName=logFileName
        self.suspendprintout=False
        self.suspenddebug=False
        if level:
            self.setLevel(level)
        else:
            self.setLevel(NORMAL)
        #self.progName, self.file_extension = os.path.splitext(sys.argv[0])
    def setLevel(self,lvl):
        if type(lvl) is str:
            lvl1=lvl.upper()
            if lvl1=="NONE": lvl=NONE
            if lvl1=="NORMAL": lvl=NORMAL
            if lvl1=="VERBOSE": lvl= VERBOSE
            if lvl1=="DEBUG": lvl=DEBUG
            if lvl1=="SILENT": lvl=SILENT
        self.level=lvl
        #INIT files
        thedate=datetime.strftime(datetime.now(),'%Y-%m-%d %H:%M:%S')
        msg='BEGIN:'+thedate
        if self.level == DEBUG:
            folder=os.path.dirname(self.debugFileName)
#            if os.path.exists(folder):
            fdebug = open(self.debugFileName, "w")
            fdebug.write(msg+'\n')
            fdebug.close()
#            else:
#                print("Error file "+self.debugFileName+" does'nt exist ! ")
#                exit(1)
        if self.logFileName != "":
            folder=os.path.dirname(self.logFileName)
            if folder=='': folder='./'
#            if os.path.exists(folder):
            flog = open(self.logFileName, "w")
            flog.write(msg+'\n')
            flog.close()
#            else:
#                print("Error file "+self.logFileName+" does'nt exist ! ")
#                exit(1)
        if self.outputFileName != "":
            folder=os.path.dirname(self.outputFileName)
            if folder=='': folder='./'
#            if os.path.exists(folder):
            fout = open(self.outputFileName, "w")
            fout.write('')
            fout.close()
#            else:
#                print("Error file "+self.outputFileName+" does'nt exist ! ")
#                exit(1)
    def humanJsonFormat(self,jsonToConvert,depth=None, compact=False):
        """
        used for printing with the format JSON not human python
        """
        f = io.StringIO()
        pprint(jsonToConvert,f,depth=depth, compact=compact)
        txt=f.getvalue()
        return txt
    def list_cmpact(self,jsonToConvert,depth=99):
        """
        used for printing List one item per line
        """
        f = io.StringIO()
        pprint(jsonToConvert,f)
        txt=f.getvalue()
        sub=re.findall(r'(\n +)[^]|(\r\n )[^]',txt)
        sub2=list(reversed(sorted(list(dict.fromkeys(sub)))))
        l=len(sub2)
        for indx,r in enumerate(sub2):
            if l-indx > depth:
                txt=txt.replace(r,"")
        return txt
    def echo(self,messagelevel,msg):
        if self.level>=messagelevel and self.printout:
            if not self.suspendprintout:
                print(msg)
        if self.level==DEBUG and not self.suspenddebug:
            if os.path.exists(self.debugFileName):
                fdebug = open(self.debugFileName, "a")
                fdebug.write(msg+'\n')
                fdebug.close()
            else:
                fdebug = open(self.debugFileName, "w")
                fdebug.write(msg+'\n')
                fdebug.close()
        if self.logFileName != "":
            lvlmaxlog=self.level
            if lvlmaxlog>=DEBUG: lvlmaxlog=VERBOSE
            if (lvlmaxlog>=messagelevel and not self.suspendprintout) or (lvlmaxlog==DEBUG and not self.suspenddebug):
                if os.path.exists(self.logFileName):
                    flog = open(self.logFileName, "a")
                    flog.write(msg+'\n')
                    flog.close()
                else:
                    flog = open(self.logFileName, "w")
                    flog.write(msg+'\n')
                    flog.close()
    def suspend_print(self):
        #help for reducing debug between modules
        self.suspendprintout=True
    def continue_print(self):
        self.suspendprintout=False
    def suspend_debug(self):
        #help for reducing debug between modules
        self.suspenddebug=True
    def continue_debug(self):
        self.suspenddebug=False
    def writeOutput(self,mode='w',text='',filename=''):
        msg=str(text)
        outputFileName=self.outputFileName
        if filename!='': outputFileName=filename
        if outputFileName!='':
            if os.path.exists(outputFileName):
                foutput = open(outputFileName, mode)
                foutput.write(msg+'\n')
            else:
                foutput = open(outputFileName, "w")
                foutput.write(msg+'\n')
    def writeLog(self,mode='w',text='',filename=''):
        msg=str(text)
        logFileName=self.logFileName
        if filename!='': logFileName=filename
        if logFileName!='':
            if os.path.exists(logFileName):
                foutput = open(logFileName, mode)
                foutput.write(msg+'\n')
            else:
                foutput = open(logFileName, "w")
                foutput.write(msg+'\n')
