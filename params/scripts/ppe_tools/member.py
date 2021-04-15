import os
import netCDF4

class Member(object):
    """
    Stores and works with a dictionary of ParamInfos.
    
    Parameters
    ----------
    name : str 
        A name for the member. Used as filename with write() method.
    paramdict: dict
        A dictionary containing all of the relevant ParamInfo's, 
        keyed by parameter name.
    basefile: str
        Path to the basepft file.
        e.g. \'/glade/p/cgd/tss/people/oleson/modify_param/ctsm51_params.c210217_kwo.c210222.nc\'
    minmax: str, optional
        Optional metadata indicating if the member is a minimum or maximum perturbation.
        Should be either \'min\' or \'max\'
    flag: str, optional
        Optional metadata to indicate a given flag.

    Returns
    -------
    member :
        New member object populated with the various ParamInfo's
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

    def BFB(self,tol=0):
        """
        Tests if all param values are within some tolerance of default values

        Parameters
        ----------
        tol : float, optional
            tolerance for equivalence testing

        Returns
        -------
        bfb : bool
            Logical test for if all parameters equal their default values
        """
        bfb=True
        for param in self._paramdict:
            val     = self._paramdict[param].value
            defval  = self._paramdict[param].default
            
            #test for equivalence
            matches = abs(val-defval)<=tol

            #must handle 0- and multi-dimensional parameters
            if type(matches)==bool:
                match = matches
            else:
                match = matches.all()
            if not match:
                bfb=False
                break #need not continue with False

        return bfb

    def write(self,paramdir,nldir):
        """
        write out this member's paramfile and nl_mods file

        paramfile and nlfile inherit Member.name and will write to:
            paramfile -> paramdir/name.nc
            nlfile    -> nldir/name.txt

        Existing files will be overwritten.

        Parameters
        ----------
        paramdir : str
            path to directory for writing paramfiles
        nldir : str
            path to directory for writing nlfiles
        """
        # force dirs to end in /
        if not paramdir[-1]=='/':
            paramdir=paramdir+'/'
        if not nldir[-1]=='/':
            nldir=nldir+'/'
        
        #establish paramfile and nlmods file names
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
