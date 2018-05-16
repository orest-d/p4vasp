#!/usr/bin/python2
#
# HappyDoc:docStringFormat='ClassicStructuredText'
#
#  p4vasp is a GUI-program and a library for processing outputs of the
#  Vienna Ab-inition Simulation Package (VASP)
#  (see http://cms.mpi.univie.ac.at/vasp/Welcome.html)
#
#  Copyright (C) 2003  Orest Dubay <odubay@users.sourceforge.net>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

from sys import *
import traceback
from string import *

class DummyFile:
    def write(self,x):
        pass
    def close(self):
        pass
    def flush(self):
        pass

class PrintFile:
    def write(self,x):
        print x
    def close(self):
        pass
    def flush(self):
        pass

def indent(s,istring):
    """Intend *s* by *istring*.
    If istring is an iteger, istring is changed to istring*INDENT
    (INDENT contains two whitespaces by default).
    Then *istring* is added to the beginning of every line of *s*.
    """
    l=split(s,"\n")
    if len(l)<2:
        return s
    else:
        return l[0]+"\n"+join(map(lambda x,i=istring:i+x, l[1:]),"\n")

class MessageDriver:
    def __init__(self,logfile=DummyFile(),closeflag=0,printing=1):
        self.closeflag=closeflag
        self.printing=printing
        if type(logfile)==type(""):
            try:
                logfile=open(logfile,"w")
                self.closeflag=1
            except IOError:
                logfile=PrintFile()
                self.closeflag=0

        self.logfile=logfile
        self.pstep=0

    def printText(self,txt):
        if self.printing:
            print(txt)

    def status(self,txt):
        self.printText(txt)
        self.logfile.write("STATUS:%s\n"%indent(txt,"       "))
        self.logfile.flush()

    def error(self,txt):
        if self.printing:
            stderr.write("ERROR : %s\n"%indent(txt,"       "))
        self.logfile.write("ERROR : %s\n"%indent(txt,"       "))
        self.logfile.flush()

    def step(self, step=None,total=None):
        if (step is None) or (total is None) or (total<=0):
            self.pstep+=1
            s="-/|\\"
            stdout.write("Progress: %s\r"%s[self.pstep%4])
        else:
            stdout.write("Progress: %4d/%4d %s\r"%(step,total,int(20.0*step/total)*"#"))


    def message(self,txt):
        self.printText(txt)
        self.logfile.write("MSG   :%s\n"%indent(txt,"       "))
        self.logfile.flush()

    def confirm(self,txt):
        self.printText(txt)
        self.logfile.write("CMSG  :%s\n"%indent(txt,"       "))
        self.logfile.flush()
        raw_input("Press ENTER to continue...")

    def confirm_error(self,txt):
        self.printText("Error: "+txt)
        self.logfile.write("CERR  :%s\n"%indent(txt,"       "))
        self.logfile.flush()
        raw_input("Press ENTER to continue...")

    def exception(self,etype=None,value=None,trace=None):
        if etype is None:
            etype,value,trace=exc_info()
        if self.printing:
            traceback.print_exception(etype,value,trace)
        txt=join(traceback.format_exception(etype,value,trace))
        self.logfile.write("EXCEPT:%s\n"%indent(txt,"       "))
        self.logfile.flush()
    def __del__(self):
        self.logfile.flush()
        if self.closeflag:
            self.logfile.close()
