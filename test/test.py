#!/usr/bin/env python2
# Copyright (C) 2012 Orest Dubay <dubay@danubiananotech.com>
import unittest
import testSystemPM
import testPaint3DInterface
import testMeshTools
import testPovrayPaint3D
import testColladaPaint3D
import testIsosurface
import testStructure
import testSelection
import testAtominfo
import testDyna

if __name__ == '__main__':
    suite_list=[]
    suite_list.append(unittest.TestLoader().loadTestsFromModule(testSystemPM))
    suite_list.append(unittest.TestLoader().loadTestsFromModule(testPaint3DInterface))
    suite_list.append(unittest.TestLoader().loadTestsFromModule(testMeshTools))
    suite_list.append(unittest.TestLoader().loadTestsFromModule(testPovrayPaint3D))
    suite_list.append(unittest.TestLoader().loadTestsFromModule(testColladaPaint3D))
    suite_list.append(unittest.TestLoader().loadTestsFromModule(testIsosurface))
    suite_list.append(unittest.TestLoader().loadTestsFromModule(testStructure))
    suite_list.append(unittest.TestLoader().loadTestsFromModule(testSelection))
    suite_list.append(unittest.TestLoader().loadTestsFromModule(testAtominfo))
    suite_list.append(unittest.TestLoader().loadTestsFromModule(testDyna))
    suite=unittest.TestSuite(suite_list)
    unittest.TextTestRunner().run(suite)
