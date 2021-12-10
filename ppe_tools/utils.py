import os
import numpy as np
from ppe_tools import ParamInfo

def parse_val(loc,defval,thisval,sgn=1):
    '''
    Parse the value to be used to set a new parameter value

    Parameters
    ----------
    loc : str
        Flag for whether the parameter can be found on the paramfile (\'P\') 
        or within the namelist (\'N\')
        Should be either \'P\' or \'N\'
    defval : numpy array
        The default value of the given parameter
    thisval : str, float, numpy array
        The input value that will be parsed.
        Contains special logic to apply percent perturbations:
            e.g. thisval=\'30percent\' will apply a 30 percent increase to defval
            Must contain the exact word \'percent\'
    sgn : integer, optional
        Integer that can be used to modify the sign of a percent perturbation.
        e.g. thisval=\'30percent\' along with sgn=-1 will apply a 30 percent REDUCTION to defval

    Returns
    -------
    value : float or numpy array
        The new parameter value correctly formatted to match either the paramfile or nlfile format
    '''

    if 'percent' in str(thisval):
        #logic to handle percent perturbations
        prcnt = float(thisval.split("percent")[0])
        value = defval+sgn*prcnt/100*defval
    elif loc=='N':
        #no work needed for other nl cases
        value = thisval
    elif not thisval.shape:
        #handles float/integer inputs
        if not defval.shape:
            #thisval and defval shape match, no work
            value=thisval
        else:
            #thisval and defval shape mismatch, populate new array with defval
            value=np.zeros(defval.shape)
            value[:]=thisval
    elif thisval.shape==defval.shape:
        #handles array inputs, when it matches defval shape
        value = thisval
    else:
        #otherwise tile the input to match defval shape
        #eg kmax,rootprof_beta
        value = np.tile(thisval,[defval.shape[0],1])
    return value


def get_default(param,loc,ds,lndin):
    """
    return the default value for a given parameter
    """
    if loc=='N':
        # search lnd_in file for the parameter by name and put output in a tmp file
        cmd = 'grep '+param+' '+lndin
        tmp = os.popen(cmd).read().split()[2]

        # cases where scientific notation is specified by a "d"
        if 'd' in tmp:
            tmp = tmp.split('d')
            x = float(tmp[0])*10**float(tmp[1])
        else:
            x = float(tmp)
    else:
        x=ds[param].values
        
    return x

def make_paraminfo(param,s,range_info,pfile,lndin,flag=None):

    minval           = range_info['min']
    maxval           = range_info['max']
    loc              = range_info['loc']
    defval           = get_default(param,loc,pfile,lndin)
    thismin          = parse_val(loc,defval,minval,-1)
    thismax          = parse_val(loc,defval,maxval,1)

    value            = thismin+(thismax-thismin)*s
    paraminfo        = ParamInfo(param, loc, defval, value,lhc=s,flag=flag)

    return paraminfo