import os
import numpy as np
import xarray as xr
import cftime
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import glob

#define the directory structure to find files
def get_files(name,htape,keys):
    topdir     = '/glade/campaign/asp/djk2120/PPEn11/' 
    thisdir    = topdir+name+'/hist/'
    files      = [glob.glob(thisdir+'*'+key+'*'+htape+'*.nc')[0] for key in keys]
    return files

def ppe_init(csv='/glade/scratch/djk2120/PPEn11/surv.csv'):
    paramkey = pd.read_csv(csv)
    keys = paramkey.key

    #fetch the sparsegrid landarea
    la_file = '/glade/scratch/djk2120/PPEn08/sparsegrid_landarea.nc'
    la = xr.open_dataset(la_file).landarea  #km2
    # pft area
    f = get_files('CTL2010','h1',keys[0])[0]
    lapft = get_lapft(la,f)
    
    
    #load conversion factors
    attrs = pd.read_csv('agg_units.csv',index_col=0)

    #dummy dataset
    p,m = get_params(keys,paramkey)
    ds0 = xr.Dataset()
    ds0['param']  =xr.DataArray(p,dims='ens')
    ds0['minmax'] =xr.DataArray(m,dims='ens')
    ds0['key']    =xr.DataArray(keys,dims='ens')
    whit = xr.open_dataset('./whit/whitkey.nc')
    ds0['biome']      = whit['biome']
    ds0['biome_name'] = whit['biome_name']
    
    return ds0,la,lapft,attrs,paramkey,keys
def get_ensemble(data_vars,ensemble,htape,
                 csv='/glade/scratch/djk2120/PPEn11/surv.csv',
                 keys=[],paramkey='',p=True,extras=[]):

    def preprocess(ds):
        return ds[data_vars]

    if csv:
        ds0,la,lapft,attrs,paramkey,keys = ppe_init(csv=csv)
    
    #read in the dataset
    files = get_files(ensemble,htape,keys)
    ds = xr.open_mfdataset(files,combine='nested',concat_dim='ens',
                           parallel=p,preprocess=preprocess)

    #diagnose htape
    htape = files[0].split('clm2.')[1].split('.')[0]
    
    #make time more sensible
    if htape=='h0' or htape=='h1':
        ds['time'] = xr.cftime_range(str(2005),periods=len(ds.time),freq='MS')
    elif htape=='h5':
        nt = len(ds.time)
        t  = ds.time.isel(time=np.arange(nt)<nt-1)
        ds = ds.isel(time=np.arange(nt)>0)
        ds['time']=t

    #specify extra variables
    if not extras:
        if htape=='h1':
            extras     = ['pfts1d_lat','pfts1d_lon','pfts1d_itype_veg']
        else:
            extras     = ['grid1d_lat','grid1d_lon']

    
    #add in some extra variables
    ds0 = xr.open_dataset(files[0])
    for extra in extras:
        ds[extra]=ds0[extra]
        
    #append some info about key/param/minmax/biome
    params,minmaxs = get_params(keys,paramkey) 
    ds['key']    = xr.DataArray(keys,dims='ens')
    ds['param']  = xr.DataArray(params,dims='ens')
    ds['minmax'] = xr.DataArray(minmaxs,dims='ens')
    whit         = xr.open_dataset('./whit/whitkey.nc')
    ds['biome']      = whit['biome']
    ds['biome_name'] = whit['biome_name']
    if htape=='h1':
        ds['pft'] = ds.pfts1d_itype_veg

    return ds


def get_map(da):
    '''
    Regrid from sparsegrid to standard lat/lon
    
    Better to do any dimension-reducing math before calling this function. 
    Could otherwise be pretty slow...
    '''
    
    #ACCESS the sparsegrid info
    thedir  = '/glade/u/home/forrest/ppe_representativeness/output_v4/'
    thefile = 'clusters.clm51_PPEn02ctsm51d021_2deg_GSWP3V1_leafbiomassesai_PPE3_hist.annual+sd.400.nc'
    sg = xr.open_dataset(thedir+thefile)
    
    #DIAGNOSE the shape of the output map
    newshape = []
    coords=[]
    #  grab any dimensions that arent "gridcell" from da
    for coord,nx in zip(da.coords,da.shape):
        if nx!=400:
            newshape.append(nx)
            coords.append((coord,da[coord].values))
    #  grab lat/lon from sg
    for coord in ['lat','lon']:
        nx = len(sg[coord])
        newshape.append(nx)
        coords.append((coord,sg[coord].values))

    #INSTANTIATE the outgoing array
    array = np.zeros(newshape)+np.nan
    nd    = len(array.shape)
    
    #FILL the array
    ds = xr.open_dataset('/glade/scratch/djk2120/PPEn11/hist/CTL2010/PPEn11_CTL2010_OAAT0399.clm2.h0.2005-02-01-00000.nc')
    for i in range(400):
        lat=ds.grid1d_lat[i]
        lon=ds.grid1d_lon[i]
        cc = sg.rcent.sel(lat=lat,lon=lon,method='nearest')
        ix = sg.cclass==cc
        
        
        if nd==2:
            array[ix]=da.isel(gridcell=i)
        else:
            nx = ix.sum().values
            array[:,ix]=np.tile(da.isel(gridcell=i).values[:,np.newaxis],[1,nx])
    
    #OUTPUT as DataArray
    da_map = xr.DataArray(array,name=da.name,coords=coords)
    da_map.attrs=da.attrs

    return da_map

def get_params(keys,paramkey):
    params=[]
    minmaxs=[]
    for key in keys:
        ix     = paramkey.key==key
        params.append(paramkey.param[ix].values[0])
        minmaxs.append(paramkey.minmax[ix].values[0])
    return params,minmaxs

def month_wts(nyears):
    '''
    returns an xr.DataArray of days per month, tiled for nyears
    '''
    days_pm  = [31,28,31,30,31,30,31,31,30,31,30,31]
    return xr.DataArray(np.tile(days_pm,nyears),dims='time')

def get_lapft(la,sample_h1):
    
    tmp = xr.open_dataset(sample_h1)

    nx = len(tmp.pfts1d_lat)
    pfts1d_area = np.zeros(nx)
    for i,lat,lon in zip(range(nx),tmp.pfts1d_lat,tmp.pfts1d_lon):
        ixlat = abs(lat-tmp.grid1d_lat)<0.1
        ixlon = abs(lon-tmp.grid1d_lon)<0.1
        ix    = (ixlat)&(ixlon)

        pfts1d_area[i] = la[ix]

    lapft = pfts1d_area*tmp.pfts1d_wtgcell
    lapft.name = 'patch area'
    lapft.attrs['long_name'] = 'pft patch area, within the sparsegrid'
    lapft.attrs['units'] = 'km2'
    return lapft

def get_cfs(attrs,datavar,ds):
    if datavar in attrs.index:
        cf1   = attrs.cf1[datavar]
        cf2   = attrs.cf2[datavar]
        units = attrs.units[datavar]
    else:
        cf1   = 1/365
        cf2   = 0        #flag to use 1/la.sum()
        if datavar in ds:
            units = ds[datavar].attrs['units']
        else:
            units = 'tbd'       
    return cf1,cf2,units

def ann_mean(x,cf=1/365):
    ny = len(np.unique(x['time.year']))
    xann = cf*(month_wts(ny)*x).groupby('time.year').sum()
    return xann

def reg_mean(x,la,cf=0,g=[]):
    if len(g)==0: #global mean
        g = la.copy(deep=True)*0+1
        g.name = 'glob'
    if cf==0:
        cf = 1/la.groupby(g).sum()
    xreg = cf*(la.values*x).groupby(g).sum().compute()
    if 'glob' in xreg.dims:
        xreg = xreg.isel(glob=0).drop('glob')
    return xreg

def calc_mean(datavar,ens,d='global',
              csv='/glade/scratch/djk2120/PPEn11/surv.csv',
              overwrite=False,
              save=True):
    
    f = ens+'_'+datavar+'_ann.nc'
    preload = '/glade/u/home/djk2120/clm5ppe/data/'+f
    
    if not glob.glob(preload):
        preload = '../data/'+f

    if overwrite:
        os.system('rm '+preload)
      
    if glob.glob(preload):
        xout = xr.open_dataset(preload)
    else:
        ds0,la,lapft,attrs,paramkey,keys = ppe_init(csv=csv)
        dvs   = datavar.split('-')
        domains = {'h0':['global','biome'],
                   'h1':['pft']}
        xout = xr.Dataset()
        for htape,la_x in zip(['h0','h1'],[la,lapft]):
            ds    = get_ensemble(dvs,ens,htape,csv='',keys=keys,paramkey=paramkey)
            cf1,cf2,units = get_cfs(attrs,datavar,ds)
            if dvs[0] in ds:
                x     = ds[dvs[0]]
                if len(dvs)==2:
                    ix = ds[dvs[1]]>0
                    x  = (x/ds[dvs[1]]).where(ix).fillna(0)

                for domain in domains[htape]:
                    if domain=='global':
                        g=[]
                    else:
                        g=ds[domain]

                    xann     = ann_mean(x,cf1)
                    xann_reg = reg_mean(xann,la_x,cf2,g)                
                    v = datavar+'_'+domain
                    xout[v]=xann_reg
                
        xout.attrs={'units':units}
    
    if not glob.glob(preload):
        if save:
            if not os.path.isdir('../data/'):
                os.system('mkdir ../data')
            xout.to_netcdf(preload)
    
    #######
    v = datavar+'_'+d
    x = xout[v]
    xm    = x.mean(dim='year')
    xiav  = x.std(dim='year')
    units = xout.attrs['units']
    
    return xm,xiav,units

def find_pair(da,params,minmax,p):
    '''
    returns a subset of da, corresponding to parameter-p
        the returned pair corresponds to [p_min,p_max]
    '''
    ixmin = np.logical_and(params==p,minmax=='min')
    ixmax = np.logical_and(params==p,minmax=='max')
    
    #sub in default if either is missing
    if ixmin.sum().values==0:
        ixmin = params=='default'
    if ixmax.sum().values==0:
        ixmax = params=='default'
        
    emin = da.ens.isel(ens=ixmin).values[0]
    emax = da.ens.isel(ens=ixmax).values[0]

    return da.sel(ens=[emin,emax])

def top_n(da,nx,params,minmax,uniques=[]):
    '''
    Sort for the largest perturbation effects
    
    returns lists of xmin, xmax, and the param_name for the top nx perturbations
    '''
    
    if not uniques:
        uniques = list(np.unique(params))
        if 'default' in uniques:
            uniques.remove('default')
    
    xmins=[];xmaxs=[];dxs=[]
    for u in uniques:
        pair  = find_pair(da,params,minmax,u)
        xmin  = pair[0].values
        xmax  = pair[1].values
        dx    = abs(xmax-xmin)

        xmins.append(xmin)
        xmaxs.append(xmax)
        dxs.append(dx)

    ranks = np.argsort(dxs)

    pvals = [uniques[ranks[i]] for i in range(-nx,0)]
    xmins = [xmins[ranks[i]]   for i in range(-nx,0)]
    xmaxs = [xmaxs[ranks[i]]   for i in range(-nx,0)]
    
    return xmins,xmaxs,pvals

def rank_plot(da,ds,nx,ll=True,title=None,xlabel=None):
    xmins,xmaxs,pvals = top_n(da,nx,ds.param,ds.minmax)
    xdef = da.isel(ens=0)
    plt.plot([xdef,xdef],[0,nx-1],'k:',label='default')
    plt.scatter(xmins,range(nx),marker='o',facecolors='none', edgecolors='r',label='low-val')
    plt.plot(xmaxs,range(nx),'ro',label='high-val')
    
    if ll:
        plt.legend(loc=3)
    i=-1
    for xmin,xmax in zip(xmins,xmaxs):
        i+=1
        plt.plot([xmin,xmax],[i,i],'r')
    plt.yticks(range(nx),pvals)
    if not xlabel:
        xlabel = da.name+' ['+da.attrs['units']+']'
    if not title:
        title = da.name
    plt.xlabel(xlabel)
    plt.title(title);

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
