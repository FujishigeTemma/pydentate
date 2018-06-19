# -*- coding: utf-8 -*-
"""
The analysis module provides the function to analyse the data generated by
pyDentate. Data files generated by pyDentate have the .pydd extension.
This extension simply allows to identify files that contain the raw data
as opposed to files that contain for example plots. All data files are python
shelves and shelving is handled by ouropy.

Functions
---------


@author: daniel
"""

import numpy as np
from scipy.signal import correlate2d, convolve2d, convolve
from sklearn.preprocessing import normalize
#from burst_generator_inhomogeneous_poisson import inhom_poiss
import shelve
import matplotlib.pyplot as plt
import pylab

def tri_filter(signal, kernel_delta):
    """
    kernel_delta
        width of kernel in datapoints
    """
    kernel = np.append(np.arange(kernel_delta/2),np.arange(kernel_delta/2,-1,-1))
    # convolve2d has proven PAINFULLY slow for some reason
    #signal_conv = convolve2d(signal,kernel,'same')
    new_signal = []
    for x in signal:
        new_signal.append(convolve(x, kernel, 'same'))
    signal_conv = np.array(new_signal)
    return signal_conv

def correlate_signals(signal1,signal2):
    """Correlates two nxm dimensional signals.
    Correlates sig1n with Sign2n along m and then averages all n correlation
    coefficients.
    Used Pearson Correlation Coefficient. Does not work for us because of NaN
    values if one signal is silent.
    """
    corrs = []
    for idx in range(signal1.shape[0]):
        sig1 = signal1[idx] - pylab.std(signal1[idx])
        sig2 = signal2[idx] - pylab.std(signal2[idx])
        #cor = sum(sig1*sig2)/(len(sig1)*pylab.std(sig1)*pylab.std(sig2))
        cor = sum(sig1*sig2)/(np.sqrt(sum(sig1**2))*np.sqrt(sum(sig2**2)))
        corrs.append(cor)
    
    corrs = np.array(corrs)
    return np.nanmean(corrs)

def avg_dotprod_signals(signal1,signal2):
    """Average dot product of signal1 and signal2"""
    non_silent_sigs = np.unique(np.concatenate((np.argwhere(signal1.any(axis=1)),np.argwhere(signal2.any(axis=1)))))
    non_silent_sigs.sort()
    product = signal1[non_silent_sigs]*signal2[non_silent_sigs]
    prod_sum = product.sum(axis=1)
    avg_dot_product = prod_sum.mean()
    return avg_dot_product

def avg_dotprod_signals_tbinned(signal1,signal2, len_bin = 1000):
    """Average dot product of signal1 and signal2"""
    # Normalize every time bin invididually
    
    signal1 = np.reshape(signal1[:,0:int((signal1.shape[1]/len_bin)*len_bin)],
                         (signal1.shape[0], signal1.shape[1]/len_bin,len_bin), len_bin)
    signal1 = signal1[:,0:5,:]
    signal2 = np.reshape(signal2[:,0:int((signal2.shape[1]/len_bin)*len_bin)],
                     (signal2.shape[0], signal2.shape[1]/len_bin,len_bin), len_bin)
    signal2 = signal2[:,0:5,:]

    sig1 = []
    for x in signal1:
        sig1.append(normalize(x,axis=1))
    signal1 = np.array(sig1)
    
    sig2 = []
    for x in signal2:
        sig2.append(normalize(x, axis=1))
    signal2 = np.array(sig2)

    product = signal1*signal2
    prod_sum = product.sum(axis=2)

    silent_sigs = np.argwhere(np.logical_and(np.invert(signal1.any(axis=2)), np.invert(signal2.any(axis=2))))

    for x in silent_sigs:
        prod_sum[x[0],x[1]] = np.NaN
    avg_dot_product = np.nanmean(prod_sum, axis=0)
    return avg_dot_product

def time_stamps_to_signal(time_stamps, dt_signal, t_start, t_stop):
    """Convert an array of timestamps to a signal where 0 is absence and 1 is
    presence of spikes
    """
    # Construct a zero array with size corresponding to desired output signal
    sig = np.zeros((np.shape(time_stamps)[0],int((t_stop-t_start)/dt_signal)))
    
    # Find the indices where spikes occured according to time_stamps
    time_idc = []
    for x in time_stamps:
        curr_idc = []
        for y in x:
            curr_idc.append((y-t_start)/ dt_signal)
        time_idc.append(curr_idc)
    
    # Set the spike indices to 1
    for sig_idx, idc in enumerate(time_idc):
        sig[sig_idx,np.array(idc,dtype=np.int)] = 1

    return sig

if __name__ == '__main__':
    temporal_patterns = inhom_poiss()
    time_sig = time_stamps_to_signal(temporal_patterns,
                                     dt_signal=0.1,
                                     t_start=0,
                                     t_stop=1000)
