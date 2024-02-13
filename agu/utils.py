import xarray as xr
import numpy as np
import glob
def amean(da):
    #annual mean of monthly data
    m  = da['time.daysinmonth']
    cf = 1/365
    xa = cf*(m*da).groupby('time.year').sum().compute()
    return xa

def gmean(da,la):
    if 'gridcell' in da.dims:
        dim='gridcell'
    else:
        dim=['lat','lon']
    x=(da*la).sum(dim=dim)/la.sum()
    return x.compute()

def bmean(da,la,biome):
    x=1/la.groupby(biome).sum()*(da*la).groupby(biome).sum()
    return x.compute()

def pmean(da,lapft):
    lasum=lapft.groupby('pft').sum().compute()
    x=1/lasum*(lapft*da).groupby(lapft.pft).sum()
    return x.compute()

def fix_time(ds):
    yr0=str(ds['time.year'][0].values)
    nt=len(ds.time)
    ds['time'] = xr.cftime_range(yr0,periods=nt,freq='MS',calendar='noleap') #fix time bug
    return ds

def get_exp(exp,dvs,yr0,yr1,tape='h0'):
    ''' Retrieve a subsetted dataset for the chosen experiment.

    Function arguments:
    exp -- one of 'transient', 'SSP126', 'SSP370'
    dvs -- data variables, e.g. ['TLAI','GPP']
    yr0/yr1 -- time range, inclusive
    tape -- history tape, one of 'h0', 'h1', 'h5'

    Returns:
    ds -- xarray dataset
    '''
    
    d='/glade/campaign/cgd/tss/projects/PPE/PPEn11_LHC/'+exp+'/hist/'
    yrs=parse_yrs((yr0,yr1),d,tape)
    files=[get_files(yr,d,tape) for yr in yrs]
    dims=['time','member']
    member=['LHC'+str(i).zfill(4) for i in range(501)]
    appends={'member':member}
    if tape=='h0':
        singles=['RAIN','SNOW','FSDS','TBOT','QBOT']
    else:
        singles=[]
    ds=get_ds(files,dims,dvs=dvs,appends=appends,singles=singles)
    return ds.sel(time=slice(str(yr0),str(yr1)))


def get_postp(exp):
    ''' Fetch the post-processed PPE as an xarray dataset.

    Function arguments:
    exp -- one of 'transient', 'SSP126', 'SSP370'

    Returns:
    ds -- xarray dataset

    Post-processing info:
    We computed the global annual average for a small set of common data variables.
    '''
    
    files=sorted(glob.glob('/glade/u/home/djk2120/ppe_clean/agu/postp/ag.'+exp+'.*'))
    ds=xr.open_mfdataset(files,combine='by_coords',parallel=True)
    return ds


def get_files(ystr,d,tape):
    return sorted(glob.glob(d+'*'+tape+'*'+ystr+'*.nc'))

def parse_yrs(yy,d,tape):
    ''' discern the years indicated in the desired history file 
    e.g. yy=(1995,2014) --> ystrs=['1995','2005']
    '''
    files=sorted(glob.glob(d+'*LHC0000*'+tape+'*'))
    yr0=np.array([int(f.split('.')[-2][:4]) for f in files])
    yr1=yr0+yr0[1]-yr0[0]
    ystrs=[str(yr0[(yr0<=yr)&(yr1>yr)][0])
           for yr in range(yy[0],yy[1]+1)]
    return np.unique(ystrs)

def get_ds(files,dims,dvs=[],appends={},singles=[]):
    if dvs:
        def preprocess(ds):
            return ds[dvs]
    else:
        def preprocess(ds):
            return ds

    ds = xr.open_mfdataset(files,combine='nested',concat_dim=dims,
                           parallel=True,
                           preprocess=preprocess)
    f=np.array(files).ravel()[0]
    htape=f.split('clm2')[1][1:3]

    #extra variables
    tmp = xr.open_dataset(f)
    extras=['grid1d_lat','grid1d_lon']
    ds[extras]=tmp[extras]
    
    #fix up time dimension, swap pft
    if (htape=='h0')|(htape=='h1'):
        ds=fix_time(ds)
    if (htape=='h1'):
        ds['pft']=tmp.pfts1d_itype_veg

    if singles:
        ds1=get_ds([f[0] for f in files],['time'])
        ds[singles]=ds1[singles]
    
    for append in appends:
        ds[append]=appends[append]
        
             
    return ds

def colorkey(x,nbins):
    cmap = plt.cm.viridis(np.linspace(0,1,nbins),alpha=0.5)
    x0,x1=x.quantile([0.05,0.95])
    qx=np.floor(nbins*(x-x0)/(x1-x0)).compute().astype(int)
    qx[qx<0]=0
    qx[qx>=nbins]=nbins-1
    colors=[cmap[q] for q in qx]
    edges=np.linspace(x0,x1,nbins+1)
    edges[0]=x.min().values
    edges[-1]=x.max().values
    mids=0.5*(edges[1:]+edges[:-1]).reshape([-1,1])

    return colors,edges,mids,x0,x1


def ord(i):
    if i%10==1:
        o=str(i)+'st'
    elif i%10==2:
        o=str(i)+'nd'
    else:
        o=str(i)+'th'
    return o


def brown_green():
    '''
    returns a colormap based on colorbrewer diverging brown->green
    '''

    # colorbrewer colormap, diverging, brown->green
    cmap = np.zeros([11,3]);
    cmap[0,:] = 84,48,5
    cmap[1,:] = 140,81,10
    cmap[2,:] = 191,129,45
    cmap[3,:] = 223,194,125
    cmap[4,:] = 246,232,195
    cmap[5,:] = 245,245,245
    cmap[6,:] = 199,234,229
    cmap[7,:] = 128,205,193
    cmap[8,:] = 53,151,143
    cmap[9,:] = 1,102,94
    cmap[10,:] = 0,60,48
    cmap = matplotlib.colors.ListedColormap(cmap/256)
    
    return cmap