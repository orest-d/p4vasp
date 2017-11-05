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

#ifndef Structure_h
#define Structure_h
#include <stdio.h>
#include "AtomInfo.h"
#include "ClassInterface.h"
#include "Exceptions.h"

/**
 * Structure encapsulates the structural information:
 * cell basis, information about atom types (AtomInfo)
 * and atomic positions.
 * It also defines several methods for manipulating the structure,
 * direct/carthesian coordinates conversion, reading and writing POSCAR
 * files and so on...
 */
class Structure : public ClassInterface{
  public:

  ///Returns "Structure".
  virtual const char *getClassName();
#ifdef SWIG
%mutable;
#endif
  /**
   * Scaling flag.
   * Contains 1 or 3, depending on the number of scaling coeficients
   * in the 2nd line of the POSCAR file.
   */
  int scaling_flag;
  /**
   * Allocation increment step.
   * When more position (and selective) vectors are required than are available
   * (Structure::allocated),
   * e.g. by calling Structure::append(double*),
   * then at least allocated+allocation_step AtomtypesRecords are allocated.
   */
  int allocation_step;
#ifdef SWIG
%immutable;
#endif
  /**
   * Scaling scalar/vector
   * contains scaling values from the 2nd line of POSCAR (1.0 by default).
   */
  double scaling[3];
  /// Basis vectors
  double basis[9];
  /// Reciprocal basis vectors
  double rbasis[9];
  /// Total number of atoms
  int total_number_of_atoms;
  /// Memory is allocated for Structure::allocated atoms.
  int allocated;
  /// Pointer to AtomInfo.
  AtomInfo *info;
  
#ifndef SWIG
  /// Pointers to basis vectors
  double *basis1,*basis2,*basis3;
  /// Pointers to reciprocal basis vectors
  double *rbasis1,*rbasis2,*rbasis3;
  /// Array containing the atom positions.
  double *positions;
  /**
   * Array containing the selective flags or NULL
   * when no selective information is available.
   * (Structure::isSelective() is false).
   */
  int  *selective;
  ///Buffer containing the matrix with minimum distances.
  double *mindist_matrix;
#endif

#ifdef SWIG
%mutable;
#endif

  ///Comment line.
  char *comment;
  /**
   * Coordinates switch.
   * can contain string starting with 'c' or 'k' (carthesian),
   * 'd' (direct coordinates)
   * or NULL (means direct coordinates).
   * The case is not important.
   */
  char *coordinates;

  Structure();
  Structure(Structure *s);
  virtual ~Structure();
#ifndef SWIG   
  /**
   * Read POSCAR from string.
   * String argument is destroyed, but not deleted.
   */
  int parse_destructively(char *s);
#endif   
  /**
   * Correct the scaling factors (second POSCAR line) such that scale=1.0.
   */
  void correctScaling();
  /**
   * Read POSCAR from string.
   * String argument is not destroyed.
   */
  int parse(const char *s);
  ///Read POSCAR from file.
  int read(char *path);
  ///Write as a POSCAR to file.
  int write(char *path);
  /**
   * Returns POSCAR as a string.
   */
  const char *toString();
  
#ifndef SWIG  
  ///Create Structure from a POSCAR file (given by path).
  Structure(char *path);
  ///Create Structure from a POSCAR file.
  Structure(FILE *);
  /**
   * Parse a POSCAR file split to lines.
   * lines is an array of pointers to lines
   * pos is the index of the starting line
   * Positive allocate instructs to allocate space at least for
   * 'allocate' atoms.
   */
  int parse(char **lines,int pos=0,int allocate = -1);
  /// Read Structure from POSCAR file.
  int read(FILE *f);
  /// Write Structure as a POSCAR file.
  int write(FILE *f);
#endif


  /// Returns true if containing selective dynamics
  int isSelective();

  /// Returns true if in Carthesian coordinates
  int isCarthesian();

  /// Returns true if in Direct coordinates
  int isDirect();

  /// Returns the value of selective for i-th degree of freedom
  int getSelectiveDOF(int i);

  /// Sets the value of selective for i-th degree of freedom
  void setSelectiveDOF(int i,int value);
  
  /**
   * Controls the selective dynamics.
   * If the argument is false, selective dynamics flags are erased
   * and the array containing the selective dynamics informations
   * (Structure::selective) is deleted.
   * If the argument is true, and the selective array already exists,
   * nothing happens (values are not affected).
   * If the array does not exist, it is created and filled with 1.
   */
  void setSelective(int flag);
  
//  int speciesIndex(int index);

  /**
   * Updates and returns the reciprocal basis.
   * this should be called, when the Structure::basis is changed.
   */
  double *updateRecipBasis();

  /// The same as Structure::updateRecipBasis()
  double *getRecipBasis();

  /**
   * Converts positions from direct to Carthesian coordinates,
   * event when already in carthesian.
   * This function should be probably never used directly.
   */
  void forceConvertToCarthesian();

  /**
   * Converts positions from Carthesian to direct coordinates,
   * event when already in direct.
   * This function should be probably never used directly.
   */
  void forceConvertToDirect();

  /**
   * Set Carthesian coordinates.
   * According to the value of the argument
   * converts to Carthesian (true) or direct (false) coordinates
   * if necessary.
   */   
  void setCarthesian(int flag=1);

  /**
   * Set direct coordinates.
   * According to the value of the argument
   * converts to direct (true) or Carthesian (false) coordinates
   * if necessary.
   */   
  void setDirect(int flag=1);
  
#ifndef SWIG  
  inline double *operator[](int i);
  double *dir2cart(double *dest);
  double *cart2dir(double *dest);
  double *dirVectorToUnitCell(double *v);
  double *dirVectorToCenteredUnitCell(double *v);
  double *cartVectorToUnitCell(double *v);
  double *cartVectorToCenteredUnitCell(double *v);
  double *vectorToUnitCell(double *v);
  double *vectorToCenteredUnitCell(double *v);
#endif
  
  /// Convert direct vector to carthesian
  double *dir2cart(double *dest,double *src);
  /// Convert carthesian vector to direct
  double *cart2dir(double *dest,double *src);
  double *dirVectorToUnitCell(double *dest, double *v);
  double *dirVectorToCenteredUnitCell(double *dest, double *v);
  double *cartVectorToUnitCell(double *dest, double *v);
  double *cartVectorToCenteredUnitCell(double *dest, double *v);
  double *vectorToUnitCell(double *dest,double *v);
  double *vectorToCenteredUnitCell(double *dest,double *v);

//  int realloc(int n);
//  int allocate(int n);
  
  void toUnitCell();
  void toCenteredUnitCell();
  double mindistCartVectors(double *a, double *b);
  double mindistDirVectors(double *a, double *b);
  double *createMindistMatrix();
//  void createAtomTypesTable();
  void deleteMindistMatrix();
  double getMindist(int i,int j);

//  void setPotcar(FILE *f);
//  void setPotcar(char *path="POTCAR");

  void clean();
  void setStructure(Structure *p);
  Structure *clone();
//  long createHalfBondsList(double *vecbuff,int *index,long limit,double factor=1.0,int countbonds=0);
//  long countHalfBonds(double factor=1.0){
//    return createHalfBondsList(NULL,NULL,0,factor,1);
//  }

  int len();
  
  int getNumberOfSpecies();
  AtomtypesRecord *getRecord(int i);


  double *get(int i);
  void set(int i,double x,double y,double z);

  void allocate(int n);
  void realloc(int alloc);
  void append(double x, double y, double z);
#ifndef SWIG  
  void append(double *v);
#endif  
  void delitem(int i);
  void setScaling(int i,double x){
    if ((scaling_flag==1) && (i==0)){
      scaling[0]=x;
    }
    else if ((scaling_flag==3) && (i>=0) && (i<3)){
      scaling[i]=x;
    }
    else{
      printf("Warning: Structure::setScaling(%d,%f) scaling_flag=%d\n",
      i,x,scaling_flag);
    }
  }
  
  protected:
    char *toString_buffer;
    
  
};

#ifndef SWIG
inline double *Structure::operator[](int i){
#if CHECK>1
  if (positions==NULL){
    THROW_NP_EXC("positions=NULL found in Structure.operator[]");
  }
  if ((i<0) || (i>=total_number_of_atoms)){
    THROW_R_EXC("Structure::operator [] failed.",0,total_number_of_atoms,i);
  }
#endif
  return &positions[3*i];
}
#endif

#endif
