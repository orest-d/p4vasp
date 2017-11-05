#HAPPYDOC=happydoc
EPYDOC=epydoc
DOXYGEN=doxygen

doc: api

api: python_api c_api

python_api:
	-mkdir api/python	
	$(EPYDOC) --html -o./api/python --url ../index.html --graph all --name p4vasp ../lib/p4vasp/*.py ../lib/p4vasp/applet/*.py ../lib/p4vasp/paint3d/*.py 

c_api:
	-mkdir api/c
	$(DOXYGEN)

clean_api:
	-rm -Rf api/c
	-rm -Rf api/python

cleanall:clean_api
