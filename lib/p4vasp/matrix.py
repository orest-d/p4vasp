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
"""

from math import sqrt,acos,sin,cos
from string import joinfields, split, atof, atoi,join
from types import *
from UserList import *

try:
    if StringType not in StringTypes:
        raise "This can't be true: StringType not in StringTypes !!!"
except NameError:
    StringTypes=(StringType,UnicodeType)



def isMatrix(obj):
    "Check whether *obj* is a *Matrix* ."
    return isinstance(obj,Matrix)

def isVector(obj):
    "Check whether *obj* is a *Vector* ."
    return isinstance(obj,Vector)

class Vector(UserList):
    """Vector object.
  Inherits from *UserList* , basic vector manipulation operations are defined.
  Some operations make sense only for 3d voctors.
    """
    def __init__(self,x=0.0,y=0.0,z=0.0):
        """Create new *Vector*
    *Vector* can have arbitrary dimensions.
    It can be created in following ways:

        * Vector()              - equivalent to Vector(0.0,0.0,0.0),

        * Vector(1.0,2.0,3.0)   - vector with listed elements (only for 3d vector),

        * Vector('1.0 2.0 3.0') - vector created from string. Elements are floats separated by whitespace,

        * Vector([1.0,2.0,3.0]) - vector from a list of floats,

        * Vector(v)             - created from other vector.

    Note: *Vector* is not a *Matrix* subclass.
        """
        if type(x) in StringTypes:
            UserList.__init__(self,map(float,split(x)))
        if (type(x) in [ListType,TupleType]) or isinstance(x,UserList):
            UserList.__init__(self,map(float,x))
        elif type(x) in [IntType,FloatType,ComplexType]:
            UserList.__init__(self,[x,y,z])
        else:
            raise "Unknown init parameters in Vector(%s,%s,%s)"%(repr(x),repr(y),repr(z))

    def __add__(self,o):
        "Vector addition."
        if isVector(o):
            if len(o)==3 and len(self)==3:
                return Vector(self[0]+o[0],self[1]+o[1],self[2]+o[2])
            else:
                l=[]
                for x in range(min(len(self),len(o))):
                    l.append(self[i]+o[i])
                return Vector(l)
        else:
            raise TypeError, "other is no vector in vector addition"

    __radd__=__add__

    def __sub__(self,o):
        "Vector subtraction."
        if isVector(o):
            if len(o)==3 and len(self)==3:
                return Vector(self[0]-o[0],self[1]-o[1],self[2]-o[2])
            else:
                l=[]
                for i in range(min(len(self),len(o))):
                    l.append(self[i]-o[i])
                return Vector(l)
        else:
            raise TypeError, "other is no vector in vector subtraction"

    def __rsub__(self,o):
        "Vector subtraction."
        if isVector(o):
            if len(o)==3 and len(self)==3:
                return Vector(o[0]-self[0],o[1]-self[1],o[2]-self[2])
            else:
                l=[]
                for x in range(min(len(self),len(o))):
                    l.append(o[i]-self[i])
                return Vector(l)
        else:
            raise TypeError, "other is no vector in right vector subtraction"

    def __neg__(self):
        "Negative Vector (-v)"
        return Vector(map(lambda x:-x,self.data))


    def __mul__(self,other):
        """Vector multiplication.
    The *other* parameter can be:
    * scalar - result is vector multiplied by a scalar
    * vector - result is scalar product of two vectors
        """
        if isVector(other):
            sum=0.0
            for i in range(3):
                sum=sum+self[i]*other[i]
            return sum
        elif isMatrix(other):
            raise TypeError, "other must not be a matrix"
        else:
            return Vector(map(lambda x,a=other:a*x,self.data))

    def __rmul__(self,other):
        """Vector multiplication.
    The *other* parameter can be a scalar.
        """
        return Vector(map(lambda x,a=other:a*x,self.data))

    def cross(self,other):
        """Cross product."""
        if isVector(other):
            tmp=Vector()
            tmp[0]=self[1]*other[2]-self[2]*other[1]
            tmp[1]=self[2]*other[0]-self[0]*other[2]
            tmp[2]=self[0]*other[1]-self[1]*other[0]
            return tmp
        else:
            raise TypeError, "other is no vector in cross product"

    def length(self):
        "Length of vector."
        return sqrt(reduce(lambda x,y:x+y,map(lambda z:z*z,self.data)))

    def normal(self):
        "Normalized vector. The result has *length()=1* ."
        l=self.length()
        if l == 0:
            raise ZeroDivisionError, "self is a zero-length vector"
        else:
            return (1.0/l)*self

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
        s = ""
        t=map(lambda x:type(x) == FloatType,self)
        if reduce(lambda x,y: x and y, t):
            for i in range(0,len(self)):
                s = s + ("%+14.10f " % (self[i]))
            return s
        else:
            return join(map(str,self))

    def __repr__(self):
        "Python style representation."
        return "Vector([%s])"%join(map(repr,self),",")
    def write(self,f):
        "Write vector into the file *f* (in string representation)."
        f.write(str(self)+"\n")

    def clone(self):
        "Create copy of the vector."
        return Vector(self)

    def get(self,i):
        "The same as *self[i]*"
        return self[i]
    def set(self,i,value):
        "The same as *self[i]=value*"
        self[i]=value


class Matrix(UserList):
    """Matrix object.
  The matrix is represented as a list of lists (rank 2 matrix).

  *Matrix* can have arbitrary dimensions.
  Two (read only) attributes containing the matrix dimensionality are defined:
  *m* is the same as *len(self)* and *m* is *len(self[0])* .

  Usual operations are defined: matrix addition, subtraction and multiplication,
  vector and scalr multiplication, determinant (for 3d matrix), inversion (for 3d matrix) and some more...

    """
    def __init__(self,m=3,n=3):
        """Create a new *Matrix* .

    *Matrix* can be created in following ways:

        * Matrix()    - equivalent to Matrix(3,3),

        * Matrix(3,3) - create a 3x3 matrix filled with zeros,

        * Matrix([[1.0,0.0,0.0],[0.0,1.0,0.0],[0.0,0.0,1.0]]) - create the matrix from a list.
          The list must have all elements of the same size. This is not checked, but it can cause troubles
          if not fulfilled.
        """
        if type(m)==IntType:
            w=[]
            for j in range(0,n):
                w.append([0.0]*m)
            UserList.__init__(self,w)
        else:
            UserList.__init__(self,m)

    def get(self,i,j):
        "The same as *self[i][j]* ."
        return self[i][j]
    def set(self,i,j,value):
        "The same as *self[i][j]=value* ."
        self[i][j]=value

    def __repr__(self):
        "Python style representation."
        return "Matrix(%s)"%repr(self.data)

    def __str__(self):
        "String representation."
        if type(self[0][0]) == FloatType:
            s="Matrix:\n"
            for a in self:
                s+=join(map(lambda x:"%+14.12f "%x,a))
                s+="\n"
            return s
        else:
            s="Matrix:\n"
            for a in self:
                s+=join(map(lambda x:"%-14s "%str(x),a))
                s+="\n"
            return s



    def __getattr__(self,x):
        "Definnes *m* and *n* wrappers."
        if x=="m":
            return len(self)
        elif x=="n":
            return len(self[0])
        else:
            raise AttributeError(x)

    def __add__(self,other):
        "Matrix addition."
        if isMatrix(other):
            if (self.m != other.m) or (self.n != other.n):
                raise TypeError,"ranks differ in addition (%d,%d)!=(%d,%d)."%(self.m,self.n,other.m,other.n)
            tmp=self.clone()
            for i in range(0,len(self)):
                x=tmp[i]
                y=other[i]
                for j in range(0,len(x)):
                    x[j]+=y[j]
            return tmp
        else:
            raise TypeError,"error in matrix addition"

    __radd__=__add__

    def __sub__(self,other):
        "Matrix subtraction."
        if isMatrix(other):
            if (self.m != other.m) or (self.n != other.n):
                raise TypeError,"ranks differ in subtraction (%d,%d)!=(%d,%d)."%(self.m,self.n,other.m,other.n)
            tmp=self.clone()
            for i in range(0,len(self)):
                x=tmp[i]
                y=other[i]
                for j in range(0,len(x)):
                    x[j]-=y[j]
            return tmp

        else:
            raise TypeError,"error in matrix subtraction"

    def __rsub__(self,other):
        "Matrix subtraction."
        if isMatrix(other):
            if (self.m != other.m) or (self.n != other.n):
                raise TypeError,"ranks differ in subtraction (%d,%d)!=(%d,%d)."%(self.m,self.n,other.m,other.n)
            tmp=self.clone()
            for i in range(0,min(len(self),len(other))):
                x=tmp[i]
                y=other[i]
                for j in range(0,min(len(x),len(y))):
                    x[j]=y[j]-x[j]
            return tmp

        else:
            raise TypeError,"error in matrix subtraction"

    def __neg__(self):
        "Matrix negation. (-m)"
        tmp=[]
        for i in range(0,len(self)):
            tmp.append(map(lambda x:-x,self[i]))
        return Matrix(tmp)


    def __mul__(self,other):
        "Multiplication with *other* matrix, vector or scalar."
        if isMatrix(other):
            if self.n != other.n:
                raise TypeError,"ranks differ in matrix multiplication (%d,%d)!=(%d,%d)."%(self.m,self.n,other.m,other.n)
            tmp=Matrix(self.n,other.n)
            for i in range(0,tmp.m):
                for j in range(0,tmp.n):
                    for k in range(0,self.n):
                        tmp[i][j]+=self[i][k]*other.get(k,j)

            return tmp
        elif isVector(other):
            if self.n != len(other):
                raise TypeError,"ranks differ in matrix*vector multiplication Matrix(%d,%d)*Vector(%d)."%(self.m,self.n,len(other))
            tmp=Vector([0.0]*self.m)
            for i in range(0,self.m):
                for j in range(0,self.n):
                    tmp[i]+=self[i][j]*other[j]
            return tmp
        elif type(other) in (IntType,FloatType,ComplexType):
            tmp=self.clone()
            for i in range(len(self)):
                tmp[i]*=other
            return tmp
        else:
            raise TypeError,"unknown type in matrix multiplication"

    def __rmul__(self,other):
        "Multiplication with *other* matrix."
        if isMatrix(other):
            if self.n != other.n:
                raise TypeError,"ranks differ in matrix multiplication (%d,%d)!=(%d,%d)."%(self.m,self.n,other.m,other.n)
            tmp=Matrix(other.n,self.n)
            for i in range(0,tmp.m):
                for j in range(0,tmp.n):
                    for k in range(0,other.n):
                        tmp.set(i,j,tmp.get(i,j)+other.get(i,k)*self.get(k,j))

            return tmp
        else:
            raise TypeError,"error in right matrix multiplication"

    def det(self):
        "Determinant - defined for 3x3 matrix only."
        if(self.m == 3 and self.n == 3):
            return (self[0][0]*self[1][1]*self[2][2] - self[0][0]*self[2][1]*self[1][2] \
                  - self[0][1]*self[1][0]*self[2][2] + self[0][1]*self[2][0]*self[1][2] \
                  + self[0][2]*self[1][0]*self[2][1] - self[0][2]*self[2][0]*self[1][1])
        else:
            raise TypeError, "determinants of third order defined only"

    def subDet(self,I,J):
        "Subdeterminant *(I,J)* (for 3x3 matrix only). Used in *inverse()* ."
        if(self.m == 3 and self.n == 3):
            v=[]
            for i in range(0,3):
                if i != I:
                    for j in range(0,3):
                        if j != J:
                            v.append(self[i][j])
            a,b,c,d=v
            return a*d-b*c
        else:
            raise TypeError, "subdeterminants of third order defined only"

    def inverse(self):
        "Inverse matrix (for 3x3 matrix only)."
        if(self.m == 3 and self.n == 3):
            D=self.det()
            M=Matrix(3,3)
            for i in range(0,3):
                for j in range(0,3):
                    M[i][j]=(-1)**(i+j)*self.subDet(j,i)/D
            return M
        else:
            raise TypeError, "subdeterminants of third order defined only"

    def clone(self):
        "Create a copy of the matrix."
        m=Matrix(self.m,self.n)
        for i in range(0,self.m):
            for j in range(0,self.n):
                m[i][j]=self[i][j]
        return m

    def trans(self):
        "Transpose the matrix. This changes the matrix *self* and returns it."
        m=Matrix(self.n,self.m)
        for i in range(0,self.m):
            for j in range(0,self.n):
                m[j][i]=self[i][j]
        self.data=m.data
        return self

    def zero(self):
        "Fill the matrix with zeros and return *self* ."
        for i in range(0,self.m):
            for j in range(0,self.n):
                self[i][j]=0.0
        return self

    def identity(self):
        "Fill the matrix with identity matrix and return *self* ."
        self.zero()
        for i in range(0,min(self.m,self.n)):
            self[i][i]=1.0
        return self

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
        S=a/sqrt(x*x+y*y+z*z)
        x*=S
        y*=S
        z*=S

    cx=cos(x)
    cy=cos(y)
    cz=cos(z)
    sx=sin(x)
    sy=sin(y)
    sz=sin(z)

    dest=Matrix()
    dest[0][0]=  cy*cz;
    dest[1][0]= -sz*cy;
    dest[2][0]=  sy;

    dest[0][1]=  sx*sy*cz+cx*sz;
    dest[1][1]=  cx*cz-sx*sy*sz;
    dest[2][1]=  -sx*cy;

    dest[0][2]= sx*sz - cx*sy*cz;
    dest[1][2]= cx*sy*sz+sx*cz;
    dest[2][2]= cx*cy;
    return dest;


ex=Vector(1.,0.,0.)
ey=Vector(0.,1.,0.)
ez=Vector(0.,0.,1.)

if __name__=="__main__":

    A=Matrix()
    v=Vector(1,2,3)
    A.identity()
    A[1][2]=3
    B=A.clone()
    B[0][0]=2
    B[0][1]=4
    A.trans()

    print repr(A)
    print A
    print A*v

    print "A",A
    print "B",B
    print "B*A",B*A

#A.set([1.0,2.0,3.0,4.0,5.0,6.0,7.0,8.0,9.0])
#B=Matrix()
#B.set([1.1,2.2,3.3,4.4,5.5,6.6,7.7,8.8,9.9])
#C=Matrix(3,1,[4,4,4])
#D=Matrix(3,3,[-23, 1.9, 14.0, 0, 123.45, -99.1, 0.0003, 0.1, 1.0])

#v=Vector( 1.1, 2.2, 3.3)
#w=Vector(11.1,22.2,33.3)
