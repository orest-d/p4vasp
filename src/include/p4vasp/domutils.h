#ifndef domutils_h
#define domutils_h

#include <ODP/Element.h>
#include <ODP/CharacterNodes.h>
#include <ODP/string.h>
#include <p4vasp/FArray.h>
#include <p4vasp/Structure.h>

double *createvec3d(ODPNode *node);
FArray1D *createFArray1Dsimple(ODPNode *node);
FArray2D *createFArray2Dsimple(ODPElement *elem,const char *tag,long minx=0,long
miny=0);
FArray2D *createFArray2DsimpleN(ODPNode *node,const char *tag,long minx=0,long
miny=0);
Structure *createStructure(ODPElement *elem);
Structure *createStructureN(ODPNode *node);

#endif
