import unittest
from p4vasp.Dyna import *

class TestDyna(unittest.TestCase):
    def testParsing(self):
        d=Dyna()
        d.parse("""graphite
1 0.0
recip
   51
'A'      0.00
0.000    0.000    0.500
0.000    0.000    0.000
'&1G'    0.00
0.000    0.000    0.000
0.500    0.000    0.000
'M'      0.00
0.500    0.000    0.000
0.33333333333333  0.33333333333333  0.000
'K'      0.00
0.33333333333333  0.33333333333333  0.000
0.000    0.000    0.000
'&1G'    0.00
""")
        self.assertEquals(d.comment,"graphite")
        self.assertEquals(d.isReciprocal(),True)
        self.assertEquals(d.size,51)
        self.assertEquals(len(d.segments),4)
        self.assertEquals(len(d.labels),4)
        self.assertEquals(d.labels,[['A',''],['&1G',''],['M',''],['K','&1G']])
        self.assertEquals(d.segments[0],(Vector(0.0,0.0,0.5),Vector(0.0,0.0,0.0)))

    def testReciprocal(self):
        d=Dyna()
        a=10
        d.parse("""fcc
1 0.0
Cartesian
   51
'X'      0.00
0.000    0.000    0.100
0.050    0.000    0.100
'W'    0.00
""")
        self.assertEquals(d.isCartesian(),True)
        recip=d.withBasis([Vector(0,a/2,a/2),Vector(a/2,0,a/2),Vector(a/2,a/2,0)]).reciprocal()
        self.assertEquals(recip.segments[0],(Vector(0.5,0.5,0.0),Vector(0.5,0.75,0.25)))

    def testCartesian(self):
        d=Dyna()
        a=10
        d.parse("""fcc
1 0.0
Reciprocal
   51
'X'      0.00
0.500    0.500    0.000
0.500    0.750    0.250
'W'    0.00
""")
        self.assertEquals(d.isCartesian(),False)
        recip=d.withBasis([Vector(0,a/2,a/2),Vector(a/2,0,a/2),Vector(a/2,a/2,0)]).reciprocal()
        self.assertEquals(recip.segments[0],(Vector(0.5,0.5,0.0),Vector(0.5,0.75,0.25)))
        cart=d.withBasis([Vector(0,a/2,a/2),Vector(a/2,0,a/2),Vector(a/2,a/2,0)]).cartesian()
        self.assertEquals((cart.segments[0][0]-Vector(0.0,0.0,1.0/a)).length()<0.001,True)
        self.assertEquals((cart.segments[0][1]-Vector(0.5/a,0.0,1.0/a)).length()<0.001,True)
    def testPointsAlongPath(self):
        d=Dyna()
        d.parse("""graphite
1 0.0
recip
   51
'A'      0.00
0.000    0.000    0.500
0.000    0.000    0.000
'&1G'    0.00
0.000    0.000    0.000
0.500    0.000    0.000
'M'      0.00
0.500    0.000    0.000
0.33333333333333  0.33333333333333  0.000
'K'      0.00
0.33333333333333  0.33333333333333  0.000
0.000    0.000    0.000
'&1G'    0.00
""")
        self.assertEquals(d.isReciprocal(),True)
        self.assertEquals(d.size,51)
        p=list(d.pointsAlongPath(3))
        self.assertEquals(len(p),12)
        self.assertEquals(p[0],Vector(0,0,0.5))
        self.assertEquals(p[1],Vector(0,0,0.25))
        self.assertEquals(p[2],Vector(0,0,0.0))

    def testPointsAlongPathWithDistanceAndLabel(self):
        d=Dyna()
        d.parse("""graphite
1 0.0
recip
   51
'A'      0.00
0.000    0.000    0.500
0.000    0.000    0.000
'&1G'    0.00
0.000    0.000    0.000
0.500    0.000    0.000
'M'      0.00
0.500    0.000    0.000
0.33333333333333  0.33333333333333  0.000
'K'      0.00
0.33333333333333  0.33333333333333  0.000
0.000    0.000    0.000
'&1G'    0.00
""")
        p=list(d.pointsAlongPathWithDistanceAndLabel(3))
        self.assertEquals(len(p),12)
        self.assertEquals(p[0],(Vector(0,0,0.5),0.0,"A"))
        self.assertEquals(p[1],(Vector(0,0,0.25),0.25,None))
        self.assertEquals(p[2],(Vector(0,0,0.0),0.5,None))
        self.assertEquals(p[3],(Vector(0,0,0.0),0.5,"&1G"))
        self.assertEquals(p[11][0],Vector(0,0,0.0))
        self.assertEquals(p[11][2],"&1G")


if __name__ == '__main__':
    unittest.main()
