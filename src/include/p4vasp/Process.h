#ifndef Process_h
#define Process_h
#include <stdio.h>

class Process{
  protected:
  char buff[255];
  bool is_status;
  bool is_error;
  long _total;
  long _step;
  public:
  virtual long total();
  virtual long step();
  virtual const char *status();
  virtual const char *error();
  virtual long next();
  virtual ~Process();
};

#endif
