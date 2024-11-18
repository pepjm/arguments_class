#!/usr/bin/env python 
# version 1.4
import sys
import argparse
import json
import os
import io
import time
from datetime import datetime as dt,timedelta as delta
import json
from pprint import pprint
import getpass as gp
import base64

class arguments:
    def __init__(self,help="help.json",base64prefix='',base64postfix='',base64inside=''):
        self.path, self.prog_name = os.path.split(sys.argv[0])
        if os.path.dirname(help)=='': help=os.path.join(self.path,help)
        self.prog_shortname, self.file_extension = os.path.splitext(self.prog_name)
        self.prog_shortname, self.file_extension = os.path.splitext(self.prog_name)
        self.debug_file=os.path.join(self.path,self.prog_shortname+'.debug')
        self.output_file=os.path.join(self.path,self.prog_shortname+".out")
        self.input_file=os.path.join(self.path,self.prog_shortname+".input")
        self.log_file=os.path.join(self.path,self.prog_shortname+".log")
        self.help=help
        self.base64prefix=base64prefix
        self.base64postfix=base64postfix
        self.base64inside=base64inside
        self.base64=False
        self.dolog=True
        self.doprint=True
        self.parameters=self.parse()
        self.password=""
        para=self.merge_initial_parameters(self.parameters)
    def setbase64(self,value=False):
        self.base64=value
    def change_output(self,thefile):
        self.output_file=thefile
    def change_input(self,thefile):
        self.input_file=thefile
    def read_file_input(self,filename=""):
        data=None
        if filename=='': filename=self.input_file
        if os.path.isfile(filename):
            with open(filename, 'r') as f:
                data = f.read()
        else:
            print("Help file '"+filename+"' does not exist !")
            exit()
        return data
    def human(self,jsonToConvert):
        """
        used for printing with the format JSON not human python
        """
        f = io.StringIO()
        pprint(jsonToConvert,f)
        txt=f.getvalue()
        return txt
    def merge_initial_parameters(self,theoptions):
        if theoptions.input:
            self.change_input(theoptions.input)
        if theoptions.execute:
            self.execute=theoptions.execute
        if hasattr(theoptions,'nolog') and theoptions.nolog:
            self.dolog=False
            self.log_file=''
        if hasattr(theoptions,'noprint') and theoptions.noprint: self.doprint=False
        if hasattr(theoptions,'folder') and theoptions.folder!='':
            if not os.path.isdir(theoptions.folder):
                print("Wrong Folder"); exit()
        if hasattr(theoptions,'debugfile') and theoptions.debugfile:
            self.debug_file=theoptions.debugfile
        elif theoptions.folder!='':
            bn=os.path.basename(self.debug_file)
            self.debug_file=os.path.join(theoptions.folder,bn)
        if hasattr(theoptions,'outputfile') and theoptions.outputfile:
            self.output_file=theoptions.outputfile
        elif theoptions.folder!='':
            bn=os.path.basename(self.output_file)
            self.output_file=os.path.join(theoptions.folder,bn)
        if hasattr(theoptions,'inputfile') and theoptions.inputfile:
            self.input_file=theoptions.inputfile
        elif theoptions.folder!='':
            bn=os.path.basename(self.input_file)
            self.input_file=os.path.join(theoptions.folder,bn)
        if hasattr(theoptions,'logfile') and theoptions.logfile:
            self.log_file=theoptions.logfile
        elif theoptions.folder!='':
            bn=os.path.basename(self.log_file)
            self.log_file=os.path.join(theoptions.folder,bn)
        return self
    def inithelp(self):
        help=self.help
        parser=None
        with open(help, 'r') as f:
            data = json.load(f)
        if "help" in data:
            myhelp=data["help"]
            if "epilog" in myhelp: myepilog=myhelp["epilog"]
            else: myepilog="..."
            if "description" in myhelp: mydescription=myhelp["description"]
            else: mydescription="..."
            parser = argparse.ArgumentParser(
                prog=self.prog_name,
                description=mydescription,
                epilog=myepilog)
            if "arg" in myhelp:
                args=myhelp["arg"]
                for arg in args:
                    if "name" in arg:
                        myname=arg["name"].split(',')
                        if "metavar" in arg: mymetavar=arg["metavar"]
                        else: mymetavar=None
                        if "default" in arg: mydefault=arg["default"]
                        else: mydefault=None
                        if "help" in arg: myhelp=arg["help"]
                        else: myhelp=None
                        if "required" in arg: myrequired=arg["required"]
                        else: myrequired=None
                        if "action" in arg: myaction=arg["action"]
                        else: myaction=None
                        if "type" in arg: mytype=arg["type"]
                        else: mytype=None
                        if mytype=='int':
                            parser.add_argument(*myname, default=mydefault,help=myhelp,required=myrequired,action=myaction,type=int)
                        else:
                            parser.add_argument(*myname, default=mydefault,help=myhelp,required=myrequired,action=myaction)
        else:
            #default
            parser = argparse.ArgumentParser(
                prog=program,
                description=' ... ',
                epilog='help missing')
        return parser

    def str2bool(selv,v):
        if isinstance(v, bool):
            return v
        if v.lower() == "true":
            return True
        elif v.lower() == "false":
            return False
        else:
            raise argparse.ArgumentTypeError('Boolean value expected: true or false')
    def isbase64(self,st):
        try:
            sbbytes=st
            if isinstance(st,str):
                sbbytes=bytes(st,'ascii')
            elif isinstance(st,bytes):
                sbbytes=st
            else:
                return False
            deco0=base64.b64decode(sbbytes)
            deco=deco0.decode('ascii')
            val1=base64.b64encode(deco0).decode("utf-8")
            if st == val1:
                return True
            else:
                return False
        except Exception:
            return False
    def decodebase64PrefixPostfix(self,val):
        val0=val
        try:
            val1 = str(base64.b64decode(val0).decode('ascii'))
        except:
            return "Error: Password wrong format !"
        if self.base64prefix != '':
            if len(self.base64prefix)<len(val1) :
                fix=val1[:len(self.base64prefix)]
                if self.base64prefix==fix:
                    val1=val1[len(self.base64prefix):]
                else:
                    return "Error: Password wrong formatted !"
            else:
                return "Error: Password wrong formatted !"
        if self.base64postfix != '':
            if len(self.base64postfix)<len(val1) :
                fix=val1[-len(self.base64postfix):]
                if self.base64postfix==fix:
                    val1=val1[:-len(self.base64postfix)]
                else:
                    return "Error: Password wrong formatted !"
            else:
                return "Error: Password wrong formatted !"
        val=val1
        if self.base64inside!='':
            for i in range(len(self.base64inside)):
                val=val.replace(self.base64inside[i],'')
        return val
    def decodebase64(self,val):
        val = str(base64.b64decode(val).decode('ascii'))
        return val
    def parse(self):
        parserprg=self.inithelp()
        options= parserprg.parse_args()
        return options
    def findUserPassword(self,usr,pw):
        ok=""
        user=usr
        pwd=pw
        if user==None or user=="":
            user= input("Enter your user: ")
        if user=='':
            ok="Error: empty User"
        if pwd==None or pwd=="":
            pwd=gp.getpass(prompt='Password: ', stream=None)
            if pwd == '':
                ok="Error: empty password !"
        if self.base64:
            pwd=self.decodebase64PrefixPostfix(pwd)
            if "Error: Password wrong" in pwd: 
                ok=pwd
        return user,pwd,ok

if __name__ == "__main__":
    print("Using directly the class")
    args=arguments("secondhelp.json")
    print("args==>")
    print(args.human(vars(args)))
    print("parameters==>")
    if args.parameters:
        pprint(args.human(vars(args.parameters)))
    else:
        print("cannot read the help !")
