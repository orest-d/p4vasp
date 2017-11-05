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



"""
Set utilities.
This module contains functions that allow handling lists as sets.
(Set is a list, which does not contain duplicate elements.)
"""
def to_set(l):
    "Removes duplicite elements from  *l*. Equivalent to append_set([],l)"
    set=[]
    for x in l:
        if x not in set:
            set.append(x)
    return set

def append_set(l,set):
    "Set addition - *set* is appended to set *l* ."
    for x in set:
        if x not in l:
            l.append(x)
    return l

def join_sets(sets):
    "Join all sets in the list *sets* into one set."
    l=[]
    for s in sets:
        append_set(l,s)
    return l

def contains_set(l,set):
    "Check if all elements of *set* are present in *l* ."
    for x in set:
        if x not in l:
            return 0
    return 1

def contains_some_elements_from_set(l,set):
    "Check if all elements of *set* are present in *l* ."
    for x in set:
        if x in l:
            return 1
    return 0

def remove_set(l,set):
    "Remove all elements of *set* from *l* ."
    for x in set:
        if x in l:
            l.remove(x)
    return l

def find_sequence(l,s):
    """Searches the subsequence s in the sequence l (len(l)>=len(s)).
  Index of the first occurence is returned, otherwise *None* is returned.
  """
    if len(s)<=len(l):
        for i in range(len(l)-len(s)+1):
            if l[i:i+len(s)]==s:
                return i
    return None

def remove_sequence(l,s):
    """Removes the subsequence s from the sequence l (if the subsequence is present).
  The result is returned.
  """
    i=find_sequence(l,s)
    if i is not None:
        return l[:i] + l[i+len(s):]
    return l
