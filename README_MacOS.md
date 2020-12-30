p4vasp compillation in MacOS:
(Tested on macOS 11.1)

0) Install Xcode command-line tools:
```
xcode-select --install
```

1) Using [macports](https://www.macports.org/install.php) to install dependencies:
```
sudo port install python27
sudo port install py27-pip
sudo port install py27-gobject
sudo port install gettext
sudo port install py-pygtk +x11
sudo port -v -s install fltk
```
Also, as we are going to use clang(gcc) that comes with the command-line tools, if you have installed gcc via macports, deactivate it:
```
sudo port select --set gcc none
```

2) Select our newly install python and pip as default:
```
sudo port select --set pip pip27
sudo port select --set python2 python27
```
Note that if you have a virtual environment, deactivate it.

3) Using pip to install:
```
pip install pyopengl numpy
```

4) Apply patches:
```
cp src/Makefile.MacOS src/Makefile
```
__OPTIONAL__: apply patch for VASP v5.4.4 and up:
```
patch -p0 < 544_update.patch
```

5) Compile p4vasp:
```
make local
make
```
__OPTIONAL__: change install dir by modify `install/Configuration.mk` file.

6) Install p4vasp:
```
make install
```
