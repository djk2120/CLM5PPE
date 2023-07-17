import os
import numpy as np
import xarray as xr
import cftime
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import glob
import dask

from esem import gp_model
from scipy import stats
#import gpflow

from sklearn.metrics import mean_squared_error, r2_score
from sklearn import preprocessing

def standardize(data):
    return preprocessing.scale(data)

def normalize(var):
    return (var-min(var))/(max(var)-min(var))

def unnormalize(norm_var,raw_var):
    return norm_var*np.array(max(raw_var)-min(raw_var)) + np.array(min(raw_var))

def plot_validation(emulator, X_test, y_test, ax):
    
    y_pred, y_pred_var = emulator.predict(X_test.values)
    
    r2 = np.corrcoef(y_test,y_pred)

    ax.plot([-3,3],[-3,3],c='k',linestyle='--',label='1:1 line')
    ax.scatter(y_test,y_pred)
    ax.text(-3,2,'R2 = '+str(np.round(r2[0,1],3)),fontsize=10)
    ax.set_xlabel('CLM (standardized)',fontsize = 10)
    ax.set_ylabel('Emulator (standardized)',fontsize = 10)

def train_GPemulator(data,params,ntest,kernel,ax):
    Y = standardize(data)
    
    # split training and testing data
    X_test, X_train = params[:ntest], params[ntest:]
    y_test, y_train = Y[:ntest], Y[ntest:]
    
    # define emulator model and train
    emulator = gp_model(np.array(X_train),np.array(y_train),kernel=kernel) # using default kernel
    emulator.train()
    
    plot_validation(emulator, X_test, y_test, ax)
    
    return emulator