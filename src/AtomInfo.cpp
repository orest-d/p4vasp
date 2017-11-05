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

#include <stdio.h>
#include <string.h>
#include <p4vasp/AtomInfo.h>
#include <stdlib.h>

AtomtypesRecord *AtomInfo::default_record = NULL;

const char *AtomInfo::getClassName(){
  return "AtomInfo";
}


AtomInfo::AtomInfo(AtomInfo *a){
#if VERBOSE>1
  printf("AtomInfo::AtomInfo(AtomInfo) (constructor) %p\n",this);
#endif

  if (default_record == NULL){
    default_record = new AtomtypesRecord();
#if CHECK>0
    if (default_record == NULL){
      THROW_MA_EXC("AtomInfo::default_record allocation failed.");
    }
#endif
    default_record->setElement("?");
    default_record->red      = 1.0;
    default_record->green    = 1.0;
    default_record->blue     = 1.0;
    default_record->radius   = 1.0;
    default_record->covalent = 1.0;
    default_record->mass     = 0.0;        
  }
  
  atomtypes=NULL;
  allocated=0;
  types=0;
  if (a!=NULL){
    setAtomInfo(a);  
  }
}

AtomInfo::AtomInfo(int alloc){
#if VERBOSE>1
  printf("AtomInfo::AtomInfo(%d) (constructor) %p\n",alloc,this);
#endif

  if (default_record == NULL){
    default_record = new AtomtypesRecord();
#if CHECK>0
    if (default_record == NULL){
      THROW_MA_EXC("AtomInfo::default_record allocation failed.");
    }
#endif
    default_record->setElement("?");
    default_record->red      = 1.0;
    default_record->green    = 1.0;
    default_record->blue     = 1.0;
    default_record->radius   = 1.0;
    default_record->covalent = 1.0;
    default_record->mass     = 0.0;        
  }


  atomtypes=NULL;
  allocated=0;
  types=0;
#ifdef NO_THROW
  realloc(alloc);
#else    
  try{
    realloc(alloc);
  }
  catch(MemoryAllocationException){
    throw MemoryAllocationException(this,"realloc() failed in  AtomInfo()"
                                         " constructor.");
  }
#endif  
}

AtomInfo::~AtomInfo(){
#if VERBOSE>1
  printf("AtomInfo::~AtomInfo() (destructor) %p\n",this);
#endif
  if (atomtypes != NULL){
    free(atomtypes);
  }
}

void AtomInfo::realloc(int alloc){
  AtomtypesRecord *new_atomtypes;
  if (alloc!=allocated){
    if (alloc>0){
      new_atomtypes = (AtomtypesRecord *)calloc(alloc,sizeof(AtomtypesRecord));
      if (new_atomtypes==NULL){
        THROW_MA_EXC("realloc() failed");
      }
      long count=types;
      if (alloc<count) count=alloc;
      if (count>0){
	memcpy(new_atomtypes,atomtypes,sizeof(AtomtypesRecord)*count);
      }
      types=(int)count;
      allocated=alloc;
    }
    else{
      types=0;
      allocated=0;
      new_atomtypes=NULL;
    }
    if (atomtypes!=NULL){
      free(atomtypes);
    }
    atomtypes=new_atomtypes;
  }
}

void AtomInfo::append(AtomtypesRecord *r){
  if (allocation_step<=0) allocation_step=1;
  if ((types+1)>allocated){
    realloc(allocated+allocation_step);
  }
  memmove(&atomtypes[types],r,sizeof(AtomtypesRecord));
  types++;
}

void AtomInfo::allocate(int n){
  if (n>allocated){
#ifdef NO_THROW
    realloc(n);
#else  
    try{
      realloc(n);
    }
    catch(MemoryAllocationException){
      throw MemoryAllocationException(this,"realloc() failed in  allocate()");
    }
#endif      
  }
  types=n;
}

AtomtypesRecord *AtomInfo::getRecord(int i){
#if CHECK>0
  if ((i<0) || (i>=types)){
    THROW_R_EXC("Index out of range in get().",0,types,i);
  }
#endif
  return &atomtypes[i];
}

void AtomInfo::setRecord(int i,AtomtypesRecord *value){
#if CHECK>0
  if ((i<0) || (i>=types)){
    THROW_R_EXC("Index out of range in set().",0,types,i);
  }
#endif
  memmove(&atomtypes[i],value,sizeof(AtomtypesRecord));
}

AtomtypesRecord *AtomInfo::getRecordForAtom(int i){
  int I=speciesIndex(i);
#if CHECK>0
  if (I<0){
    char buff[256];
    snprintf(buff,250,
    "Index not found in AtomInfo.getRecordForAtom(%d) types=%d, Natoms=%d.\n",
    i, types, getNatoms());
    THROW_EXC(buff);
  }
#endif
  return &atomtypes[I];
}

AtomtypesRecord *AtomInfo::getRecordForElement(const char *x){
  long hash = getAtomtypesRecordHash(x);
  for (int i = 0;i<types;i++){
    AtomtypesRecord *r = getRecord(i);
    if (r->hash == hash){
      return r;
    }
  }
  return NULL;
}

AtomtypesRecord *AtomInfo::getRecordForElementSafe(const char *x,int i=0,int m=-1){
  AtomtypesRecord *r = getRecordForElement(x);
  if (r!=NULL)  return r;
  if (m==-1)    m=types;
  if (types<m)  m=types;  
  if (m<=0)     return default_record;  
  return getRecord(i%m);
}

void AtomInfo::fillAttributesWithTable(AtomInfo *table){
#if CHECK>0
  if (table==NULL){
    THROW_NP_EXC("fillAttributesWithTable() failed");
  }
#endif
  for (int i=0; i<types; i++){
    AtomtypesRecord *dr = getRecord(i);
#if CHECK>1
    if (dr==NULL){
      THROW_NP_EXC("getRecord()=NULL"
                   " in fillAttributesWithTable()");
    }
#endif    
    AtomtypesRecord *tr = table->getRecordForElementSafe(dr->getElement(),i);
#if CHECK>1
    if (tr==NULL){
      THROW_NP_EXC("table->getRecordForElementSafe()=NULL"
                   " in fillAttributesWithTable()");
    }
#endif    
    dr->mass     = tr->mass;
    dr->radius   = tr->radius;
    dr->covalent = tr->covalent;
    dr->red      = tr->red;
    dr->green    = tr->green;
    dr->blue     = tr->blue;        
  }
}

int AtomInfo::speciesIndex(int j){
  for (int i=0; i<types; i++){
    j-=atomtypes[i].atomspertype;
    if (j<0) return i;
  }
  return -1;
}

int AtomInfo::getNatoms(){
  int Natoms=0;
  for (int i=0; i<types; i++){
    Natoms+=atomtypes[i].atomspertype;
  }
  return Natoms;
}

void AtomInfo::clean(){
  if (atomtypes!=NULL){
    free(atomtypes);
    atomtypes=NULL;
  }
  types=0;
  allocated=0;
}

void AtomInfo::setAtomInfo(AtomInfo *a){
  clean();
#if CHECK>0
  if (a==NULL){
    THROW_NP_EXC("NULL argument in AtomInfo::setAtomInfo(NULL)");
  }
#endif

#ifdef NO_THROW
  realloc(a->allocated);
#else  
  try{
    realloc(a->allocated);
  }
  catch(MemoryAllocationException){
    throw MemoryAllocationException(this,"realloc() failed in  setAtomInfo()");
  }  
#endif

  types=a->types;
  allocation_step=a->allocation_step;
  memcpy(atomtypes,a->atomtypes,sizeof(AtomtypesRecord)*types);
}

AtomInfo *AtomInfo::clone(){
  AtomInfo *a = new AtomInfo(this);
#if CHECK>0  
  if (a==NULL){
    THROW_MA_EXC("AtomInfo::clone() failed.");
  }
#endif
  return a;
}

void AtomInfo::delitem(int i){
  if (i<0){
    i+=types;
  }
#if CHECK>0
  if ((i<0)||(i>=types)){
    THROW_R_EXC("AtomInfo::delitem() index out of range.",0,types,i);
  }
  if (atomtypes==NULL){
    THROW_NP_EXC("atomtypes=NULL in AtomInfo::delitem().");
  }
#endif
  long count = types-i-1;
  if (count>0){
    memmove(&atomtypes[i],&atomtypes[i+1],sizeof(AtomtypesRecord)*count);
    types--;
  }
}

int AtomInfo::len(){
  return types;
}
