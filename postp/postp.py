import sys
import os
import xarray as xr
import numpy as np
import dask
from datetime import date


cfs={}
for c in ['GPP','NPP','NEP','NBP','AR','HR','ER','COL_FIRE_CLOSS']:
    cfs[c]={'mean':(24*60*60,1e-9,'PgC/yr'),
            'std':(24*60*60/365,None,'gC/m2/d'),
            'amp':(24*60*60,None,'gC/m2/d')}
cfs['QRUNOFF']={'mean':(24*60*60/365,None,'mm/d'),
                'std':(24*60*60/365,None,'mm/d'),
                'amp':(24*60*60,None,'mm/d')}


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

def crunch(ds,v,la,op='mean',domain='global',cfs={},whit=None):
    ln=ds[v].attrs['long_name']
    if domain=='global':
        g=[]
    elif domain=='biome':
        g=whit.biome
    elif domain=='pft':
        g=ds.pft
        
    if v in cfs:
        cf1,cf2,u=cfs[v][op]
    else:
        cf1,cf2,u=None,None,ds[v].attrs['units']
    
    if op=='amp':
        if not cf1:cf1=1
        da=cf1*(ds[v].groupby('time.year').max()-
                ds[v].groupby('time.year').min()).mean(dim='year')
    elif op=='mean':
        da=amean(ds[v],cf=cf1).mean(dim='year')
    elif op=='std':
        da=amean(ds[v],cf=cf1).std(dim='year')
        
    n=v+'_'+domain+'_'+op
    out=gmean(da,la,cf=cf2,g=g)
    out.name=n
    out.attrs={'units':u,'long_name':ln}
    
    if domain=='global':
        da.name=v+'_gridded_'+op
        if v in cfs:
            u=cfs[v]['std'][2]
        da.attrs={'units':u,'long_name':ln}
        out=(out,da)
        
    return out

def postproc(d,exp,key):
    sg=xr.open_dataset('sparsegrid_landarea.nc')
    la={'global':sg.landarea,'biome':sg.landarea,
        'pft':sg.landarea_pft}
    whit = xr.open_dataset('whitkey.nc')

    files=sorted(glob.glob(d+exp+'/hist/*'+key+'*.nc'))
    tapes=[f.split('clm2')[1].split('.')[1] for f in files]
    files={t:f for t,f in zip(tapes,files)}

    f=files['h0'].split('/')[-1].split('h0')
    fout=f[0]+'postp'+f[1]
    
    dsets={}
    for tape in ['h0','h1']:
        ds=xr.open_dataset(files[tape])
        if (tape=='h1')|(tape=='h0'):
            yr0=str(ds['time.year'][0].values)
            nt=len(ds.time)
            ds['time']=xr.cftime_range(yr0,periods=nt,freq='MS',calendar='noleap')
        if tape=='h1':
            ds['pft']=ds.pfts1d_itype_veg
            la['pft']['pft']=ds.pfts1d_itype_veg
        dsets[tape]=ds
    dsets={'global':dsets['h0'],'biome':dsets['h0'],'pft':dsets['h1']}
    
    dvs=['GPP','AR','HR','NPP','NBP',
         'EFLX_LH_TOT','FCTR','FCEV','FGEV',
         'SOILWATER_10CM','TWS','QRUNOFF','SNOWDP','H2OSNO',
         'TLAI','FSR',
         'FAREA_BURNED','COL_FIRE_CLOSS',
         'TOTVEGC','TOTECOSYSC','TOTSOMC_1m']
    
    out=xr.Dataset()
    domains=['global','global','global','biome','pft']
    ops=['mean','std','amp','mean','mean']

    for v in dvs:
        for d,op in zip(domains,ops):
            ds=dsets[d]
            if v in ds.data_vars:
                if not (v=='HR')&(d=='pft'):
                    x=crunch(ds,v,la[d],op=op,domain=d,cfs=cfs,whit=whit)
                    if len(x)==2:
                        for x in x:
                            out[x.name]=x
                    else:
                        out[x.name]=x
            
    return out




def main():
    exp=f.split('PPEn11/')[1].split('/')[0]
    key=f.split('_')[-1].split('.')[0]
    d0='/glade/campaign/asp/djk2120/PPEn11/'
    d=d+exp+'/postp/'
    if not os.path.isdir(d):
        os.system('mkdir -p '+d)

    out=postproc(d0,exp,key)

    w=d+f.split('/')[-1].split('.')[0]+'.nc'
    out.attrs['Date']=str(date.today())
    out.attrs['Author']='djk2120@ucar.edu'
    out.attrs['Original']=f
    out.to_netcdf(w)
    
main()
