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

def pmean(da,la):
    xp=(1/la.groupby('pft').sum()*(da*la).groupby('pft').sum()).compute()
    return xp

### Error metrics

def normalize(var):
    return (var-min(var))/(max(var)-min(var))

def unnormalize(norm_var,raw_var):
    return norm_var*np.array(max(raw_var)-min(raw_var)) + np.array(min(raw_var))

def cal_rmse(mod, obs):
    return np.sqrt(np.mean((mod-obs)**2))
    
def cal_nse(mod, obs): # Nash-Sutcliffe model efficiency coefficient
    mo = np.nanmean(obs)
    a = np.nansum([(mi - oi) ** 2 for mi, oi in zip(mod, obs)])
    b = np.nansum([(oi - mo) ** 2 for oi in obs])
    return 1 - a / b

def cal_nnse(mod, obs): # normalized Nash-Sutcliffe model efficiency coefficient
    mo = obs.mean()
    a = ((mod - obs) ** 2).sum()
    b = ((obs - mo) ** 2).sum()
    nse = 1 - a / b
    return 1 / (2 - nse)

def cal_mape(mod, obs): # mean absolute percent error
    mo = np.nanmean(obs)
    ape = [np.abs(mi - oi) / mo for mi, oi in zip(mod, obs)]
    return np.nanmean(ape,axis=0)

def cal_tape(mod, obs): # total absolute percent error
    mo = np.nanmean(obs)
    ape = [np.abs(mi - oi) / mo for mi, oi in zip(mod, obs)]
    return np.nansum(ape)

def cal_tae(mod, obs): # 
    error = np.abs(mod - obs)
    return np.sum(error,axis=0)
 
def month_of_annmax(data,v,):
    d = data.to_dataframe()
    d['month'] = d.index.month
    mon_max = d.loc[d.groupby(d.index.year)[v].idxmax()]
    
    return mon_max.month.values
    
def coef_var(data,temporal=True):
    if temporal:
        d = detrend(data)
    else:
        d = data
    stdev = np.std(d)
    m = np.mean(data)
    cv = stdev/m
    return cv


# Miscelleneous

def detrend(data):
    from sklearn.linear_model import LinearRegression
    # remove linear trend
    X = [i for i in range(0, len(data))]
    X = np.reshape(X, (len(X), 1))
    y = data
    model = LinearRegression()
    model.fit(X, y)

    trend = model.predict(X)

    detrended = [y[i]-trend[i] for i in range(0, len(data))]
    
    return detrended

def in_ellipse(point,center,radius):
    # all inputs are two dimensional arrays
    # returns TRUE if point is within ellipse
    x = point[0]; y = point[1]
    h = center[0]; k = center[1]
    rx = radius[0]; ry = radius[1]
    
    out = ((x-h)**2)/rx**2 + ((y-k)**2)/ry**2 
    
    return out<=1

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