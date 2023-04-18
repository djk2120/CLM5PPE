import os
import numpy as np
import xarray as xr
import cftime
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import glob
import dask

from sklearn.metrics import mean_squared_error, r2_score


def normalize(var):
    return (var-min(var))/(max(var)-min(var))

def unnormalize(norm_var,raw_var):
    return norm_var*np.array(max(raw_var)-min(raw_var)) + np.array(min(raw_var))

def plot_validation(emulator, X_test, y_test, error):
    y_pred, y_pred_var = emulator.predict(X_test.values)
    
    rms = mean_squared_error(y_test, y_pred, squared=False)
    r2 = r2_score(y_test,y_pred)

    plt.figure(figsize=[7,3])
    ax = plt.subplot(1,2,1) # normalized space
    ax.plot([0,1],[0,1],c='k',linestyle='--',label='1:1 line')
    ax.scatter(y_test,y_pred)
    ax.text(0,0.95,'R2 = '+str(np.round(r2,3)),fontsize=10)
    ax.text(0,0.90,'RMSE = '+str(np.round(rms,3)),fontsize=10)
    ax.set_title('Normalized',fontsize = 10)

    ax = plt.subplot(1,2,2) # original space
    y_test_raw = unnormalize(y_test,error)
    ax.plot([min(y_test_raw),max(y_test_raw)],[min(y_test_raw),max(y_test_raw)],c='k',linestyle='--',label='1:1 line')
    ax.scatter(y_test_raw,unnormalize(y_pred,error))
    ax.set_title('Original',fontsize = 10)

