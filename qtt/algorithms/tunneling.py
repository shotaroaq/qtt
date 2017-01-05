# -*- coding: utf-8 -*-
"""
Created on Fri Nov 11 17:11:56 2016

@author: diepencjv
"""

#%%
import scipy.optimize
import numpy as np
import scipy.ndimage

def polmod_all_2slopes(x, par, kT=0.001):
    ''' Polarization line model
    
    Arguments:
        x (1 x N array): gate voltages
        par (1 x 6 array): parameters for the model
            - par[0]: tunnel coupling
            - par[1]: average x value
            - par[2]: background signal
            - par[3]: slope on left side
            - par[4]: slope on right side
            - par[5]: sensitivity
        kt (float): temperature in mV
        
    Returns:
        E (float): 
    '''
# TODO: adjust s.t. functionality and documentation work for different input units (volts, electronvolts, etc.)
    x = x - par[1]
    
    Om = np.sqrt(x**2 + 4 * par[0]**2)
    E = 1/2 * (1 + x / Om * np.tanh(Om / (2 * kT)))
    slopes = par[3] + (par[4] - par[3]) * E
    E = par[2] + x * slopes + E * par[5]
    
    return E

def polweight_all_2slopes(delta, data, par, kT=0.001):
    ''' Cost function for polarization fitting
    
    Arguments:
        delta (array)
        data (array)
        par (array)
        
    Returns:
        total (float)
    '''
    mod = polmod_all_2slopes(delta, par, kT=kT)
    diffs = data - mod
    norms = np.sqrt(np.sum(diffs**2))
    total = np.sum(norms)
    
    return total    
    
def fit_pol_all(delta, data, kT=0.001, maxfun=None):
    ''' Calculate initial values for fitting and fit
    
    Arguments:
        delta (array)
        data (array)
        
    Returns:
        par_fit (array)
    '''
    numpts = round(len(delta)/10)
    t_guess = 1*4.2/80
    slope_guess = np.polyfit(delta[-numpts:], data[-numpts:], 1)[0]
    dat_noslope = data - slope_guess * (delta-delta[0])
#    delta_offset_guess = delta[int(np.round(len(data)/2))-1]
#    trans_idx = (np.abs(dat_noslope - np.percentile(dat_noslope, 10) - sensitivity_guess/2)).argmin()
    dat_noslope_1der = scipy.ndimage.filters.gaussian_filter(dat_noslope, sigma=5, order=1)
    trans_idx = np.abs(dat_noslope_1der).argmax() # does not work for higher tunnel couplings, alternative may be using that there are three dominant slopes
    sensitivity_guess = np.sign(data[0]-data[-1])*np.sign(dat_noslope_1der[trans_idx])*(np.percentile(dat_noslope, 90) - np.percentile(dat_noslope, 10))
    delta_offset_guess = delta[trans_idx]
    sensor_offset_guess = data[trans_idx] - sensitivity_guess / 2
    
    par_guess = np.array([t_guess, delta_offset_guess, sensor_offset_guess, slope_guess, slope_guess, sensitivity_guess]) # second slope guess could be done more accurately

    func = lambda par: polweight_all_2slopes(delta, data, par, kT=kT)
    par_fit = scipy.optimize.fmin(func, par_guess, maxfun=maxfun)

    return par_fit, par_guess
