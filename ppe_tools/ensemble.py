import os
import numpy as np
import xarray as xr
from skopt.space import Space
from skopt.sampler import Lhs
from ppe_tools import Member, ParamInfo
from ppe_tools.utils import parse_val, get_default, make_paraminfo

class Ensemble(object):
    """
    Stores and works with a bunch of Members.
    """
    def __init__(self,basefile,pdir=None,ndir=None,lnd_in=None):
        self._members=[]
        self._basefile=basefile
        self._pdir=pdir
        self._ndir=ndir
        if lnd_in:
            self._lndin=lnd_in
        else:
            self._lndin='/glade/work/oleson/lmbirch_wkattge.n01_ctsm5.1.dev006/cime/scripts/clm51_lmbirchwkattgen01ctsm51d006_2deg_GSWP3V1_PPE_1850pAD/CaseDocs/lnd_in'
    @property
    def members(self):
        return self._members
    
    @property
    def nmemb(self):
        return len(self._members)

    def add_member(self,member):
        self._members.append(member)

    def add_mf(self,mf,prefix,nextnum=None):
        ds = xr.open_dataset(self._basefile,decode_times=False)
        paramdict={}
        for param in mf:
            loc = mf[param]['loc']
            if 'minmax' in mf[param]:
                minmax = mf[param]['minmax']
            else:
                minmax = None
            if 'flag' in mf[param]:
                flag = mf[param]['flag']
            else:
                flag = None
            if loc=='P':
                defval = ds[param].values
            else:
                defval = nl_default(param,self._lndin)
            thisval = mf[param]['value']
            value   = parse_val(loc,defval,thisval)
            paramdict[param]= ParamInfo(param, loc, defval, value)
        if not nextnum:
            nextnum = self.nmemb+1
        pname  = prefix+str(nextnum).zfill(4)
        member = Member(pname,paramdict,self._basefile,minmax,flag)
        self.add_member(member)

    def add_oaats(self,oaats,prefix,nextnum,skipBFB=True):
        ct = nextnum-1
        ds = xr.open_dataset(self._basefile,decode_times=False)
        sgns = {'min':-1,'max':1}

        for param in oaats:
            loc    = oaats[param]['loc']
            defval = get_default(param,loc,ds,self._lndin)

            for minmax in ['min','max']:
                thisval = oaats[param][minmax]
                sgn     = sgns[minmax]
                value   = parse_val(loc,defval,thisval,sgn)

                ct +=1
                pname  = prefix+str(ct).zfill(4)
                paraminfo = ParamInfo(param, loc, defval, value)
                paramdict = {param:paraminfo}
                member = Member(pname,paramdict,self._basefile,minmax)
                
                if type(defval)==float:
                    tol = 1e-10*defval
                elif defval.shape:
                    tol = max(1e-10,1e-10*max(defval.ravel()))
                else:
                    tol = 1e-10*defval
                bfb = member.BFB(tol=tol)


                if skipBFB&bfb:
                    print(param+'-'+minmax+' looks BFB.... skipping')
                    ct -=1
                else:
                    self.add_member(member)

    def add_lhcs(self,range_info,prefix,nextnum,n_samples):
        ct = nextnum-1
        params = [p for p in range_info]

        space = Space([(0.,1.) for p in params])
        lhs = Lhs(lhs_type="classic", criterion=None)
        lhc = lhs.generate(space.dimensions, n_samples)

        pfile = xr.open_dataset(self._basefile,decode_times=False)

        for i in range(n_samples):
            ct+=1
            paramdict={}

            for s,param in zip(lhc[i],params):
                
                if range_info[param]['flagged']:
                    for r in range_info[param]['flagged']:
                        rng          = range_info[param]['flagged'][r]
                        paraminfo    = make_paraminfo(r,s,rng,pfile,self._lndin,flag=param)
                        paramdict[r] = paraminfo
                else:
                    paraminfo = make_paraminfo(param,s,range_info[param],pfile,self._lndin)
                    paramdict[param] = paraminfo

            pname  = prefix+str(ct).zfill(4)
            member = Member(pname,paramdict,self._basefile)
            self.add_member(member)
    

    
    
    def write(self,default_key='',oaatfile='',lhcfile=''):
        if oaatfile:
            f = open(oaatfile, "a")
            if default_key:
                output = "%s,%s,%s\n" % (default_key,'default','default')
                f.write(output)
            for member in self.members:
                params = [*member.paramdict]
                if len(params)==1:
                    output = "%s,%s,%s\n" % (member.name,params[0],member.minmax)
                else:
                    output = "%s,%s,%s\n" % (member.name,member.flag,member.minmax)
                f.write(output)
            f.close()
        
        if lhcfile:
            f = open(lhcfile, "a")
            
            #write the file header
            m = self.members[0]
            params = [*m.paramdict]
            f.write('member')
            flags = []
            for param in params:
                flag = m.paramdict[param].flag
                if flag:
                    if flag not in flags:
                        f.write(','+flag)
                        flags.append(flag)
                else:
                    f.write(','+param)
            f.write('\n')

            #looping through members, write all param weightings
            for member in self.members:
                f.write(member.name)
                params = [*member.paramdict]
                flags = []
                for param in params:
                    flag = member.paramdict[param].flag
                    s    = str(member.paramdict[param].lhc)
                    if flag:
                        if flag not in flags:
                            f.write(','+s)
                            flags.append(flag)
                    else:
                        f.write(','+s)
                f.write('\n')
            f.close()
        
        if default_key:
            pfile  = self._pdir+default_key+'.nc'
            nlfile = self._ndir+default_key+'.txt'
            cmd = 'cp '+self._basefile+' '+pfile
            ret = os.system(cmd)
            with open(nlfile,"w") as file:
                output = "! user_nl_clm namelist options written by generate_params:\n"
                file.write(output)
        for member in self.members:
            member.write(self._pdir,self._ndir)
