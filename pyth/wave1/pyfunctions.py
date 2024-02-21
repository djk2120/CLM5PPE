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
    f='/glade/work/djk2120/ppe_savs/pbmean/sg_lapxb.nc'
    lapxb=xr.open_dataset(f).lapxb
    ix=(lapxb.pxb>9)&(lapxb.mean(dim='year').sum(dim='pft')>minarea)
    dapb = 1/lapxb.sum(dim='pft')*(lapxb.isel(pxb=ix)*da).sum(dim='pft')

    #append useful labels
    pb=dapb.pxb
    dapb['pft']  =np.floor(pb/10).astype(int)
    dapb['biome']=(pb-10*dapb.pft).astype(int)

    return dapb

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

def get_obs_bmean(in_file,st_yr,en_yr,variable,max=False):
    ds = xr.open_dataset(in_file)
    t=slice(str(st_yr),str(en_yr))
    da=ds[variable].sel(time=t)

    la = get_la()
    jvals, ivals = get_sparsegrid() # function in pyfunctions.py
    da_sg = da[:,jvals,ivals]

    if (max):
        am = amax(da_sg).mean(dim='year').compute()
    else:
        am = amean(da_sg).mean(dim='year').compute()

    bm = bmean(am,la)

    return bm

def LHC_score(n,nbins,num_params,sample):
    # sample is np array with rows as ensemble members and columns as parameters
    # zero is a perfect Latin Hypercube
    Pb = n/nbins
    dim_count = []
    for di in range(num_params):
        data = sample[:,di]
        bin_count = []
        for bi in range(nbins):
            bin_width = 1/20
            bin_min = bi/nbins
            bin_max = bi/nbins+bin_width
            Ab = np.sum((data>bin_min)&(data<bin_max))
    
            bin_count.append(np.abs(Pb - Ab))
        dim_count.append(np.sum(bin_count))
    
    return np.sum(dim_count)