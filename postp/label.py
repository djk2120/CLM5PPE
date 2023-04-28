import xarray as xr
import pandas as pd
import numpy as np

d='/glade/u/home/djk2120/ppe_clean/postp/'
ds=xr.open_dataset(d+'OAAT.nc')
df=pd.read_csv(d+'survkey.csv')
params=df.param.values
df=pd.read_csv(d+'exps.txt',header=None)
exps=df[0].values
ds['param']=params
ds['minmax']=['min','max']
ds['exp']=exps
whit=xr.open_dataset(d+'whitkey.nc')
ds['biome_name']=xr.DataArray(whit.biome_name.values,dims='biome')
ds['la']=xr.open_dataset(d+'sparsegrid_landarea.nc').landarea
f='/glade/campaign/asp/djk2120/PPEn11/paramfiles/LHC0000.nc'
tmp=xr.open_dataset(f)
ds['pft_name']=xr.DataArray([str(p)[2:-1].strip() for p in tmp.pftname.values[:17]],dims='pft')
ds.attrs.pop('history');
ds.to_netcdf(d+'OAAT_surv.nc')
