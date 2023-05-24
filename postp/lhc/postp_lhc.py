import numpy as np
import pandas as pd
import xarray as xr
import sys

def preprocess(ds):
    dvs=[]
    if float(abs((ds.time[1]-ds.time[0])/(28*24*60*60*1e9)-1))<0.05:
        nt=len(ds.time)
        yr0=ds['time.year'].values[0]
        ds['time']=xr.cftime_range(str(yr0),periods=nt,freq='MS',calendar='noleap')
    if len(dvs)>0:
        ds=ds[dvs]
    return ds

def amean(da,cf=1/365,u=None):
    #annual mean
    m  = da['time.daysinmonth']
    xa = cf*(m*da).groupby('time.year').sum().compute()
    xa.name=da.name
    xa.attrs=da.attrs
    if u:
        x.attrs['units']=u
    return xa

def gmean(da,la,g=[],cf=None,u=None):
    '''
    g defines the averaging group,
    g=[] is global, otherwise use ds.biome or ds.pft
    '''
    if len(g)==0:
        g=xr.DataArray(np.tile('global',len(da.gridcell)),dims='gridcell',name='biome')
    if not cf:
        cf=1/la.groupby(g).sum()

    x=cf*(da*la).groupby(g).sum()
    x.name=da.name
    x.attrs=da.attrs
    if u:
        x.attrs['units']=u
    if len(x.dims)>0:
        if x.dims[0]!='ens':
            x=x.T  
    
    return x.compute()

def makeann(file_list):
    files=pd.read_csv(file_list,header=None)[0].values
    lafile='/glade/u/home/djk2120/ppe_clean/pyth/sparsegrid_landarea.nc'
    bfile='/glade/u/home/djk2120/ppe_clean/pyth/whit/whitkey.nc'
    la=xr.open_dataset(lafile).landarea
    whit=xr.open_dataset(bfile)
    g=xr.DataArray([str(whit.biome_name[int(i)].values) for i in whit.biome.values],dims='gridcell',name='biome')
    dvs=['TOTVEGC','TOTECOSYSC','TOTSOMC','TOTSOMC_1m','TLAI','GPP','HR','AR','COL_FIRE_CLOSS','NPP','NEP','NBP']
    dout='/glade/scratch/djk2120/postp/'
    for f in files:
        key='LHC'+f.split('LHC')[1].split('.')[0]
        ystr=f.split('.')[-2][:4]
        fout=dout+'ccycle.ann.'+key+'.'+ystr+'.nc'
        ds=preprocess(xr.open_dataset(f))

        ann={}
        for v in dvs:
            xg=gmean(amean(ds[v]),la)
            xb=gmean(amean(ds[v]),la,g=g)
            ann[v]=xr.concat([xg,xb],dim='biome')

        out=xr.Dataset(ann)
        out.attrs={'orig':f,'key':key,'lafile':lafile,'bfile':bfile}
        out.to_netcdf(fout,unlimited_dims='year')


file_list=sys.argv[1]
makeann(file_list)
