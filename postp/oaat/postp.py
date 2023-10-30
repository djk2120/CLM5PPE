import xarray as xr
import glob
import numpy as np
import sys

def ppfiles(k,exps,top='/glade/campaign/cgd/tss/projects/PPE/PPEn11_OAAT/'):

    h1=[glob.glob(top+exp+'/hist/*'+k+'*h1*')[0] for exp in exps]
    h0=[glob.glob(top+exp+'/hist/*'+k+'*h0*')[0] for exp in exps]
    return h0,h1

def amean(da):
    #annual mean of monthly data
    m  = da['time.daysinmonth']
    cf = 1/365
    xa = cf*(m*da).groupby('time.year').sum().compute()
    return xa

def pftmean(da,lapft,pft):
    x=1/lapft.groupby(pft).sum()*(lapft*da).groupby(pft).sum()
    return x.compute()
    
def bmean(da,la,b):
    x=1/la.groupby(b).sum()*(la*da).groupby(b).sum()
    return x.compute()

def gmean(da,la):
    if 'gridcell' in da.dims:
        dim='gridcell'
    else:
        dim=['lat','lon']
    x=(da*la).sum(dim=dim)/la.sum()
    return x.compute()

def fix_time(ds):
    yr0=str(ds['time.year'][0].values)
    nt=len(ds.time)
    ds['time'] = xr.cftime_range(yr0,periods=nt,freq='MS',calendar='noleap') #fix time bug
    return ds

def postp(k):
    exps=['CTL2010','C285','C867','AF1855','AF2095','NDEP']
    h0,h1=ppfiles(k,exps)
    
    dvs=['GPP','AR','HR','NPP','NBP','NEP','ER',
         'EFLX_LH_TOT','FCTR','FCEV','FGEV','BTRANMN','FGR','FSH',
         'SOILWATER_10CM','TWS','QRUNOFF','SNOWDP','H2OSNO','FSNO',
         'TLAI','FSR','ALTMAX','TV','TG',
         'FAREA_BURNED','COL_FIRE_CLOSS',
         'TOTVEGC','TOTECOSYSC','TOTSOMC_1m',
         'TOTVEGN','TOTECOSYSN']
    def pp(ds):
        return ds[dvs]
    
    ds=fix_time(xr.open_mfdataset(h0,combine='nested',concat_dim='exp',
                              preprocess=pp))
    ds1=fix_time(xr.open_mfdataset(h1,combine='nested',concat_dim='exp'))
    
    la=xr.open_dataset('sparsegrid_landarea.nc').landarea
    lapft=xr.open_dataset('sparsegrid_landarea.nc').landarea_pft
    
    b=xr.open_dataset('whitkey.nc').biome
    pft=xr.DataArray(ds1.pfts1d_itype_veg.isel(exp=0).values,dims='pft',name='pft')
    out=xr.Dataset()
    
    for v in dvs:

        x=amean(ds[v])
        amp=(ds[v].groupby('time.year').max()-ds[v].groupby('time.year').min()).mean(dim='year').compute()

        out[v+'_gridded_mean']=x.mean(dim='year')

        out[v+'_global_amp'] =gmean(amp,la)
        out[v+'_global_std'] =gmean(x.std(dim='year'),la)
        out[v+'_global_mean']=gmean(x.mean(dim='year'),la)

        out[v+'_biome_amp']  =bmean(amp,la,b)
        out[v+'_biome_std']  =bmean(x.std(dim='year'),la,b)
        out[v+'_biome_mean'] =bmean(x.mean(dim='year'),la,b)

        if v in ds1.data_vars:
            if v!='HR':
                x=amean(ds1[v])
                amp=(ds1[v].groupby('time.year').max()-ds1[v].groupby('time.year').min()).mean(dim='year').compute()

                out[v+'_pft_amp']  =pftmean(amp,lapft,pft)
                out[v+'_pft_std']  =pftmean(x.std(dim='year'),lapft,pft)
                out[v+'_pft_mean'] =pftmean(x.mean(dim='year'),lapft,pft)


        for dv in out.data_vars:
            if v in dv:
                out[dv].attrs=ds[v].attrs
    out['exp']=exps
    
    out.to_netcdf('/glade/scratch/djk2120/postp/oaat/'+k+'.postp.nc')
    return


k=sys.argv[1]
postp(k)
