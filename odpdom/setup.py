#!/usr/bin/env python

from distutils.core import setup, Extension
from glob import *

odpdomsrc=glob("*.cpp")
#print odpdomsrc

setup(name="odpdom",
      version="0.2.1",
      description="Oversized Document Parser - XML/DOM",
      author="Orest Dubay",
      author_email="dubay@ap.univie.ac.at",
      url="http://sourceforge.net/projects/odpdom",
      license="LGPL",
      py_modules=["ODPdom","cODP"],
      ext_modules=[
        Extension("_cODP",odpdomsrc,
          include_dirs=["include"],
	  define_macros=[
	    ('PY_DOMEXC_MODULE','"ODPdom."'),
#	    ('PY_DOMEXC_MODULE','"xml.dom."'),
	    ('CHECK','1'),
#	    ('NO_THROW',None),
#	    ('NO_POS_CACHE',None),
	    ('VERBOSE','0')
          ]
	)	  
      ],
      long_description="""ODPdom is a simple non-validating DOM (Document Object Model)
parser written in C++.
It can handle relatively large XML files with the size in order of 100 MB pro file.
ODPdom provides an interface to Python."""      
     )

