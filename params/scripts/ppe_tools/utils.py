import os
import numpy as np

def parse_val(param,loc,defval,thisval,sgn=1):
    if 'percent' in str(thisval):
        prcnt = float(thisval.split("percent")[0])
        value = defval+sgn*prcnt/100*defval
    elif loc=='N':
        value = thisval
    elif not thisval.shape:
        if not defval.shape:
            value=thisval
        else:
            value=np.zeros(defval.shape)
            value[:]=thisval
    elif thisval.shape==defval.shape:
        value = thisval
    else:
        value = np.tile(thisval,[defval.shape[0],1])
    return value


def nl_default(param,lndin):
    """
    use a lnd_in file to retrieve default namelist param value 
    """ 
    # search lnd_in file for the parameter by name and put output in a tmp file
    cmd = 'grep '+param+' '+lndin+' > tmp.zqz'
    ret = os.system(cmd)

    # parse the value from the parameter name
    f = open('tmp.zqz', 'r')
    tmp = f.read().split()[2]
    f.close()

    # cases where scientific notation is specified by a "d"
    if 'd' in tmp:
        tmp = tmp.split('d')
        x = float(tmp[0])*10**float(tmp[1])
    else:
        x = float(tmp)
        
    os.system('rm tmp.zqz')   
    return x
