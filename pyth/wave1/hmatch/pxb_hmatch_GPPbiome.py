import numpy as np
import pandas as pd
import xarray as xr
import tensorflow as tf
import sys

# input to script
idx = sys.argv[1]

#############################################
#############################################
# Setup
whit=xr.open_dataset('../whit/whitkey.nc')
biome_names = whit.biome_name.values
pfts=xr.open_dataset('/glade/campaign/asp/djk2120/PPEn11/paramfiles/OAAT0000.nc').pftname
pft_names=[str(p)[2:-1].strip() for p in pfts.values]

nbiomes = 10
npfts = 17
biome_ids = [1,3,5,6,7,8]
GPP = pd.read_csv("../FLUXCOM-GSWP3_GPP_amean_bmean_2001-2010.csv")
GPP_var = pd.read_csv("../FLUXCOM_GPP_amean_bmean_variance.csv")
bp_index = np.load('../bp_index.npy', allow_pickle=True).item()

# load LHC PPE parameter sets 
lhckey = '/glade/campaign/asp/djk2120/PPEn11/csvs/lhc220926.txt'
df = pd.read_csv(lhckey)
lhc_params = df.drop(columns='member')
num_params = len(lhc_params.columns)

pft_params   = ['froot_leaf','kmax','krmax','leaf_long','leafcn','lmr_intercept_atkin','medlynslope','medlynintercept','psi50','slatop','stem_leaf','theta_cj']
pftix=np.array([p in pft_params for p in lhc_params])

#############################################
# load sample

n_usamp = 100
n_psamp = 1000

sample = np.loadtxt("/glade/work/linnia/CLM-PPE-LAI_tests/wave1.1/samples/PxB_sample_"+str(idx)+".txt", delimiter=',')

#############################################
# function to calculate total Biome GPP from PFT contributions
f='/glade/work/djk2120/ppe_savs/pbmean/sg_lapxb.nc'
lapxb=xr.open_dataset(f).lapxb
ix=(lapxb.pxb>9)&(lapxb.mean(dim='year').sum(dim='pft')>0)
pxb_la = lapxb.isel(pxb=ix).sum(dim='pft')
pb_la = pxb_la.sel(year=slice(2001,2010)).mean(dim='year').compute()

whit = xr.open_dataset('../../whit/whitkey.nc')
la = xr.open_dataset('/glade/u/home/djk2120/clm5ppe/pyth/sparsegrid_landarea.nc').landarea  #km2
biome_la = la.groupby(whit.biome).sum()

#############################################
# Calculate implausibility GPP

uset_I = np.empty((n_usamp,nbiomes))*np.NaN
set_I = np.empty((n_usamp*n_psamp,nbiomes))*np.NaN

pred = np.empty((n_usamp*n_psamp,npfts,nbiomes))*np.NaN
pred_var = np.empty((n_usamp*n_psamp,npfts,nbiomes))*np.NaN

data = GPP

for b in biome_ids:
    o = GPP.GPP[b]
    ovar = GPP_var.GPP[b]

    I_tmp = np.empty((n_usamp,n_psamp,nbiomes))*np.NaN
    
    for i,p in enumerate(bp_index[biome_names[b]]):  
        pxb = p*10+b
        la_p = pb_la.sel(pxb=pxb).values
        
        loaded_emulator = tf.saved_model.load('/glade/u/home/linnia/clm5ppe/pyth/wave1/models_gpp/pft'+str(p)+'_biome'+str(b))
        y, y_var = loaded_emulator.predict(sample)
        
        pred[:,p,b] = y.numpy().flatten()
        pred_var[:,p,b] = y_var.numpy().flatten()

        if (i ==0):
            y_pred_all = la_p*y.numpy().flatten()
            y_pred_var_all = la_p*y_var.numpy().flatten()

        else:
            y_pred_all = np.column_stack((y_pred_all,la_p*y.numpy().flatten()))
            y_pred_var_all = np.column_stack((y_pred_var_all,la_p*y_var.numpy().flatten()))

    y_pred_biome = np.sum(y_pred_all,axis=1)*(1/biome_la[b].values)
    y_pred_var_biome = np.sum(y_pred_var_all,axis=1)*(1/biome_la[b].values)
        
    I = np.abs(o-y_pred_biome) / np.sqrt(ovar + y_pred_var_biome)
    set_I[:,b] = I
    I_tmp[:,:,b] = I.reshape((n_usamp,n_psamp))
        
    ix = I_tmp.copy()
    ix[ix<3] = 1
    ix[ix>=3] = 0
    x = np.nanmean(ix,axis=2)
    uset_I[:,b] = np.any(x==1,axis=1)

np.save("/glade/work/linnia/CLM-PPE-LAI_tests/wave1.1/predicted/PxB_GPP_I_sample"+str(idx)+".npy", set_I)
np.save("/glade/work/linnia/CLM-PPE-LAI_tests/wave1.1/predicted/PxB_GPP_pred_sample"+str(idx)+".npy", pred)
np.save("/glade/work/linnia/CLM-PPE-LAI_tests/wave1.1/predicted/PxB_GPP_predvar_sample"+str(idx)+".npy", pred_var)

#####################################################
# identify universal sets that have PFT sets in NROY for all PFTs
ix_usets = np.where(np.nanmean(uset_I,axis=1)==1)[0] 
bool_usets = (np.nanmean(uset_I,axis=1)==1) 

np.save("/glade/work/linnia/CLM-PPE-LAI_tests/wave1.1/selected/PxB_GPP_NROYusets_sample"+str(idx)+".npy", bool_usets)

