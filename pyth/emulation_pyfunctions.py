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
import gpflow
import tensorflow as tf

from sklearn.metrics import mean_squared_error, r2_score
from sklearn import preprocessing
from sklearn.preprocessing import StandardScaler

def standardize(data):
    dat = data.values.reshape(-1, 1)
    scaler = StandardScaler()
    scaler.fit(dat)
    scaled = scaler.transform(dat)
    return scaled

def unstandardize(data,raw_data):
    dat = raw_data.values.reshape(-1, 1)
    scaler = StandardScaler()
    scaler.fit(dat)
    return scaler.inverse_transform(data)

#def standardize(data):
#    return preprocessing.scale(data)

def normalize(var):
    return (var-min(var))/(max(var)-min(var))

def unnormalize(norm_var,raw_var):
    return norm_var*np.array(max(raw_var)-min(raw_var)) + np.array(min(raw_var))

def plot_validation(y_test, y_pred, ax):
    
    r2 = np.corrcoef(y_test.flatten(),y_pred.flatten())

    ax.plot([-3,3],[-3,3],c='k',linestyle='--',label='1:1 line')
    ax.scatter(y_test,y_pred)
    ax.text(-3,2.5,'R2 = '+str(np.round(r2[0,1],3)),fontsize=10)
    ax.set_xlabel('CLM (standardized)',fontsize = 10)
    ax.set_ylabel('Emulator (standardized)',fontsize = 10)

def trainGP_ESEm(data,params,ntest,ax,kernel=None):
    Y = standardize(data)
    
    # split training and testing data
    X_test, X_train = params[:ntest], params[ntest:]
    y_test, y_train = Y[:ntest], Y[ntest:]
    
    # define emulator model and train
    if kernel is not None : 
        emulator = gp_model(np.array(X_train),np.array(y_train),kernel=kernel)
    else:
        emulator = gp_model(np.array(X_train),np.array(y_train)) # using default kernel
    
    emulator.train()
    
    y_pred, y_pred_var = emulator.predict(X_test.values)
    
    plot_validation(y_test, y_pred, ax)
    
    return emulator

def trainGP_GPFlow(data,params,ntest,ax,kernel):
    Y = standardize(data)
    nparams = np.shape(params)[1]
    
    # split training and testing data
    X_test, X_train = params[:ntest], params[ntest:]
    y_test, y_train = Y[:ntest], Y[ntest:]
    
    # define emulator model and train
    emulator = gpflow.models.GPR(data=(X_train, y_train), kernel=kernel, mean_function=None)

    opt = gpflow.optimizers.Scipy()
    opt_logs = opt.minimize(emulator.training_loss, emulator.trainable_variables, options=dict(maxiter=1000))
    
    y_pred, y_var = emulator.predict_f(X_test.values)
    
    # plot validation
    plot_validation(y_test, np.array(y_pred), ax)
    
    return emulator