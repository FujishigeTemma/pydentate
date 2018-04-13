# -*- coding: utf-8 -*-
"""
This module implements the class StandardNetwork.
StandardNetwork creates a ring network as defined in Santhakumar et al. 2005
with some changes as in Yim et al. 2015.
See StandardNetwork docstring for details.
Created on Tue Nov 28 13:01:38 2017

@author: DanielM
"""

from neuron import h, gui
import ouropy
import matplotlib.pyplot as plt
import numpy as np
from granulecell import GranuleCell
from mossycell_cat import MossyCell
from basketcell import BasketCell
from hippcell import HippCell

class DisinhibitedNetwork(ouropy.gennetwork.GenNetwork):
    """ This model implements the ring model from Santhakumar et al. 2005.
    with some changes as in Yim et al. 2015.
    It features inhibition but omits the MC->GC connection.
    """
    
    name = "TunedNetwork"
    def __init__(self, seed=None, temporal_patterns=np.array([]), spatial_patterns_gcs=np.array([]),
                 spatial_patterns_bcs=np.array([]), sprouting=0):
        self.init_params = locals()
        self.init_params['self'] = str(self.init_params['self'])
        # Setup cells
        self.mk_population(GranuleCell, 2000)
        self.mk_population(MossyCell, 60)
        self.mk_population(BasketCell, 24)
        self.mk_population(HippCell, 24)

        # Set seed for reproducibility
        if seed:
            self.set_numpy_seed(seed)

        # Setup recordings
        self.populations[0].record_aps()
        self.populations[1].record_aps()
        self.populations[2].record_aps()
        self.populations[3].record_aps()

        temporal_patterns = np.atleast_2d(temporal_patterns)
        if type(spatial_patterns_gcs) == np.ndarray and type(temporal_patterns) == np.ndarray:
            #spatial_patterns_gcs = np.atleast_2d(spatial_patterns_gcs)
            for pat in range(len(spatial_patterns_gcs)):
                # PP -> GC
                #Original
                """ouropy.gennetwork.PerforantPathPoissonTmgsyn(self.populations[0],
                                                           temporal_patterns[pat],
                                                           spatial_patterns_gcs[pat],
                                                           'dd', 5.5, 0, 1, 0, 0, 2*10**(-2))"""
                ouropy.gennetwork.PerforantPathPoissonTmgsyn(self.populations[0],
                                                           temporal_patterns[pat],
                                                           spatial_patterns_gcs[pat],
                                                           'dd', 5.5, 0, 1, 0, 0, 0.40825*10**(-2))   

        if type(spatial_patterns_bcs) == np.ndarray and type(temporal_patterns) == np.ndarray:
            #spatial_patterns_bcs = np.atleast_2d(spatial_patterns_bcs)
            for pat in range(len(spatial_patterns_bcs)):
                # PP -> BC
                ouropy.gennetwork.PerforantPathPoissonTmgsyn(self.populations[2],
                                                           temporal_patterns[pat],
                                                           spatial_patterns_bcs[pat],
                                                           'ddend', 6.3, 0, 1, 0, 0, 1*10**(-2))
        """
        call signature of tmgsynConnection
        tmgsynConnection(self, pre_pop, post_pop, target_pool, target_segs,
                divergence, tau_1, tau_facil, U, tau_rec, e, thr, delay, weight)
        """
		  # Sprouting
        ouropy.gennetwork.tmgsynConnection(self.populations[0], self.populations[0],
                                           100, 'proxd', sprouting, 5.5, 0, 1,
                                           0, 0, 10, 0.8, 2*10**(-3))

        # GC -> MC
        ouropy.gennetwork.tmgsynConnection(self.populations[0], self.populations[1],
                                  12, 'proxd',
                                  1, 6.2, 500, 0.1, 0, 0, 10, 1.5, 0.2*10**(-2) * 10)

        # GC -> BC
        #Weight x4, target_pool = 2
        ouropy.gennetwork.tmgsynConnection(self.populations[0], self.populations[2],
                                           8, 'proxd',
                                           1, 0.6, 500, 1, 0, 0, 10, 0.8, 18.8*10**(-3))

        # GC -> HC
        # Divergence x4; Weight doubled; Connected randomly.
        """ouropy.gennetwork.tmgsynConnection(self.populations[0], self.populations[3],
                                           24, 'proxd',
                                           3, 0.6, 0, 1, 0, 0, 10, 1.5, 0.5*10**(-3))"""
        ouropy.gennetwork.tmgsynConnection(self.populations[0], self.populations[3],
                                           24, 'proxd',
                                           12, 0.6, 500, 1, 0, 0, 10, 1.5, 1.0*10**(-3))

        # MC -> GC
        """self.mk_Exp2SynConnection(self.populations[1], self.populations[0],
                                     350, 'proxd',
                                     200, 1.5, 5.5, 0, 10, 3, 0.3*10**(-3))"""

        # MC -> MC
        ouropy.gennetwork.tmgsynConnection(self.populations[1], self. populations[1],
                                           24, 'proxd',
                                           3, 2.2, 0, 1, 0, 0, 10, 2, 0.5*10**(-3))

        # MC -> BC
        ouropy.gennetwork.tmgsynConnection(self.populations[1], self.populations[2],
                                           12, 'proxd',
                                           1, 0.1, 0, 1, 0, 0, 10, 3, 0.3*10**(-3))

        # MC -> HC
        ouropy.gennetwork.tmgsynConnection(self.populations[1], self.populations[3],
                                           20, 'midd',
                                           2, 3.6, 0, 1, 0, 0, 10, 3, 0.2*10**(-3))

        # BC -> GC
        # Nr. synapses x3; Weight *1/4
        ouropy.gennetwork.tmgsynConnection(self.populations[2], self.populations[0],
                                           560, 'soma',
                                           400, 5.5, 0, 1, 0, -70, 10, 0.85, 0)

        # BC -> MC        
        ouropy.gennetwork.tmgsynConnection(self.populations[2], self.populations[1],
                                           28, 'proxd',
                                           3, 3.3, 0, 1, 0, -70, -10, 1.5, 0)

        # BC -> BC
        ouropy.gennetwork.tmgsynConnection(self.populations[2], self.populations[2],
                                           12,'proxd',
                                           2, 1.8, 0,1,0,-70, -10, 0.8, 0)

        # HC -> GC
        # Weight x10; Nr synapses x4
        ouropy.gennetwork.tmgsynConnection(self.populations[3], self.populations[0],
                                           2000, 'dd',
                                           640, 6, 0, 1, 0, -70, 10, 1.6, 0)

        # HC -> MC
        ouropy.gennetwork.tmgsynConnection(self.populations[3], self.populations[1],
                                           60, ['mid1d', 'mid2d'],
                                           4, 6, 0, 1, 0, -70, 10, 1, 0)

        # HC -> BC
        ouropy.gennetwork.tmgsynConnection(self.populations[3], self.populations[2],
                                           24, 'ddend',
                                           4, 5.8, 0, 1, 0, -70, 10, 1.6, 0)

if __name__ == '__main__':
    """A testrun for StandardNetwork"""
    # Insert path for your relevant nrnmech.dll
    """Path on PhD room office PC"""
    h.nrn_load_dll("C:\\Users\\DanielM\\Repos\\models_dentate\\dentate_gyrus_Santhakumar2005_and_Yim_patterns\\dentategyrusnet2005\\nrnmech.dll")
    """Path on home PC"""
    #h.nrn_load_dll("C:\\Users\\daniel\\repos\\nrnmech.dll")
    np.random.seed(1000)
    #temporal_patterns = np.random.poisson(10,(1,3)).cumsum(axis=1)
    temporal_patterns = np.array([3])
    spatial_patterns_gcs = np.random.choice(2000,400,replace=False)
    #spatial_patterns_gcs = np.arange(400)
    spatial_patterns_bcs = np.random.choice(24,2,replace=False)
    
    nw = DisinhibitedNetwork(seed = 10000, temporal_patterns = temporal_patterns,
                         spatial_patterns_gcs = spatial_patterns_gcs,
                         spatial_patterns_bcs = spatial_patterns_bcs, sprouting = 0)

    cell_measured = []
    for x in nw.populations[1]:
        cell_measured.append(x._voltage_recording())

    print("TEST")

    h.cvode.active(0)
    dt = 0.1
    h.steps_per_ms = 1.0/dt
    h.tstop = 1500
    h.finitialize(-60)
    h.t = -2000
    h.secondorder = 0
    h.dt = 10
    while h.t < -100:
        h.fadvance()
        #print(h.t)
    h.secondorder = 2
    h.t = 0
    h.dt = 0.1
    print("Test2")
    """Setup run control for -100 to 1500"""
    h.frecord_init() # Necessary after changing t to restart the vectors
    while h.t < 200:
        h.fadvance()
        #print(h.t)
        
    nw.populations[0].plot_aps()
    plt.xlim((0,200))
    