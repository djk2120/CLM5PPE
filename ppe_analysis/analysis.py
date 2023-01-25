import os
import numpy as np
import xarray as xr
import cftime
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import glob

cfs={'QRUNOFF':{'cf1':24*60*60,'cf2':None},
     'GPP': {'cf1':24*60*60,'cf2':1e-9},
     'AR':  {'cf1':24*60*60,'cf2':1e-9},
     'HR':  {'cf1':24*60*60,'cf2':1e-9},
     'NBP': {'cf1':24*60*60,'cf2':1e-9},
     'FAREA_BURNED': {'cf1':24*60*60,'cf2':1}}
units={'QRUNOFF':'mm/d',
       'GPP':'PgC/yr',
       'HR':'PgC/yr',
       'AR':'PgC/yr',
       'NBP':'PgC/yr',
       'FAREA_BURNED':'km2'}

def get_files(exp,tape='h0',yy=()):

    top='/glade/campaign/asp/djk2120/PPEn11/'
    d=top+exp+'/hist/'

    oaats=['CTL2010','C285','C867','AF1855','AF2095','NDEP']
    key={oaat:'/glade/campaign/asp/djk2120/PPEn11/csvs/surv.csv' for oaat in oaats}
    yys={oaat:(2005,2014) for oaat in oaats}
    key['transient']='/glade/campaign/asp/djk2120/PPEn11/csvs/lhc220926.txt'
    yys['transient']=(1850,2014)
    

    df=pd.read_csv(key[exp])  
    if not yy:
        yr0,yr1=yys[exp]
    else:
        yr0,yr1=yy
    
    if exp=='transient':
        keys = df.member.values
        appends={}
        params=[]
        for p in df.keys():
            if p!='member':
                appends[p]=xr.DataArray(np.concatenate(([np.nan],df[p].values)),dims='ens')
                params.append(p)
        appends['params']=xr.DataArray(params,dims='param')
        keys=np.concatenate((['LHC0000'],keys))
        appends['key']=xr.DataArray(keys,dims='ens')

    else:
        keys=df.key.values
        appends={v:xr.DataArray(df[v].values,dims='ens') for v in ['key','param','minmax']}

        
    if exp=='transient':
        fla='landarea_transient.nc'
    else:
        fla='landarea_oaat.nc'
    la=xr.open_dataset(fla)
    appends['la']=la.landarea
    if tape=='h1':
        appends['lapft']=la.landarea_pft
        

    fs   = np.array(sorted(glob.glob(d+'*'+tape+'*')))
    yrs  = np.array([int(f.split(tape)[1][1:5]) for f in fs])
    mems = [f.split('/')[8].split('_')[-1].split('.')[0] for f in fs]
    ix   = [mem in keys for mem in mems]
    
    files=fs[ix]
    yrs=yrs[ix]
    
    #bump back yr0, if needed
    uyrs=np.unique(yrs)
    yr0=uyrs[(uyrs/yr0)<=1][-1]

    #find index to subset files
    ix    = (yrs>=yr0)&(yrs<=yr1)
    yrs   = yrs[ix]
    files = files[ix] 

    ny=len(np.unique(yrs))
    nens=len(keys)

    if ny>1:
        files = files.reshape([nens,ny])
        files = [list(f) for f in files]
        dims  = ['ens','time']
    else:
        dims  = 'ens'
    
    return files,appends,dims


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

    #add extra variables
    tmp = xr.open_dataset(f)
    for v in tmp.data_vars:
        if 'time' not in tmp[v].dims:
            if v not in ds:
                ds[v]=tmp[v]
    
    #fix up time dimension, swap pft
    if (htape=='h0')|(htape=='h1'):
        yr0=str(ds['time.year'][0].values)
        nt=len(ds.time)
        ds['time'] = xr.cftime_range(yr0,periods=nt,freq='MS',calendar='noleap') #fix time bug
    if (htape=='h1'):
        ds['pft']=ds['pfts1d_itype_veg']
        
    
    for append in appends:
        ds[append]=appends[append]
        
             
    return ds

def get_exp(exp,dvs=[],tape='h0',yy=(),defonly=False):
    '''
    exp: 'transient','CTL2010','C285','C867','AF1855','2095','NDEP'
    dvs:  e.g. ['TLAI']    or [] returns all available variables
    tape: 'h0','h1',etc.
    yy:   e.g. (2005,2014) or () returns all available years
    '''
    files,appends,dims=get_files(exp,tape=tape,yy=yy)
    
    if defonly:
        files=files[0]
        dims='time'
        
    ds=get_ds(files,dims,dvs=dvs,appends=appends)
    
    
    f,a,d=get_files(exp,tape='h0',yy=yy)
    singles=['RAIN','SNOW','TSA','RH2M','FSDS','WIND']
    tmp=get_ds(f[0],'time',dvs=singles)
    for s in singles:
        ds[s]=tmp[s]
    
    if len(yy)>0:  
        ds=ds.sel(time=slice(str(yy[0]),str(yy[1])))
    
    ds['PREC']=ds.RAIN+ds.SNOW
    
    t=ds.TSA-273.15
    rh=ds.RH2M/100
    es=0.61094*np.exp(17.625*t/(t+234.04))
    ds['VPD']=((1-rh)*es).compute()
    ds['VPD'].attrs={'long_name':'vapor pressure deficit','units':'kPa'}
    ds['VP']=(rh*es).compute()
    ds['VP'].attrs={'long_name':'vapor pressure','units':'kPa'}
    
    whit = xr.open_dataset('./whit/whitkey.nc')
    ds['biome']=whit.biome
    ds['biome_name']=whit.biome_name
                
    #get the pft names
    pfts=xr.open_dataset('/glade/campaign/asp/djk2120/PPEn11/paramfiles/OAAT0000.nc').pftname
    pfts=[str(p)[2:-1].strip() for p in pfts.values][:17]
    ds['pft_name']=xr.DataArray(pfts,dims='pft_id')
    
    return ds

def amean(da):
    #annual mean
    if da.name in cfs:
        cf=cfs[da.name]['cf1']
    else:
        cf=1/365

    m  = da['time.daysinmonth']
    xa = cf*(m*da).groupby('time.year').sum().compute()
    xa.name=da.name
    return xa

def gmean(da,la,g=[]):
    '''
    g defines the averaging group,
    g=[] is global, otherwise use ds.biome or ds.pft
    '''
    if len(g)==0:
        g=xr.DataArray(np.tile('global',len(da.gridcell)),dims='gridcell')
    if da.name in cfs:
        cf=cfs[da.name]['cf2']
    else:
        cf=1/la.groupby(g).sum()
    x=cf*(da*la).groupby(g).sum()
    x.name=da.name
    x.attrs=da.attrs
    if x.name in units:
        x.attrs['units']=units[da.name]
    if 'group' in x.dims:
        x=x.isel(group=0)
    if len(x.dims)>0:
        if x.dims[0]!='ens':
            x=x.T  
    
    return x.compute()

def get_ix(ds,pft):
    ix=ds.pfts1d_itype_veg==pft
    a=ds.pfts1d_lat[ix]
    o=ds.pfts1d_lon[ix]
    
    nlon=len(ds.lon)
    nlat=len(ds.lat)
    nx=len(a)

    lats=xr.DataArray(np.tile(ds.lat.values.reshape([-1,1,1]),[1,nlon,nx]),dims=['lat','lon','pft'])
    lons=xr.DataArray(np.tile(ds.lon.values.reshape([1,-1,1]),[nlat,1,nx]),dims=['lat','lon','pft'])
    ix=((abs(lats-a)<0.25)&(abs(lons-o)<0.25)).sum(dim='pft')
    
    return ix==1
def pftgrid(da,ds):

    #set up dims for outgoing data array
    dims=[]
    s=[]
    ix=get_ix(ds,1)
    for dim in da.dims:
        if dim !='pft':
            dims.append(dim)
            s.append(len(da[dim]))
    dims=[*dims,*ix.dims]
    s=[*s,*ix.shape]
    ndims=len(dims)

    das=[]
    ix0=[slice(None) for i in range(ndims-2)]

    pfts=np.unique(ds.pfts1d_itype_veg)
    for pft in pfts:
        out=np.zeros(s)+np.nan
        if pft>0:
            ix=get_ix(ds,pft)
            ix2=tuple([*ix0,ix])
            ixp=ds.pfts1d_itype_veg==pft
            out[ix2]=da.isel(pft=ixp)
        das.append(xr.DataArray(out.copy(),dims=dims))

    da_out=xr.concat(das,dim='pft')
    da_out['pft']=pfts
    da_out['lat']=ds.lat
    da_out['lon']=ds.lon
    for dim in da.dims:
        if dim !='pft':
            da_out[dim]=da[dim]
    
    return da_out

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

def rank_plot(da,ds,nx,ax=None):
    xmins,xmaxs,pvals = top_n(da,nx,ds.param,ds.minmax)
    xdef = da.isel(ens=0)
    
    if not ax:
        fig=plt.figure()
        ax=fig.add_subplot()
    
    ax.plot([xdef,xdef],[0,nx-1],'k:',label='default')
    ax.scatter(xmins,range(nx),marker='o',facecolors='none', edgecolors='r',label='low-val')
    ax.plot(xmaxs,range(nx),'ro',label='high-val')

    i=-1
    for xmin,xmax in zip(xmins,xmaxs):
        i+=1
        ax.plot([xmin,xmax],[i,i],'r')
    ax.set_yticks(range(nx))
    ax.set_yticklabels([p[:15] for p in pvals])



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
