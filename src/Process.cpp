#include <p4vasp/Process.h>

long Process::total(){
  return _total;
}

long Process::step(){
  return _step;
}

const char *Process::status(){
  return (is_status)?(buff):(NULL);
}

const char *Process::error(){
  return (is_error)?(buff):(NULL);
}

long Process::next(){
  return 0;
}

Process::~Process(){
}

