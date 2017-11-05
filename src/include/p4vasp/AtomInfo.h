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

#ifndef AtomInfo_h
#define AtomInfo_h
#include "AtomtypesRecord.h"
#include "ClassInterface.h"
#include "Exceptions.h"

/**
 * Array of AtomtypesRecords.
 * This class can hold several AtomtypesRecord structures and
 * provides access to them.
 *
 * There are reserved Atominfo::allocated AtomtypesRecords in the memory
 * (accessible through the AtomInfo::atomtypes pointer).
 * However, the actual array can be smaller. Its length is kept in the
 * AtomInfo::types variable. The array-elements can be accessed
 * through various functions (AtomInfo::getRecord(int), operator [])
 * which (can) perform index range checking.
 * New record(s) can be added using AtomInfo::append(AtomtypesRecord*)
 * and AtomInfo::allocate(int).
 */ 
class AtomInfo :public ClassInterface{
  public:

/// Returns "AtomInfo".
  virtual const char *getClassName();  

#ifdef SWIG
%immutable;
#endif

  /** Number of AtomtypeRecord records.
   * This is the number of "occupied" AtomtypeRecord records.
   */
  int types;

#ifndef SWIG  
  /// Pointer to the array of AtomtypeRecord records.
  AtomtypesRecord *atomtypes;  
  static AtomtypesRecord *default_record;
  
  /**
   * Count of allocated AtomtypeRecord records.
   * This is actual length of the AtomInfo::atomtypes array.
   * This has to be greater or equall to AtomInfo::types.
   */
  int allocated;
  /// A wrapper to AtomInfo::getRecord(int).
  AtomtypesRecord *operator[](int i){return getRecord(i);};
  /// Copy constructor.
  AtomInfo(AtomInfo *a);
#endif

  /**
   * Allocation step.
   * When more records are required than are available (AtomInfo::allocated),
   * e.g. by calling AtomInfo::append(AtomtypesRecord*),
   * then at least allocated+allocation_step AtomtypesRecords are allocated.
   */
  int allocation_step;

  /**
   * Constructor.
   * Optionally the number of allocated AtomtypesRecords can be specified.
   */
  AtomInfo(int alloc=16);

  virtual ~AtomInfo();

  /// Append one AtomtypesRecord.
  void append(AtomtypesRecord* r);

  /**
   * Reserve memory for alloc AtomtypesRecords.
   * If alloc==allocated, nothing happens
   * If alloc>types, the memory is reallocated and old AtomtypesRecords
   * are copied.
   * If alloc<types, the memory is reallocated and first alloc old AtomtypesRecords
   * are copied, AtomInfo::types is set to alloc.
   * If alloc==0, memory is cleaned, AtomInfo::types and AtomInfo::allocated
   * is set to zero and AtomInfo::atomtypes is set to NULL.
   */ 
  void realloc(int alloc);

  /**
   * Allocate n AtomtypesRecords.
   * Calls AtomInfo::realloc(int) if necessary and sets AtomInfo::types to n.
   */
  void allocate(int n);

  /**
   * Returns the i-th AtomtypesRecord.
   */
  AtomtypesRecord *getRecord(int i);
  
  /**
   * Set the i-th AtomtypesRecord to value.
   * The value is copied.
   */
  void setRecord(int i,AtomtypesRecord *value);
  
  /**
   * Returns the AtomtypesRecord for the i-th atom.
   * The same as getRecord(speciesIndex(i)).
   */
  AtomtypesRecord *getRecordForAtom(int i);

  /**
   * Returns the AtomtypesRecord with element==x.
   */
  AtomtypesRecord *getRecordForElement(const char *x);

  /**
   * Returns the AtomtypesRecord with element==x.
   * When such record is not found, return i-th record (i%min(types,m)).
   * (m=-1 acts like m=types)
   * When there is no record available, returns AtomInfo::default_record.
   */
  AtomtypesRecord *getRecordForElementSafe(const char *x,int i,int m);
  
  /**
   * Get species index for atom j.
   */
  int speciesIndex(int j);
  
  /**
   * Count the number of atoms.
   */
  int getNatoms();
  
  /**
   * Sets the content to a.
   */
  void setAtomInfo(AtomInfo *a);
  
  /**
   * Free memory and set the AtomInfo::types and AtomInfo::allocated to 0.
   */
  void clean();
  
  /**
   * Return a copy of this.
   */
  AtomInfo *clone();

  /**
   * Detele record i.
   */
  void delitem(int i);
  
  /**
   * Returns the length of AtomInfo
   * (this is AtomInfo::types)
   */
  int len();

  /* Fills in the attributes mass, radius, covalent, red, green and blue
   * from the table (argument) according to "element" field (or more exactly
   * hash field).
   */
  void fillAttributesWithTable(AtomInfo *table);
    
};

#endif
