######################################################################
# INSTALATION DIRECTORIES:                                           #
######################################################################
# ROOT          - root directory (need not be set, just for testing) #
# P4VASP_HOME   - home directory of p4vasp distribution              #
# PYTHON_PATH   - where th python-home is (usually /usr/lib/python)  #
# SITE_PACKAGES - where python modules will go                       #
#                 (usually /usr/lib/python/site-packages)            #
# INCLUDEDIR    - where the headder-files will go                    #
#                 (usually /usr/include)                             #
# LIBDIR        - where the development libraries will go            #
#                 (usually /usr/lib)                                 #
# BINDIR        - where the executable will go (e.g. /usr/bin)       #
######################################################################

-include install/Configuration.mk

P4VCONFIG     = lib/p4vasp/config.py
VINFO         = vinfo.py
SETENVIRONMENT= setenvironment.sh
P4V           = p4v

.PHONY: p4vasp
.PHONY: doc
.PHONY: clean_p4vasp
.PHONY: clean_odpdom
.PHONY: cleanall_doc
.PHONY: cleanall_p4vasp
.PHONY: cleanall_odpdom
.PHONY: install_pythonpkg
.PHONY: install_gui
.PHONY: install_devel
.PHONY: install
.PHONY: uninstall_pythonpkg
.PHONY: uninstall_gui
.PHONY: uninstall_devel
.PHONY: uninstall
.PHONY: uninstallsh
.PHONY: p4vasp_config
.PHONY: setenvironment
.PHONY: launcher
.PHONY: appletlist

all: p4vasp
local:
	cd install && python configure.py local
config:
	cd install && python configure.py
p4vasp: p4vasp_config uninstallsh appletlist
	cd odpdom && $(MAKE) libODP.a
	cd src && $(MAKE)
p4vasp_config:
	echo "p4vasp_home='$(P4VASP_HOME)'" >$(P4VCONFIG)
	cat $(VINFO) >> $(P4VCONFIG)
devver:
	echo "name       ='p4vasp-devel'" > $(VINFO)
	echo "version    ='DEVELOPMENT'" >> $(VINFO)
	echo "release    ='1'" >> $(VINFO)
	echo "build_date ='`date`'" >> $(VINFO)
setenvironment:
	echo "# set p4vasp environment variables"   >  $(SETENVIRONMENT)
	echo "export PATH=\$$PATH:"$(BINDIR) >> $(SETENVIRONMENT)
launcher:
	echo "#!`which sh`" >$(P4V)
	echo "export LD_PRELOAD=libstdc++.so.6" >>$(P4V)
	echo "export PYTHONPATH=\$$PYTHONPATH:"$(SITE_PACKAGES) >>$(P4V)
	echo "#export APPMENU_DISPLAY_BOTH=1" >>$(P4V)
	echo "export UBUNTU_MENUPROXY=0" >>$(P4V)
	echo "export P4VASP_HOME="$(P4VASP_HOME) >> $(P4V)
	echo "exec python "$(BINDIR)"/p4v.py \"\$$@\"" >>$(P4V)
appletlist:
	cd install && python makeappletlist.py
bashrc:setenvironment
	echo "" >> ~/.bashrc
	cat $(SETENVIRONMENT) >> ~/.bashrc
fltk:
	cd ext && sh build-fltk.sh
doc:
	cd doc && $(MAKE)
clean_p4vasp:
	rm -f data/glade/*.bak
	rm -f data/glade2/*.bak
	rm -f data/glade2/*.gladep
	cd src && $(MAKE) clean
clean_odpdom:
	cd odpdom && $(MAKE) clean
cleanall_doc:
	cd doc && $(MAKE) cleanall
cleanall_p4vasp:
	rm -f lib/p4vasp/config.py
	rm -f lib/p4vasp/*.pyc
	rm -f lib/p4vasp/*.pyo
	rm -f lib/p4vasp/*.bak
	rm -f lib/p4vasp/*~
	rm -f lib/p4vasp/paint3d/*.pyc
	rm -f lib/p4vasp/paint3d/*.pyo
	rm -f lib/p4vasp/paint3d/*.bak
	rm -f lib/p4vasp/paint3d/*~
	rm -f lib/p4vasp/export/*.pyc
	rm -f lib/p4vasp/export/*.pyo
	rm -f lib/p4vasp/export/*.bak
	rm -f lib/p4vasp/export/*~
	rm -f lib/p4vasp/applet/*.pyc
	rm -f lib/p4vasp/applet/*.pyo
	rm -f lib/p4vasp/applet/*.bak
	rm -f lib/p4vasp/applet/*~
	rm -f lib/p4vasp/applet/appletlist.py
	rm -f lib/p4vasp/piddle/*.pyc
	rm -f lib/p4vasp/piddle/*.pyo
	rm -f lib/p4vasp/piddle/*.bak
	rm -f lib/p4vasp/piddle/*~
	rm -f lib/p4vasp/piddle/piddleGTKp4/*.pyc
	rm -f lib/p4vasp/piddle/piddleGTKp4/*.pyo
	rm -f lib/p4vasp/piddle/piddleGTKp4/*.bak
	rm -f lib/p4vasp/piddle/piddleGTKp4/*~
	rm -f lib/p4vasp/piddle/piddleGTK2p4/*.pyc
	rm -f lib/p4vasp/piddle/piddleGTK2p4/*.pyo
	rm -f lib/p4vasp/piddle/piddleGTK2p4/*.bak
	rm -f lib/p4vasp/piddle/piddleGTK2p4/*~
	rm -f test/*.pyc
	rm -f test/*.pyo
	rm -f test/*.bak
	rm -f test/*~
	rm -f utils/*.pyc
	rm -f utils/*.pyo
	rm -f utils/*.bak
	rm -f utils/*~
	rm -f install/*.pyc
	rm -f install/*.pyo
	rm -f install/*.bak
	rm -f install/*~
	rm -f log
	rm -f p4vasp.log
	rm -f p4v
	rm -f install/Configuration.mk
	rm -f *~
	rm -f *.pyc
	rm -f *.pyo
	rm -f *.bak
	cd src && $(MAKE) cleanall
cleanall_odpdom:
	cd odpdom && $(MAKE) cleanall
cleanall_ext:
	cd ext && sh clean.sh

clean: clean_p4vasp clean_odpdom
cleanall: cleanall_p4vasp cleanall_odpdom cleanall_doc cleanall_ext

install_pythonpkg:p4vasp
	mkdir -p $(SITE_PACKAGES)/p4vasp
	cd lib; cp -R p4vasp $(SITE_PACKAGES); cd ..
	chmod -R 755 $(SITE_PACKAGES)/p4vasp
	chmod    644 $(SITE_PACKAGES)/p4vasp/*
	chmod -R 755 $(SITE_PACKAGES)/p4vasp/applet
	chmod -R 644 $(SITE_PACKAGES)/p4vasp/applet/*
	chmod -R 755 $(SITE_PACKAGES)/p4vasp/paint3d
	chmod -R 644 $(SITE_PACKAGES)/p4vasp/paint3d/*
	chmod -R 755 $(SITE_PACKAGES)/p4vasp/export
	chmod -R 644 $(SITE_PACKAGES)/p4vasp/export/*
	chmod -R 755 $(SITE_PACKAGES)/p4vasp/piddle
	cd src; install -m755  cp4vasp.py _cp4vasp.so $(SITE_PACKAGES); cd ..

install_gui:install_pythonpkg uninstallsh launcher
	mkdir -p     $(P4VASP_HOME)
	cp -R data   $(P4VASP_HOME)
	cp -R utils  $(P4VASP_HOME)
	chmod -R 755 $(P4VASP_HOME)/data
	chmod    644 $(P4VASP_HOME)/data/*
	chmod    755 $(P4VASP_HOME)/data/glade
	chmod    644 $(P4VASP_HOME)/data/glade/*
	chmod    755 $(P4VASP_HOME)/data/glade/pixmaps
	chmod    644 $(P4VASP_HOME)/data/glade/pixmaps/*
	chmod    755 $(P4VASP_HOME)/data/glade2
	chmod    644 $(P4VASP_HOME)/data/glade2/*
	chmod    755 $(P4VASP_HOME)/data/glade2/pixmaps
	chmod    644 $(P4VASP_HOME)/data/glade2/pixmaps/*
	chmod    755 $(P4VASP_HOME)/data/graphs
	chmod    644 $(P4VASP_HOME)/data/graphs/*
	chmod    755 $(P4VASP_HOME)/data/images
	chmod    644 $(P4VASP_HOME)/data/images/*
	chmod    755 $(P4VASP_HOME)/data/database
	chmod    644 $(P4VASP_HOME)/data/database/*
	chmod -R 755 $(P4VASP_HOME)/utils

	install -m755 uninstall.sh $(P4VASP_HOME)/uninstall.sh
	install -m755 diagnostic.py $(P4VASP_HOME)/diagnostic.py

	install -m644 BUGS FAQS LICENSE README $(P4VASP_HOME)
	mkdir -p $(BINDIR)
	install -d -m755     $(BINDIR)
	install -m755 p4v.py $(BINDIR)/p4v.py
	install -m755 $(P4V) $(BINDIR)/$(P4V)

install_doc:
	mkdir -p       $(P4VASP_HOME)
	cp -R doc      $(P4VASP_HOME)
	chmod -R 755   $(P4VASP_HOME)/doc
	chmod    644   $(P4VASP_HOME)/doc/*
	chmod -R 755   $(P4VASP_HOME)/doc/api
	chmod    644   $(P4VASP_HOME)/doc/api/*
	chmod -R 755   $(P4VASP_HOME)/doc/api/c
	chmod -R 755   $(P4VASP_HOME)/doc/api/python
	chmod -R 755   $(P4VASP_HOME)/doc/intro
	chmod    644   $(P4VASP_HOME)/doc/intro/*

install_devel:install_pythonpkg
	mkdir -p $(LIBDIR)
	mkdir -p $(INCLUDEDIR)/ODP
	mkdir -p $(INCLUDEDIR)/p4vasp
	cp -R odpdom/include/ODP $(INCLUDEDIR)
	cp -R src/include/p4vasp $(INCLUDEDIR)
	chmod 755 $(INCLUDEDIR)/ODP
	chmod 755 $(INCLUDEDIR)/p4vasp
	chmod 644 $(INCLUDEDIR)/ODP/*
	chmod 644 $(INCLUDEDIR)/p4vasp/*
	cp src/libp4vasp.a $(LIBDIR)
	chmod 644 $(LIBDIR)/libp4vasp.a
	cp odpdom/libODP.a $(LIBDIR)
	chmod 644 $(LIBDIR)/libODP.a
install:install_gui install_devel

uninstallsh:
	echo "#!/bin/sh" >uninstall.sh
	echo "rm -Rf $(SITE_PACKAGES)/p4vasp" >>uninstall.sh
	echo "rm -Rf $(SITE_PACKAGES)/cp4vasp.py" >>uninstall.sh
	echo "rm -Rf $(SITE_PACKAGES)/_cp4vasp.so" >>uninstall.sh
	echo "rm -f  $(BINDIR)/p4v.py" >>uninstall.sh
	echo "rm -f  $(BINDIR)/p4v" >>uninstall.sh
	echo "rm -Rf $(INCLUDEDIR)/ODP" >>uninstall.sh
	echo "rm -Rf $(INCLUDEDIR)/p4vasp" >>uninstall.sh
	echo "rm -Rf $(LIBDIR)/libp4vasp.a " >>uninstall.sh
	echo "rm -Rf $(LIBDIR)/libODP.a" >>uninstall.sh
	echo "rm -Rf $(P4VASP_HOME)" >>uninstall.sh
uninstall_pythonpkg:
	rm -Rf $(SITE_PACKAGES)/p4vasp
	rm -Rf $(SITE_PACKAGES)/cp4vasp.py
	rm -Rf $(SITE_PACKAGES)/_cp4vasp.so

uninstall_gui:
	rm -Rf $(P4VASP_HOME)
	rm -f  $(BINDIR)/p4v.py
	rm -f  $(BINDIR)/p4v

uninstall_devel:
	rm -Rf $(INCLUDEDIR)/ODP
	rm -Rf $(INCLUDEDIR)/p4vasp
	rm -Rf $(LIBDIR)/libp4vasp.a
	rm -Rf $(LIBDIR)/libODP.a
uninstall:uninstall_gui uninstall_devel uninstall_pythonpkg
