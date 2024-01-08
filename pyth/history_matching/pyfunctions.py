import os
import numpy as np
import xarray as xr
import cftime
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import glob
import dask

# spatial averaging

whit = xr.open_dataset('./whit/whitkey.nc')
def bmean(da,la):
    g=whit.biome
    xb=1/la.groupby(g).sum()*(la*da).groupby(g).sum(dim='gridcell').compute()
    xb['biome_name']=xr.DataArray(whit.biome_name.values,dims='biome')
    return xb

def amax(da,cf=1):
    #annual max
    m  = da['time.daysinmonth']
    xa = da.groupby('time.year').max().compute()
    return xa

def amean(da,cf=1/365):
    #annual mean
    m  = da['time.daysinmonth']
    xa = cf*(m*da).groupby('time.year').sum().compute()
    xa.name=da.name
    return xa

def pmean(da,la):
    xp=(1/la.groupby('pft').sum()*(da*la).groupby('pft').sum()).compute()
    return xp

def pbmean(da,minarea=5e4):
    #read in biome vector and pft vector
    whit=xr.open_dataset('whit/whitkey.nc')
    f='/glade/campaign/cgd/tss/projects/PPE/PPEn11_LHC/transient/hist/PPEn11_transient_LHC0000.clm2.h1.2005-02-01-00000.nc'
    ds=xr.open_dataset(f)
    pft=ds.pfts1d_itype_veg

    #define the pft-x-biome group
    pftbiome=xr.DataArray(np.zeros(ds.pft.shape)+np.nan,dims='pft',name='pb')
    for i in range(1,17):
        pftbiome[pft==i]=whit.biome+10*i

    lapft=xr.open_dataset('landarea_transient.nc').landarea_pft
    a=lapft.groupby('time.year').mean()

    asum=a.groupby(pftbiome).sum()
    asum=asum.where(asum>minarea)
    dapb=1/asum*(a*da).groupby(pftbiome).sum().compute()
    
    #append useful labels
    pb=dapb.pb
    dapb['pft']  =np.floor(pb/10).astype(int)
    dapb['biome']=(pb-10*dapb.pft).astype(int)
    
    return dapb


# load observational data

def get_la():
    #get landarea info
    la_file = '/glade/u/home/djk2120/clm5ppe/pyth/sparsegrid_landarea.nc'
    la = xr.open_dataset(la_file).landarea  #km2
    
    return la

def get_sparsegrid():
    # get sparse grid info:
    f='/glade/campaign/asp/djk2120/PPEn11/transient/hist/PPEn11_transient_LHC0500.clm2.h0.2010-02-01-00000.nc'
    ds2=xr.open_dataset(f)
    ivals=ds2.grid1d_ixy.astype(int)-1  #python indexing starts at 0
    jvals=ds2.grid1d_jxy.astype(int)-1
    return jvals, ivals

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

def get_SP(htape):
    # returns CLM-SP simulated TLAI on sparse grid (2000)
    # we think the LAI is the MODIS climatology from (2003-2007)

    jvals, ivals = get_sparsegrid()
    
    if htape == 'h0':
        ds_sp=xr.open_dataset('/glade/scratch/linnia/archive/LAI_SP_ctsm51d115/lnd/hist/LAI_SP_ctsm51d115.clm2.h0.2000-02-01-00000.nc')
        ds_sp['time']=xr.cftime_range('2000',periods=12,freq='MS',calendar='noleap')
        SP_sg = ds_sp.TLAI[:,jvals,ivals]
    
    elif htape =='h1':
        # load SP on pfts (full grid)
        ds_sp=xr.open_dataset('/glade/scratch/linnia/archive/LAI_SP_ctsm51d115/lnd/hist/LAI_SP_ctsm51d115.clm2.h1.2000-02-01-00000.nc')
        ds_sp['time']=xr.cftime_range('2000',periods=12,freq='MS',calendar='noleap')
        #sg=xr.open_dataset('../clusters.clm51_PPEn02ctsm51d021_2deg_GSWP3V1_leafbiomassesai_PPE3_hist.annual+sd.400.nc')
        #la=sg.landfrac*sg.area
        SP_sg = ds_sp.TLAI
        
    else: 
        print('htape must be h1 or h0')
        
    return SP_sg

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
