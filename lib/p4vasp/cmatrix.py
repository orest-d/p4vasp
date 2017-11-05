#
# HappyDoc:docStringFormat='ClassicStructuredText'
#
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
#
# Acknowledgement: This code was inspired by matrix.py
# from Mario Chemnitz <ucla@hrz.tu-chemnitz.de>.



"""
Basic *Vector* and *Matrix* manipulation library.
This module defines objects *Vector* and *Matrix* with (almost)
the same api as the matrix.py, but cmatrix.py uses functions written in C.
The other difference is, that it is restricted to 3d vectors and matrices only.

There are two reasons to use this module:

  * performance - the performance of *cmatrix* can be from 1.5 up to more than 10 times
    better than for the *matrix* (depending on the operation)

  * *cmatrix* can provide a convenient interface to other 3d vector-based
    objects implemented in C.

Objects *Matrix* and *Vector* are instances of the corresponding objects
from the *matrix* module.
Objects of *cmatrix* can interact with the *matrix* objects - mixed types
can be used in operations.

Limitations:

  * only 3d objects,

  * only *float* (double) type.

Bugs: Sometimes the objects needs to be deleted explicitely by *del* statement
in order to avoid exceptions.
"""


from math import sqrt,acos,sin,cos
from string import joinfields, split, atof, atoi,join
from types import *
from _cp4vasp import *
from UserList import *
import p4vasp.matrix

try:
    if StringType not in StringTypes:
        raise "This can't be true: StringType not in StringTypes !!!"
except NameError:
    StringTypes=(StringType,UnicodeType)


def isCMatrix(obj):
    "Check whether *obj* is a *Matrix* from *cmatrix* module."
    return isinstance(obj,Matrix)

def isCVector(obj):
    "Check whether *obj* is a *Vector* from *cmatrix* module."
    return isinstance(obj,Vector)

def isMatrix(obj):
    "Check whether *obj* is a *Matrix* ."
    return isinstance(obj,p4vasp.matrix.Matrix)

def isVector(obj):
    "Check whether *obj* is a *Vector* ."
    return isinstance(obj,p4vasp.matrix.Vector)

class Vector(p4vasp.matrix.Vector):
    """3D Vector object implemented using c-functions.
  Basic vector manipulation operations are defined.
  The *self.pointer* attribute contains a *swig* string-pointer
  to a double[3] array.
    """
    def __init__(self,x=0.0,y=0.0,z=0.0,pointer=None,isref=0):
        """Create new *Vector*
    *Vector* can have arbitrary dimensions.
    It can be created in following ways:

        * Vector()              - equivalent to Vector(0.0,0.0,0.0),

        * Vector(1.0,2.0,3.0)   - vector with listed elements (only for 3d vector),

        * Vector('1.0 2.0 3.0') - vector created from string. Elements are floats separated by whitespace,

        * Vector([1.0,2.0,3.0]) - vector from a list of floats,

        * Vector(v)             - created from other vector,

        * Vector(pointer=function3d(...)) - create from pointer string.

    The *pointer* parameter is a string conatining the pointer to *double* array,
    as returned by the c-functions created using *swig* .
    Additionaly if parameter *isref* is true, the pointer is considered
    to be a "reference" and the object is not deleted in __del__.
    This flag can be used if the array of *double* is a part of an larger
    array (e.g. matrix).

    Note: *Vector* is not a *Matrix* subclass.
        """

        self.isref=isref
        if pointer:
            self.pointer = pointer
        elif isCVector(x):
            self.pointer = clone3d(x.pointer)
        elif type(x) in StringTypes:
            x,y,z=map(float,split(x))
            self.pointer=createvec3d(x,y,z)
        elif (type(x) in [ListType,TupleType]) or isinstance(x,UserList):
            x,y,z=map(float,x)
            self.pointer=createvec3d(x,y,z)
        elif type(x) in [IntType,FloatType,ComplexType]:
            self.pointer=createvec3d(x,y,z)
        else:
            raise "Unknown init parameters in Vector(%s,%s,%s)"%(repr(x),repr(y),repr(z))

    def __add__(s,o):
        "Vector addition."
        if isCVector(o):
            return Vector(pointer=createplus3d(s.pointer,o.pointer))
        elif isVector(o):
            return Vector(s[0]+o[0],s[1]+o[1],s[2]+o[2])
        else:
            raise TypeError, "other is no vector in vector addition"

    __radd__=__add__

    def __sub__(s,o):
        "Vector subtraction."
        if isCVector(o):
            return Vector(pointer=createminus3d(s.pointer,o.pointer))
        elif isVector(o):
            return Vector(s[0]-o[0],s[1]-o[1],s[2]-o[2])
        else:
            raise TypeError, "other is no vector in vector subtraction"

    def __rsub__(s,o):
        "Vector subtraction."
        if isCVector(o):
            return Vector(pointer=createminus3d(o.pointer,s.pointer))
        elif isVector(o):
            return Vector(o[0]-s[0],o[1]-s[1],o[2]-s[2])
        else:
            raise TypeError, "other is no vector in right vector subtraction"

    def __neg__(self):
        "Negative Vector (-v)"
        return Vector(pointer=createneg3d(self.pointer))


    def __mul__(self,o):
        """Vector multiplication.
    The *other* parameter can be:
    * scalar - result is vector multiplied by a scalar
    * vector - result is scalar product of two vectors.
        """
        if isCVector(o):
            return scalprod3d(self.pointer,o.pointer)
        elif isVector(other):
            sum=0.0
            for i in range(3):
                sum+=self[i]*o[i]
            return sum
        elif isMatrix(other):
            raise TypeError, "other must not be a matrix"
        else:
            return Vector(pointer=createscalmultiply3d(self.pointer,float(other)))

    def __rmul__(self,other):
        """Vector multiplication.
    The *other* parameter can be a scalar.
        """
        return Vector(pointer=createscalmultiply3d(self.pointer,float(other)))

    def cross(self,other):
        """Cross product."""
        if isCVector(other):
            return Vector(pointer=createcrossprod3d(self.pointer,other.pointer))
        elif isVector(other):
            return Vector(self[1]*other[2]-self[2]*other[1],
                          self[2]*other[0]-self[0]*other[2],
                          self[0]*other[1]-self[1]*other[0])
        else:
            raise TypeError, "other is no vector in cross product"

    def length(self):
        "Length of vector."
        return veclength3d(self.pointer)

    def normal(self):
        "Normalized vector. The result has *length()=1* ."
        l=veclength3d(self.pointer)
        if l == 0:
            raise ZeroDivisionError, "self is a zero-length vector"
        else:
            return Vector(pointer=createscaldivide3d(self.pointer,l))

    def angle(self,other):
        """Angle that contains the vector with the *other* vector.
    Calculated using *acos()* of a scalar product.
        """
        if isVector(other):
            tmp=(1.0/(self.length()*other.length()))*(self*other)
            if tmp>=-1.0 and tmp <=1.0:
                return acos(tmp)
            else:
                raise "domain error in function acos()!"
        else:
            raise TypeError, "other is no vector"

    def __str__(self):
        "String representation: values separated by whitespace."
        return "%+14.10f %+14.10f %+14.10f " % (self[0],self[1],self[2])

    def __repr__(self):
        "Python style representation."
        return "Vector([%+14.10f, %+14.10f, %+14.10f])"%(self[0],self[1],self[2])
    def write(self,f):
        "Write vector into the file *f* (in string representation)."
        f.write(str(self)+"\n")

    def clone(self):
        "Create copy of the vector."
        return Vector(pointer=clone3d(self.pointer))

    def __len__(self):
        "Returns 3."
        return 3

    def __getitem__(self,i):
        "Defines *self[i]*"
        return getVecElement3d(self.pointer,i)

    def __setitem__(self,i,value):
        "Defines *self[i]=value*"
        setVecElement3d(self.pointer,i,value)

    def get(self,i):
        "The same as *self[i]*"
        return getVecElement3d(self.pointer,i)
    def set(self,i,value):
        "The same as *self[i]=value*"
        setVecElement3d(self.pointer,i,value)

    def __del__(self):
        "Destroys the vector."
        if self.pointer and (not self.isref):
            deletevec3d(self.pointer)
        self.pointer=None


class Matrix(p4vasp.matrix.Matrix):
    """3D Matrix object implemented using c-functions.
  *Matrix* can be only 3*3 matrix of floats.

  Usual operations are defined: matrix addition, subtraction and multiplication,
  vector and scalr multiplication, determinant, inversion and some more...

    """
    m=3
    n=3
    def __init__(self,init=None,pointer=None, isref=0):
        """Create a new *Matrix* .

    *Matrix* can be created in following ways:

        * Matrix()    - create a 3x3 Matrix filled with zeros,

        * Matrix([[1.0,0.0,0.0],[0.0,1.0,0.0],[0.0,0.0,1.0]]) - create the matrix from a list,
          The list must have 3 elements of the size 3,

        * Matrix(m)   - create new matrix from matrix m,

        * Matrix(pointer=function3d(...)) - create from pointer string.

    The *pointer* parameter is a string conatining the pointer to *double* array,
    as returned by the c-functions created using *swig* .
    Additionaly if parameter *isref* is true, the pointer is considered
    to be a "reference" and the object is not deleted in __del__.
        """
        self.isref=isref
        if pointer:
            self.pointer=pointer
        elif isCMatrix(init):
            self.pointer=clonemat3d(init.pointer)
        elif init:
            self.pointer=createmat3d(init[0][0],init[0][1],init[0][2],
                                     init[1][0],init[1][1],init[1][2],
                                     init[2][0],init[2][1],init[2][2])
        else:
            self.pointer=createzeromat3d()


    def get(self,i,j):
        "The same as *self[i][j]* , but (a bit) more efficient."
        return getMatElement3d(self.pointer,i,j)
    def set(self,i,j,value):
        "The same as *self[i][j]=value* , but (a bit) more efficient."
        setMatElement3d(self.pointer,i,j,value)

    def __repr__(self):
        "Python style representation."
        s="CMatrix([\n"
        for i in range(3):
            s+="  ["
            s+=str(self.get(i,0))
            s+=","
            s+=str(self.get(i,1))
            s+=","
            s+=str(self.get(i,2))
            s+="]"
            if i<2:
                s+=",\n"
            else:
                s+="\n"
        s+="],pointer='%s',isref=%d)"%(self.pointer,self.isref)
        return s

    def __str__(self):
        "String representation."
        s="CMatrix:\n"
        for i in range(3):
            s+="%+14.10f %+14.10f %+14.10f\n"%(self.get(i,0),self.get(i,1),self.get(i,2))
        return s


    def __add__(self,other):
        "Matrix addition."
        if isCMatrix(other):
            return Matrix(pointer=createplusmat3d(self.pointer,other.pointer))
        elif isMatrix(other):
            if (other.m!=3) or (other.n!=3):
                raise TypeError,"ranks differ in additon (3,3)!=(%d,%d)."%(other.m,other.n)
            tmp=Matrix()
            for i in range(0,len(self)):
                for j in range(0,len(x)):
                    tmp.set(i,j,self.get(i,j)+other[i][j])
            return tmp
        else:
            raise TypeError,"error in matrix addition"

    __radd__=__add__

    def __sub__(self,other):
        "Matrix subtraction."
        if isCMatrix(other):
            return Matrix(pointer=createminusmat3d(self.pointer,other.pointer))
        elif isMatrix(other):
            if (other.m != 3) or (other.n != 3):
                raise TypeError,"ranks differ in subtraction (3,3)!=(%d,%d)."%(other.m,other.n)
            tmp=Matrix()
            for i in range(0,len(self)):
                for j in range(0,len(x)):
                    tmp.set(i,j,self.get(i,j)-other[i][j])
            return tmp
        else:
            raise TypeError,"error in matrix subtraction"

    def __rsub__(self,other):
        "Matrix subtraction."
        if isCMatrix(other):
            return Matrix(pointer=createminusmat3d(other.pointer,self.pointer))
        elif isMatrix(other):
            if (other.m != 3) or (other.n != 3):
                raise TypeError,"ranks differ in subtraction (3,3)!=(%d,%d)."%(other.m,other.n)
            tmp=Matrix()
            for i in range(0,len(self)):
                for j in range(0,len(x)):
                    tmp.set(i,j,-self.get(i,j)+other[i][j])
            return tmp
        else:
            raise TypeError,"error in matrix subtraction"


    def __neg__(self):
        "Matrix negation. (-m)"
        return Matrix(pointer=createnegmat3d(self.pointer))


    def __mul__(self,other):
        "Multiplication with *other* matrix, vector or scalar."
        if isCMatrix(other):
            return Matrix(pointer=createmultiplymatmat3d(self.pointer,other.pointer))
        elif isCVector(other):
            return Vector(pointer=createmultiplymatvec3d(self.pointer,other.pointer))
        elif isMatrix(other):
            if other.n!=3 or other.m!=3:
                raise TypeError,"ranks differ in matrix multiplication (3,3)!=(%d,%d)."%(other.m,other.n)
            tmp=Matrix()
            for i in range(3):
                for j in range(3):
                    for k in range(3):
                        tmp.set(i,j,tmp.get(i,j)+self.get(i,k)*other.get(k,j))
            return tmp
        elif isVector(other):
            if len(other)!=3:
                raise TypeError,"ranks differ in matrix*vector multiplication Matrix(3,3)*Vector(%d)."%(len(other))
            tmp=Vector(other[0],other[1],other[2])
            mulmatvec3d(self.pointer,tmp.pointer)
            return tmp
        elif type(other) in (IntType,FloatType):
            return Matrix(pointer=createmultiplymatscal3d(self.pointer,float(other)))
        else:
            raise TypeError,"unknown type in matrix multiplication"

    def __rmul__(self,other):
        "Multiplication with *other* matrix."
        if isCMatrix(other):
            return Matrix(pointer=createmultiplymatmat3d(other.pointer,self.pointer))
        elif isMatrix(other):
            if (other.n!=3) or (other.m!=3):
                raise TypeError,"ranks differ in matrix multiplication (3,3)!=(%d,%d)."%(other.m,other.n)
            tmp=Matrix()
            for i in range(3):
                for j in range(3):
                    for k in range(3):
                        tmp.set(i,j,tmp.get(i,j)+other.get(i,k)*self.get(k,j))
            return tmp
        else:
            raise TypeError,"error in right matrix multiplication"

    def det(self):
        "Determinant - defined for 3x3 matrix only."
        return detmat3d(self.pointer)

    def subDet(self,I,J):
        "Subdeterminant *(I,J)* (for 3x3 matrix only). Used in *inverse()* . Implemented in python."
        if(self.m == 3 and self.n == 3):
            v=[]
            for i in range(0,3):
                if i != I:
                    for j in range(0,3):
                        if j != J:
                            v.append(self.get(i,j))
            a,b,c,d=v
            return a*d-b*c
        else:
            raise TypeError, "subdeterminants of third order defined only"

    def inverse(self):
        "Inverse matrix (for 3x3 matrix only). Implemented (mostly) in python."
        if(self.m == 3 and self.n == 3):
            D=detmat3d(self.pointer)
            M=Matrix()
            for i in range(3):
                for j in range(3):
                    M.set(i,j,(-1)**(i+j)*self.subDet(j,i)/D)
            return M
        else:
            raise TypeError, "subdeterminants of third order defined only"

    def clone(self):
        "Create a copy of the matrix."
        return Matrix(pointer=clonemat3d(self.pointer))

    def trans(self):
        "Transpose the matrix. This changes the matrix *self* and returns it."
        transmat3d(self.pointer)
        return self

    def zero(self):
        "Fill the matrix with zeros and return *self* ."
        zeromat3d(self.pointer)
        return self

    def identity(self):
        "Fill the matrix with identity matrix and return *self* ."
        identitymat3d(self.pointer)
        return self

    def __del__(self):
        "Destroys the matrix."
        if self.pointer and (not self.isref):
            deletemat3d(self.pointer)
        self.pointer=None

    def __getitem__(self,i):
        "Return *self[i]* as a *Vector* ."
        return Vector(pointer=getMatVecElement3d(self.pointer,i),isref=1)
    def __setitem__(self,i,v):
        "Set *self[i]* to *value* (vector, tuple or list). "
        if isCVector(v):
            setMatVecElement3d(self.pointer,i,v.pointer)
        else:
            self.set(i,0,v[0])
            self.set(i,1,v[1])
            self.set(i,2,v[2])

def Rx(w=0):
    "Return matrix of rotation around x axis. Parameter *w* is in radians."
    return Matrix([[1.0,    0.0,     0.0],
                   [0.0, cos(w), -sin(w)],
                   [0.0, sin(w),  cos(w)]])

def Ry(w=0):
    "Return matrix of rotation around y axis. Parameter *w* is in radians."
    return Matrix([[ cos(w), 0.0, sin(w)],
                   [    0.0, 1.0,    0.0],
                   [-sin(w), 0.0, cos(w)]])

def Rz(w=0):
    "Return matrix of rotation around z axis. Parameter *w* is in radians."
    return Matrix([[cos(w), -sin(w), 0.0],
                   [sin(w),  cos(w), 0.0],
                   [0.0,     0.0,    1.0]])

def rotmat(x,y,z,a=None):
    """Return matrix of rotation around (x,y,z) axis. Parameter *a* is in radians.
  If *a* is missing (or *None* ), then the length of the vector  (x,y,z) (in radians)
  specifies the rotation.
    """
    if a:
        return Matrix(pointer=createrotmat3da(x,y,z,a))
    else:
        return Matrix(pointer=createrotmat3d(x,y,z))

ex=Vector(1.,0.,0.)
ey=Vector(0.,1.,0.)
ez=Vector(0.,0.,1.)

if __name__=="__main__":
    from time import clock
    import matrix
    print "create v"
    v=Vector(1,2,3)
    print v
    print "create A"
    A=Matrix()
    print A
    print "identity"
    A.identity()
    print A
    w=A[1]
    print "A[1]"
    print w
    print A[1]

    print "w",w[0],w[1],w[2]
    A.set(1,2,3)
    print "set 1,2,3"
    print A
    print "A[0][2]=5"
    A[0][2]=5
    print A
    print "clone"
    B=A.clone()
    print B
    print "B.set..."
    B.set(0,0,2)
    B.set(0,1,4)
    print B
    print "B[2][2]+=1"
    B[2][2]+=1
    print B

    A.trans()

    print repr(A)
    print A
    print A*v

    print "A",A
    print "B",B
    print "B*A",B*A
    print "del A"
    del A
    print "del B"
    del B
    print "END test 1"

    c=clock()
    m=Vector(0,0,0)
    for i in range(10000):
        m=m+m
    dc=clock()-c
    cdc=dc
    print "C      vector addition clock",dc

    c=clock()
    m=matrix.Vector(0,0,0)
    for i in range(10000):
        m=m+m
    dc=clock()-c
    pdc=dc
    print "python vector addition clock",dc
    print "p/c",pdc/cdc
    print

    c=clock()
    m=Matrix()
    for i in range(10000):
        m=m*m
    dc=clock()-c
    cdc=dc
    print "C      matrix multiply clock",dc

    c=clock()
    m=matrix.Matrix()
    for i in range(10000):
        m=m*m
    dc=clock()-c
    pdc=dc
    print "python matrix multiply clock",dc
    print "p/c",pdc/cdc
    print

#A.set([1.0,2.0,3.0,4.0,5.0,6.0,7.0,8.0,9.0])
#B=Matrix()
#B.set([1.1,2.2,3.3,4.4,5.5,6.6,7.7,8.8,9.9])
#C=Matrix(3,1,[4,4,4])
#D=Matrix(3,3,[-23, 1.9, 14.0, 0, 123.45, -99.1, 0.0003, 0.1, 1.0])

#v=Vector( 1.1, 2.2, 3.3)
#w=Vector(11.1,22.2,33.3)
