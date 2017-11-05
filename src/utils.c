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

#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <ctype.h>
#include <p4vasp/utils.h>
#include <p4vasp/Exceptions.h>
#include <errno.h>

//#define VERBOSE 4
//#define CHECK 5

char *lstrip(char *s){
  int i;
  for (i=0; s[i]!='\0'; i++){
    if (!isspace(s[i])){
      break;
    }
  }
#if VERBOSE>3
  printf("lstrip('%s')='%s';\n",s,&s[i]);
#endif
  return &s[i];
}

char *rstrip(char *s){
  int i;
#if VERBOSE>3
  printf("rstrip('%s')=",s);
#endif
  for (i=0; s[i]!='\0'; i++){
    ;
  }
  i--;
  if (i>0){
    for (;i>0; i--){
      if (isspace(s[i])){
        s[i]='\0';
      }
      else{
        break;
      }
    }
  }
#if VERBOSE>3
  printf("'%s';\n",s);
#endif
  return s;
}

char *strip(char *s){
#if VERBOSE>3
  printf("split('%s');\n",s);
#endif
  return lstrip(rstrip(s));
}

long countLines(char *s){
  long N=1;
  for (long i=0;s[i]!='\0';i++){
    if (s[i]=='\n'){
      N++;
    }
  }
#if VERBOSE>3
  printf("countLines()=%ld;\n",N);
#endif
  return N;
}

char **splitLines(char *s){
  long N=countLines(s);
  long P=1;
  char **array=new (char *)[N+1];
  array[N]=NULL;
#if VERBOSE>3
  printf("splitLines(...) (N=%ld);\n",N);
#endif
#if CHECK>0
  if (array==NULL){
    fprintf(stderr,"Array memory allocation error in splitLines(). (N=%ld)\n",N);
    exit(-1);
  }
#endif
  array[0]=s;
  for(long i=0; s[i]!='\0';i++){
    if (s[i]=='\n'){
      s[i]='\0';
#if CHECK>1
      if (P>=N){
        fprintf(stderr,"Pointer P > Array dimmension N in splitLines(). (P=%ld,N=%ld)\n",P,N);
        exit(-1);
      }
#endif
      array[P]=&s[i+1];
      P++;
    }
  }
#if VERBOSE>4
  for (long i=0; i<N; i++){
    printf("  %3ld: '%s'\n",i,array[i]);
  }
#endif

  return array;
}

long arrayLength(char **array){
  long N;
  for (N=0; array[N]!=NULL; N++){
    ;
  }
#if VERBOSE>3
  printf("arrayLength()=%ld;\n",N);
#endif
  return N;
}

long countWords(const char *s){
  long N=0;
  for (long i=0;s[i]!='\0';i++){
    if (!isspace(s[i])){
      N++;
      for(;!isspace(s[i]);i++){
        if (s[i]=='\0'){
          return N;
        }
      }
    }
  }
#if VERBOSE>3
  printf("countWords()=%ld;\n",N);
#endif
  return N;
}

char **splitWords(char *s){
  long N=countWords(s);
  long P=0;
  char **array=new (char *)[N+1];
  array[N]=NULL;
#if VERBOSE>3
  printf("splitWords('%s') (N=%ld);\n",s,N);
#endif
#if CHECK>0
  if (array==NULL){
    NTHROW_MA_EXC("Array memory allocation error in splitWords().");
  }
#endif
  if (s[0]=='\0'){
    array[0]=NULL;
    return array;
  }
  for (long i=0;s[i]!='\0';i++){
    if (!isspace(s[i])){
#if CHECK>1
      if (P>=N){
	NTHROW_R_EXC("Pointer P > Array dimmension N in splitWords().",0,N,P);
      }
#endif
      array[P]=&s[i];
      P++;
      for(;!isspace(s[i]);i++){
        if (s[i]=='\0'){
#if VERBOSE>3
          for (long i=0; i<N; i++){
            printf("  %3ld: '%s'\n",i,array[i]);
          }
#endif
          return array;
        }
      }
    }
    if (isspace(s[i])){
      s[i]='\0';
    }
  }

#if VERBOSE>4
  for (long i=0; i<N; i++){
    printf("  %3ld: '%s'\n",i,array[i]);
  }
#endif

  return array;
}

char *clone(const char *s){
  long l=strlen(s);
  char *d = new char[l+1];
#if CHECK>0
  if (s==NULL){
    NTHROW_NP_EXC("Can't clone(NULL) string.");
  }
#endif

#if VERBOSE>3
  printf("string clone('%s');\n",s);
#endif
#if CHECK>0
  if (d==NULL){
    NTHROW_MA_EXC("String clone() failed.");
  }
#endif
  memcpy(d,s,l+1);
  return d;
}

char *loadFile(const char *path){
  FILE *f=fopen(path,"r");
#if CHECK>0
  if (f==NULL){
    char s[255];
    snprintf(s,250,"fopen() failed in loadFile('%s')\n%s",path,strerror(errno));
    NTHROW_EXC(s);
  }
#endif
  if (fseek(f,0L,SEEK_END)==-1){
    char s[255];
    snprintf(s,250,"fseek() failed in loadFile('%s')\n%s",path,strerror(errno));
    NTHROW_EXC(s);
  }
  long l=ftell(f);
#if CHECK>0
  if (l==-1){
    char s[255];
    snprintf(s,250,"ftell() failed in loadFile('%s')\n%s",path,strerror(errno));
    NTHROW_EXC(s);
  }
#endif
#if VERBOSE>3
  printf("loadFile('%s'); (length=%ld)\n",path,l);
#endif
  rewind(f);
  char *buff= new char[l+1];
#if CHECK>0
  if (buff==NULL){
    char s[255];
    snprintf(s,250,"loadFile('%s') failed. (requested buffer length was %ld)\n",path,l);
    NTHROW_MA_EXC(s);
  }
#endif
  if (l==0){
    buff[0]='\0';
    return buff;
  }

  long rl=fread(buff,1,l,f);
#if CHECK>0
  if (rl!=l){
    char s[255];
    snprintf(s,250,"fread() failed in loadFile('%s'); l=%ld\n%s",path,l,strerror(errno));
    NTHROW_EXC(s);
  }
#endif
  fclose(f);
  return buff;
}

char **cloneShallow(char **s){
  long l=arrayLength(s);
  char **b=new (char *)[l+1];
#if CHECK>0
  if (b==NULL){
    NTHROW_MA_EXC("Memory allocation error in cloneShallow().");
  }
#endif
  for (long i=0; i<=l; i++){
    b[i]=s[i];
  }
  return b;
}

char *getLine(FILE *f){
  static char buff[MAXLINEBUFF];
  char *r=fgets(buff,MAXLINEBUFF-1,f);
  if (r==NULL){
    return NULL;
  }
  return clone(buff);
}

char *getWord(FILE *f){
  static char buff[MAXWORDBUFF];
  int i;
  int c;
  do{
    c=fgetc(f);
  }while(isspace(c));
  for (i=0; i<(MAXWORDBUFF-1); i++){
    if (isspace(c) || c==EOF){
      break;
    }
    buff[i]=c;
    c=fgetc(f);
  }
  buff[i]='\0';
  return clone(buff);
}

