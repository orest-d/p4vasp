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

from UserList import *
from p4vasp.message import *


class Process:
    def total(self):
        return None
    def step(self):
        return None
    def status(self):
        return None
    def error(self):
        return None
    def next(self):
        return 0


class Scheduler(UserList):
    def __init__(self):
        UserList.__init__(self)

    def next(self):
        while 1:
            if len(self)==0:
                return
            try:
                return self[0].next()
            except StopIteration:
#        print "delete finished"
                del self[0]

    def run(self):
        while 1:
            if len(self)==0:
                return
            try:
                self[0].next()
            except StopIteration:
                del self[0]

    def scheduleFirst(self,g):
        self.insert(0,g)

    def schedule(self,g):
        self.append(g)

    def firstTaskToBack(self):
        x=self[0]
        del self[0]
        self.append(x)
