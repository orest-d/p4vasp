import unittest
from p4vasp.SystemPM import *
from tempfile import mkstemp
from os import remove, close

class TestSystemPM(unittest.TestCase):
    def setUp(self):
        self.paths=[]
    def tearDown(self):
        for p in self.paths:
            remove(p)

    def turnOffMessages(self):
        from p4vasp.message import MessageDriver
        self.messageDriverBackup=msg()
        setMessageDriver(MessageDriver(printing=False))
    def turnOnMessages(self):
        setMessageDriver(self.messageDriverBackup)

    def makeVasprun(self,content):
        f,path=mkstemp(prefix="vasprun",suffix=".xml")
        self.paths.append(path)
        close(f)
        f=open(path,"w+")
        f.write('<?xml version="1.0" encoding="ISO-8859-1"?>\n')
        f.write('<modeling>\n')
        f.write(content)
        f.write('\n</modeling>\n')
        f.close()
        return path

    def makeXMLSystemPM(self,content):
        path=self.makeVasprun(content)
        s=XMLSystemPM(path)
        return s

    def testOpen(self):
        s=self.makeXMLSystemPM("")
        self.assertEquals(None,s.STRUCTURE)

    def testDielectric(self):
        s=self.makeXMLSystemPM("""
     <dielectricfunction>
      <imag>
       <array>
        <dimension dim="1">gridpoints</dimension>
        <field>energy</field>
        <field>xx</field>
        <field>yy</field>
        <field>zz</field>
        <field>xy</field>
        <field>yz</field>
        <field>zx</field>
        <set> <r> 10 20 30 40 50 60 70</r><r> 11 21 31 41 51 61 71</r></set>
       </array>
      </imag>
      <real>
       <array>
        <dimension dim="1">gridpoints</dimension>
        <field>energy</field>
        <field>xx</field>
        <field>yy</field>
        <field>zz</field>
        <field>xy</field>
        <field>yz</field>
        <field>zx</field>
        <set> <r> 12 22 32 42 52 62 72</r><r> 13 23 33 43 53 63 73</r></set>
       </array>
      </real>
     </dielectricfunction>""")
        self.assertIsNotNone(s.DIELECTRIC)
        self.assertEquals(s.DIELECTRIC[0][0],[10,20,30,40,50,60,70],"Imaginary part, first row should match")
        self.assertEquals(s.DIELECTRIC[0][1],[11,21,31,41,51,61,71],"Imaginary part, second row should match")
        self.assertEquals(s.DIELECTRIC[1][0],[12,22,32,42,52,62,72],"Real part, first row should match")
        self.assertEquals(s.DIELECTRIC[1][1],[13,23,33,43,53,63,73],"Real part, second row should match")

    def testDielectricFunctions(self):
        s=self.makeXMLSystemPM("""
     <dielectricfunction comment="DF 1">
      <imag>
       <array>
        <dimension dim="1">gridpoints</dimension>
        <field>energy</field>
        <field>xx</field>
        <field>yy</field>
        <field>zz</field>
        <field>xy</field>
        <field>yz</field>
        <field>zx</field>
        <set> <r> 10 20 30 40 50 60 70</r><r> 11 21 31 41 51 61 71</r></set>
       </array>
      </imag>
      <real>
       <array>
        <dimension dim="1">gridpoints</dimension>
        <field>energy</field>
        <field>xx</field>
        <field>yy</field>
        <field>zz</field>
        <field>xy</field>
        <field>yz</field>
        <field>zx</field>
        <set> <r> 12 22 32 42 52 62 72</r><r> 13 23 33 43 53 63 73</r></set>
       </array>
      </real>
     </dielectricfunction>
     <dielectricfunction comment="DF 2">
      <imag>
       <array>
        <dimension dim="1">gridpoints</dimension>
        <field>energy</field>
        <field>xx</field>
        <field>yy</field>
        <field>zz</field>
        <field>xy</field>
        <field>yz</field>
        <field>zx</field>
        <set> <r> 14 24 34 44 54 64 74</r><r> 15 25 35 45 55 65 75</r></set>
       </array>
      </imag>
      <real>
       <array>
        <dimension dim="1">gridpoints</dimension>
        <field>energy</field>
        <field>xx</field>
        <field>yy</field>
        <field>zz</field>
        <field>xy</field>
        <field>yz</field>
        <field>zx</field>
        <set> <r> 16 26 36 46 56 66 76</r><r> 17 27 37 47 57 67 77</r></set>
       </array>
      </real>
     </dielectricfunction>
    """)
        self.assertIsNotNone(s.DIELECTRIC_FUNCTIONS)
        self.assertEquals(s.DIELECTRIC_FUNCTIONS[0][0][0],[10,20,30,40,50,60,70],"Imaginary part, first row should match")
        self.assertEquals(s.DIELECTRIC_FUNCTIONS[0][0][1],[11,21,31,41,51,61,71],"Imaginary part, second row should match")
        self.assertEquals(s.DIELECTRIC_FUNCTIONS[0][1][0],[12,22,32,42,52,62,72],"Real part, first row should match")
        self.assertEquals(s.DIELECTRIC_FUNCTIONS[0][1][1],[13,23,33,43,53,63,73],"Real part, second row should match")
        self.assertEquals(s.DIELECTRIC_FUNCTIONS[1][0][0],[14,24,34,44,54,64,74],"Imaginary part, first row should match")
        self.assertEquals(s.DIELECTRIC_FUNCTIONS[1][0][1],[15,25,35,45,55,65,75],"Imaginary part, second row should match")
        self.assertEquals(s.DIELECTRIC_FUNCTIONS[1][1][0],[16,26,36,46,56,66,76],"Real part, first row should match")
        self.assertEquals(s.DIELECTRIC_FUNCTIONS[1][1][1],[17,27,37,47,57,67,77],"Real part, second row should match")
        self.assertEquals(s.DIELECTRIC_FUNCTIONS_COMMENTS,["DF 1","DF 2"])

    def testProjectedEigenvaluesEnergies(self):
        self.turnOffMessages()
        s=self.makeXMLSystemPM("""
      <projected>
       <eigenvalues>
        <array>
         <dimension dim="1">band</dimension>
         <dimension dim="2">kpoint</dimension>
         <dimension dim="3">spin</dimension>
         <field>eigene</field>
         <field>occ</field>
         <set>
          <set comment="spin 1">
           <set comment="kpoint 1">
            <r>  -1.2    1.0000 </r>
            <r>  -1.1    1.0000 </r>
            <r>  -1.0    0.0000 </r>
           </set>
          </set>
         </set>
        </array>
       </eigenvalues>
      </projected>
    """)
        self.assertIsNotNone(s.PROJECTED_EIGENVALUES_ENERGIES)
        self.assertEquals(len(s.PROJECTED_EIGENVALUES_ENERGIES),1,"Spin dimensionshould match")
        self.assertEquals(len(s.PROJECTED_EIGENVALUES_ENERGIES[0]),1,"K-point dimensionshould match")
        self.assertEquals(len(s.PROJECTED_EIGENVALUES_ENERGIES[0][0]),3,"Number of bands should match")
        self.assertEquals(s.PROJECTED_EIGENVALUES_ENERGIES[0][0][0][0],-1.2,"First energy should match")
        self.assertEquals(s.PROJECTED_EIGENVALUES_ENERGIES[0][0][0][1],1.0,"First occupancy should match")
        self.assertEquals(s.PROJECTED_EIGENVALUES_ENERGIES[0][0][1][0],-1.1,"2nd energy should match")
        self.assertEquals(s.PROJECTED_EIGENVALUES_ENERGIES[0][0][1][1],1.0,"2nd occupancy should match")
        self.assertEquals(s.PROJECTED_EIGENVALUES_ENERGIES[0][0][2][0],-1.0,"3rd energy should match")
        self.assertEquals(s.PROJECTED_EIGENVALUES_ENERGIES[0][0][2][1],0.0,"3rd occupancy should match")
        self.turnOnMessages()
    def testEmptySystemPMStructure(self):
        self.turnOffMessages()
        s = XMLSystemPM()
        self.assertIsNotNone(s.INITIAL_STRUCTURE)
        self.turnOnMessages()
    def testPrimitiveStructure(self):
        self.turnOffMessages()
        s=self.makeXMLSystemPM("""
 <atominfo>
  <atoms>      64 </atoms>
  <types>       1 </types>
  <array name="atomtypes" >
   <dimension dim="1">type</dimension>
   <field type="int">atomspertype</field>
   <field type="string">element</field>
   <field>mass</field>
   <field>valence</field>
   <field type="string">pseudopotential</field>
   <set>
    <rc><c>  64</c><c>C </c><c>     12.01100000</c><c>      4.00000000</c><c>  PAW_PBE C 08Apr2002                   </c></rc>
   </set>
  </array>
 </atominfo>
 <structure name="initialpos" >
  <crystal>
   <varray name="basis" >
    <v>       7.13400000       0.00000000       0.00000000 </v>
    <v>       0.00000000       7.13400000       0.00000000 </v>
    <v>       0.00000000       0.00000000       7.13400000 </v>
   </varray>
   <i name="volume">    363.07748210 </i>
   <varray name="rec_basis" >
    <v>       0.14017382       0.00000000       0.00000000 </v>
    <v>       0.00000000       0.14017382       0.00000000 </v>
    <v>       0.00000000       0.00000000       0.14017382 </v>
   </varray>
  </crystal>
  <varray name="positions" >
   <v>       0.00000000       0.00000000       0.00000000 </v>
   <v>       0.50000000       0.00000000       0.00000000 </v>
   <v>       0.00000000       0.50000000       0.00000000 </v>
   <v>       0.50000000       0.50000000       0.00000000 </v>
   <v>       0.00000000       0.00000000       0.50000000 </v>
   <v>       0.50000000       0.00000000       0.50000000 </v>
   <v>       0.00000000       0.50000000       0.50000000 </v>
   <v>       0.50000000       0.50000000       0.50000000 </v>
   <v>       0.25000000       0.25000000       0.00000000 </v>
   <v>       0.75000000       0.25000000       0.00000000 </v>
   <v>       0.25000000       0.75000000       0.00000000 </v>
   <v>       0.75000000       0.75000000       0.00000000 </v>
   <v>       0.25000000       0.25000000       0.50000000 </v>
   <v>       0.75000000       0.25000000       0.50000000 </v>
   <v>       0.25000000       0.75000000       0.50000000 </v>
   <v>       0.75000000       0.75000000       0.50000000 </v>
   <v>       0.00000000       0.25000000       0.25000000 </v>
   <v>       0.50000000       0.25000000       0.25000000 </v>
   <v>       0.00000000       0.75000000       0.25000000 </v>
   <v>       0.50000000       0.75000000       0.25000000 </v>
   <v>       0.00000000       0.25000000       0.75000000 </v>
   <v>       0.50000000       0.25000000       0.75000000 </v>
   <v>       0.00000000       0.75000000       0.75000000 </v>
   <v>       0.50000000       0.75000000       0.75000000 </v>
   <v>       0.25000000       0.00000000       0.25000000 </v>
   <v>       0.75000000       0.00000000       0.25000000 </v>
   <v>       0.25000000       0.50000000       0.25000000 </v>
   <v>       0.75000000       0.50000000       0.25000000 </v>
   <v>       0.25000000       0.00000000       0.75000000 </v>
   <v>       0.75000000       0.00000000       0.75000000 </v>
   <v>       0.25000000       0.50000000       0.75000000 </v>
   <v>       0.75000000       0.50000000       0.75000000 </v>
   <v>       0.12500000       0.12500000       0.12500000 </v>
   <v>       0.62500000       0.12500000       0.12500000 </v>
   <v>       0.12500000       0.62500000       0.12500000 </v>
   <v>       0.62500000       0.62500000       0.12500000 </v>
   <v>       0.12500000       0.12500000       0.62500000 </v>
   <v>       0.62500000       0.12500000       0.62500000 </v>
   <v>       0.12500000       0.62500000       0.62500000 </v>
   <v>       0.62500000       0.62500000       0.62500000 </v>
   <v>       0.37500000       0.37500000       0.12500000 </v>
   <v>       0.87500000       0.37500000       0.12500000 </v>
   <v>       0.37500000       0.87500000       0.12500000 </v>
   <v>       0.87500000       0.87500000       0.12500000 </v>
   <v>       0.37500000       0.37500000       0.62500000 </v>
   <v>       0.87500000       0.37500000       0.62500000 </v>
   <v>       0.37500000       0.87500000       0.62500000 </v>
   <v>       0.87500000       0.87500000       0.62500000 </v>
   <v>       0.12500000       0.37500000       0.37500000 </v>
   <v>       0.62500000       0.37500000       0.37500000 </v>
   <v>       0.12500000       0.87500000       0.37500000 </v>
   <v>       0.62500000       0.87500000       0.37500000 </v>
   <v>       0.12500000       0.37500000       0.87500000 </v>
   <v>       0.62500000       0.37500000       0.87500000 </v>
   <v>       0.12500000       0.87500000       0.87500000 </v>
   <v>       0.62500000       0.87500000       0.87500000 </v>
   <v>       0.37500000       0.12500000       0.37500000 </v>
   <v>       0.87500000       0.12500000       0.37500000 </v>
   <v>       0.37500000       0.62500000       0.37500000 </v>
   <v>       0.87500000       0.62500000       0.37500000 </v>
   <v>       0.37500000       0.12500000       0.87500000 </v>
   <v>       0.87500000       0.12500000       0.87500000 </v>
   <v>       0.37500000       0.62500000       0.87500000 </v>
   <v>       0.87500000       0.62500000       0.87500000 </v>
  </varray>
 </structure>
   <structure name="primitive_cell" >
    <crystal>
     <varray name="basis" >
      <v>       1.78350000       1.78350000       0.00000000 </v>
      <v>       1.78350000       0.00000000      -1.78350000 </v>
      <v>       0.00000000       1.78350000      -1.78350000 </v>
     </varray>
     <i name="volume">     11.34617132 </i>
     <varray name="rec_basis" >
      <v>       0.28034763       0.28034763       0.28034763 </v>
      <v>       0.28034763      -0.28034763      -0.28034763 </v>
      <v>      -0.28034763       0.28034763      -0.28034763 </v>
     </varray>
    </crystal>
    <varray name="positions" >
     <v>       0.00000000       0.00000000       0.00000000 </v>
     <v>      -0.25000000      -0.25000000      -0.25000000 </v>
    </varray>
   </structure>
    """)
        self.assertIsNotNone(s.PRIMITIVE_STRUCTURE)
        self.assertEquals(len(s.PRIMITIVE_STRUCTURE),2,"primitive structure should have two atoms")
        self.assertEquals(s.PRIMITIVE_STRUCTURE[0][0], 0.0,"coordinates should match")
        self.assertEquals(s.PRIMITIVE_STRUCTURE[0][1], 0.0,"coordinates should match")
        self.assertEquals(s.PRIMITIVE_STRUCTURE[0][2], 0.0,"coordinates should match")
        self.assertEquals(s.PRIMITIVE_STRUCTURE[1][0],-0.25,"coordinates should match")
        self.assertEquals(s.PRIMITIVE_STRUCTURE[1][1],-0.25,"coordinates should match")
        self.assertEquals(s.PRIMITIVE_STRUCTURE[1][2],-0.25,"coordinates should match")
        self.assertEquals(s.PRIMITIVE_STRUCTURE.info.atomspertype,[2],"Atominfo should have correct size")
        self.turnOnMessages()
    def testPrimitiveIndex(self):
        self.turnOffMessages()
        s=self.makeXMLSystemPM("""
  <dynmat>
   <varray name="primitive_index" >
    <v type="int" >        1 </v>
    <v type="int" >       44 </v>
   </varray>
  </dynmat>
    """)
        self.assertIsNotNone(s.PRIMITIVE_INDEX)
        self.assertEquals(len(s.PRIMITIVE_INDEX),2,"Primitive index dimension should match")
        self.assertEquals(s.PRIMITIVE_INDEX[0],1,"First index should match")
        self.assertEquals(s.PRIMITIVE_INDEX[1],44,"Second index should match")
        self.turnOnMessages()

if __name__ == '__main__':
    unittest.main()
