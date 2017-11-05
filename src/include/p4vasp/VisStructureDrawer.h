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

#ifndef VisStructureDrawer_h
#define VisStructureDrawer_h
#include "VisPrimitiveDrawer.h"
#include "threads.h"
#include <FL/gl.h>
#include <GL/glu.h>
#include "AtomInfo.h"
#include "Structure.h"

class AtomId{
  public:  
  AtomId();
  int atom,nx,ny,nz;
};


class VisStructureDrawer : public VisPrimitiveDrawer{
  long   bondcount;
  int    *bondindex;
  double *bondvec;
  double bond_factor;
  double bond_radius;
  double radius_factor;
  
  int    select_object_slices;
  int    select_object_stacks;
  int    update_structure_flag;
  int    nx,ny,nz;
  AtomId *select_buffer;
  int    select_count,select_size;
  MUTEX(select_mutex);
  MUTEX(structure_mutex);

  void   selectLock(){MUTEX_LOCK(select_mutex);}
  void   selectUnlock(){MUTEX_UNLOCK(select_mutex);}
  void   structureLock(){MUTEX_LOCK(structure_mutex);}
  void   structureUnlock(){MUTEX_UNLOCK(structure_mutex);}
  void   rescaleSelectBuffer(int len=-1,int force=0);
  void   appendSelected_nolock(int atom,int nx=0,int ny=0,int nz=0);	  
  void   removeSelectedItem_nolock(int i);				  
  int    findSelectedAtom_nolock(int atom,int nx=0,int ny=0,int nz=0);    
  void   selectAtom_nolock(int atom,int nx, int ny, int nz);		  
  void   deselectAtom_nolock(int atom,int nx, int ny, int nz);  	  
  

#if (!defined(NO_GL_LISTS)) && (!defined(NO_GL_LISTS_S))
  int select_object_list;
  int structure_spheres_list;
  int structure_bonds_list;
  int structure_cell_list;
  
  int so_list_init_flag;
#endif  
  void       initSelectObject();
  Structure *structure;

  void       updateCellList(double *lattice);
  void       updateCellList();
  void       updateSpheresList();
  void       updateBondsList();


  void       drawCell();
  void       drawSpheres();
  void       drawSelection();
  void       drawBonds();

  long       createHalfBondsList(int storeflag=1);
  long       countHalfBonds();
   
  public:
  
  float cell_red,cell_green,cell_blue;
  float bond_red,bond_green,bond_blue;

#ifdef SWIG
%immutable;
#endif  
  AtomInfo  *info;

  int cell_line_width;
  int showcellflag;

  void       updateStructure();

  void       setMultiple(int a,int b,int c);
  void       setMultiple1(int a);
  void       setMultiple2(int a);
  void       setMultiple3(int a);
  int        getMultiple1();
  int        getMultiple2();
  int        getMultiple3();
    
  
  VisStructureDrawer();
  virtual const char *getClassName();
#ifndef SWIG    
  virtual void init();  	    
  virtual void draw();  	    
  virtual int  handle(int event);    
#endif  
  virtual ~VisStructureDrawer();

  int        switchSelectionByPick(int x, int y);

  void       setPrimitivesResolution(int r);
  void       selectObject(double x,double y,double z,double radius,double phase=0.0);
  
  void       fillInfo();
  void       setStructure(Structure *s);
  Structure *getStructure();

  	     	      

  double     getRadiusFactor();
  void       setRadiusFactor(double r);
  double     getBondRadius();
  void       setBondRadius(double r);
  double     getBondFactor();
  void       setBondFactor(double r);
  void       showCell(int f=1);
  int        getCellLineWidth();
  void       setCellLineWidth(int w);
  void       setCellColor(float r,float g,float b);
  void       setBondColor(float r,float g,float b); 

  AtomId     *getSelected(int i);
  int        getSelectedCount();
  void       appendSelected(int atom,int nx=0,int ny=0,int nz=0);  
  void       notifySelected(int atom,int nx=0,int ny=0,int nz=0);  
  void       notifyDeselected(int atom,int nx=0,int ny=0,int nz=0);  
  void       removeSelectedAll();
  void       removeSelectedItem(int i);
  int        findSelectedAtom(int atom,int nx=0,int ny=0,int nz=0);
  void       selectAtom(int atom,int nx, int ny, int nz);
  void       deselectAtom(int atom,int nx, int ny, int nz);
  void       switchAtomSelection(int atom,int nx, int ny, int nz);    
};

#endif
