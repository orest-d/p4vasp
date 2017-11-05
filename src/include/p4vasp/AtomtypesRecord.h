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

#ifndef AtomtypesRecord_h
#define AtomtypesRecord_h
#include "ClassInterface.h"

long getAtomtypesRecordHash(const char *s);

/**
 * This class holds the atomtype informations:
 * element,
 * atoms per type,
 * mass,
 * valence,
 * pseudopotential informations (type, specie, version),
 * covalent radius,
 * ball radius,
 * ball color (red, green and blue components in range 0.0-1.0),
 * hidden flag,
 * selected flag.
 */
class AtomtypesRecord : public ClassInterface{
  public:
  ///Returns "AtomtypesRecord".
  virtual const char *getClassName();
  
  AtomtypesRecord();
  virtual ~AtomtypesRecord();
  ///Should contain hash value computed from AtomtypesRecord::element.
  long hash;
#ifndef SWIG
  AtomtypesRecord(AtomtypesRecord *a);
  ///Element name
  char element[6];
#endif
  ///Number of atoms per type
  int atomspertype;
  ///Mass (in a.u.)
  float mass;
  ///Valence
  float valence;
#ifndef SWIG
  ///Pseudopotential type  (e.g. PAW_GGA)
  char pp_type[24];
  ///Pseudopotential specie  (e.g. C_s)
  char pp_specie[12];
  ///Pseudopotential version  (in the form of a datum)
  char pp_version[48];
  ///Buffer for holding joined pseudopotential information
  char pseudopotential[100];
#endif  
  ///Ball radius
  float radius;
  ///Covalent radius
  float covalent;
  ///n
  int n;
  ///Red color component in range 0.0 - 1.0
  float red;
  ///Green color component in range 0.0 - 1.0
  float green;
  ///Blue color component in range 0.0 - 1.0
  float blue;  
  
  ///Flag used by Drawer - if true, the atom is invisible
  int hidden;
  
  ///Flag used in selection routines - if true, atom is selected
  int selected;

  ///Function for getting the element name
  char *getElement();
  ///Function for setting the element name
  void setElement(const char *s);
  ///Function for getting the pseudopotential type
  char *getPPType();
  ///Function for getting the pseudopotential specie
  char *getPPSpecie();
  ///Function for getting the pseudopotential version
  char *getPPVersion();
  ///Function for getting the pseudopotential (joined)
  char *getPseudopotential();

  ///Function for setting the pseudopotential type
  void setPPType(char *s);
  ///Function for setting the pseudopotential specie
  void setPPSpecie(char *s);
  ///Function for setting the pseudopotential version
  void setPPVersion(char *s);
  ///Function for setting the pseudopotential (separated by whitespace)
  void setPseudopotential(char *s);
  
  ///Fill the record with default values.
  void clean();
  ///Set the content to a.
  void setAtomtypesRecord(AtomtypesRecord *a);
  ///Get a pointer to a copy of this.
  AtomtypesRecord *clone();
};

#endif
