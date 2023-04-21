import sys
import os
import xarray as xr
import numpy as np
import dask
from datetime import date


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



def main():
    f=sys.argv[1]
    exp=f.split('PPEn11/')[1].split('/')[0]    
    d='/glade/campaign/asp/djk2120/PPEn11/'+exp+'/postp/'
    if not os.path.isdir(d):
        os.system('mkdir -p '+d)

    w=d+f.split('/')[-1].split('.')[0]+'.nc'
    
    ds=xr.open_dataset(f)
    yr0=str(ds['time.year'][0].values)
    nt=len(ds.time)
    ds['time']=xr.cftime_range(yr0,periods=nt,freq='MS',calendar='noleap')
    la=xr.open_dataset('sparsegrid_landarea.nc').landarea
    whit = xr.open_dataset('whitkey.nc')
  
    dvs=['GPP','AR','HR','NPP','NBP',
         'EFLX_LH_TOT','FCTR','FCEV','FGEV',
         'SOILWATER_10CM','TWS',
         'TLAI','FSR',
         'FAREA_BURNED','COL_FIRE_CLOSS',
         'TOTVEGC','TOTECOSYSC','TOTSOMC_1m']

    out=xr.Dataset()
    for v in dvs:   

        u=ds[v].attrs['units']
        xann=amean(ds[v])

        das={}
        das['mean']=xann.mean(dim='year')
        das['std']=xann.std(dim='year')
        das['amp']=(ds[v].groupby('time.year').max()-ds[v].groupby('time.year').min()).mean(dim='year')

        
        g={'global':[],'biome':whit.biome}
        domains=['global','global','global','biome']
        ops=['mean','std','amp','mean']

        for d,op in zip(domains,ops):
            n=v+'_'+d+'_'+op
            out[n]=gmean(das[op],la,g=g[d])
            out[n].attrs['units']=u

        out[v+'_gridded_mean']=das['mean']
        out[v+'_gridded_mean'].attrs['units']=u
        out[v+'_gridded_std']=das['std']
        out[v+'_gridded_std'].attrs['units']=u

    out.attrs['Date']=str(date.today())
    out.attrs['Author']='djk2120@ucar.edu'
    out.attrs['Original']=f
    out.to_netcdf(w)
    
main()
