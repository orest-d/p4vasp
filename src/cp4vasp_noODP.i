/*
 *  p4vasp is a GUI-program and library for processing outputs of the
 *  Vienna Ab-inition Simulation Package (VASP)
 *  (see http://cms.mpi.univie.ac.at/vasp/Welcome.html)
 *  
 *  Copyright (C) 2003  Orest Dubay <odubay@users.sourceforge.net>
 *
 *  This program is free software; you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation; either version 2 of the License, or
 *  (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *   You should have received a copy of the GNU General Public License
 *  along with this program; if not, write to the Free Software
 *  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */

%module cp4vasp
%{
#include <exception>
//#include <new>
//#include <stdexcept>
#include <p4vasp/Exceptions.h>
#include <p4vasp/ClassInterface.h>
#include <p4vasp/AtomtypesRecord.h>
#include <p4vasp/AtomInfo.h>
#include <p4vasp/vecutils3d.h>
#include <p4vasp/Structure.h>
#include <p4vasp/Chgcar.h>
#include <p4vasp/VisMain.h>
#include <p4vasp/VisWindow.h>
#include <p4vasp/VisDrawer.h>
#include <p4vasp/VisNavDrawer.h>
#include <p4vasp/VisPrimitiveDrawer.h>
#include <p4vasp/VisStructureDrawer.h>
#include <p4vasp/VisStructureArrowsDrawer.h>
#include <p4vasp/VisIsosurfaceDrawer.h>
%}



//%include "include/p4vasp/Exceptions.h"

#ifndef NO_THROW
#  ifdef SIMPLE_EXCEPTIONS
%except(python) {
  try{
    $function
  }
  catch(exception &e){
    PyErr_SetString(PyExc_Exception,e.what());
    return NULL;
  }
}
#else
%exception {
  try{
    $function
  }
  catch(RangeException e){
    PyErr_SetString(PyExc_IndexError,e.what());
    return NULL;
  }
  catch(MemoryAllocationException e){
    PyErr_SetString(PyExc_MemoryError,e.what());
    return NULL;
  }
  catch(NullPointerException e){
    PyErr_SetString(PyExc_RuntimeError,e.what());
    return NULL;
  }
  catch(Exception e){
    PyErr_SetString(PyExc_Exception,e.what());
    return NULL;
  }
  catch(exception &e){
    PyErr_SetString(PyExc_Exception,e.what());
    return NULL;
  }
}
#  endif
#endif

%include "include/p4vasp/ClassInterface.h"
%include "include/p4vasp/AtomtypesRecord.h"
%include "include/p4vasp/AtomInfo.h"
%include "include/p4vasp/vecutils3d.h"
%include "include/p4vasp/Structure.h"
%include "include/p4vasp/Chgcar.h"
%include "include/p4vasp/VisMain.h"
%include "include/p4vasp/VisWindow.h"
%include "include/p4vasp/VisDrawer.h"
%include "include/p4vasp/VisNavDrawer.h"
%include "include/p4vasp/VisPrimitiveDrawer.h"
%include "include/p4vasp/VisStructureDrawer.h"
%include "include/p4vasp/VisStructureArrowsDrawer.h"
