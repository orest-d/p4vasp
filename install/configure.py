import sys
import os.path

class Configuration:
    def root(self):
        return "/"
    def site_packages(self):
        for path in sys.path:
            if "local" in path:
                continue
            path1,tail=os.path.split(path)
            if tail=="site-packages":
                return path
        for path in sys.path:
            if "local" in path:
                continue
            path1,tail=os.path.split(path)
            if tail=="dist-packages":
                return path
        for path in sys.path:
            path1,tail=os.path.split(path)
            if tail=="site-packages":
                return path
        for path in sys.path:
            path1,tail=os.path.split(path)
            if tail=="dist-packages":
                return path
        for path in sys.path:
            path1,tail=os.path.split(path)
            if "python" in tail:
                return path
        if len(sys.path):
            return sys.path[0]
        return "./"
    def p4vasp_home(self):
        return os.path.join(self.root(),"usr","lib","p4vasp")
    def include(self):
        return os.path.join(self.root(),"usr","include")
    def lib(self):
        return os.path.join(self.root(),"usr","lib")
    def bin(self):
        return os.path.join(self.root(),"usr","bin")
    def config(self):
        return """
    ROOT          = %s
    P4VASP_HOME   = %s
    SITE_PACKAGES = %s
    INCLUDEDIR    = %s
    LIBDIR        = %s
    BINDIR        = %s
    """%(
      self.root(),
      self.p4vasp_home(),
      self.site_packages(),
      self.include(),
      self.lib(),
      self.bin()
    )
    config_file="Configuration.mk"

    def save(self):
        f=open(self.config_file,"w")
        f.write(self.config())
        f.close()

class Local(Configuration):
    def root(self):
        return os.getenv('HOME')
    def site_packages(self):
        return os.path.join(self.root(),"p4vasp","python-packages")
    def p4vasp_home(self):
        return os.path.join(self.root(),"p4vasp")
    def include(self):
        return os.path.join(self.root(),"p4vasp","include")
    def lib(self):
        return os.path.join(self.root(),"p4vasp","lib")
    def bin(self):
        return os.path.join(self.root(),"p4vasp","bin")

if __name__=="__main__":
    if len(sys.argv)>1 and sys.argv[1]=='local':
        Local().save()
    else:
        Configuration().save()
