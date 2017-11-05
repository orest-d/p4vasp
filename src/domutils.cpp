#include <stdio.h>
#include <stdlib.h>
#include <p4vasp/domutils.h>
#include <p4vasp/utils.h>
#include <p4vasp/vecutils3d.h>
#include <locale.h>

double *createvec3d(ODPNode *node){
  char *s;
  switch(node->getNodeType()){
    case ODPNode::TEXT_NODE:
    case ODPNode::CDATA_SECTION_NODE:
    case ODPNode::ATTRIBUTE_NODE:
    {
      s=ODP_strclone(node->getNodeValue());
      double *r=createvec3d(s);
      delete s;
      return r;
    }
    case ODPNode::ELEMENT_NODE:
    {
      ODPNodeList *nl=node->getChildNodes();
      unsigned long l=nl->getLength();
      for (unsigned long i=0; i<l; i++){
        ODPNode *child=nl->item(i);
	switch(child->getNodeType()){
	  case ODPNode::TEXT_NODE:
	  case ODPNode::CDATA_SECTION_NODE:
	    s=ODP_strclone(child->getNodeValue());
	    double *r=createvec3d(s);
	    delete s;
	    delete child;
	    delete nl;
	    return r;
	}
	delete child;
      }
      delete nl;
    }
  }
  return createvec3d(0.0,0.0,0.0);
}

FArray1D *createFArray1Dsimple(ODPNode *node){
  char *s;
  switch(node->getNodeType()){
    case ODPNode::TEXT_NODE:
    case ODPNode::CDATA_SECTION_NODE:
    case ODPNode::ATTRIBUTE_NODE:
    {
      s=ODP_strclone(node->getNodeValue());
      FArray1D *a = new FArray1D(countWords(s));
      a->parseStringDestructively(s);
      delete s;
      return a;
    }
    case ODPNode::ELEMENT_NODE:
    {
      ODPNodeList *nl=node->getChildNodes();
      unsigned long l=nl->getLength();
      for (unsigned long i=0; i<l; i++){
        ODPNode *child=nl->item(i);
	switch(child->getNodeType()){
	  case ODPNode::TEXT_NODE:
	  case ODPNode::CDATA_SECTION_NODE:
	    s=ODP_strclone(child->getNodeValue());
	    FArray1D *a = new FArray1D(countWords(s));
	    a->parseStringDestructively(s);
	    delete s;
	    delete child;
	    delete nl;
	    return a;
	}
	delete child;
      }
      delete nl;
    }
  }
  return NULL;
}

FArray2D *createFArray2Dsimple(ODPElement *elem,const char *tag,long minx,long miny){
#if VERBOSE>0
  printf("createFArray2Dsimple(elem,%s,%ld,%ld)\n",tag,minx,miny);
#endif
  setlocale (LC_ALL,"C");
  long dimx=minx;
  long dimy=miny;
  ODPNodeList *nlt=elem->getElementsByTagName(tag);
  long L=nlt->getLength();
//  printf("  count(%s):%ld\n",tag,L);
  if (L>dimx){
    dimx=L;
  }
  char ***w= new char **[L];
  char **s=new char *[L];
  for (long i=0;i<L;i++){
    ODPNodeList *nl=nlt->item(i)->getChildNodes();
    unsigned long l=nl->getLength();
    for (unsigned long j=0; j<l; j++){
      ODPNode *child=nl->item(j);
      unsigned short t=child->getNodeType();
      if ((t==ODPNode::TEXT_NODE)||(t==ODPNode::CDATA_SECTION_NODE)){
	s[i]=ODP_strclone(child->getNodeValue());
	w[i]=splitWords(s[i]);
	long d=arrayLength(w[i]);
	if (d>dimy){
	  dimy=d;
	}
	break;
      }
    }
    delete nl;
  }
  delete nlt;
//  printf("  dimensions:%ld %ld\n",dimx,dimy);
  FArray2D *a=new FArray2D(dimx,dimy);
  a->clear();
  for (long i=0; i<L; i++){
    for (long j=0; j<dimy; j++){
      if (w[i][j]==NULL){
        break;
      }
//      printf ("Locale is: %s\n", setlocale(LC_ALL,NULL) );
//      printf("ATOF[%3d %3d] %s -> %f\n",i,j,w[i][j],atof(w[i][j]));
      a->set(i,j,atof(w[i][j]));
    }
    delete w[i];
    delete s[i];
  }
  delete w;
  delete s;
  return a;
}

FArray2D *createFArray2DsimpleN(ODPNode *node,const char *tag,long minx,long miny){
  ODPElement *elem=new ODPElement(node);
  FArray2D *a=createFArray2Dsimple(elem,tag,minx,miny);
  delete elem;
  return a;
}

Structure *createStructure(ODPElement *elem){
  Structure *s=new Structure();
  ODPNodeList *nl=elem->getElementsByTagName("crystal");
  if (nl->getLength()==0){
    printf("Warning: No <crystal> section in structure definition.\n");
    s->basis[0]=1.0;
    s->basis[1]=0.0;
    s->basis[2]=0.0;
    s->basis[3]=0.0;
    s->basis[4]=1.0;
    s->basis[5]=0.0;
    s->basis[6]=0.0;
    s->basis[7]=0.0;
    s->basis[8]=1.0;
  }
  else{
    ODPElement *eelem=new ODPElement(nl->item(0));
    ODPNodeList *nlb=eelem->getElementsByTagName("varray");
//    ODPElement *belem=NULL;

    if (nlb->getLength()==0){
      printf("Warning: No <varray> in <crystal> section.\n");
      s->basis[0]=1.0;
      s->basis[1]=0.0;
      s->basis[2]=0.0;
      s->basis[3]=0.0;
      s->basis[4]=1.0;
      s->basis[5]=0.0;
      s->basis[6]=0.0;
      s->basis[7]=0.0;
      s->basis[8]=1.0;
    }
    FArray2D *b=createFArray2DsimpleN(nlb->item(0),"v",3,3);
    s->basis[0]=b->get(0,0);
    s->basis[1]=b->get(0,1);
    s->basis[2]=b->get(0,2);
    s->basis[3]=b->get(1,0);
    s->basis[4]=b->get(1,1);
    s->basis[5]=b->get(1,2);
    s->basis[6]=b->get(2,0);
    s->basis[7]=b->get(2,1);
    s->basis[8]=b->get(2,2);
    delete b;
    delete eelem;
    delete nlb;
  }
  delete nl;
  nl=elem->getElementsByTagName("varray");
  ODPElement *velem=NULL;
  for (int i=0; i<int(nl->getLength());i++){
//    printf("I=%d/%d %p\n",i,nl->getLength(),nl->item(i));
    velem=new ODPElement(nl->item(i));
    if (ODP_strcmp(velem->getAttribute("name"),"positions")==0){
//      printf("found %d\n",i);
      break;
    }
    delete velem;
    velem=NULL;
  }
  if (velem==NULL){
    printf("Warning: No <varray name=\"positions\"> section in the structure"
    " definition.\n");
  }
  else{
    FArray2D *v=createFArray2DsimpleN(velem,"v",0,3);
    delete velem;
    int sx=v->sizeX();
    s->allocate(sx);
    for (int i=0; i<sx;i++){
      s->set(i,v->get(i,0),v->get(i,1),v->get(i,2));
    }
  }
  delete nl;
  return s;
}

Structure *createStructureN(ODPNode *node){
  ODPElement *elem=new ODPElement(node);
  Structure  *s=createStructure(elem);
  delete elem;
  return s;
}
