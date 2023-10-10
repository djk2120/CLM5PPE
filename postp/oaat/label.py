import xarray as xr
import pandas as pd
import datetime

f='/glade/scratch/djk2120/postp/oaat/OAAT_surv.nc'
ds=xr.open_dataset(f)

df=pd.read_csv('/glade/campaign/cgd/tss/projects/PPE/PPEn11_OAAT/helpers/surviving.csv')
ds['param']=df.param.values
ds['minmax']=['min','max']
whit=xr.open_dataset('whitkey.nc')
ds['biome_name']=xr.DataArray(whit.biome_name.values,dims='biome')
f='/glade/campaign/asp/djk2120/PPEn11/paramfiles/LHC0000.nc'
tmp=xr.open_dataset(f)
ds['pft_name']=xr.DataArray([str(p)[2:-1].strip() for p in tmp.pftname.values[:17]],dims='pft')
ds.attrs={'contact':'djk2120@ucar.edu',
          'written on':str(datetime.date.today()),
          'codebase':'https://github.com/ESCOMP/CTSM/tree/branch_tags/PPE.n11_ctsm5.1.dev030',
          'script1':'/glade/u/home/djk2120/ppe_clean/postp/oaat/postp.py',
          'script2':'/glade/u/home/djk2120/ppe_clean/postp/oaat/enscat.sh'}

ds.to_netcdf('/glade/campaign/cgd/tss/projects/PPE/PPEn11_OAAT/postp/PPEn11_OAAT_surv.nc')
