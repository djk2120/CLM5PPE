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
pft_ids = [1,2,3,4,5,6,7,8,10,11,12,13,14,15]
pb_index = np.load('../pb_index.npy',allow_pickle='TRUE').item()
SP_LAI_max = xr.open_dataset("../CLM-SP_LAI_pxb_amax_2003-2007.nc")
SP_LAI_mean = xr.open_dataset("../CLM-SP_LAI_pxb_amean_2003-2007.nc")
LAI_var = pd.read_csv("../LAI_amean_bmean_variance.csv",sep=',')

# load LHC PPE parameter sets 
lhckey = '/glade/campaign/asp/djk2120/PPEn11/csvs/lhc220926.txt'
df = pd.read_csv(lhckey)
lhc_params = df.drop(columns='member')
num_params = len(lhc_params.columns)

pft_params   = ['froot_leaf','kmax','krmax','leaf_long','leafcn','lmr_intercept_atkin','medlynslope','medlynintercept','psi50','slatop','stem_leaf','theta_cj']
pftix=np.array([p in pft_params for p in lhc_params])

#############################################
# build sample

n_usamp = 100
u_sample = np.random.rand(n_usamp,20)

n_psamp = 1000
p_sample = np.random.rand(n_psamp,12)

sample=np.zeros([n_usamp*n_psamp,num_params])
sample[:,~pftix]= np.repeat(u_sample,n_psamp,axis=0)
sample[:,pftix]= np.tile(p_sample,(n_usamp,1))

np.savetxt("/glade/work/linnia/CLM-PPE-LAI_tests/wave1/samples/PxB_sample_"+str(idx)+".txt", sample, delimiter=',')

#############################################
# Calculate implausibility

uset_I = np.empty((n_usamp,npfts))*np.NaN
set_I = np.empty((n_usamp*n_psamp,npfts,nbiomes))*np.NaN

pred = np.empty((n_usamp*n_psamp,npfts,nbiomes))*np.NaN
pred_var = np.empty((n_usamp*n_psamp,npfts,nbiomes))*np.NaN

for p in pft_ids:
    I_tmp = np.empty((n_usamp,n_psamp,nbiomes))*np.NaN
    
    for b in pb_index[pft_names[p]]:  

        loaded_emulator = tf.saved_model.load('/glade/u/home/linnia/clm5ppe/pyth/wave1/models_lai/pft'+str(p)+'_biome'+str(b))
        y, y_var = loaded_emulator.predict(sample)
        
        pred[:,p,b] = y.numpy().flatten()
        pred_var[:,p,b] = y_var.numpy().flatten()

        pxb = p*10+b
        if (p < 12): # not grass
            o = SP_LAI_max.TLAI.sel(pxb=pxb).values[0]
        else: # grass
            o = SP_LAI_mean.TLAI.sel(pxb=pxb).values[0]
        ovar = LAI_var.TLAI[b]

        I = np.abs(o-y) / np.sqrt(ovar + y_var)
        set_I[:,p,b] = I[:,0]
        I_tmp[:,:,b] = I.reshape((n_usamp,n_psamp))
        
    ix = I_tmp.copy()
    ix[ix<3] = 1
    ix[ix>=3] = 0
    x = np.nanmean(ix,axis=2)
    uset_I[:,p] = np.any(x==1,axis=1)

uset_I[:,9] = np.NaN # ignore this PFT

np.save("/glade/work/linnia/CLM-PPE-LAI_tests/wave1/predicted/PxB_LAI_I_sample"+str(idx)+".npy", set_I)
np.save("/glade/work/linnia/CLM-PPE-LAI_tests/wave1/predicted/PxB_LAI_pred_sample"+str(idx)+".npy", pred)
np.save("/glade/work/linnia/CLM-PPE-LAI_tests/wave1/predicted/PxB_LAI_predvar_sample"+str(idx)+".npy", pred_var)

#####################################################
# identify universal sets that have PFT sets in NROY for all PFTs
ix_usets = np.where(np.nanmean(uset_I,axis=1)==1)[0] 
bool_usets = (np.nanmean(uset_I,axis=1)==1) 

np.save("/glade/work/linnia/CLM-PPE-LAI_tests/wave1/selected/PxB_LAI_NROYusets_sample"+str(idx)+".npy", bool_usets)

#####################################################
# randomly select one PFT set per Universal set (for each PFT)
sample_NROY = np.empty((len(ix_usets),num_params,npfts))*np.NaN
for pft in pft_ids:
    bool_pft_biome = np.empty((len(ix_usets),nbiomes,n_psamp))*np.NaN # index of NROY sets for each PFT each Biome
    for b in pb_index[pft_names[pft]]:
        v = np.reshape(set_I[:,pft,b],(n_usamp,n_psamp))
        bool_pft_biome[:,b,:] = v[ix_usets,:]<3
    
    ix_set = []
    for u in range(len(ix_usets)):        
        ix_all_psets = np.where(np.nanmean(bool_pft_biome,axis=1)[u,:]==1)[0]
        ix_pset = np.random.choice(ix_all_psets, size= 1,replace=False)[0]
        
        ix_set.append(ix_usets[u]*n_psamp + ix_pset)
        
    sample_NROY[:,:,pft] = sample[ix_set,:]
    
np.save("/glade/work/linnia/CLM-PPE-LAI_tests/wave1/selected/PxB_LAI_NROYsets_sample"+str(idx)+".npy", sample_NROY)


