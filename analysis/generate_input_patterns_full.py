# -*- coding: utf-8 -*-
"""
This script generates the input patterns as they are generated in paradigm_pattern_separation
and saves them to individual files for later processing.

@author: DanielM
"""

import os
import numpy as np
import shelve
import analysis_main
from pyDentate.burst_generator_inhomogeneous_poisson import inhom_poiss
from sklearn.preprocessing import normalize

# Generate the temporal patterns
np.random.seed(10000)
temporal_patterns = inhom_poiss()
runs = range(376)
save_path = "C:\\Users\\Daniel\\pyDentateData\\pattern_separation_data\\input_patterns\\"
file_prefix = "input_patterns_run_"

temporal_patterns = analysis_main.time_stamps_to_signal(temporal_patterns, 0.1, 0, 600)
temporal_patterns = analysis_main.tri_filter(temporal_patterns, 200)
temporal_patterns_norm = normalize(temporal_patterns, axis=1)
pattern_shape = temporal_patterns.shape

for x in runs:
    curr_pattern = np.zeros(temporal_patterns.shape)
    curr_pattern_norm = np.zeros(temporal_patterns.shape)
    curr_pattern[x:x+24,:] = temporal_patterns[x:x+24,:]
    np.savez(save_path + file_prefix + str(x).zfill(3), curr_pattern)
    curr_pattern_norm[x:x+24,:] = temporal_patterns_norm[x:x+24,:]
    np.savez(save_path + file_prefix + str(x).zfill(3) + '_norm', curr_pattern_norm)

"""
for x in data_files:
    data = shelve.open(data_path + x)
    curr_spike_data = analysis_main.time_stamps_to_signal(data['net_tuned.TunedNetwork']['populations'][0]['ap_time_stamps'], dt_signal=0.1, t_start=0, t_stop=600)
    np.savez(save_path + x + '_spike_data', curr_spike_data)
    curr_spike_data_conv = analysis_main.tri_filter(curr_spike_data, 200)
    np.savez(save_path + x + '_spike_data_convolved', curr_spike_data)
"""