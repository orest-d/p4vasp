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


import _cp4vasp
import cp4vasp
import p4vasp.util
import p4vasp.Structure
import p4vasp.Array
from types import *
from p4vasp.cmatrix import *

dummy_pointers=[]
dummy_cstr=cp4vasp.Structure()
PySwigObjectType=type(dummy_cstr.this)

def save_dummy_pointer(x):
#  dummy_pointers.append(x)
#  print "dummy pointers:",dummy_pointers
    pass

def extractPointer(x):
#  print "Extract pointer",x
#  while type(x) is not StringType:
    while type(x) is not PySwigObjectType:
#    print "  extract",x
        s=x.this
        x.thisown=0
        del x
        x=s
#  print "  ----->",x

    return x

class AtomtypesRecord(cp4vasp.AtomtypesRecord,p4vasp.Structure.AtomtypesRecord):
    _keys_=map(intern,["element",
                       "atomspertype",
                       "mass",
                       "valence",
                       "pseudopotential",
                       "radius",
                       "covalent",
                       "n",
                       "red",
                       "green",
                       "blue"])


    def __init__(self,init=None,pointer=None):
        if isinstance(init,p4vasp.Structure.AtomtypesRecord):
            self.this = extractPointer(_cp4vasp.new_AtomtypesRecord())
            self.thisown=1
            self.setAtomtypesRecord(init)
        elif pointer:
            self.this=pointer
            self.thisown=0
        else:
            self.this = extractPointer(_cp4vasp.new_AtomtypesRecord())
            self.thisown = 1

    def getFields(self):
        "Return the list of supported fields."
        return self._keys_

    def clone(self):
        "Returns a copy of *self* ."
        val=AtomtypesRecord(pointer=_cp4vasp.AtomtypesRecord_clone(self.this))
        val.thisown=1
        return val

    __setmethods__ = {}
    for _s in []: __setmethods__.update(_s.__setmethods__)
    __setmethods__.update({
        "hash"            : _cp4vasp.AtomtypesRecord_hash_set,
        "atomspertype"    : _cp4vasp.AtomtypesRecord_atomspertype_set,
        "mass"            : _cp4vasp.AtomtypesRecord_mass_set,
        "valence"         : _cp4vasp.AtomtypesRecord_valence_set,
        "radius"          : _cp4vasp.AtomtypesRecord_radius_set,
        "covalent"        : _cp4vasp.AtomtypesRecord_covalent_set,
        "n"               : _cp4vasp.AtomtypesRecord_n_set,
        "red"             : _cp4vasp.AtomtypesRecord_red_set,
        "green"           : _cp4vasp.AtomtypesRecord_green_set,
        "blue"            : _cp4vasp.AtomtypesRecord_blue_set,
        "element"         : _cp4vasp.AtomtypesRecord_setElement,
        "hidden"          : _cp4vasp.AtomtypesRecord_hidden_set,
        "selected"        : _cp4vasp.AtomtypesRecord_selected_set,
        "pp_type"         : _cp4vasp.AtomtypesRecord_setPPType,
        "pp_specie"       : _cp4vasp.AtomtypesRecord_setPPSpecie,
        "pp_version"      : _cp4vasp.AtomtypesRecord_setPPVersion,
        "pseudopotential" : _cp4vasp.AtomtypesRecord_setPseudopotential
    })

    def __setattr__(self,name,value):
        if (name in ("this","thisown","_keys_")): self.__dict__[name] = value; return
        method = AtomtypesRecord.__setmethods__.get(name,None)
        if method: return method(self.this,value)
        self.__dict__[name] = value

    __getmethods__ = {}
    for _s in []: __getmethods__.update(_s.__getmethods__)
    __getmethods__.update({
        "hash"            : _cp4vasp.AtomtypesRecord_hash_get,
        "atomspertype"    : _cp4vasp.AtomtypesRecord_atomspertype_get,
        "mass"            : _cp4vasp.AtomtypesRecord_mass_get,
        "valence"         : _cp4vasp.AtomtypesRecord_valence_get,
        "radius"          : _cp4vasp.AtomtypesRecord_radius_get,
        "covalent"        : _cp4vasp.AtomtypesRecord_covalent_get,
        "n"               : _cp4vasp.AtomtypesRecord_n_get,
        "red"             : _cp4vasp.AtomtypesRecord_red_get,
        "green"           : _cp4vasp.AtomtypesRecord_green_get,
        "blue"            : _cp4vasp.AtomtypesRecord_blue_get,
        "element"         : _cp4vasp.AtomtypesRecord_getElement,
        "hidden"          : _cp4vasp.AtomtypesRecord_hidden_get,
        "selected"        : _cp4vasp.AtomtypesRecord_selected_get,
        "pp_type"         : _cp4vasp.AtomtypesRecord_getPPType,
        "pp_specie"       : _cp4vasp.AtomtypesRecord_getPPSpecie,
        "pp_version"      : _cp4vasp.AtomtypesRecord_getPPVersion,
        "pseudopotential" : _cp4vasp.AtomtypesRecord_getPseudopotential
    })

    def __getattr__(self,name):
        method = AtomtypesRecord.__getmethods__.get(name,None)
        if method: return method(self.this)
        raise AttributeError,name

    def __len__(self):return len(self._keys_)

    def __getitem__(self,i):
        if (type(i) is IntType):
            i=self._keys_[i]
        method = AtomtypesRecord.__getmethods__.get(i,None)
        if method: return method(self.this)
        raise IndexError,i

    def __setitem__(self,i,value):
        if (type(i) is IntType):
            i=self._keys_[i]
        method = AtomtypesRecord.__setmethods__.get(i,None)
        if method: return method(self.this,value)
        raise AttributeError,name

    def __str__(self):
        s="cAtomtypesRecord{\n"
        for x in self.getFields():
            s+="  %-10s = %s\n"%(x,str(self[x]))
        s+="}\n"
        return s

    def __repr__(self):
        return "<C AtomtypesRecord instance at %s>" % (self.this,)

    def setAtomtypesRecord(self,a):
        if isinstance(a,cp4vasp.AtomtypesRecord):
            _cp4vasp.AtomtypesRecord_setAtomtypesRecord(self.this,a)
        elif isinstance(a,p4vasp.Structure.AtomtypesRecord):
            f=a.getFields();
            for x in self.getFields():
                if x in f:
                    self[x]=a[x]
        else:
            raise TypeError,a
    def __del__(self, destroy= _cp4vasp.delete_AtomtypesRecord):
        try:
            if self.thisown:
#          print "del AtomtypesRecord",self.this
                destroy(self.this)
                save_dummy_pointer(self.this)
        except: pass

class AtomInfo(cp4vasp.AtomInfo,p4vasp.Structure.AtomInfo):
    element=None
    help_record=AtomtypesRecord()
    def __init__(self,init=None,pointer=None):
        if pointer:
            self.this = pointer
            self.thisown = 0
        elif isinstance(init,p4vasp.Structure.AtomInfo):
            self.this = extractPointer(_cp4vasp.new_AtomInfo(0))
            self.thisown = 1
            self.setAtomInfo(init)
        elif type(init) is IntType:
            self.this = extractPointer(_cp4vasp.new_AtomInfo(init))
            self.thisown = 1
        elif type(init) in StringTypes:
            self.this = extractPointer(_cp4vasp.new_AtomInfo(0))
            self.thisown = 1
            ai=p4vasp.Structure.AtomInfo(init)
            self.setAtomInfo(ai)
        elif init:
            self.this = extractPointer(_cp4vasp.new_AtomInfo(0))
            self.thisown = 1
            self.readFromNode(init)
        else:
            self.this = extractPointer(_cp4vasp.new_AtomInfo(10))
            self.thisown = 1

    def setAtomInfo(self,a):
        if isinstance(a,cp4vasp.AtomInfo):
            _cp4vasp.AtomInfo_setAtomInfo(self.this,extractPointer(a))
        elif isinstance(a,p4vasp.Structure.AtomInfo):
            self.allocate(len(a))
            for i in range(len(a)):
                self.setRecord(i,a[i])
        else:
#        print "cStructure.setAtomInfo",a
            raise TypeError,a

    def __delitem__(self,i):
        self.delitem(i)

    def append(self,value):
        if isinstance(value,cp4vasp.AtomtypesRecord):
            _cp4vasp.AtomInfo_append(self.this,value)
        elif isinstance(value,p4vasp.Structure.AtomtypesRecord):
            value=AtomtypesRecord(value)
            _cp4vasp.AtomInfo_append(self.this,value)
        else:
            raise TypeError,value

    def extend(self,l):
        "Calls *self.append()* for every element of *l* ."
        for x in l:
            self.append(x)

    def getRecord(self,i):
        return AtomtypesRecord(pointer=extractPointer(_cp4vasp.AtomInfo_getRecord(self.this,i)))

    def setRecord(self,i,value):
        """Set the record *i* to *value* .
  Performs value conversion, if necessary.
        """
        if isinstance(value,cp4vasp.AtomtypesRecord):
            _cp4vasp.AtomInfo_setRecord(self.this,i,value)
        elif isinstance(value,p4vasp.Structure.AtomtypesRecord):
            self.help_record.setAtomtypesRecord(value)
            _cp4vasp.AtomInfo_setRecord(self.this,i,self.help_record.this)
        else:
            raise TypeError,value

    def __repr__(self):
        return "<C AtomInfo instance at %s>" % (self.this,)


    __getmethods__ = {}
    for _s in []: __getmethods__.update(_s.__getmethods__)
    __getmethods__.update({
        "types"           : _cp4vasp.AtomInfo_types_get,
        "allocation_step" : _cp4vasp.AtomInfo_allocation_step_get,
        "Natoms"          : _cp4vasp.AtomInfo_getNatoms
    })

    def __len__(self):
        return int(self.types)

    def __getattr__(self,name):
        if name=="atomspertype":
            return map(lambda x:x.atomspertype,self)
        else:
            method = AtomInfo.__getmethods__.get(name,None)
            if method: return method(self.this)
            raise AttributeError,name

    def __getitem__(self,i):
        return self.getRecord(i)
    def __setitem__(self,i,value):
        self.setRecord(i,value)

    def readFromNode(self,elem):
        "Read the *AtomInfo* from the xml element node."
        self.element=elem
        a=p4vasp.Structure.AtomtypesArray(
          p4vasp.util.getChildrenByTagName(elem,"array",name="atomtypes")[0])
        self.allocate(len(a))
        for i in range(len(a)):
            self.setRecord(i,a.getRecord(i))

    def setFieldContent(self,field,l):
        """Set content of one *field* (specified by field name or index),
    *l* is the list of values. When the *len(l)* != *len(self)* ,
    then min(len(l),len(self)) values are set.
        """
        if field in AtomtypesRecord._keys_:
            for i in range(0,min(len(self),len(l))):
                self.data[i][field] = l[i]
        else:
            raise AttributeError,field

    def fillAttributesWithTable(self,table):
        """
        Fills array with following attributes:

          * mass

          * radius

          * covalent

          * red

          * green

          * blue

        Table must be an AtomInfo or AtomtypesArray and it must contain
        all those attributes.
        """

        if isinstance(table,cp4vasp.AtomInfo):
            _cp4vasp.AtomInfo_fillAttributesWithTable(self.this,table)
        else:
            for i in range(0,len(self)):
                dr=self[i]
                dt=table.getRecordForElementSafe(dr.element,i)
                dr.mass     = dt.mass
                dr.radius   = dt.radius
                dr.covalent = dt.covalent
                dr.red      = dt.red
                dr.green    = dt.green
                dr.blue     = dt.blue

    def __del__(self, destroy= _cp4vasp.delete_AtomInfo):
#      print "del AtomInfo",self.this,self.thisown
        try:
            if self.thisown: destroy(self.this)
        except: pass

class SelectiveArrayItemWrapper:
    """Array wrapper needed for simulating Structure.selective.
  This simulates one item of SelectiveArrayWrapper (3d integer-valued vector)
    """
    def __init__(self,s,n):
        self.s=s
        self.n=n
    def __len__(self):
        return 3
    def __getitem__(self,i):
        return self.s.getSelectiveDOF(self.n*3+i)
    def __setitem__(self,i,value):
        self.s.setSelectiveDOF(self.n*3+1,value)
    def __repr__(self):
        return "[%d,%d,%d]"%(self[0],self[1],self[2])
    __str__=__repr__

class SelectiveArrayWrapper:
    """Array wrapper needed for simulating Structure.selective
  This simulates array of 3d integer-valued vectors.
    """

    def __init__(self,s):
        self.s=s
    def __len__(self):
        return len(self.s)
    def __getitem__(self,i):
        return SelectiveArrayItemWrapper(self.s,i)
    def __setitem__(self,i,v):
        if len(v)>3:
            print "Warning: len(v)=%d in SelectiveArrayWrapper.__setitem__"%len(v)
        s=self.s
        s.setSelectiveDOF(3*i+0,v[0])
        s.setSelectiveDOF(3*i+1,v[1])
        s.setSelectiveDOF(3*i+2,v[2])
    def __repr__(self):
        s="[\n"
        for i in range(len(self)):
            s+="  "+repr(self[i])+",\n"
        s+="]\n"
        return s
    __str__=__repr__


class Structure(p4vasp.Structure.Structure):
    def __init__(self,init=None,pointer=None):
        if isinstance(init,p4vasp.Structure.Structure):
            self.this    = extractPointer(_cp4vasp.new_Structure())
            self.thisown = 1
            self.setStructure(init)
        elif type(init) in (StringType,UnicodeType,FileType):
            self.this    = extractPointer(_cp4vasp.new_Structure())
            self.thisown = 1
            self.read(init)
        elif init:
            self.this    = extractPointer(_cp4vasp.new_Structure())
            self.thisown = 1
            self.readFromNode(init)
        elif pointer:
            self.this=pointer
            self.thisown=0
        else:
            self.this    = extractPointer(_cp4vasp.new_Structure())
            self.thisown = 1
#        cp4vasp.Structure.__init__(self)

    def readFromNode(self,elem,atominfo=0):
        self.element=elem
        self.setStructure(p4vasp.Structure.Structure(elem,atominfo))

    def read(self,f):
        if (type(f) is StringType):
            _cp4vasp.Structure_read(self.this,f)
        else:
            _cp4vasp.Structure_parse(self.this,f.read())

    def write(self,f):
        if (type(f) is StringType):
            _cp4vasp.Structure_write(self.this,f)
        else:
            f.write(self.toString())

    def updateRecipBasis(self):
        return _cp4vasp.Structure_updateRecipBasis(self.this)

    def dir2cart(self,v):
        dest=Vector()
        if not isCVector(v):
            v=Vector(v)
        _cp4vasp.Structure_dir2cart(self.this,dest.pointer,v.pointer)
        return dest

    def cart2dir(self,v):
        dest=Vector()
        if not isCVector(v):
            v=Vector(v)
        _cp4vasp.Structure_cart2dir(self.this,dest.pointer,v.pointer)
        return dest

    def dirVectorToUnitCell(self,v):
        dest=Vector()
        if not isCVector(v):
            v=Vector(v)
        _cp4vasp.Structure_dirVectorToUnitCell(self.this,dest.pointer,v.pointer)
        return dest

    def dirVectorToCenteredUnitCell(self,v):
        dest=Vector()
        if not isCVector(v):
            v=Vector(v)
        _cp4vasp.Structure_dirVectorToCenteredUnitCell(self.this,dest.pointer,v.pointer)
        return dest

    def cartVectorToUnitCell(self,v):
        dest=Vector()
        if not isCVector(v):
            v=Vector(v)
        _cp4vasp.Structure_cartVectorToUnitCell(self.this,dest.pointer,v.pointer)
        return dest

    def cartVectorToCenteredUnitCell(self,v):
        dest=Vector()
        if not isCVector(v):
            v=Vector(v)
        _cp4vasp.Structure_cartVectorToCenteredUnitCell(self.this,dest.pointer,v.pointer)
        return dest

    def vectorToUnitCell(self,v):
        dest=Vector()
        if not isCVector(v):
            v=Vector(v)
        _cp4vasp.Structure_vectorToUnitCell(self.this,dest.pointer,v.pointer)
        return dest

    def vectorToCenteredUnitCell(self,v):
        dest=Vector()
        if not isCVector(v):
            v=Vector(v)
        _cp4vasp.Structure_vectorToCenteredUnitCell(self.this,dest.pointer,v.pointer)
        return dest

    def mindistCartVectors(self,a,b):
        if not isCVector(a):
            a=Vector(a)
        if not isCVector(b):
            b=Vector(b)
        return _cp4vasp.Structure_mindistCartVectors(self.this,a.pointer,b.pointer)

    def mindistDirVectors(self,a,b):
        if not isCVector(a):
            a=Vector(a)
        if not isCVector(b):
            b=Vector(b)
        return _cp4vasp.Structure_mindistDirVectors(self.this,a.pointer,b.pointer)

    def setStructure(self,s):
        if isinstance(s,cp4vasp.Structure):
            _cp4vasp.Structure_setStructure(self.this,s)
        elif isinstance(s,p4vasp.Structure.Structure):
            self.info.setAtomInfo(s.info)
            self.scaling=s.scaling
            self.basis[0]=s.basis[0]
            self.basis[1]=s.basis[1]
            self.basis[2]=s.basis[2]
            self.updateRecipBasis()
            if s.coordinates:
                self.coordinates=s.coordinates
            else:
                self.coordinates="Direct"
            if s.comment:
                self.comment=str(s.comment)
            else:
                self.comment=""

            self.allocate(len(s))
            for i in range(len(s)):
                self[i]=s[i]
            sel=s.selective
            if s.isSelective():
                self.setSelective(1)
                for i in range(len(s)):
                    v=sel[i]
                    self.setSelectiveDOF(3*i+0,v[0])
                    self.setSelectiveDOF(3*i+1,v[1])
                    self.setSelectiveDOF(3*i+2,v[2])

    def getNumberOfSpecies(self):
        return _cp4vasp.Structure_getNumberOfSpecies(self.this)

    def getRecord(self,i):
        val = apply(_cp4vasp.Structure_getRecord,args)
        if val: val = AtomtypesRecordPtr(val)
        return val

    __setmethods__ = {}
    for _s in []: __setmethods__.update(_s.__setmethods__)
    __setmethods__.update({
        "comment"         : _cp4vasp.Structure_comment_set,
        "coordinates"     : _cp4vasp.Structure_coordinates_set,
        "scaling_flag"    : _cp4vasp.Structure_scaling_flag_set,
        "allocation_step" : _cp4vasp.Structure_allocation_step_set,
    })
    def __setattr__(self,name,value):
        if (name == "this") or (name == "thisown"): self.__dict__[name] = value; return

        if name=="scaling":
            if len(value)==1:
                self.scaling_flag=1
                self.setScaling(0,value[0])
            else:
                self.scaling_flag=3
                self.setScaling(0,value[0])
                self.setScaling(1,value[1])
                self.setScaling(2,value[2])
            return
        method = Structure.__setmethods__.get(name,None)
        if method: return method(self.this,value)
        self.__dict__[name] = value

    __getmethods__ = {}

    for _s in []: __getmethods__.update(_s.__getmethods__)
    __getmethods__.update({
        "scaling_flag"          : _cp4vasp.Structure_scaling_flag_get,
        "scaling"               : _cp4vasp.Structure_scaling_get,
        "basis"                 : lambda x: Matrix(pointer=_cp4vasp.Structure_basis_get(x),isref=1),
        "rbasis"                : lambda x: Matrix(pointer=_cp4vasp.Structure_rbasis_get(x),isref=1),
        "total_number_of_atoms" : _cp4vasp.Structure_total_number_of_atoms_get,
        "allocated"             : _cp4vasp.Structure_allocated_get,
        "allocation_step"       : _cp4vasp.Structure_allocation_step_get,
        "info"                  : lambda x : AtomInfo(pointer=_cp4vasp.Structure_info_get(x).this),
        "comment"               : _cp4vasp.Structure_comment_get,
        "coordinates"           : _cp4vasp.Structure_coordinates_get,
    })
    def __getattr__(self,name):
        if name=="Natoms":
            return self.info.Natoms
        if name=="atomspertype":
            return self.info.atomspertype
        if name=="selective":
            return self.getselective_()
        if name=="scaling":
            v=Vector(pointer=_cp4vasp.Structure_scaling_get(self.this),isref=1)
            if self.scaling_flag==3:
                return v
            elif self.scaling_flag==1:
                return [v[0]]
            else:
                return None
        method = Structure.__getmethods__.get(name,None)
        if method:
            return method(self.this)
        raise AttributeError,name

    def setSelective(self,flag):
        return _cp4vasp.Structure_setSelective(self.this,flag)

    def getselective_(self):
        if self.isSelective():
            return SelectiveArrayWrapper(self)
        else:
            return None

    def __repr__(self):
        return "<C Structure instance at %s>" % (self.this,)

    def __len__(self):
        return int(_cp4vasp.Structure_len(self.this))

    def __getitem__(self,i):
        return Vector(pointer=_cp4vasp.Structure_get(self.this,i),isref=1)
    def __setitem__(self,i,v):
        _cp4vasp.Structure_set(self.this,i,v[0],v[1],v[2])

    def __delitem__(self,i):
        self.delitem(i)

    def append(self,v):
        _cp4vasp.Structure_append(self.this,v[0],v[1],v[2])
    def extend(self,l):
        for x in l:
            self.append(x)

    def toString(self):
        return _cp4vasp.Structure_toString(self.this)

    def parse(self,s):
        return _cp4vasp.Structure_parse(self.this,s)

    def isSelective(self):
        return _cp4vasp.Structure_isSelective(self.this)
    def isCarthesian(self):
        return _cp4vasp.Structure_isCarthesian(self.this)
    def isDirect(self):
        return _cp4vasp.Structure_isDirect(self.this)
    def getSelectiveDOF(self,i):
        return _cp4vasp.Structure_getSelectiveDOF(self.this,i)
    def setSelectiveDOF(self,i,j):
        return _cp4vasp.Structure_setSelectiveDOF(self.this,i,j)
    def __del__(self, destroy= _cp4vasp.delete_Structure):
        try:
            if self.thisown:
#         print "del cStructure"
                destroy(self.this)
                save_dummy_pointer(self.this)
        except: pass

    def getRecipBasis(self):
        return _cp4vasp.Structure_getRecipBasis(self.this)
    def forceConvertToCarthesian(self):
        return _cp4vasp.Structure_forceConvertToCarthesian(self.this)
    def forceConvertToDirect(self):
        return _cp4vasp.Structure_forceConvertToDirect(self.this)
    def setCarthesian(self,flag=1):
        return _cp4vasp.Structure_setCarthesian(self.this,flag)
    def setDirect(self,flag=1):
        return _cp4vasp.Structure_setDirect(self.this,flag)
    def toUnitCell(self):
        return _cp4vasp.Structure_toUnitCell(self.this)
    def toCenteredUnitCell(self):
        return _cp4vasp.Structure_toCenteredUnitCell(self.this)
    def createMindistMatrix(self):
        return _cp4vasp.Structure_createMindistMatrix(self.this)
    def deleteMindistMatrix(self):
        return _cp4vasp.Structure_deleteMindistMatrix(self.this)
    def getMindist(self,i,j):
        return _cp4vasp.Structure_getMindist(self.this,i,j)
    def clean(self):
        return _cp4vasp.Structure_clean(self.this)
    def clone(self):
        return Structure(pointer=_cp4vasp.Structure_clone(self.this))
    def len(self):
        return _cp4vasp.Structure_len(self.this)
    def get(self,i):
        return _cp4vasp.Structure_get(self.this,i)
    def set(self,i,x,y=None,z=None):
        if y is None:
            return _cp4vasp.Structure_set(self.this,x[0],x[1],x[2])
        else:
            return _cp4vasp.Structure_set(self.this,x,y,z)
    def allocate(self,n):
        return _cp4vasp.Structure_allocate(self.this,n)
    def realloc(self,n):
        return _cp4vasp.Structure_realloc(self.this,n)
    def delitem(self,i):
        return _cp4vasp.Structure_delitem(self.this,i)
    def correctScaling(self):
        return _cp4vasp.Structure_correctScaling(self.this)
    def setScaling(self,i,x):
        return _cp4vasp.Structure_setScaling(self.this,i,x)
