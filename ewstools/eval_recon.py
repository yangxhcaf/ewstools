#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 11:47:31 2019

@author: tbury

Function to reconstruct the Jacobian from time-series data.
See Williamson (2015) for implementation details.

"""

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


# Imoprt trajectoreis dataframe
df_traj = pd.read_csv('../../ews_seasonal/models_ricker/ricker_seasonal/data_export/ews_stat_evaltest/traj.csv', index_col=['rb','rnb','Time'])
df_traj.rename(columns={'Non-breeding':'x', 'Breeding':'y'}, inplace=True)

rb_vals = df_traj.index.levels[0]
rnb_vals = df_traj.index.levels[1]

# Select time series to analyse
df_in = df_traj.loc[(2,-1)]

# Visualise with plot
df_in[['x','y']].plot()


#------------------------
##  Function to compute lag-1 autocovariance matrix

def compute_autocov(df_in):
    '''
    Computes the autocovariance (lag-1) matrix of n 
    time series provided in df_in.
    
    Using the definition
        phi_ij = < X_i(t+1) X_j(t) >
    for each element of the autocovariance matrix phi.
    
    Input:
        df_in: DataFrame with n columns indexed by time
    Ouptut:
        np.array of autocovariance matrix
    '''
    
    # Obtain column names of df_in
    col_names = df_in.columns
    # Number of variables
    n = len(col_names)
    
    
    # Define function to compute autocovariance of two columns
    def autocov_cols(a,b):
        '''
        Computes autocovariance of two columns (can be the same)
        Note that this does not commute (a<->b) in general
        Input:
            a,b: Series indexed by time
        Output:
            float: autocovariance between the columns
        '''
        
        # Shift the column of a by 1
        a_shift = a.shift(1)
        
        # Put into a dataframe
        df_temp = pd.concat([a_shift,b], axis=1)
        
        # Compute covariance of columns a and b_shift
        cov = df_temp.cov().iloc[0,1]
        
        # Output
        return cov
            
        
    # Compute elements of autocovariance matrix
    list_elements = []
    
    for i in range(n):
        for j in range(n):
            a = df_in[col_names[i]]
            b = df_in[col_names[j]]
            # Compute autocovaraince between cols
            autocov = autocov_cols(a,b)
            # Append to list of elements
            list_elements.append(autocov)
    
    # Create autocovariance matrix from list of elements
    ar_autocov = np.array(list_elements).reshape(n,n)

    # Output
    return ar_autocov






#---------------------------------------
## Function to do Jacobian reconstruction 


def jac_recon(df_in):
    '''
    Constructs estimate of Jacobian matrix from stationary time-series data
    and outputs the eigenvalues
    Input:
        df_in: DataFrame with two columns indexed by time
    Output:
        np.array: Jacobian matrix
    '''
    
    # Compute autocovaraince matrix from columns
    ar_autocov = compute_autocov(df_in)
    
    # Compute the covariance matrix (built in function)
    ar_cov = df_in.cov()
    
    # Estimate of Jacobian (formula in Williamson (2015))
    # Requires computation of an inverse matrix
    jac = np.matmul(ar_autocov, np.linalg.inv(ar_cov))
      
    # Compute eigenvalues and eigenvectors
    evals, evecs = np.linalg.eig(jac)

    # Dictionary of data output
    dic_out = {'Eigenvalues':evals, 
               'Eigenvectors':evecs,
               'Jacobian':jac}
    
    return dic_out


