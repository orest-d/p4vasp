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



from UserDict import *
from UserList import *
from string import *
from sys import *
from p4vasp.matrix import *
from p4vasp import *
from p4vasp.util import *
from p4vasp.Dictionary import *
from p4vasp.Array import *


try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

class AtomtypesRecord(ArrayRecord):
    """This is an ArrayRecord adapted to handle atomtypes more effectively.
  This defines three fake-attributes to access the *pseudopotential* field parts.
  The *pseudopotential* field contains three parts: type (e.g. PAW_GGA), specie (e.g. C_s),
  and version. These fields can be accessed using attributes *pp_type*, *pp_specie*
  and *pp_version* as it would be real fields (with the exception of the dictionary
  access).

  Alternatively the methods *getPPType()* , *getPPSpecie()* , *getPPVersion()* ,
  *setPPType()* , *setPPSpecie()* and *setPPVersion()* can be used for accessing
  the *pseudopotential* field parts.

   When the *pseudopotential* field can not be splitted to three parts,
  the missing parts are replaced by "?", this can be done by the method *touchPP()* .

    """
    def __init__(self,array,record=None):
        """Create new *ArrayRecord* .
        If record can be an instance of *AtomtypesRecord* , possibly from
        another *Array* than *array* . Fields are then translated according to
        field names. This could be used for conversion between different array-types.
        """
        if isinstance(record,AtomtypesRecord):
            ArrayRecord.__init__(self,array,None)
            self.setAtomtypesRecord(record)
        else:
            ArrayRecord.__init__(self,array,record)

        self.pp_index_=self.array_.fieldIndex("pseudopotential")

    def setAtomtypesRecord(self,a):
        if isinstance(a,AtomtypesRecord):
            f=a.getFields();
            for x in self.getFields():
                if x in f:
                    self[x]=f[x]
#    elif isinstance(init,cp4vasp.AtomtypesRecord):
#      cp4vaspc.AtomtypesRecord_setAtomtypesRecord(self,a)
        else:
            raise TypeError,a

    def getPPType(self):
        try:
            return split(self.record_[self.pp_index_])[0]
        except:
            return None
    def getPPSpecie(self):
        try:
            return split(self.record_[self.pp_index_])[1]
        except:
            return None
    def getPPVersion(self):
        try:
            return split(self.record_[self.pp_index_])[2]
        except:
            return None

    def touchPP(self):
        """Fill missing parts of the *pseudopotential* field with "?"."""
        v=split(self.record_[self.pp_index_])
        v+=["?"]*(3-len(v))
        self.record_[self.pp_index_]=join(v)

    def setPPType(self,value):
        v=split(self.record_[self.pp_index_])
        v+=["?"]*(3-len(v))
        v[0]=value
        self.record_[self.pp_index_]=join(v)

    def setPPSpecie(self,value):
        v=split(self.record_[self.pp_index_])
        v+=["?"]*(3-len(v))
        v[1]=value
        self.record_[self.pp_index_]=join(v)

    def setPPVersion(self,value):
        v=split(self.record_[self.pp_index_])
        v+=["?"]*(3-len(v))
        v[2]=value
        self.record_[self.pp_index_]=join(v)

    def __getattr__(self,attr):
        if attr in self.array_.field:
            return self.record_[self.array_.fieldIndex(attr)]
        elif attr=="pp_type":
            return self.getPPType()
        elif attr=="pp_specie":
            return self.getPPSpecie()
        elif attr=="pp_version":
            return self.getPPVersion()
        else:
            raise AttributeError(attr)

    def __setattr__(self,attr,value):
        if (attr in ["record_","array_","pp_index_"]):
            self.__dict__[attr]=value
        elif attr=="pp_type":
            self.setPPType(value)
        elif attr=="pp_specie":
            self.setPPSpecie(value)
        elif attr=="pp_version":
            self.setPPVersion(value)
        elif attr in self.array_.field:
            self.__dict__["record_"][self.array_.field.index(attr)]=value

class DefaultAtomtypesRecord:
    """This object is returned by default by the
  AtomtypesArray.getRocordForElementSafe() (or similar methods)
  when no suitable record is found.
  This should not happen in normal conditions.
  However it serves as backup defaults for atom colors and radii.
    """
    mass     = 0.0
    radius   = 1.0
    covalent = 1.0
    red      = 1.0
    green    = 1.0
    blue     = 1.0

class AtomtypesArray(Array):
    """This is a special array for keeping atomtypes.
  There is no counterpart for this object in the cStructure module,
  therefore it is recomended to use AtomInfo class rather than directly AtomtypesArray
  whenever possible.

  Usual fields are:

      || **index** || **field**        || **type**        ||
      ||  0        || atomspertype     || INT_TYPE        ||
      ||  1        || element          || STRING_TYPE     ||
      ||  2        || mass             || FLOAT_TYPE      ||
      ||  3        || valence          || FLOAT_TYPE      ||
      ||  4        || pseudopotential  || STRING_TYPE     ||

    """
    default_record = DefaultAtomtypesRecord()
    def __init__(self,data=[],name="atomtypes"):
        """Creates new AtomtypesArray the same way than the Array is.
    When using a python list as the *data* argument, usual fields are created automaticaly
    (including field types and formats of course).
        """
        Array.__init__(self,data,name=name)
        if isinstance(data,AtomtypesArray):
            self.setAtomtypesArray(a)
        elif type(data) is ListType:
            self.dimension=["type"]
            self.field=["atomspertype",
                        "element",
                        "mass",
                        "valence",
                        "pseudopotential"]
            self.type =[INT_TYPE,
                        STRING_TYPE,
                        FLOAT_TYPE,
                        FLOAT_TYPE,
                        STRING_TYPE]
            self.format=["%3d",
                         "%2s",
                         "%8.4f",
                         "%6.4f",
                         "%s"]
    def setAtomtypesArray(self,a):
        if a is None:
            self.dimension=["type"]
            self.field=["atomspertype",
                        "element",
                        "mass",
                        "valence",
                        "pseudopotential"]
            self.type =[INT_TYPE,
                        STRING_TYPE,
                        FLOAT_TYPE,
                        FLOAT_TYPE,
                        STRING_TYPE]
            self.format=["%3d",
                         "%2s",
                         "%8.4f",
                         "%6.4f",
                         "%s"]
        else:
#      print a
#      print a.dimension
#      print a.field
#      print a.type
#      print a.format
            self.dimension=a.dimension[:]
            self.field=a.field[:]
            self.type=a.type[:]
            self.format=a.format[:]
            self.data=[]
            for i in range(len(a)):
#        print i,a[i],a[i].getRecord()
                if isinstance(a[i],ArrayRecord):
                    self.data.append(a[i].getRecord()[:])
                else:
                    self.data.append(a[i][:])
#      self.data=map(lambda x:x[:],a.data)

    def setAtomtypesFormats(self):
        "Set default formats for usual fields."
        a=self
        a.setFormatForField("atomspertype",   "%3d")
        a.setFormatForField("element",        "%2s")
        a.setFormatForField("mass",           "%8.4f")
        a.setFormatForField("valence",        "%6.4f")
        a.setFormatForField("pseudopotential","%s")

    def getRecord(self,i):
        "Get record as *AtomtypesRecord*"
        return AtomtypesRecord(self,self[i])

    def getRecordForElement(self,x):
        "Get record with *element* = *x* ."
        x=strip(x)
        j=self.fieldIndex("element")
        d=self.data
        for i in range(0,len(self)):
            if strip(d[i][j])==x:
                return self.getRecord(i)
        return None

    def getRecordForElementSafe(self,x,i=0,m=-1):
        "Get record with *element* = *x* ."
        r=self.getRecordForElement(x)
        if r is not None: return r
        if m==-1 : m=len(self)
        if len(self)<m : m=len(self)
        if m<=0: return self.default_record
        return self[i%m]

    def __str__(self):
        return "Atomtypes"+Array.__str__(self)

    def allocate(self,i):
        """Allocate space for *i* number of fields. This erases all data."""
        r=AtomtypesRecord(self)
        self.data=map(lambda x:x[:],[r.getRecord()]*i)

    def setFieldContent(self,field,l):
        """Set content of one *field* (specified by field name or index),
    *l* is the list of values. When the *len(l)* != *len(self)* ,
    then min(len(l),len(self)) values are set.
        """
        if type(field) in StringTypes:
            field=self.fieldIndex(field)

        for i in range(0,min(len(self),len(l))):
            self.data[i][field] = l[i]


    def fillAttributesWithTable(self,table):
        """
    Update following attributes:

      * mass

      * radius

      * covalent

      * red

      * green

      * blue

    Table must be an AtomInfo or AtomtypesArray and it must contain
    all those attributes.
    If an element is not present in *self*, it is added from *table*.
        """
        if "mass" not in self.field:
            self.addField("mass",    FLOAT_TYPE,format="%8.4f",value=0.0)
        if "radius" not in self.field:
            self.addField("radius",  FLOAT_TYPE,format="%6.4f",value=0.0)
        if "covalent" not in self.field:
            self.addField("covalent",FLOAT_TYPE,format="%6.4f",value=0.0)
        if "red" not in self.field:
            self.addField("red",     FLOAT_TYPE,format="%6.4f",value=0.0)
        if "green" not in self.field:
            self.addField("green",   FLOAT_TYPE,format="%6.4f",value=0.0)
        if "blue" not in self.field:
            self.addField("blue",    FLOAT_TYPE,format="%6.4f",value=0.0)

        for i in range(0,len(self)):
            dr=self.getRecord(i)
            dt=table.getRecordForElementSafe(dr.element,i)
            dr.mass     = dt.mass
            dr.radius   = dt.radius
            dr.covalent = dt.covalent
            dr.red      = dt.red
            dr.green    = dt.green
            dr.blue     = dt.blue



class AtomInfo(ToXMLHelper):
    """This object contains informations about atoms.
  As most (presently all) irredundant information is contained in *self.atomtypes*
  *AtomtypesArray* , most of the methodes are just wrappers to this array.
  Also the (read only) attributes *types* , *atomspertype* and *Natoms* are calculated from
  the *atomtypes* array.

  The *types* attribute is the number of atom types ( *len(self.atomtypes)* ),
  *atomspertype* is the number of atoms per type ( *atomspertype* fields of *self.atomtypes* )
  and *Natoms* is the total number of atoms (sum of *atomspertype* ).
    """
    def __init__(self,init=None):
        """Create the *AtomInfo*
        Yhe init parameter can be:

          * *None* - creates an empty *AtomInfo* (default)

          * integer number - allocates space for *init* records

          * string - reads *AtomInfo* from file given by path *init* (xml format)

          * xml element - creates *AtomInfo* from xml element node.
        """
        self.atomtypes=AtomtypesArray()
        if init:
            if type(init) is IntType:
                self.allocate(init)
            elif type(init) in StringTypes:
                dom=parseXML(init)
                self.readFromNode(dom.getElementsByTagName("atominfo")[0])
            elif isinstance(init,AtomInfo):
                self.atomtypes.setAtomtypesArray(init.atomtypes)
            else:
                self.readFromNode(init)

    def readFromNode(self,elem):
        "Read the *AtomInfo* from the xml element node."
        self.element=elem
        self.atomtypes=AtomtypesArray(getChildrenByTagName(elem,"array",name="atomtypes")[0])

    def __getattr__(self,name):
        if name=="types":
            return len(self.atomtypes)
        elif name=="atomspertype":
            return map(lambda x,i=self.atomtypes.field.index("atomspertype"):x[i],self.atomtypes.data)
        elif name=="Natoms":
            return reduce(lambda x,y:x+y,self.atomspertype)
        if name=="default_record":
            return self.atomtypes.default_record
        else:
            raise AttributeError


    def getRecord(self,i):
        """Wrapper to *self.atomtypes.getRecord(i)* ."
    Get atomtype (as a *AtomtypesRecord* ) for specie *i* ."""
        return self.atomtypes.getRecord(i)

    def allocate(self,i):
        """Wrapper to *self.atomtypes.allocate(i)* .
    Allocate space for *i* number of fields. This erases all data."""
        return self.atomtypes.allocate(i)

    def setFieldContent(self,field,l):
        "Wrapper to *self.atomtypes.setFieldContent(field,l)* ."
        return self.atomtypes.setFieldContent(field,l)

    def speciesIndex(self,j):
        "If *j* is the atom index (starting from 0), return its number of specie (starting from 0)."
        a=self.atomspertype
        for i in range(0,len(a)):
            j-=a[i]
            if j<0:
                return i
        return None
    def firstAtomIndexForSpecie(self,j):
        "If *j* is the specie index (starting from 0), return the index of the first atom of this specie."
        if j==0:
            return 0
        return reduce(lambda x,y:x+y,self.atomspertype[:j])
    def lastAtomIndexForSpecie(self,j):
        "If *j* is the specie index (starting from 0), return the index of the last atom of this specie increased by one."
        l=self.atomspertype[:(j+1)]
        if len(l)==0:
            return 0
        if len(l)==1:
            return l[0]
        return reduce(lambda x,y:x+y,l)
    def findRecordIndexContaining(field,value):
        "Find index of a record, that fullfills *record.field==value* ."
        for i in range(len(self)):
            if self[i][field]==value:
                return i
        return None
    def findRecordContaining(field,value):
        "Find index of a record, that fullfills *record.field==value* ."
        for r in self.atomtypes:
            if r[field]==value:
                return r
        return None

    def getRecordForAtom(self,i):
        "Get atomtype (as a *AtomtypesRecord* ) for atom *i* ."
        return self.atomtypes.getRecord(self.speciesIndex(i))

    def createAtomsArray(self,fields=["element","atomtype"]):
        """Create an array containing atomtype for every atom. Fields can be specified.
    The field *atomtype* would containt *atomtype* ( *specie* ) index.
    This is used by *writexml* method.
        """
        a=Array(name="atoms")
        a.dimension=["ion"]
        a.field=fields
        a.type=[]
        for x in a.field:
            if x in self.atomtypes.field:
                a.type.append(self.atomtypes.getFieldType(x))
            elif x=="atomtype":
                a.type.append(INT_TYPE)
            else:
                raise "Unknown field '%s'."%x
        for i in range(0,self.Natoms):
            r=ArrayRecord(a)
            ai=self.speciesIndex(i)
            t=self.getRecord(ai)
            for x in fields:
                if x=="atomtype":
                    r.atomtype=ai+1
                else:
                    r[x]=t[x]
            a.append(r.getRecord())
        return a

    def downscale(self,factor):
        """Reduce the number all atom types by given factor.
    This can be used e.g. when reducing a supercell atominfo to a primitive cell."""
        for i in range(len(self)):
            self[i].atomspertype=self[i].atomspertype/factor

    def writexml(self,f,indent=0,extended=0):
        """Write in xml representation to a file *f*, indented by *indent* (integer).
    When *extended* is true, write also redundant informations.
        """
        in0  =indent*INDENT
        in1 =(indent+1)*INDENT
        f.write('%s<atominfo>\n'%in0)
        if extended:
            f.write('%s<atoms> %d </atoms>\n'%(in1,self.Natoms))
            f.write('%s<types> %s </types>\n'%(in1,join(map(str,self.atomspertype))))
            a=self.createAtomsArray()
            a.format=["%2s","%3d"]
            a.name="atoms"
            a.writexml(f,indent+1,rcmode=1)
        self.atomtypes.writexml(f,indent+1,rcmode=1)

        f.write('%s</atominfo>\n'%in0)

    def __len__(self):
        "Count of atomtypes records."
        return len(self.atomtypes)
    def __getitem__(self,i):
        "Wrapper to *self.atomtypes.getRecord(i)* ."
        return self.atomtypes.getRecord(i)
    def __setitem__(self,i,value):
        """Wrapper to *self.setRecord(i,value)* ."
        """
        if isinstance(value,ArrayRecord):
            self.atomtypes[i]=value.getRecord()[:]
        else:
            self.atomtypes[i]=value
    def __delitem__(self,i):
        del self.atomtypes[i]

    def setRecord(self,i,value):
        """Set the record *i* to *value* .
    Performs value conversion, if necessary.
        """
        if isinstance(value,ArrayRecord):
            if value.getArray() is not self.atomtypes:
                value=AtomtypesRecord(self.atomtypes,value)
            self.atomtypes[i]=value.getRecord()[:]
        else:
            self.atomtypes[i]=value

    def allocate(self,i):
        """Allocate space for *i* number of fields. This erases all data."""
        self.atomtypes.allocate(i)

    def append(self,value):
        """Wrapper to *self.atomtypes.append()* .
    The *getRecord()* is applied to *ArrayRecord* *value* before storing.
        """
        ar
        if isinstance(value,ArrayRecord):
            self.atomtypes.append(value.getRecord())
        else:
            self.atomtypes.append(value)

    def appendEmpty(self):
        """Creates an empty record at the end of the table and returns it back.
        """
        ar=ArrayRecord(self.atomtypes)
        self.atomtypes.append(ar)
        return ar

    def extend(self,l):
        "Calls *self.append()* for every element of *l* ."
        for x in l:
            self.append(x)

    def getRecordForElement(self,x):
        "Get record with *element* = *x* ."
        return self.atomtypes.getRecordForElement(x)

    def getRecordForElementSafe(self,x,i=0,m=-1):
        "Get record with *element* = *x* ."
        return self.atomtypes.getRecordForElementSafe(x,i,m)
    def removeRecordsWithZeroAtomspertype(self):
        "Removes records with atomspertype==0."
        index=self.atomtypes.fieldIndex("atomspertype")
        if index is not None:
            i=0
            a=self.atomtypes
            while i<len(a):
                if a[i][index]:
                    i+=1
                else:
                    del a[i]

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
        self.atomtypes.fillAttributesWithTable(table)

    def updateAttributes(self,table):
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
        a=self.atomtypes
        if "mass" not in a.field:
            a.addField("mass",    FLOAT_TYPE,format="%8.4f",value=0.0)
        if "radius" not in a.field:
            a.addField("radius",  FLOAT_TYPE,format="%6.4f",value=0.0)
        if "covalent" not in a.field:
            a.addField("covalent",FLOAT_TYPE,format="%6.4f",value=0.0)
        if "red" not in a.field:
            a.addField("red",     FLOAT_TYPE,format="%6.4f",value=0.0)
        if "green" not in a.field:
            a.addField("green",   FLOAT_TYPE,format="%6.4f",value=0.0)
        if "blue" not in a.field:
            a.addField("blue",    FLOAT_TYPE,format="%6.4f",value=0.0)

        for i in range(0,len(table)):
            dt=table.getRecord(i)
            dr=self.getRecordForElement(dt.element)
            if dr is None:
                dr=self.appendEmpty()
                dr.element=dt.element
            dr.mass     = dt.mass
            dr.radius   = dt.radius
            dr.covalent = dt.covalent
            dr.red      = dt.red
            dr.green    = dt.green
            dr.blue     = dt.blue

class Structure(ToXMLHelper,Parseable,ToString):
    """This class can be used for keeping and manipulating the structural data.
  It can be read (and written) as a xml node as well as a POSCAR file.
  Thus it can be used to convert between the xml representation and classical POSCAR files.
  Different transformation routines are defined here for cartheian/direct conversion,
  scaling, replication and so on.

  *Structure* can be treated as an array containing vectors ( *Vector* )
  with coordinates.

  Limitations:
  the scaling factors in POSCAR file are not implemented yet correctly.
    """
    def __init__(self,elem=None):
        """Create *Structure* .
    The *elem* parameter can be a xml element node, a file object containing POSCAR,  a path to a POSCAR
    or a Structure object.
        """
        self.info        = AtomInfo()
        self.basis       = VArray([Vector(1.0,0.0,0.0),Vector(0.0,1.0,0.0),Vector(0.0,0.0,1.0)])
        self.updateRecipBasis()
        self.positions   = VArray(name="positions")
        self.selective   = None
        self.coordinates = None
        self.comment     = ""
        self.name        = None
        self.scaling     = [1.0]
        if (type(elem) in StringTypes) or type(elem) is FileType:
            self.read(elem)
        elif isinstance(elem,Structure):
            self.setStructure(elem)
        elif elem is not None:
            self.readFromNode(elem)

    def readFromNode(self,elem,atominfo=0):
        """Read the *Structure* from a xml element node;
        *elem* is the source DOM element,
        *atominfo* can contain the AtomInfo instance, that will be stored in Structure.info.

        If *atominfo* is *0* or missing, parent nodes of *elem* are searched for
        AtomInfo records and it is read automatically.
        """
        self.element     = elem
        try:
            self.coordinates = elem.getAttribute("coordinates")
        except AttributeError:
            self.coordinates = None
        try:
            self.name        = elem.getAtrribute("name")
        except AttributeError:
            self.name = ""
        if atominfo==0:
            e=getInheritedElementsByTagName(elem,"atominfo")
            if len(e):
                self.info=AtomInfo(e[0])
        else:
            self.info=atominfo

        crystal=elem.getElementsByTagName("crystal")[0]
        self.basis       = VArray(crystal.getElementsByTagName("varray")[0])
        self.basis.convertToVector()

        try:
            v=VArray()
            v.readFromNodeFast(getChildrenByTagName(elem,"varray")[0])
            self.positions=v
        except:
            self.positions   = VArray(getChildrenByTagName(elem,"varray")[0])

        self.positions.convertToVector()
        s=getChildrenByTagName(elem,"varray",name="selective")
        if len(s):
            self.selective=VArray(s[0])

    def read(self,f="POSCAR",closeflag=0):
        """Read POSCAR from file *f* (file object or path).
        """
        import re

        if (type(f) == type("")):
            f = open(f,"r")
            closeflag = 1

        self.name="POSCAR"
        self.comment    = removeNewline(f.readline())
        s = removeNewline(f.readline())
        try:
            self.scaling    = map(float,split(s))
        except:
            raise ParseException('Error reading scaling factor(s). ("%s")' % s)

        for i in range(0,3):
            line = removeNewline(f.readline())
            s = split(line)
            try:
                self.basis[i] = Vector(float(s[0]),float(s[1]),float(s[2]))
            except:
                raise ParseException('Error parsing lattice vector %d.(%s)'%(i+1,line))

        s = removeNewline(f.readline())

        if (re.match("[\\s]*[a-zA-Z]",s) != None):
            types=s
            atom=split(s)
            if len(atom)!=len(self.info):
                self.info.allocate(len(atom))
            self.info.setFieldContent("element",atom)

            s = removeNewline(f.readline())
            try:
                atomspertype = map(int,split(s))
                if len(atomspertype)!=len(self.info):
                    self.info.allocate(len(atomspertype))
                self.info.setFieldContent("atomspertype",atomspertype)
            except:
                raise ParseException('Error reading the number of atoms per atomic species. ("%s")' % s)
        else:
            if len(strip(s))==0:
                s = removeNewline(f.readline())
#      try:
            atomspertype = map(int,split(s))
            if len(atomspertype)!=len(self.info):
                self.info.allocate(len(atomspertype))
            self.info.setFieldContent("atomspertype",atomspertype)
#      except:
#        raise ParseException('Error reading the number of atoms per atomic species. ("%s")' % s)

        s = strip(removeNewline(f.readline()))
        if (s==""):
            s="Direct"
#      raise ParseException('Empty line, where "Cartesian", "Direct" or "Selective" is expected.')

        if (upper(s[0])=="S"):
            s = removeNewline(f.readline())
            self.setSelective(1)
        else:
            self.selective = None
        if (s==""):
            raise ParseException('Empty line found, where "Cartesian" or "Direct" is expected')
        if (not (upper(s[0]) in ("C","K","D"))):
            raise ParseException('"Cartesian" or "Direct" expected, but "%s" found instead.'%s)

        if upper(s[0]) in ("C","K"):
            self.coordinates=s
        else:
            self.coordinates=None

        self.positions = VArray(name="positions")
        cl = 0
        for j in self.atomspertype:
            for i in range(0,j):
                cl = cl + 1
                line=f.readline()
                if (line==""):
                    raise ParseException('Missing coordinate line(s). (coord. line %d)'%(cl))
                s = split(line)

                try:
                    v = Vector(float(s[0]),float(s[1]),float(s[2]))
                    self.positions.append(v)
                except:
                    raise ParseException('Error parsing vector on coordinate line %d.(%s)'%(cl,line))

                if self.isSelective():
                    try:
                        self.selective.append(map(lambda x:upper(x) in ('T','.TRUE.'),s[3:6]))
                    except:
                        raise ParseException('Error parsing selection on coordinate line %d.(%s)'%(cl,line))

        if (closeflag):
            f.close()

    def write(self,f="POSCAR",newformat=1,closeflag=0):
        "Write POSCAR to file *f* (file object or path)."
        if (type(f) == type("")):
            f = open(f,"w+")
            closeflag = 1
        if self.comment:
            f.write(removeNewline(self.comment)+"\n")
        else:
            f.write("unknown system\n")
        f.write("%s\n"%join(map(str,self.scaling)," "))

        kv = self.basis
        f.write(str(kv[0])+"\n")
        f.write(str(kv[1])+"\n")
        f.write(str(kv[2])+"\n")
        if newformat:
            try:
                elems=""
                for x in self.info:
                    elems+=" "+x["element"]
                elems=strip(elems)
                if len(elems):
                    f.write(elems+"\n")
            except:
                msg().exception()
        f.write(" "+join(map(str,self.atomspertype))+"\n")
        if (self.isSelective()):
            f.write("Selective\n")

        if self.isCartesian():
            f.write(removeNewline(self.coordinates)+"\n")
        else:
            f.write("Direct\n")

        if (self.isSelective()):
            for i in range(0,len(self)):
                f.write(str(self[i])+" "+xmlrepr(self.selective[i],LOGICAL_TYPE)+"\n")
        else:
            for i in range(0,len(self)):
                f.write(str(self[i])+"\n")

        if (closeflag):
            f.close()


    def __getattr__(self,name):
        """Wrappers to *self.info.types* , *self.info.atomspertype* and *self.info.Natoms* are defined.

        types -- number of species,

        atomspertype -- array containing number of atom per specie for every specie,

        Natoms -- number of atoms, should be identical to len()

        """
        if name=="types":
            return self.info.types
        elif name=="atomspertype":
            return self.info.atomspertype
        elif name=="Natoms":
            return self.info.Natoms
        else:
            raise AttributeError(name)

    def __len__(self):
        "Returns the number of atoms."
        return len(self.positions)
    def __getitem__(self,i):
        "Returns the position *Vector* of atom *i* ."
        return self.positions[i]
    def __setitem__(self,i,v):
        "Sets the position of atom *i* to *v* . Argument *v* is converted to *Vector* if necessary."
        if isinstance(v,Vector):
            self.positions[i]=v
        else:
            self.positions[i]=Vector(v[0],v[1],v[2])
    def __delitem__(self,i):
        "Deletes the position *Vector* of atom *i* ( wrapper to removeAtom(i) )."
        #del self.positions[i]
        self.removeAtom(i)

    def append(self,v):
        "Appends *v* to positions. Argument *v* is converted to *Vector* if necessary."
        if isinstance(v,Vector):
            self.positions.append(v)
        else:
            self.positions.append(Vector(v[0],v[1],v[2]))
        self.selective.append([0,0,0])
    def extend(self,l):
        """Extends positions with the list *l* .
    List is converted to a listo of *Vector* s if necessary.
    """
        self.positions.extend(map(Vector,l))
        for i in range(0,len(self.positions)-len(self.selective)):
            self.selective.append([0,0,0])

    def getCellVolume(self):
        "Returns the volume of the unit cell"
        v=self.basis[0].cross(self.basis[1])
        return abs(v*self.basis[2])

    def speciesIndex(self,i):
        """Wrapper to *self.info.speciesIndex(i)*
    If *i* is the atom index (starting from 0), return its number of specie (starting from 0)."""
        return self.info.speciesIndex(i)
    def getRecord(self,i):
        """Wrapper to *self.info.getRecord(i)*
    Get atomtype (as a *AtomtypesRecord* ) for specie *i* ."""
        return self.info.getRecord(i)
    def getRecordForAtom(self,i):
        """Wrapper to *self.info.getRecordForAtom(i)*
    Get atomtype (as a *AtomtypesRecord* ) for atom *i* ."""
        return self.info.getRecordForAtom(i)
    def updateRecipBasis(self,l=None):
        """Calculate reciprocal basis from the direct basis.
    Returns the *VArray* with the new basis.
    The parameter *l* specifies the direct basis for conversion. If *None* , the *self.basis* is used.
        """
        if l is None:
            l=self.basis

        Omega=l[0]*(l[1].cross(l[2]))
        b0=1.0/Omega*(l[1].cross(l[2]))
        b1=1.0/Omega*(l[2].cross(l[0]))
        b2=1.0/Omega*(l[0].cross(l[1]))

        self.rbasis=VArray([b0,b1,b2],name="rec_basis")
        return self.rbasis

    def forceConvertToCartesian(self):
        return self.forceConvertToCartesian()
    def forceConvertToCartesian(self):
        """Perform the conversion from direct to cartesian coordinates,
    even if the *Structure* is in cartesian coordinates. The coordinates flag remains unchanged."""

        for i in range(0,len(self)):
            w = (self.basis[0]*self[i][0])+\
                (self.basis[1]*self[i][1])+\
                (self.basis[2]*self[i][2])
            self[i] = w

    def forceConvertToDirect(self):
        """Perform the conversion from cartesian to direct coordinates,
    even if the *Structure* is in direct coordinates. The coordinates flag remains unchanged."""
        rbasis=self.updateRecipBasis()

        for i in range(0,len(self)):
            v=self[i]
            self[i] = Vector(v*rbasis[0],v*rbasis[1],v*rbasis[2])

    def isSelective(self):
        "Returns true if the *Structure* contains selection flags."
        return self.selective is not None

    def isCartesian(self):
        return self.isCarthesian()

    def isCarthesian(self):
        "Returns true if the *Structure* is in cartesian coordinates."
        if self.coordinates:
            if len(self.coordinates):
                return lower(self.coordinates[0]) in ("c","k")
        return 0
    def isDirect(self):
        "Returns true if the *Structure* is in direct coordinates."
        return not self.isCartesian()

    def setSelective(self,f=1):
        """Switches the selection flags on (off).
    When switched off, the selection flags are deleted.
    When not *self.isSelective()" and *f=1*, all flags are set to true.
        """
        if (f):
            if ( not self.isSelective() ):
                s=[]
                for i in range(0,len(self)):
                    s.append([1,1,1])
                self.selective=VArray(s,t=LOGICAL_TYPE,name="selective")
        else:
            self.selective=None

    def setCartesian(self):
        return self.setCarthesian()

    def setCarthesian(self):
        """When in direct coordinates, converts to cartesian coordinates."""
        if (self.isDirect()):
            self.forceConvertToCartesian()
            self.coordinates = "Cartesian"

    def setDirect(self):
        """When in cartesian coordinates, converts to direct coordinates."""
        if (self.isCartesian()):
            self.forceConvertToDirect()
            self.coordinates = "Direct"

    def replicateCell(self,n1,n2,n3):
        """Replicate the cell by (n1,n2,n3)."""
        w = []
        if self.isDirect():
            isdirect=1
            self.setCartesian()
        else:
            isdirect=0

        atn = [0]

        atomspertype=self.atomspertype
        for i in range(0, len(atomspertype)):
            atn.append(atn[i]+atomspertype[i])

        for at in range(0, len(atomspertype)):
            for a in range(0,n1):
                for b in range(0,n2):
                    for c in range(0,n3):
                        for i in range(atn[at],atn[at+1]):
                            v = self[i]+a*self.basis[0]+b*self.basis[1]+c*self.basis[2]
                            w.append(v)
        self.positions.data = w

        if self.isSelective():
            sel=[]
            for at in range(0, len(atomspertype)):
                for a in range(0,n1*n2*n3):
                    for i in range(atn[at],atn[at+1]):
                        sel.append(self.selective[i][:])
            self.selective=sel

        for i in range(0, len(atomspertype)):
            self.getRecord(i).atomspertype *= n1*n2*n3
        self.basis[0]=self.basis[0]*n1
        self.basis[1]=self.basis[1]*n2
        self.basis[2]=self.basis[2]*n3

        if isdirect:
            self.setDirect()

    def translate(self,v,selection=None):
        """Adds *v* to all (when *selection* is *None* )
    or specified (by the list of indexes in *selection* ) coordinates."""
        if selection is None:
            selection=range(0,len(self))
        for i in selection:
            self[i] = self[i]+v

    def transform(self,m,selection=None):
        """Multiplies all (when *selection* is *None* )
    or specified (by the list of indexes in *selection* ) coordinates with matrix *m* ."""
        if selection is None:
            selection=range(0,len(self))
        for i in selection:
            self[i] = m*self[i]

    def size(self,x,y,z,selection=None):
        """Multiplies all (when *selection* is *None* )
    or specified (by the list of indexes in *selection* ) position vector components by (x,y,z):
    (X,Y,Z)->(x*X,y*Y,z*Z)
    This does not affect the basis.

    Note: This will affect the geometry differently in direct than in cartesian coordinates.
        """
        if selection is None:
            selection=range(0,len(self))
        for i in selection:
            self[i] = Vector(x*self[i][0],y*self[i][1],z*self[i][2])

    def scale(self,x,y,z):
        """Changes the size of the system.
    Scales the basis vector components by (x,y,z) as follows::

      (b11,b12,b13) -> (x*b11,y*b12,z*b13)
      (b21,b22,b23) -> (x*b21,y*b22,z*b23)
      (b31,b32,b33) -> (x*b31,y*b32,z*b33)

    If in Cartesian coordinates, the positions are transformed in the same way.
        """

        flag=self.isCartesian()

        self.setDirect()
        self.basis[0]=Vector(self.basis[0][0]*x,self.basis[0][1]*y,self.basis[0][2]*z)
        self.basis[1]=Vector(self.basis[1][0]*x,self.basis[1][1]*y,self.basis[1][2]*z)
        self.basis[2]=Vector(self.basis[2][0]*x,self.basis[2][1]*y,self.basis[2][2]*z)


        if (self.isCartesian()):
            for i in range(0,len(self)):
                self[i] = Vector(x*self[i][0],y*self[i][1],z*self[i][2])

    def scaleBasis(self,x,y,z):
        """Changes the size of the system.
    The basis vectors are multiplied by *x* , *y* and *z* as follows::

      (b11,b12,b13)-> x*(b11,b12,b13)
      (b21,b22,b23)-> y*(b21,b22,b23)
      (b31,b32,b33)-> z*(b31,b32,b33)

    If the *Structure*  is in Cartesian coordinates, it is first transformed to direct and
    then transformed back to Cartesian.
        """

        flag=self.isCartesian()

        self.setDirect()
        self.basis[0]=x*self.basis[0]
        self.basis[1]=y*self.basis[1]
        self.basis[2]=z*self.basis[2]

        if flag:
            self.setCartesian()

    def dir2cart(self,v,basis=None):
        """Convert vector *v* from direct to Cartesian coord.
    Optionaly the direct basis can be specified.
    """
        if basis is None:
            basis=self.basis
        return v[0]*basis[0]+v[1]*basis[1]+v[2]*basis[2]

    def cart2dir(self,v,basis=None):
        """Convert vector *v* from Cartesian to direct coord.
    Optionaly the reciprocal basis can be specified.
    """
        if basis is None:
            basis=self.updateRecipBasis()
        return Vector(v*basis[0],v*basis[1],v*basis[2])

    def dirVectorToUnitCell(self,v):
        """Map vector *v* in direct coordinates to the unit cell."""
        u=Vector(0,0,0)
        for i in [0,1,2]:
            x=v[i]%1.0
            if x<0:
                x=x+1.0
            u[i]=x
        return u

    def dirVectorToCenteredUnitCell(self,v):
        """Map vector *v* in direct coordinates to the unit cell centered at the origin (0,0,0)."""
        u=Vector(0,0,0)
        for i in [0,1,2]:
            x=((v[i]%1.0)+2.0)%1.0
            if x>0.5:
                x-=1.0
            u[i]=x
        return u

    def cartVectorToUnitCell(self,v):
        """Map vector *v* in Cartesian coordinates to the unit cell."""
        rv=self.cart2dir(v)
        rrv=self.dirVectorToUnitCell(rv)
        return self.dir2cart(rrv)

    def cartVectorToCenteredUnitCell(self,v):
        """Map vector *v* in Cartesian coordinates to the unit cell centered at the origin (0,0,0)."""
        rv=self.cart2dir(v)
        rrv=self.dirVectorToCenteredUnitCell(rv)
        return self.dir2cart(rrv)

    def vectorToUnitCell(self,v):
        """Map vector *v* to the unit cell.
    If *self.isCartesian()* , the *self.cartVectorToUnitCell(v)* is returned else
    *self.dirVectorToUnitCell(v)* .
    """
        if self.isCartesian():
            return self.cartVectorToUnitCell(v)
        else:
            return self.dirVectorToUnitCell(v)

    def vectorToCenteredUnitCell(self,v):
        """Map vector *v* to the unit cell centered at the origin (0,0,0).
    If *self.isCartesian()* , the *self.cartVectorToCenteredUnitCell(v)* is returned else
    *self.dirVectorToCenteredUnitCell(v)* .
    """
        if self.isCartesian():
            return self.cartVectorToCenteredUnitCell(v)
        else:
            return self.dirVectorToCenteredUnitCell(v)

    def toCenteredUnitCell(self):
        """Map all positions to the unit cell centered at the origin (0,0,0)."""
        if self.isCartesian():
            for i in range(0,len(self)):
                self[i]=self.cartVectorToCenteredUnitCell(self[i])
        else:
            for i in range(0,len(self)):
                self[i]=self.dirVectorToCenteredUnitCell(self[i])

    def toUnitCell(self):
        """Map all positions to the unit cell."""
        if self.isCartesian():
            for i in range(0,len(self)):
                self[i]=self.cartVectorToUnitCell(self[i])
        else:
            for i in range(0,len(self)):
                self[i]=self.dirVectorToUnitCell(self[i])

    def mindistCartVectors(self,a,b):
        """Return the minimal distance between the **cartesian** vectors *a* and *b* in periodical cell.
    More precisely, return the min(|v|), where

          v=Aijk-Blmn;
          Aijk=a+i*basis[0]+j*basis[1]+k*basis[2]
          Blmn=b+l*basis[0]+m*basis[1]+n*basis[2]
          for arbitrary integral i,j,k,l,m,n.
    """
        return self.cartVectorToCenteredUnitCell(b-a).length()

    def mindistDirVectors(self,a,b):
        """Return the minimal (cartesian) distance between the **direct** vectors *a* and *b* in periodical cell.
    More precisely, return the min(|v|), where

          v=Aijk-Blmn;
          Aijk=dir2cart(a)+i*basis[0]+j*basis[1]+k*basis[2]
          Blmn=dir2cart(b)+l*basis[0]+m*basis[1]+n*basis[2]
          for arbitrary integral i,j,k,l,m,n.
    """
        a=self.dir2cart(a)
        b=self.dir2cart(b)
        return self.cartVectorToCenteredUnitCell(b-a).length()

    def dof2index(self,dof):
        """Convert the degree of freedom *dof* to indexes.
    Argument *dof* specifies the degree of freedom.
    A tuple with atom number and direction (x=0,y=1,z=2) index is returned.
    When not *isSelective()* , the return value is (dof/3, dof%3),
    otherwise this depends on which degrees of freedom are selected.
        """
        if self.isSelective():
            cdof = 0
            for i in range(0,len(self)):
                for j in range(0,3):
                    if self.selective[i][j]:
                        if cdof==dof:
                            return i,j
                        cdof=cdof+1
        else:
            return dof/3,dof%3

    def index2dof(self,index):
        """Convert the index(es) to the degree of freedom (dof).
    The *index* parameter can be either a atom index or a tuple
    containing atomnumber and direction (x=0,y=1,z=2).
    When not *isSelective()* , the return value is 3*(atom_index)+direction,
    otherwise this depends on which degrees of freedom are selected.
        """
        if type(index)==type(1):
            dir=0
            I=index
        else:
            I,dir=index
        if self.isSelective():
            cdof = 0
            for i in range(0,len(self)):
                for j in range(0,3):
                    if string.upper(str(self.selective[i][j])) in ["T",".TRUE."]:
                        if (i==I) and (j==dir):
                            return cdof
                        cdof=cdof+1
            return None
        else:
            return 3*I+dir

    def writexml(self,f,indent=0,extended=0):
        """Write *Structure* in xml representation.
    Tags are indented by indent*INDENT (*INDENT* contains two whitespaces by default,
    it is defined in the p4vasp.__init__.)
    If *extended* is true, also the redundant informations are written (reciprocal basis and volume).
        """
        in0  =indent*INDENT
        in1 =(indent+1)*INDENT
        in2 =(indent+2)*INDENT
        if self.name is None:
            if self.isCartesian():
                f.write('%s<structure coordinates="cartesian">\n'%(in0))
            else:
                f.write('%s<structure coordinates="direct">\n'%(in0))
        else:
            if self.isCartesian():
                f.write('%s<structure name="%s" coordinates="cartesian">\n'%(in0,self.name))
            else:
                f.write('%s<structure name="%s" coordinates="direct">\n'%(in0,self.name))
        f.write('%s<crystal>\n'%in1)
        self.basis.writexml(f,indent+2)
        if extended:
            f.write('%s<i name="volume">%f</i>\n'%(in2,self.getCellVolume()))
            updateRecipBasis().writexml(f,indent+2)
        f.write('%s</crystal>\n'%in1)
        self.positions.writexml(f,indent+1)
        if self.selective:
            self.selective.writexml(f,indent+1)
        f.write('%s</structure>\n'%in0)

    def writeXYZ(self,f="structure.xyz",closeflag=0):
        "Write *Structure* as XYZ to file *f* (file object or path)."
        if (type(f) == type("")):
            f = open(f,"w+")
            closeflag = 1
        f.write("%3d\n"%(len(self)))
        c=replace(self.comment,"\n"," ")
        c=replace(c,"\r"," ")
        f.write(c+"\n")

        for i in range(0,len(self)):
            f.write("%2s %+14.10f %+14.10f %+14.10f\n"%(self.getRecordForAtom(i).element,self[i][0],self[i][1],self[i][2]))

        if (closeflag):
            f.close()

    def getXYZstructure(self):
        """Returns an array of [atomtype ( *AtomtypesRecord* ),coordinate ( *Vector* )]."""
        v = []
        for i in range(0,len(self)):
            v.append([self.getRecordForAtom(i).element,Vector(self[i])])
        return v

    getRecipBasis=updateRecipBasis


    def appendAtom(self,specieindex,pos):
        """Add atom with the specie number *specieindex* and position *pos* .
    Returns the index of appended atom.
        """
        for i in range(len(self.info),specieindex+1):
            self.info.appendEmpty()

        index=self.info.lastAtomIndexForSpecie(specieindex)
        self.positions.insert(index,Vector(pos))
        if self.isSelective():
            self.selective.insert(index,[0,0,0])
        self.info[specieindex].atomspertype+=1
        return index

    def appendAtomOfNewSpecie(self,pos):
        """Add atom of a new specie and position *pos* .
    Returns the index of appended atom.
        """
        return self.appendAtom(len(self.info),pos)

    def appendStructure(self,structure,after="index"):
        """Append another structure.
    Species can be matched either by index (after="index", default choice),
    or by the element name (after="element")."""
        if after=="index":
            for i in range(len(structure)):
#        print "atom",i,"index",structure.info.speciesIndex(i)
                self.appendAtom(structure.info.speciesIndex(i),structure[i])
        elif after=="element":
            for i in range(len(structure)):
                j=self.info.findRecordIndexContaining(after,structure.getRecordForAtom(i)[after])
                self.appendAtom(j,structure[i])

    def keepOnly(self,select):
        """Remove all atoms *except* those selected by *select*.
    Select can be array of indices of a string representing a selective language expression
    (see p4vasp.sellang).
    This is the similar to remove(select).
        """
        import types
        import sellang
        if type(select) == types.StringType:
            select=sellang.decode(select,self)
        pos   = VArray(name="positions")
        for i in range(len(self)):
            if i in select:
                pos.append(self[i])
        if self.isSelective():
            sel=VArray(name=self.selective.name,t=LOGICAL_TYPE)
            for i in range(len(self)):
                if i in select:
                    sel.append(self.selective[i])
            self.selective=sel
        apt=[0]*self.types
        for i in select:
            j=self.info.speciesIndex(i)
            if j is not None:
                apt[j]+=1
        for i in range(len(apt)):
            self.info[i].atomspertype=apt[i]
        self.positions=pos
        self.info.removeRecordsWithZeroAtomspertype()

    def removeAtom(self,i):
        """Remove atom with index i.
        """
        del self.positions[i]
        self.info[self.info.speciesIndex(i)].atomspertype-=1
        self.info.removeRecordsWithZeroAtomspertype()
        if self.isSelective():
            del self.selective[i]

    def remove(self,select):
        """Remove atoms selected by *select*.
    Select can be array of indices of a string representing a selective language expression
    (see p4vasp.sellang).
    This is the similar to keepOnly(select).
        """
        import types
        import sellang
        if type(select)==types.IntType:
            select=[select]
        elif type(select)==types.StringType:
            select=sellang.decode(select,self)
        pos   = VArray(name="positions")
        for i in range(len(self)):
            if i not in select:
                pos.append(self[i])
        if self.isSelective():
            sel=VArray(name="selective",t=LOGICAL_TYPE)
            for i in range(len(self)):
                if i not in select:
                    sel.append(self.selective[i])
            self.selective=sel
        apt=self.atomspertype[:]
        for i in select:
            j=self.info.speciesIndex(i)
            if j is not None:
                apt[j]-=1
        for i in range(len(apt)):
            self.info[i].atomspertype=apt[i]
        self.positions=pos
        self.info.removeRecordsWithZeroAtomspertype()

    def setStructure(self,s):
        """Set the structure content to s"""
        self.clear()
        self.scaling     = s.scaling[:]
        self.basis[0][0] = s.basis[0][0]
        self.basis[0][1] = s.basis[0][1]
        self.basis[0][2] = s.basis[0][2]
        self.basis[1][0] = s.basis[1][0]
        self.basis[1][1] = s.basis[1][1]
        self.basis[1][2] = s.basis[1][2]
        self.basis[2][0] = s.basis[2][0]
        self.basis[2][1] = s.basis[2][1]
        self.basis[2][2] = s.basis[2][2]
        self.updateRecipBasis()
        if s.selective is not None:
            self.selective   = map(lambda x:x[:],s.selective)
        self.comment     = s.comment[:]
        try:
            self.element= s.element
        except:
            self.element=None
        try:
            self.coordinates = s.coordinates[:]
        except:
            self.coordinates = "Direct"
        self.positions   = VArray(name="positions")
        for x in s.positions:
            self.positions.append(Vector(x))
        self.info = AtomInfo(s.info)
        try:
            self.name        = s.name[:]
        except:
            self.name        =""
    def clear(self):
        """Clear all structure informations."""
        self.info        = AtomInfo()
        self.basis       = VArray([Vector(1.0,0.0,0.0),Vector(0.0,1.0,0.0),Vector(0.0,0.0,1.0)])
        self.updateRecipBasis()
        self.positions   = VArray(name="positions")
        self.selective   = None
        self.comment     = ""
        self.element     = None
        self.coordinates = "Direct"
        self.name        = ""

    def mindist(self,i,j):
        """calculates the minimal distance between the atoms i and j."""
        if self.isCartesian():
            return self.mindistCartVectors(self[i],self[j])
        else:
            return self.mindistDirVectors(self[i],self[j])

    def removeDuplicate(self,tiny=0.001):
        """Removes duplicate atoms in cell. By *duplicate* is understood the atoms
    with the distance to other atom lower than *tiny*."""
        l=[]
        for i in range(len(self)):
            for j in range(i+1,len(self)):
                if self.mindist(i,j)<tiny:
                    if j not in l:
                        l.append(j)
#    print "duplicate",l
        self.remove(l)

    def createMultiplied(self,n11,n12,n13,n21,n22,n23,n31,n32,n33,tinydist=0.01,tinydet=0.01):
        """New Structure is returned with the lattice vectors

      a1 -> n11*a1+n12*a2+n13*a3
      a2 -> n21*a1+n22*a2+n23*a3
      a3 -> n31*a1+n32*a2+n33*a3

    Coefficients nij should be integer numbers.
    Duplicate atoms are removed from the structure. The minimal allowed distance
    is *tinydist*. The minimal allowed volume of the new cell is tinydet.
    """
        s=self
        ns=Structure(s)
        m=Matrix(ns.basis)
        if abs(m.det())<tinydet:
            msg().error("New basis illdefined.")
            return None
        min1=min(0,n11,n21,n31,n11+n21,n21+n31,n31+n11)
        max1=max(0,n11,n21,n31,n11+n21,n21+n31,n31+n11)
        min2=min(0,n12,n22,n32,n12+n22,n22+n32,n32+n12)
        max2=max(0,n12,n22,n32,n12+n22,n22+n32,n32+n12)
        min3=min(0,n13,n23,n33,n13+n23,n23+n33,n33+n13)
        max3=max(0,n13,n23,n33,n13+n23,n23+n33,n33+n13)

    #  print min1,max1,min2,max2,min3,max3
        ns.setCartesian()
        ns.replicateCell(max1-min1,max2-min2,max3-min3)
        ns.translate(min1*s.basis[0]+min2*s.basis[1]+min3*s.basis[2])
        ns.basis[0]=n11*s.basis[0]+n12*s.basis[1]+n13*s.basis[2]
        ns.basis[1]=n21*s.basis[0]+n22*s.basis[1]+n23*s.basis[2]
        ns.basis[2]=n31*s.basis[0]+n32*s.basis[1]+n33*s.basis[2]
        ns.setDirect()
        l=[]
        for i in range(len(ns)):
            v=ns[i]
            if min(v)<0 or max(v)>1:
                l.append(i)
    #  print ns.toString()

    #  print l
        ns.remove(l)
        ns.removeDuplicate(tinydist)
        return ns

    def correctScaling(self):
        flag=self.isCartesian()
        scaling=self.scaling
        if len(scaling)==1:
            if scaling[0]!=1.0:
                self.setDirect()
                if scaling[0]>0:
                    s=scaling[0]
                else:
                    V0=abs(self.basis[0].cross(self.basis[1])*self.basis[2])
                    s=pow(abs(scaling[0])/V0,1.0/3.0)
                self.basis[0]=s*self.basis[0]
                self.basis[1]=s*self.basis[1]
                self.basis[2]=s*self.basis[2]

                self.scaling=[1.0]
                self.updateRecipBasis()
                if flag:
                    self.setCartesian()
        elif len(scaling)==3:
            self.setDirect()
            self.basis[0]=scaling[0]*self.basis[0]
            self.basis[1]=scaling[1]*self.basis[1]
            self.basis[2]=scaling[2]*self.basis[2]
            self.scaling=[1.0]
            self.updateRecipBasis()
            if flag:
                setCartesian()
        else:
            raise "Bad Structure.scaling: %s"%str(scaling)
