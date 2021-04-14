import os
import netCDF4

class Member(object):
    """
    Stores and works with a dictionary of ParamInfos.
    """

    def __init__(self, name, paramdict, basefile, minmax=None, flag=None):
        self._name = name
        self._paramdict = paramdict
        self._basefile = basefile
        self._minmax = minmax
        self._flag = flag
        
    @property
    def name(self):
        return self._name
    
    @property
    def paramdict(self):
        return self._paramdict

    @property
    def basefile(self):
        return self._basefile

    @property
    def minmax(self):
        return self._minmax

    @property
    def flag(self):
        return self._flag
    
    @name.setter
    def name(self, new_name):
        self._name = new_name
    
    def get_names(self):
        """
        Returns a list of parameter names.
        """
        
        names = []
        for param in self._paramdict:
            names.append(self._paramdict[param].name)
        return names

    def BFB(self,tol=1e-10):
        """
        Tests if all param values are within some tolerance of default values
        """
        bfb=True
        for param in self._paramdict:
            val     = self._paramdict[param].value
            defval  = self._paramdict[param].default
            matches = abs(val-defval)<tol
            if type(matches)==bool:
                match = matches
            else:
                match = matches.all()
            if not match:
                bfb=False
                break

        return bfb

    def write(self,paramdir,nldir):
        """
        write out new paramfile and nl_mods
        """
        # force dirs to end in /
        if not paramdir[-1]=='/':
            paramdir=paramdir+'/'
        if not nldir[-1]=='/':
            nldir=nldir+'/'

        pfile  = paramdir+self.name+'.nc'
        nlfile = nldir+self.name+'.txt' 

        ## CREATE and EDIT the new paramfile
        cmd = 'cp '+self._basefile+' '+pfile
        os.system(cmd)
        dset = netCDF4.Dataset(pfile,'r+')
        for param in self.get_names():
            if self._paramdict[param].location == "P":
                dset[param][:] = self._paramdict[param].value
        dset.close()

        ## CREATE and EDIT the nlfile
        # NOTE: this will create a file for each ensemble member, regardless of if nl mods are needed
        with open(nlfile,"w") as file:
            output = "! user_nl_clm namelist options written by generate_params:\n"
            file.write(output)
        for param in self.get_names():
            if self._paramdict[param].location == "N":
                with open(nlfile,"a") as file:
                    output = "%s=%s\n" % (param, self._paramdict[param].value) # TO DO: round values?
                    file.write(output)
                    

    def __repr__(self):
        return self._name
