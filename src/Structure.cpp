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
#include <ctype.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <p4vasp/utils.h>
#include <p4vasp/vecutils.h>
#include <p4vasp/AtomInfo.h>
#include <p4vasp/Structure.h>
#include <locale.h>


const char *Structure::getClassName(){
  return "Structure";
}

Structure::Structure(){
  comment=::clone("generic Structure file");
  scaling[0]=1.0;
  scaling_flag=1;
  basis1=&basis[0];
  basis2=&basis[3];
  basis3=&basis[6];
  rbasis1=&rbasis[0];
  rbasis2=&rbasis[3];
  rbasis3=&rbasis[6];
  basis1[0]=1.0;
  basis1[1]=0.0;
  basis1[2]=0.0;
  basis2[0]=0.0;
  basis2[1]=1.0;
  basis2[2]=0.0;
  basis3[0]=0.0;
  basis3[1]=0.0;
  basis3[2]=1.0;
  total_number_of_atoms = 0;
  allocated         = 0;
  allocation_step   = 8;

  coordinates       = NULL;
  positions         = NULL;
  selective         = NULL;
  mindist_matrix    = NULL;
  info              = new AtomInfo();
  toString_buffer   = NULL;
  if (info==NULL){
    THROW_MA_EXC("new AtomInfo() failed in Structure::Structure();");
  }
}

Structure::Structure(Structure *p){
#if VERBOSE>0
  printf("Structure::Structure(Structure *p)\n");
#endif
  comment=NULL;

  total_number_of_atoms = 0;
  allocated       = 0;

  scaling[0]=1.0;
  scaling_flag=1;
  basis1=&basis[0];
  basis2=&basis[3];
  basis3=&basis[6];
  rbasis1=&rbasis[0];
  rbasis2=&rbasis[3];
  rbasis3=&rbasis[6];
  basis1[0]=1.0;
  basis1[1]=0.0;
  basis1[2]=0.0;
  basis2[0]=0.0;
  basis2[1]=1.0;
  basis2[2]=0.0;
  basis3[0]=0.0;
  basis3[1]=0.0;
  basis3[2]=1.0;
  allocation_step   = 8;

  coordinates       = NULL;
  positions         = NULL;
  selective         = NULL;
  mindist_matrix    = NULL;
  info              = new AtomInfo();
  toString_buffer   = NULL;

  if (info==NULL){
    THROW_MA_EXC("new AtomInfo() failed in Structure::Structure(Structure *);");
  }

  if (p->comment!=NULL){
    comment = ::clone(p->comment);
  }
  memcpy(&scaling[0],&p->scaling[0],3*sizeof(double));
  memcpy(&basis[0],&p->basis[0],9*sizeof(double));
  basis1=&basis[0];
  basis2=&basis[3];
  basis3=&basis[6];
  memcpy(&rbasis[0],&p->rbasis[0],9*sizeof(double));
  rbasis1=&rbasis[0];
  rbasis2=&rbasis[3];
  rbasis3=&rbasis[6];
  info->setAtomInfo(p->info);
  if (p->coordinates!=NULL){
    coordinates=::clone(p->coordinates);
  }
  else{
    coordinates=NULL;
  }
  total_number_of_atoms=p->total_number_of_atoms;
  allocated=p->allocated;
#if CHECK>1
  if (allocated<total_number_of_atoms){
    char s[256];
    snprintf(s,250,"allocated<total_number_of_atoms in Structure::setStructure(); allocated=%d, total_number_of_atoms=%d\n",
      allocated,total_number_of_atoms);
    THROW_MA_EXC(s);
  }
  if (allocated<0){
    THROW_MA_EXC("allocated<0 in Structure::setStructure();");
  }
#endif
  if (allocated==0){
    positions=NULL;
  }
  else{
    positions=new double[3*allocated];
    memcpy(positions,p->positions,3*total_number_of_atoms*sizeof(double));
  }
  if (p->selective != NULL){
    selective = new int[3*allocated];
    memcpy(selective,p->selective,3*total_number_of_atoms*sizeof(int));
  }
#if VERBOSE>0
  printf("Structure::Structure(Structure *p) -\n");
#endif
}

Structure::Structure(char *path){
  scaling[0]=1.0;
  scaling_flag=1;
  basis1=&basis[0];
  basis2=&basis[3];
  basis3=&basis[6];
  rbasis1=&rbasis[0];
  rbasis2=&rbasis[3];
  rbasis3=&rbasis[6];
  allocated             = 0;
  allocation_step       = 8;
  total_number_of_atoms = 0;
  positions             = NULL;
  selective             = NULL;
  toString_buffer       = NULL;
  info                  = new AtomInfo();
  if (info==NULL){
    THROW_MA_EXC("new AtomInfo() failed in Structure::Structure(path);");
  }
  mindist_matrix        = NULL;
  this->read(path);
}

Structure::Structure(FILE *file){
  scaling[0]=1.0;
  scaling_flag=1;
  basis1=&basis[0];
  basis2=&basis[3];
  basis3=&basis[6];
  rbasis1=&rbasis[0];
  rbasis2=&rbasis[3];
  rbasis3=&rbasis[6];
  allocated             = 0;
  allocation_step       = 8;
  total_number_of_atoms = 0;
  positions             = NULL;
  selective             = NULL;
  toString_buffer       = NULL;
  info                  = new AtomInfo();
  if (info==NULL){
    THROW_MA_EXC("new AtomInfo() failed in Structure::Structure(FILE *);");
  }
  mindist_matrix        = NULL;
  this->read(file);
}

void Structure::clean(){
#if VERBOSE>1
  fprintf(stderr,"Structure::clean()\n");
#endif
  if (comment != NULL){
    delete []comment;
    comment=NULL;
  }
  total_number_of_atoms = 0;
  allocated       = 0;
  if (coordinates != NULL){
    delete []coordinates;
  }
  coordinates=NULL;
  if (positions!=NULL){
    delete []positions;
    positions=NULL;
  }
  if (selective!=NULL){
    delete []selective;
    selective=NULL;
  }
  if (toString_buffer!=NULL){
    delete []toString_buffer;
    toString_buffer=NULL;
  }
  if (mindist_matrix!=NULL){
    delete []mindist_matrix;
    mindist_matrix=NULL;
  }
  if (info!=NULL){
//    info->types=0;
    info->clean();
  }
}

Structure::~Structure(){
#if VERBOSE>1
  fprintf(stderr,"Structure::~Structure() (destructor)\n");
#endif
  clean();
  if (info!=NULL){
    delete info;
    info=NULL;
  }
}


void Structure::correctScaling(){
  int flag=isCarthesian();
  if (scaling_flag==1){
    setDirect();
    double s;
    if (scaling[0]>=0.0){
      s=scaling[0];
    }
    else{
      double buff[3];
      double V=scalmul3(basis1,cross(buff,basis2,basis3));
      s=pow(fabs(scaling[0]/V),1.0/3.0);
    }
    mul3(basis1,s);
    mul3(basis2,s);
    mul3(basis3,s);
    scaling[0]=1.0;
    updateRecipBasis();
    if (flag){
      setCarthesian();
    }
  }
  else if (scaling_flag==3){
    setDirect();
    mul3(basis1,scaling[0]);
    mul3(basis2,scaling[1]);
    mul3(basis3,scaling[2]);
    scaling[0]=1.0;
    scaling[1]=1.0;
    scaling[2]=1.0;
    scaling_flag=1;
    updateRecipBasis();
    if (flag){
      setCarthesian();
    }
  }
}

int Structure::read(char *path){
  char *s=loadFile(path);
  int f=parse_destructively(s);
  delete s;
  return f;
}

int Structure::read(FILE *f){
  char **words;
  char **lines;
  char *commentline;
  char *scaleline;
  char *basis1line;
  char *basis2line;
  char *basis3line;
  char *atomsline;
  char *speciesline;
  char *specieslinecopy;
  char *stripspeciesline;
  commentline=getLine(f);
#if CHECK>0
  if (commentline==NULL){
    THROW_EXC("Error reading the Structure comment line. (1)");
  }
#endif
  scaleline=getLine(f);
#if CHECK>0
  if (scaleline==NULL){
    THROW_EXC("Error reading the Structure scale line. (2)");
  }
#endif
  basis1line=getLine(f);
#if CHECK>0
  if (basis1line==NULL){
    THROW_EXC("Error reading the Structure 1st basis line. (3)");
  }
#endif
  basis2line=getLine(f);
#if CHECK>0
  if (basis2line==NULL){
    THROW_EXC("Error reading the Structure 2nd basis line. (4)");
  }
#endif
  basis3line=getLine(f);
#if CHECK>0
  if (basis3line==NULL){
    THROW_EXC("Error reading the Structure 3rd basis line. (5)");
  }
#endif
  speciesline=getLine(f);
#if CHECK>0
  if (speciesline==NULL){
    THROW_EXC("Error reading the Structure species/atoms line. (6)");
  }
#endif
  stripspeciesline=lstrip(speciesline);
  if (isalpha(stripspeciesline[0])){
    atomsline=speciesline;
    speciesline=getLine(f);
#if CHECK>0
    if (speciesline==NULL){
      THROW_EXC("Error reading the Structure species line. (7)");
    }
#endif
  }
  else{
    atomsline=NULL;
  }

  specieslinecopy=::clone(speciesline);
  words=splitWords(specieslinecopy);
  int nspec=arrayLength(words);
  int natoms=0;
  for (int i=0;i<nspec;i++){
    natoms+=atoi(words[i]);
  }
  delete []words;
  delete []specieslinecopy;


  lines=new char *[9+natoms];
  if (lines==NULL){
    THROW_MA_EXC("Buffer allocation failed in Structure::read(...)");
  }

  lines[0]=commentline;
  lines[1]=scaleline;
  lines[2]=basis1line;
  lines[3]=basis2line;
  lines[4]=basis3line;
  int p;
  if (atomsline==NULL){
    lines[5]=speciesline;
    p=6;
  }
  else{
    lines[5]=atomsline;
    lines[6]=speciesline;
    p=7;
  }
  for (int i=0; i<(natoms+1); i++){
    lines[i+p]=getLine(f);
  }
  lines[natoms+1+p]=NULL;
  int rpar=parse(lines);
  for (int i=0; i<(natoms+1+p); i++){
    if (lines[i]!=NULL){
      delete lines[i];
    }
  }
  delete []lines;
  return rpar;
}


int Structure::parse(const char *s){
  char *buff=::clone(s);
  int r = parse_destructively(buff);
  delete []buff;
  return r;
}

int Structure::parse_destructively(char *s){
  char **lines;
  lines=splitLines(s);
  int r=parse(lines);
#if CHECK>0
  if (lines!=NULL){
    delete []lines;
  }
#else
  delete []lines;
#endif
  return r;
}

int Structure::parse(char **lines,int pos,int allocate){
  char **words;
  char *s;
  long count;
  setlocale (LC_ALL,"C");

  long nlines = arrayLength(lines);
  clean();

  /*********************** COMMENT *************************************/
  if (pos>=nlines){
    THROW_EXC("Structure.parse() end of file. (in comment)");
  }
  comment=::clone(rstrip(lines[pos]));
  pos++;

  /*********************** SCALING *************************************/
  if (pos>=nlines){
    THROW_EXC("Structure.parse() end of file. (in scaling factors)");
  }
  words  = splitWords(lines[pos]);
  count  = arrayLength(words);
  if (count==1){
    scaling[0]=atof(words[0]);
    scaling_flag=1;
  }
  else if (count>=3){
    scaling[0]=atof(words[0]);
    scaling[1]=atof(words[1]);
    scaling[2]=atof(words[2]);
    scaling_flag=3;
  }
  else{
    char s[256];
    snprintf(s,250,"Structure.parse() error reading scaling factors:\n%s\n",lines[pos]);
    THROW_EXC(s);
  }
  pos++;
  delete words;

  /*********************** basis *************************************/
  for (int i=0; i<3;i++){
    if (pos>=nlines){
      char s[256];
      snprintf(s,250,"Structure.parse() end of file. (in basis %d)\n",i+1);
      THROW_EXC(s);
    }
    words = splitWords(lines[pos]);
    count=arrayLength(words);
    if (count<3){
      char s[256];
      snprintf(s,250,"Structure.parse() error reading basis vector %d:\n%s\n",i+1,lines[pos]);
      THROW_EXC(s);
    }
    basis[3*i+0]=atof(words[0]);
    basis[3*i+1]=atof(words[1]);
    basis[3*i+2]=atof(words[2]);
    pos++;
    delete words;
  }

  /*********************** ATOMS *************************************/
  char *atom_string=NULL;
  char **atom=NULL;
  if (pos>=nlines){
    THROW_EXC("Structure.parse() end of file. (in atoms/species)");
  }
  s=strip(lines[pos]);
  if (isalpha(s[0])){
    atom_string=::clone(s);
    atom=splitWords(atom_string);
    pos++;
    if (pos>=nlines){
      THROW_EXC("Structure.parse() end of file. (in species)");
    }
    s=strip(lines[pos]);
  }

  /*********************** SPECIES *************************************/
  words = splitWords(s);
  int number_of_species = arrayLength(words);
  if (info==NULL){
    info=new AtomInfo(number_of_species);
#if CHECK>0
    if (info==NULL){
      THROW_MA_EXC("new AtomInfo() failed in Structure::parse(...)");
    }
#endif
  }

  info->allocate(number_of_species);
  total_number_of_atoms=0;
  if (atom!=NULL){
    if (arrayLength(atom)<number_of_species){
      fprintf(stderr,
      "Warning: not enough atoms in POSCAR, atoms line ignorred.\n");
      delete atom;
      atom=NULL;
      if (atom_string!=NULL){
        delete atom_string;
        atom_string=NULL;
      }
    }
  }
  for (int i=0; i<number_of_species;i++){
    int x=atoi(words[i]);
    total_number_of_atoms+=x;
    info->getRecord(i)->atomspertype=x;
    if (atom!=NULL){
      info->getRecord(i)->setElement(atom[i]);
    }
  }
  if (atom!=NULL){
    delete atom;
    atom=NULL;
  }
  if (atom_string!=NULL){
    delete atom_string;
    atom_string=NULL;
  }

  pos++;
  delete words;

  /*********************** COORDINATES TYPE/SELECTIVE *************************************/
  if (pos>=nlines){
    THROW_EXC("Structure.parse() end of file. (positions type/selective)");
  }
  s=strip(lines[pos]);
  if (s[0]=='\0'){
    THROW_EXC("Structure.parse(): Empty line, where 'Carthesian', 'Direct' or 'Selective' is expected.");
  }
  int selective_flag=0;
  if (toupper(s[0])=='S'){
    selective_flag=1;
    pos++;
    if (pos>=nlines){
      THROW_EXC("Structure.parse() end of file. (coord type)");
    }
    s=strip(lines[pos]);
  }
  else{
    selective_flag=0;
  }

  /*********************** COORD TYPE *************************************/
  if (s[0]=='\0'){
    THROW_EXC("Structure.parse(): Empty line, where 'Carthesian' or 'Direct' is expected.");
  }
  switch(s[0]){
    case 'C':
    case 'c':
    case 'K':
    case 'k':
    case 'D':
    case 'd':
      coordinates=::clone(s);
      break;
    default:{
      char s[256];
      snprintf(s,250,"Structure.parse():  'Carthesian' or 'Direct' is expected, '%s' found instead.",s);
      THROW_EXC(s);
    }
  }
  pos++;

  /*********************** COORDINATES *************************************/
  allocated=total_number_of_atoms;
  if (allocate>allocated){
    allocated=allocate;
  }
  positions=new double[3*allocated];

#if CHECK>0
  if (positions==NULL){
    char s[256];
    snprintf(s,250,"Memory allocation error in Structure.parse() (array of coordinates) Natoms=%d\n",total_number_of_atoms);
    THROW_MA_EXC(s);
  }
#endif

  if (selective_flag){
    selective=new int[3*allocated];
#if CHECK>0
    if (selective==NULL){
      char s[256];
      snprintf(s,250,"Memory allocation error in Structure.parse() (array of selective) Natoms=%d\n",total_number_of_atoms);
      THROW_MA_EXC(s);
    }
#endif
  }

  for (int i=0; i<total_number_of_atoms; i++){
    if (pos>=nlines){
      THROW_EXC("Structure.parse() end of file. (coordinates)");
    }
    words  = splitWords(lines[pos]);
    count  = arrayLength(words);
    if (count<3){
      char s[256];
      snprintf(s,250,"Structure.parse() error reading coordinate vector %d:\n%s\n",i+1,lines[pos]);
      THROW_EXC(s);
    }
    positions[3*i+0]=atof(words[0]);
    positions[3*i+1]=atof(words[1]);
    positions[3*i+2]=atof(words[2]);
    if (isSelective()){
      if (count<6){
        char s[256];
        snprintf(s,250,"Structure.parse() error reading selective flags for atom %d:\n%s\n",i+1,lines[pos]);
        THROW_EXC(s);
      }
      for (int j=0; j<3; j++){
        char c=words[j+3][0];
        if (c=='.'){
          c=words[j+3][1];
        }
        if (toupper(c)=='T'){
          selective[3*i+j]=1;
        }
        else{
          selective[3*i+j]=0;
        }
      }
    }
    pos++;
    delete words;
  }
//  createAtomTypesTable();
  updateRecipBasis();

  return 0;

}


int Structure::write(FILE *f){
  fprintf(f,"%s\n",comment);
  if (scaling_flag==1){
    fprintf(f,"%f\n",scaling[0]);
  }
  else{
    fprintf(f,"%12.8f %12.8f %12.8f\n",scaling[0],scaling[1],scaling[2]);
  }
  for (int i=0; i<3; i++){
    fprintf(f,"%+14.10f %+14.10f %+14.10f\n",basis[3*i+0],basis[3*i+1],basis[3*i+2]);
  }
  if (info==NULL){
    fprintf(f," 0\n");
  }
  else{
    for (int i=0; i<getNumberOfSpecies(); i++){
      fprintf(f," %d",info->getRecord(i)->atomspertype);
    }
    fprintf(f,"\n");
  }
  if (isSelective()){
    fprintf(f,"Selective\n");
  }
#if CHECK>0
  if (positions==NULL){
    THROW_NP_EXC("Structure.positions=NULL in Structure.write().");
  }
#endif
  if (coordinates==NULL){
    fprintf(f,"Direct\n");
  }
  else{
    fprintf(f,"%s\n",coordinates);
  }
  for (int i=0; i<total_number_of_atoms; i++){
    fprintf(f,"%+14.10f %+14.10f %+14.10f",positions[3*i+0],positions[3*i+1],positions[3*i+2]);
    if (isSelective()){
      fprintf(f," %s %s %s\n",(selective[3*i+0]?"T":"F"),(selective[3*i+1]?"T":"F"),(selective[3*i+2]?"T":"F"));
    }
    else{
      fprintf(f,"\n");
    }
  }
  return 0;
}

int Structure::write(char *path){
  FILE *f=fopen(path,"w+");
#if CHECK>0
  if (f==NULL){
    char s[256];
    snprintf(s,250,"Structure.write('%s') open error.\n",path);
    THROW_EXC(s);
  }
#endif
  int r=this->write(f);
  fclose(f);
  return r;
}

double *Structure::updateRecipBasis(){
  double buff[3];
  double invOmega=scalmul3(basis1,cross(buff,basis2,basis3));
#if CHECK>0
  if (invOmega==0.0){
    THROW_EXC("Cell volume is zero in Structure.updateRecipbasis().");
  }
#endif
  invOmega=1.0/invOmega;
  cross(rbasis1,basis2,basis3);
  cross(rbasis2,basis3,basis1);
  cross(rbasis3,basis1,basis2);
  mul3(rbasis1,invOmega);
  mul3(rbasis2,invOmega);
  mul3(rbasis3,invOmega);
  return rbasis;
}

double *Structure::getRecipBasis(){
  return updateRecipBasis();
}

void Structure::forceConvertToCarthesian(){
#if VERBOSE>0
  printf("Structure::forceConvertToCarthesian()\n");
#endif
  double buff[3];
#if CHECK>0
  if (positions==NULL){
    THROW_NP_EXC("Structure.forceConvertToCarthesian(); positions=NULL");
  }
#endif
  for (int i=0;i<total_number_of_atoms;i++){
    double *v=&positions[3*i];
    buff[0]=0.0;
    buff[1]=0.0;
    buff[2]=0.0;
    add(buff,v[0],basis1);
    add(buff,v[1],basis2);
    add(buff,v[2],basis3);
#if VERBOSE>1
    printf("  %3d: %+10.6f %+10.6f %+10.6f -> %+10.6f %+10.6f %+10.6f\n",
    i,v[0],v[1],v[2],buff[0],buff[1],buff[2]);
#endif
    copy3(v,buff);
  }
}

void Structure::forceConvertToDirect(){
  double buff[3];
#if CHECK>0
  if (positions==NULL){
    THROW_NP_EXC("Structure.forceConvertToDirect(); positions=NULL");
  }
#endif
  updateRecipBasis();
  for (int i=0;i<total_number_of_atoms;i++){
    double *v=&positions[3*i];
    buff[0]=scalmul3(rbasis1,v);
    buff[1]=scalmul3(rbasis2,v);
    buff[2]=scalmul3(rbasis3,v);
    copy3(v,buff);
  }
}

int Structure::isCarthesian(){
  if (coordinates==NULL) return 0;
  switch(coordinates[0]){
    case 'c':
    case 'C':
    case 'k':
    case 'K':
      return 1;
    default:
      return 0;
  }
}

int Structure::isDirect(){
  if (coordinates==NULL) return 1;
  switch(coordinates[0]){
    case 'd':
    case 'D':
      return 1;
    default:
      return 0;
  }
}

void Structure::setCarthesian(int flag){
#if VERBOSE>0
  printf("Structure::setCarthesian(%d)\n",flag);
#endif
  if (flag){
    if (!isCarthesian()){
#if VERBOSE>1
      printf("  forceConvertToCarthesian();\n");
#endif
      forceConvertToCarthesian();
      if (coordinates!=NULL){
        delete coordinates;
      }
      coordinates=::clone("Carthesian");
    }
  }
  else{
    if (isCarthesian()){
#if VERBOSE>1
      printf("  forceConvertToDirect();\n");
#endif
      forceConvertToDirect();
      if (coordinates!=NULL){
        delete coordinates;
      }
      coordinates=NULL;
    }
  }
}

void Structure::setDirect(int flag){
  if (flag){
    if (!isDirect()){
      forceConvertToDirect();
      if (coordinates!=NULL){
        delete coordinates;
      }
      coordinates=NULL;
    }
  }
  else{
    if (isDirect()){
      forceConvertToCarthesian();
      if (coordinates!=NULL){
        delete coordinates;
      }
      coordinates=::clone("Carthesian");
    }
  }
}

double *Structure::dir2cart(double *dest,double *src){
#if CHECK>0
  if (dest==NULL){
    THROW_NP_EXC("Structure.dir2cart(); dest=NULL");
  }
  if (src==NULL){
    THROW_NP_EXC("Structure.dir2cart(); src=NULL");
  }
  if (basis==NULL){
    THROW_NP_EXC("Structure.dir2cart(); rbasis=NULL\n");
  }
  if (basis1==NULL){
    THROW_NP_EXC("Structure.dir2cart(); rbasis=NULL\n");
  }
  if (basis2==NULL){
    THROW_NP_EXC("Structure.dir2cart(); rbasis=NULL\n");
  }
  if (basis3==NULL){
    THROW_NP_EXC("Structure.dir2cart(); rbasis=NULL\n");
  }
#endif
  dest[0]=0.0;
  dest[1]=0.0;
  dest[2]=0.0;
  add(dest,src[0],basis1);
  add(dest,src[1],basis2);
  add(dest,src[2],basis3);
  return dest;
}

double *Structure::cart2dir(double *dest,double *src){
#if CHECK>1
  if (dest==NULL){
    THROW_NP_EXC("Structure.dir2cart(); dest=NULL\n");
  }
  if (src==NULL){
    THROW_NP_EXC("Structure.dir2cart(); src=NULL\n");
  }
  if (rbasis==NULL){
    THROW_NP_EXC("Structure.dir2cart(); rbasis=NULL\n");
  }
  if (rbasis1==NULL){
    THROW_NP_EXC("Structure.dir2cart(); rbasis1=NULL\n");
  }
  if (rbasis2==NULL){
    THROW_NP_EXC("Structure.dir2cart(); rbasis2=NULL\n");
  }
  if (rbasis3==NULL){
    THROW_NP_EXC("Structure.dir2cart(); rbasis3=NULL\n");
  }
#endif
  dest[0]=scalmul3(rbasis1,src);
  dest[1]=scalmul3(rbasis2,src);
  dest[2]=scalmul3(rbasis3,src);
  return dest;
}

double *Structure::dir2cart(double *dest){
  double buff[3];
  dir2cart(buff,dest);
  copy3(dest,buff);
  return dest;
}

double *Structure::cart2dir(double *dest){
  double buff[3];
  cart2dir(buff,dest);
  copy3(dest,buff);
  return dest;
}

void Structure::setStructure(Structure *p){
  clean();
  if (p->comment!=NULL){
    comment = ::clone(p->comment);
  }
  memcpy(&scaling[0],&p->scaling[0],3*sizeof(double));
  memcpy(&basis[0],&p->basis[0],9*sizeof(double));
  basis1=&basis[0];
  basis2=&basis[3];
  basis3=&basis[6];
  memcpy(&rbasis[0],&p->rbasis[0],9*sizeof(double));
  rbasis1=&rbasis[0];
  rbasis2=&rbasis[3];
  rbasis3=&rbasis[6];
  info->setAtomInfo(p->info);
  if (p->coordinates!=NULL){
    coordinates=::clone(p->coordinates);
  }
  else{
    coordinates=NULL;
  }
  total_number_of_atoms=p->total_number_of_atoms;
  allocated=p->allocated;
#if CHECK>1
  if (allocated<total_number_of_atoms){
    char s[256];
    snprintf(s,250,"allocated<total_number_of_atoms in Structure::setStructure(); allocated=%d, total_number_of_atoms=%d\n",
      allocated,total_number_of_atoms);
    THROW_MA_EXC(s);
  }
  if (allocated<0){
    THROW_MA_EXC("allocated<0 in Structure::setStructure();");
  }
#endif
  if (allocated==0){
    positions=NULL;
  }
  else{
    positions=new double[3*allocated];
    memcpy(positions,p->positions,3*total_number_of_atoms*sizeof(double));
  }
  if (p->selective != NULL){
    selective = new int[3*allocated];
    memcpy(selective,p->selective,3*total_number_of_atoms*sizeof(int));
  }

}

double *Structure::dirVectorToUnitCell(double *v){
  v[0]=fmod(v[0],1.0);
  if (v[0]<0.0) v[0]+=1.0;
  v[1]=fmod(v[1],1.0);
  if (v[1]<0.0) v[1]+=1.0;
  v[2]=fmod(v[2],1.0);
  if (v[2]<0.0) v[2]+=1.0;
  return v;
}

double *Structure::dirVectorToCenteredUnitCell(double *v){
  v[0]=fmod(v[0],1.0);
  if (v[0]<0.0) v[0]+=1.0;
  if (v[0]>0.5) v[0]-=1.0;
  v[1]=fmod(v[1],1.0);
  if (v[1]<0.0) v[1]+=1.0;
  if (v[1]>0.5) v[1]-=1.0;
  v[2]=fmod(v[2],1.0);
  if (v[2]<0.0) v[2]+=1.0;
  if (v[2]>0.5) v[2]-=1.0;
  return v;
}

double *Structure::dirVectorToUnitCell(double *dest,double *v){
  v[0]=fmod(v[0],1.0);
  if (v[0]<0.0) v[0]+=1.0;
  v[1]=fmod(v[1],1.0);
  if (v[1]<0.0) v[1]+=1.0;
  v[2]=fmod(v[2],1.0);
  if (v[2]<0.0) v[2]+=1.0;
  return dest;
}

double *Structure::dirVectorToCenteredUnitCell(double *dest,double *v){
  dest[0]=fmod(v[0],1.0);
  if (dest[0]<0.0) dest[0]+=1.0;
  if (dest[0]>0.5) dest[0]-=1.0;
  dest[1]=fmod(v[1],1.0);
  if (dest[1]<0.0) dest[1]+=1.0;
  if (dest[1]>0.5) dest[1]-=1.0;
  dest[2]=fmod(v[2],1.0);
  if (dest[2]<0.0) dest[2]+=1.0;
  if (dest[2]>0.5) dest[2]-=1.0;
  return dest;
}

double *Structure::cartVectorToUnitCell(double *v){
  cart2dir(v);
  dirVectorToUnitCell(v);
  dir2cart(v);
  return v;
}

double *Structure::cartVectorToCenteredUnitCell(double *v){
  cart2dir(v);
  dirVectorToCenteredUnitCell(v);
  dir2cart(v);
  return v;
}

double *Structure::cartVectorToUnitCell(double *dest,double *v){
  cart2dir(dest,v);
  dirVectorToUnitCell(dest);
  dir2cart(dest);
  return dest;
}

double *Structure::cartVectorToCenteredUnitCell(double *dest,double *v){
  cart2dir(dest,v);
  dirVectorToCenteredUnitCell(dest);
  dir2cart(dest);
  return dest;
}

void Structure::toUnitCell(){
  if (isCarthesian()){
    forceConvertToDirect();
    for (int i=0; i<total_number_of_atoms; i++){
      dirVectorToUnitCell(&positions[3*i]);
    }
    forceConvertToCarthesian();
  }
  else{
    for (int i=0; i<total_number_of_atoms; i++){
      dirVectorToUnitCell(&positions[3*i]);
    }
  }
}

void Structure::toCenteredUnitCell(){
  if (isCarthesian()){
    forceConvertToDirect();
    for (int i=0; i<total_number_of_atoms; i++){
      dirVectorToCenteredUnitCell(&positions[3*i]);
    }
    forceConvertToCarthesian();
  }
  else{
    for (int i=0; i<total_number_of_atoms; i++){
      dirVectorToCenteredUnitCell(&positions[3*i]);
    }
  }
}

double Structure::mindistCartVectors(double *a, double *b){
  double buff[3];
  copy3(buff,a);
  sub3(buff,b);
  return veclength3(cartVectorToCenteredUnitCell(buff));
}

double Structure::mindistDirVectors(double *a, double *b){
  double buff[3];
  copy3(buff,a);
  sub3(buff,b);
  dirVectorToCenteredUnitCell(buff);
  return veclength3(dir2cart(buff));
}

double *Structure::createMindistMatrix(){
#if CHECK>0
  if (total_number_of_atoms<=0){
    THROW_EXC("Structure.createMindistMatrix() total number of atoms is negative.");
  }
#endif
  if (mindist_matrix==NULL){
    mindist_matrix=new double[total_number_of_atoms*total_number_of_atoms];
  }
#if CHECK>0
  if (mindist_matrix==NULL){
    THROW_MA_EXC("Memory allocation error in Structure.createMindistMatrix().");
  }
#endif
  double d;
  if (isCarthesian()){
    for (int i=0; i<total_number_of_atoms; i++){
      mindist_matrix[(1+total_number_of_atoms)*i]=0.0;
      for (int j=i+1; j<total_number_of_atoms; j++){
        d=mindistCartVectors(&positions[3*i],&positions[3*j]);
/*
	printf("%3d %+12.8f %+12.8f %+12.8f\n",i,
	positions[3*i],positions[3*i+1],positions[3*i+2]);
	printf("%3d %+12.8f %+12.8f %+12.8f\n",j,
	positions[3*j],positions[3*j+1],positions[3*j+2]);

	printf("cr mindist cart %3d %3d %f\n",i,j,d);
*/
        mindist_matrix[i+total_number_of_atoms*j]=d;
        mindist_matrix[j+total_number_of_atoms*i]=d;
      }
    }
  }
  else{
    for (int i=0; i<total_number_of_atoms; i++){
      mindist_matrix[(1+total_number_of_atoms)*i]=0.0;
      for (int j=i+1; j<total_number_of_atoms; j++){
        d=mindistDirVectors(&positions[3*i],&positions[3*j]);
	printf("cr mindist dir %3d %3d %f\n",i,j,d);
        mindist_matrix[i+total_number_of_atoms*j]=d;
        mindist_matrix[j+total_number_of_atoms*i]=d;
      }
    }
  }
  return mindist_matrix;
}

void Structure::deleteMindistMatrix(){
  if (mindist_matrix!=NULL){
    delete mindist_matrix;
    mindist_matrix=NULL;
  }
}


double Structure::getMindist(int i, int j){
#if CHECK>1
  if ((i<0)||(i>=total_number_of_atoms)){
    THROW_R_EXC("Structure.getMindist() 1st index out of range.",
    0,total_number_of_atoms,i);
  }
  if ((j<0)||(j>=total_number_of_atoms)){
    THROW_R_EXC("Structure.getMindist() 2nd index out of range.",
    0,total_number_of_atoms,j);
  }
  if (positions==NULL){
    THROW_NP_EXC("Structure.getMindist() positions=NULL.");
  }
#endif
  if (mindist_matrix==NULL){
    if (isCarthesian()){
      return mindistCartVectors(&positions[3*i],&positions[3*j]);
    }
    else{
      return mindistDirVectors(&positions[3*i],&positions[3*j]);
    }
  }
  else{
    return mindist_matrix[i+total_number_of_atoms*j];
  }
}
/*
void Structure::setPotcar(FILE *f){
  if (atom_string!=NULL){
    delete atom_string;
    atom_string=NULL;
    atom=NULL;
  }
  if (atom!=NULL){
    for (int i=0; i<number_of_species;i++){
      if (atom[i]!=NULL){
        delete atom[i];
      }
    }
    delete atom;
  }
  atom=readAtomNames(f,number_of_species);
//  createAtomTypesTable();
}

void Structure::setPotcar(char *path){
  if (atom_string!=NULL){
    delete atom_string;
    atom_string=NULL;
    atom=NULL;
  }
  if (atom!=NULL){
    for (int i=0; i<number_of_species;i++){
      if (atom[i]!=NULL){
        delete atom[i];
      }
    }
    delete atom;
  }
  atom=readAtomNames(path,number_of_species);
//  createAtomTypesTable();
}
*/
/*
void Structure::createAtomTypesTable(){
#if VERBOSE>1
  printf("Structure.createAtomTypesTable();\n");
#endif
  if (atomtype==NULL){
#if VERBOSE>2
    printf("Structure.createAtomTypesTable() alocate space for Natoms=%d;\n",total_number_of_atoms);
#endif
    atomtype = new (AtomType *)[allocated];
#if CHECK>0
    if (atomtype==NULL){
      fprintf(stderr,"Memory allocation error in Structure.createAtomTypesTable(), Natoms=%d;\n",total_number_of_atoms);
      exit(-1);
    }
#endif
  }
  int N=0;
  if (atom==NULL){
#if VERBOSE>2
      printf("  Atom types unknown; filling in default types.\n");
#endif
    for (int i=0; i<number_of_species; i++){
      AtomType *a=getAtomTypeSafe(i);
#if CHECK>2
      if (a==NULL){
        fprintf(stderr,"getAtomTypeSafe(%d) is NULL in Structure.createAtomTypesTable() (A);\n",i);
        exit(-1);
      }
#endif
      for (int j=0; j<number_of_atoms[i];j++){
        atomtype[N]=a;
        N++;
      }
    }
  }
  else{
    int flag=0;
    for (int i=0; i<number_of_species; i++){
      AtomType *a;
      if (flag){
        a=getAtomTypeSafe(i);
#if CHECK>2
        if (a==NULL){
          fprintf(stderr,"getAtomTypeSafe(%d) is NULL in Structure.createAtomTypesTable() (B);\n",i);
          exit(-1);
        }
#endif
      }
      else{
        if (atom[i]==NULL){
          flag=1;
          a=getAtomTypeSafe(i);
#if CHECK>2
          if (a==NULL){
            fprintf(stderr,"getAtomTypeSafe(%d) is NULL in Structure.createAtomTypesTable() (C);\n",i);
            exit(-1);
          }
#endif
        }
        else{
          a=getAtomTypeSafe(atom[i],i);
#if CHECK>2
          if (a==NULL){
            fprintf(stderr,"getAtomTypeSafe('%s',%d) is NULL in Structure.createAtomTypesTable() (C);\n",atom[i],i);
            exit(-1);
          }
#endif
        }
      }
      for (int j=0; j<number_of_atoms[i];j++){
        atomtype[N]=a;
        N++;
      }
    }
  }
}
*/

/*
long Structure::createHalfBondsList(double *vecbuff,int *index,long limit,double factor,int countbonds){
  long N=0;
  double buff[3];
  for (int i=0; i<total_number_of_atoms; i++){
    for (int j=0; j<total_number_of_atoms; j++){
      double bond = factor*(atomtype[i]->covalent+atomtype[j]->covalent);
      double mindist = getMindist(i,j);
      if (mindist<=bond){
        for (int i1=-1; i1<=1; i1++){
          for (int i2=-1; i2<=1; i2++){
            for (int i3=-1; i3<=1; i3++){
              if ((i==j)&& (i3==0)) continue;
              copy3(buff,&positions[3*j]);
              sub(buff,&positions[3*i]);
              if (i1) add3(buff,i1,basis1);
              if (i2) add3(buff,i2,basis2);
              if (i3) add3(buff,i3,basis3);
              if (veclength3(buff)<=bond){
                if (N<limit){
                  mul3(buff,0.5);
                  copy3(&vecbuff[3*N],buff);
                  index[N]=i;
                }
                else{
                  if (!countbonds){
                    return -1;
                  }
                }
                N++;
              }
            }
          }
        }
      }
    }
  }
  return N;
}

*/

Structure *Structure::clone(){
  Structure *p = new Structure();
  p->setStructure(this);
  return p;
}

void Structure::setSelective(int flag){
  if (flag){
    if (selective==NULL){
      selective=new int[3*allocated];
      for (int i=0; i<3*allocated; i++){
        selective[i]=1;
      }
    }
  }
  else{
    if (selective!=NULL){
      delete selective;
      selective=NULL;
    }
  }
}

int Structure::len(){
  return total_number_of_atoms;
}


double *Structure::vectorToUnitCell(double *v){
  if (isCarthesian()) return cartVectorToUnitCell(v);
  else return dirVectorToUnitCell(v);
}
double *Structure::vectorToCenteredUnitCell(double *v){
  if (isCarthesian()) return cartVectorToCenteredUnitCell(v);
  else return dirVectorToCenteredUnitCell(v);
}

double *Structure::vectorToUnitCell(double *dest,double *v){
  if (isCarthesian()) return cartVectorToUnitCell(dest,v);
  else return dirVectorToUnitCell(dest,v);
}
double *Structure::vectorToCenteredUnitCell(double *dest,double *v){
  if (isCarthesian()) return cartVectorToCenteredUnitCell(dest,v);
  else return dirVectorToCenteredUnitCell(dest,v);
}

int Structure::isSelective(){
  return (selective!=NULL);
}

int Structure::getNumberOfSpecies(){
#if CHECK>0
  if (info==NULL){
    THROW_NP_EXC("Structure.info==NULL; found in Structure::getNumberOfSpecies()");
  }
  else{
    return info->types;
  }
#else
  return info->types;
#endif
}

AtomtypesRecord *Structure::getRecord(int i){
#if CHECK>0
  if (info==NULL){
    THROW_NP_EXC("Structure.info==NULL; found in Structure::getRecord()");
  }
#endif
  return info->getRecord(i);
}

const char *Structure::toString(){
#if VERBOSE>1
  fprintf(stderr,"Structure::toString()\n");
#endif
  if (toString_buffer!=NULL){
    delete toString_buffer;
  }
  long len = 200;
  long l=0;
  if (comment==NULL){
    len+=20;
  }
  else{
    len+=strlen(comment)+2;
  }
  if (coordinates==NULL){
    len+=20;
  }
  else{
    len+=strlen(coordinates);
  }
  len+=80*total_number_of_atoms;
  toString_buffer = new char[len];
  if (toString_buffer==NULL){
    THROW_MA_EXC("String buffer allocation error in Structure::toString();");
  }
  toString_buffer[0]='\0';
  if (comment==NULL){
    strcpy(toString_buffer,"no comment\n");
  }
  else{
    char *c=::clone(comment);
    if (c==NULL){
      THROW_MA_EXC("clone(comment) failed in Structure::toString();");
    }
    else{
      snprintf(&toString_buffer[0],len-10,"%s\n",strip(c));
      delete c;
    }
  }

  if (scaling_flag==1){
    l=strlen(toString_buffer);
    snprintf(&toString_buffer[l],len-l-10,"%f\n",scaling[0]);
  }
  else{
    l=strlen(toString_buffer);
    snprintf(&toString_buffer[l],len-l-10,"%12.8f %12.8f %12.8f\n",scaling[0],scaling[1],scaling[2]);
  }
  for (int i=0; i<3; i++){
    l=strlen(toString_buffer);
    snprintf(&toString_buffer[l],len-l-10,"%+14.10f %+14.10f %+14.10f\n",basis[3*i+0],basis[3*i+1],basis[3*i+2]);
  }
  if (info==NULL){
    l=strlen(toString_buffer);
    snprintf(&toString_buffer[l],len-l-10," 0\n");
  }
  else{
    for (int i=0; i<getNumberOfSpecies(); i++){
      l=strlen(toString_buffer);
      snprintf(&toString_buffer[l],len-l-10," %d",info->getRecord(i)->atomspertype);
    }
    l=strlen(toString_buffer);
    snprintf(&toString_buffer[l],len-l-10,"\n");
  }
  if (isSelective()){
    l=strlen(toString_buffer);
    snprintf(&toString_buffer[l],len-l-10,"Selective\n");
  }
#if CHECK>0
  if (positions==NULL){
    THROW_NP_EXC("Structure.positions=NULL in Structure.write().");
  }
#endif
  if (coordinates==NULL){
    l=strlen(toString_buffer);
    snprintf(&toString_buffer[l],len-l-10,"Direct\n");
  }
  else{
    l=strlen(toString_buffer);
    snprintf(&toString_buffer[l],len-l-10,"%s\n",coordinates);
  }
  for (int i=0; i<total_number_of_atoms; i++){
    l=strlen(toString_buffer);
    snprintf(&toString_buffer[l],len-l-10,"%+14.10f %+14.10f %+14.10f",positions[3*i+0],positions[3*i+1],positions[3*i+2]);
    if (isSelective()){
      l=strlen(toString_buffer);
      snprintf(&toString_buffer[l],len-l-10," %s %s %s\n",
        (selective[3*i+0]?"T":"F"),
	(selective[3*i+1]?"T":"F"),
	(selective[3*i+2]?"T":"F"));
    }
    else{
      l=strlen(toString_buffer);
      snprintf(&toString_buffer[l],len-l-10,"\n");
    }
  }
  return toString_buffer;
}

double *Structure::get(int i){
#if VERBOSE>1
  fprintf(stderr,"Structure::get(%d)\n",i);
#endif
  if (i<0){
    i+=total_number_of_atoms;
  }
#if CHECK>0
  if ((i<0)||(i>=total_number_of_atoms)){
    THROW_R_EXC("Index out of range in Structure::get().",0,total_number_of_atoms,i);
  }
  if (positions==NULL){
    THROW_NP_EXC("positions=NULL in Structure::get().");
  }
#endif
  return &positions[3*i];
}

void Structure::set(int i,double x,double y,double z){
#if VERBOSE>1
  fprintf(stderr,"Structure::set(%d,%f,%f,%f)\n",i,x,y,z);
#endif
  if (i<0){
    i+=total_number_of_atoms;
  }
#if CHECK>0
  if ((i<0)||(i>=total_number_of_atoms)){
    THROW_R_EXC("Index out of range in Structure::set().",
    0,total_number_of_atoms,i);
  }
  if (positions==NULL){
    THROW_NP_EXC("positions=NULL in Structure::set().");
  }
#endif
  positions[3*i+0]=x;
  positions[3*i+1]=y;
  positions[3*i+2]=z;
}

void Structure::realloc(int alloc){
#if VERBOSE>1
  fprintf(stderr,"Structure::realloc(%d)\n",alloc);
#endif
  double *new_positions=NULL;
  int *new_selective=NULL;

  if (alloc!=allocated){
    if (alloc>0){
      new_positions = new double[3*alloc];
      if (new_positions==NULL){
        THROW_MA_EXC("Structure::realloc() failed. (A)");
      }
      if (isSelective()){
	new_selective = new int[3*alloc];
	if (new_selective==NULL){
	  delete new_positions;
          THROW_MA_EXC("Structure::realloc() failed. (B)");
	}
      }
      long count=total_number_of_atoms;
      if (alloc<count) count=alloc;
      if (count>0){
	memcpy(new_positions,positions,sizeof(double)*3*count);
	if (isSelective()){
          memcpy(new_selective,selective,sizeof(int)*3*count);
	}
      }
      total_number_of_atoms=(int)count;
      allocated=alloc;
    }
    else{
      total_number_of_atoms=0;
      allocated=0;
      new_positions=NULL;
      new_selective=NULL;
    }
    if (positions!=NULL){
      delete positions;
    }
    if (selective!=NULL){
      delete selective;
    }
    positions=new_positions;
    selective=new_selective;
  }
}

void Structure::allocate(int n){
  if (n>allocated){
    realloc(n);
  }
  total_number_of_atoms=n;
}

void Structure::append(double x, double y, double z){
  if (allocation_step<=0) allocation_step=1;
  if ((total_number_of_atoms+1)>allocated){
    realloc(allocated+allocation_step);
  }
  positions[3*total_number_of_atoms+0]=x;
  positions[3*total_number_of_atoms+1]=y;
  positions[3*total_number_of_atoms+2]=z;
  if (isSelective()){
    selective[3*total_number_of_atoms+0]=0;
    selective[3*total_number_of_atoms+1]=0;
    selective[3*total_number_of_atoms+2]=0;
  }
  total_number_of_atoms++;
}

void Structure::append(double *v){
  if (allocation_step<=0) allocation_step=1;
  if ((total_number_of_atoms+1)>allocated){
    realloc(allocated+allocation_step);
  }
  positions[3*total_number_of_atoms+0]=v[0];
  positions[3*total_number_of_atoms+1]=v[1];
  positions[3*total_number_of_atoms+2]=v[2];
  if (isSelective()){
    selective[3*total_number_of_atoms+0]=0;
    selective[3*total_number_of_atoms+1]=0;
    selective[3*total_number_of_atoms+2]=0;
  }
  total_number_of_atoms++;
}

void Structure::delitem(int i){
  if (i<0){
    i+=total_number_of_atoms;
  }
#if CHECK>0
  if ((i<0)||(i>=total_number_of_atoms)){
    THROW_R_EXC("Index out of range in Structure::delitem().",0,total_number_of_atoms,i);
  }
  if (positions==NULL){
    THROW_NP_EXC("positions=NULL in Structure::delitem().");
  }
#endif
  long count = total_number_of_atoms-i-1;
  if (count>0){
    memmove(&positions[3*i],&positions[3*i+3],3*sizeof(double)*count);
    if (isSelective()){
      memmove(&selective[3*i],&selective[3*i+3],3*sizeof(int)*count);
    }
    total_number_of_atoms--;
  }
}

int Structure::getSelectiveDOF(int i){
  if (i<0){
    i+=total_number_of_atoms;
  }
#if CHECK>0
  if (!isSelective()){
    THROW_EXC("Structure::getSelectiveDOF() called while "
              "not in selectivemode.");
  }
  if ((i<0)||(i>=(3*total_number_of_atoms))){
    THROW_R_EXC("Index out of range in Structure::getSelectiveDOF().",0,3*total_number_of_atoms,i);
  }
#endif
  return selective[i];
}

void Structure::setSelectiveDOF(int i,int value){
#if CHECK>0
  if (!isSelective()){
    THROW_EXC("Structure::setSelectiveDOF() called while "
              "not in selectivemode.");
  }
  else if ((i<0)||(i>=(3*total_number_of_atoms))){
    THROW_R_EXC("Index out of range in Structure::setSelectiveDOF().",0,3*total_number_of_atoms,i);
  }
#endif
  selective[i]=value;
}
