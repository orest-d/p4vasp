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

#include <p4vasp/AtomtypesRecord.h>
#include <stdio.h>
#include <p4vasp/utils.h>
#include <p4vasp/Exceptions.h>

const char *AtomtypesRecord::getClassName(){
  return "AtomtypesRecord";
}

AtomtypesRecord::AtomtypesRecord(){
#if VERBOSE>1
  printf("AtomtypesRecord::AtomtypesRecord() (constructor) %p\n",this);
#endif
  clean();
}

AtomtypesRecord::AtomtypesRecord(AtomtypesRecord *a){
  setAtomtypesRecord(a);
}

AtomtypesRecord::~AtomtypesRecord(){
#if VERBOSE>1
  printf("AtomtypesRecord::~AtomtypesRecord() (destructor) %p\n",this);
#endif
}



char *AtomtypesRecord::getElement(){
#if VERBOSE>1
  printf("AtomtypesRecord::getElement() -> '%s'\n",element);
#endif
  return element;
}

long getAtomtypesRecordHash(const char *s){
  long hash=0L;
  long ofs=16777216L;
  for (int i=0; (i<4); i++){
    if ((s[i]=='\0')||(s[i]==' ')) break;
    hash+=s[i]*ofs;
    ofs/=256;
  }
  return hash;
}

void AtomtypesRecord::setElement(const char *s){
#if VERBOSE>1
  printf("AtomtypesRecord::setElement(%s)\n",s);
#endif
  for (int i=0; (i<4); i++){
    element[i]=s[i];
    if (s[i]=='\0') break;
  }
  element[4]='\0';
  element[5]='\0';
  hash=getAtomtypesRecordHash(s);
#if VERBOSE>1
  printf("AtomtypesRecord::setElement(%s) -> element='%s' hash=%ld\n",s,element,hash);
#endif
}  

char *AtomtypesRecord::getPPType(){
#if VERBOSE>1
  printf("AtomtypesRecord::getPPType() -> '%s'\n",pp_type);
#endif
  return pp_type;
}
char *AtomtypesRecord::getPPSpecie(){
#if VERBOSE>1
  printf("AtomtypesRecord::getPPSpecie() -> '%s'\n",pp_specie);
#endif
  return pp_specie;
}
char *AtomtypesRecord::getPPVersion(){
#if VERBOSE>1
  printf("AtomtypesRecord::getPPVersion() -> '%s'\n",pp_version);
#endif
  return pp_version;
}

char *AtomtypesRecord::getPseudopotential(){
#if VERBOSE>1
  printf("AtomtypesRecord::getPseudopotential() -> '%s'\n",pseudopotential);
#endif
  return pseudopotential;
}

void AtomtypesRecord::setPPType(char *s){
#if VERBOSE>1
  printf("AtomtypesRecord::setPPType(%s)\n",s);
#endif
  if (s!=NULL){
    if (s[0]=='\0'){
      pp_type[0]='?';
      pp_type[1]='\0';
    }
    else{  
      for (int i=0; (i<24); i++){
	pp_type[i]=s[i];
	if (s[i]=='\0') break;
      }
      pp_type[23]='\0';
    }
    snprintf(pseudopotential,99,"%s %s %s",pp_type,pp_specie,pp_version);
    pseudopotential[99]='\0';
  }
}
void AtomtypesRecord::setPPSpecie(char *s){
#if VERBOSE>1
  printf("AtomtypesRecord::setPPSpecie(%s)\n",s);
#endif
  if (s!=NULL){
    if (s[0]=='\0'){
      pp_specie[0]='?';
      pp_specie[1]='\0';
    }
    else{  
      for (int i=0; (i<12); i++){
	pp_specie[i]=s[i];
	if (s[i]=='\0') break;
      }
      pp_specie[11]='\0';
    }
    snprintf(pseudopotential,99,"%s %s %s",pp_type,pp_specie,pp_version);
    pseudopotential[99]='\0';
  }
}

void AtomtypesRecord::setPPVersion(char *s){
#if VERBOSE>1
  printf("AtomtypesRecord::setPPVersion(%s)\n",s);
#endif
  if (s!=NULL){
    if (s[0]=='\0'){
      pp_type[0]='?';
      pp_type[1]='\0';
    }
    else{  
      for (int i=0; (i<48); i++){
	pp_version[i]=s[i];
	if (s[i]=='\0') break;
      }
      pp_version[47]='\0';
    }
    snprintf(pseudopotential,99,"%s %s %s",pp_type,pp_specie,pp_version);
    pseudopotential[99]='\0';
  }
}

void AtomtypesRecord::setPseudopotential(char *s){
#if VERBOSE>1
  fprintf(stderr,"AtomtypesRecord::setPseudopotential(%s)\n",s);
#endif
  if (s!=NULL){
    char *S=::clone(s);
#if CHECK>0
    if (S==NULL){
      THROW_MA_EXC("clone(s) returns NULL in "
                   "AtomtypesRecord::setPseudopotential().");
    }
#endif
    char **v=splitWords(S);
#if CHECK>0
    if (v==NULL){
      THROW_MA_EXC("splitWords(s) returns NULL in "
                   "AtomtypesRecord::setPseudopotential()");
    }
#endif
    if (v==NULL){
      setPPType("?");
      setPPSpecie("?");
      setPPVersion("?");
    }
    else{    
      if (v[0]!=NULL){
	setPPType(v[0]);
	if (v[1]!=NULL){
	  setPPSpecie(v[1]);
	  if (v[2]!=NULL){
            setPPVersion(v[2]);
	  }
	  else{
            setPPVersion("?");
	  }
	}
	else{
	  setPPSpecie("?");
	  setPPVersion("?");
	}
      }
      else{
	setPPType("?");
	setPPSpecie("?");
	setPPVersion("?");
      }
    }
    if (v!=NULL){
      delete v;
    }
    if (S!=NULL){
      delete S;
    }
  }
}


void AtomtypesRecord::clean(){
#if VERBOSE>1
  printf("AtomtypesRecord::clean()\n");
#endif
  hash=0;
  element[0]='\0';
  element[1]='\0';
  element[2]='\0';
  element[3]='\0';
  element[4]='\0';
  atomspertype=0;
  mass=0.0;
  valence=0.0;
  for(int i=0;i<100;i++){
    pseudopotential[i]='\0';
  }
  radius=0.0;
  covalent=0.0;
  n=0;
  red          =0.0;
  green        =0.0;
  blue         =0.0;  
  pp_type[0]   ='\0';
  pp_specie[0] ='\0';
  pp_version[0]='\0';
  hidden       =0;
  selected     =0;
}

void AtomtypesRecord::setAtomtypesRecord(AtomtypesRecord *a){
  memcpy(this,a,sizeof(AtomtypesRecord));
}

AtomtypesRecord *AtomtypesRecord::clone(){
  AtomtypesRecord *a = new AtomtypesRecord(this);
#if CHECK>0  
  if (a==NULL){
    THROW_MA_EXC("AtomtypesRecord::clone() failed.\n");
  }
#endif
  return a;
}
