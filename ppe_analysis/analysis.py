import os
import numpy as np
import xarray as xr
import cftime
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import glob
import dask


def get_files(exp,tape='h0',yy=()):

    top='/glade/campaign/asp/djk2120/PPEn11/'
    d=top+exp+'/hist/'

    oaats=['CTL2010','C285','C867','AF1855','AF2095','NDEP']
    key={oaat:'/glade/campaign/asp/djk2120/PPEn11/csvs/surv.csv' for oaat in oaats}
    yys={oaat:(2005,2014) for oaat in oaats}
    key['transient']='/glade/campaign/asp/djk2120/PPEn11/csvs/lhc220926.txt'
    yys['transient']=(1850,2014)
    key['EmBE']='/glade/work/linnia/CLM-PPE-LAI_tests/exp1_EmBE/psets_exp1_EmBE_230419.txt' #LRH
    yys['EmBE']=(1850,2014) #LRH


    df=pd.read_csv(key[exp])  
    if not yy:
        yr0,yr1=yys[exp]
    else:
        yr0,yr1=yy

    if exp=='transient' or exp=='EmBE': #LRH
        keys = df.member.values
        appends={}
        params=[]
        for p in df.keys():
            if p!='member':
                appends[p]=xr.DataArray(np.concatenate(([np.nan],df[p].values)),dims='ens')
                params.append(p)
        appends['params']=xr.DataArray(params,dims='param')
        if exp=='transient': #LRH
            keys=np.concatenate((['LHC0000'],keys))
        else: #LRH
            keys=np.concatenate((['exp1_EmBE0001'],keys)) #LRH
        appends['key']=xr.DataArray(keys,dims='ens')

    else:
        keys=df.key.values
        appends={v:xr.DataArray(df[v].values,dims='ens') for v in ['key','param','minmax']}
       
    
    fs   = np.array(sorted(glob.glob(d+'*'+tape+'*')))
    yrs  = np.array([int(f.split(tape)[1][1:5]) for f in fs])

    #bump back yr0, if needed
    uyrs=np.unique(yrs)
    yr0=uyrs[(uyrs/yr0)<=1][-1]

    #find index to subset files
    ix    = (yrs>=yr0)&(yrs<=yr1)
    fs    = fs[ix] 

    #organize files to match sequence of keys
    ny=len(np.unique(yrs[ix]))
    
    if exp=='EmBE': #LRH
        fkeys=np.array([f.split('transient_')[1].split('.')[0] for f in fs]) #LRH
    else: #LRH
        fkeys=np.array([f.split(exp+'_')[1].split('.')[0] for f in fs])

    if ny==1:
        files=[fs[fkeys==k][0] for k in keys]
        dims  = 'ens'
    else:
        files=[list(fs[fkeys==k]) for k in keys]
        dims  = ['ens','time']

    #add landarea information
    if exp=='transient' or 'EmBE': #LRH
        fla='landarea_transient.nc'
    else:
        fla='landarea_oaat.nc'
    la=xr.open_dataset(fla)
    appends['la']=la.landarea
    if tape=='h1':
        appends['lapft']=la.landarea_pft
        
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

def amean(da,cf=1/365):
    #annual mean
    m  = da['time.daysinmonth']
    xa = cf*(m*da).groupby('time.year').sum().compute()
    xa.name=da.name
    return xa

def gmean(da,la,g=[],cf=None,u=None):
    '''
    g defines the averaging group,
    g=[] is global, otherwise use ds.biome or ds.pft
    '''
    if len(g)==0:
        g=xr.DataArray(np.tile('global',len(da.gridcell)),dims='gridcell')
    if not cf:
        cf=1/la.groupby(g).sum()
    with dask.config.set(**{'array.slicing.split_large_chunks': True}):
        x=cf*(da*la).groupby(g).sum()
    x.name=da.name
    x.attrs=da.attrs
    if u:
        x.attrs['units']=u
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


def get_map(da,sgmap=None):
    if not sgmap:
        sgmap=xr.open_dataset('sgmap.nc')
    return da.sel(gridcell=sgmap.cclass).where(sgmap.notnan).compute()



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

def top_n(da,nx):
    ''' return top_n by param effect '''
    dx=abs(da.sel(minmax='max')-da.sel(minmax='min'))
    ix=dx.argsort()[-nx:].values
    x=da.isel(param=ix)
    return x
def rank_plot(da,nx,ax=None):
    x = top_n(da,nx)
    xdef = da.sel(param='default',minmax='min')
    
    if not ax:
        fig=plt.figure()
        ax=fig.add_subplot()
    
    ax.plot([xdef,xdef],[0,nx-1],'k:',label='default')
    ax.scatter(x.sel(minmax='min'),range(nx),marker='o',facecolors='none', edgecolors='r',label='low-val')
    ax.plot(x.sel(minmax='max'),range(nx),'ro',label='high-val')

    i=-1
    for xmin,xmax in x:
        i+=1
        ax.plot([xmin,xmax],[i,i],'r')
    ax.set_yticks(range(nx))
    ax.set_yticklabels([p[:15] for p in x.param.values])



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
