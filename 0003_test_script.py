# -*- coding: utf-8 -*-
"""
Created on Mon Feb 06 22:13:59 2012

@author: Phil
"""

import math
import textwrap2

import matplotlib.pyplot as plt

from numpy import *
from slab import *
from slab.instruments import InstrumentManager

from liveplot import LivePlotClient

from slab.instruments import Alazar, AlazarConfig
import cProfile
import pstats

import util as util
from ehe_experiment import eHeExperiment
from time import sleep, time

if __name__ == "__main__":
    expt_path = r'S:\_Data\140312 - EonHe M007v5 Trident\data'
    prefix = 'experimental'
    fridgeParams = {
        'wait_for_temp': 0.080,
        'min_temp_wait_time': 60  #11 minutes
    }
    filamentParams = {
        "fil_amp": 4.2,
        "fil_off": -0.5,
        "fil_freq": 113e3,
        "fil_duration": 40e-3,
        "fil_delay": .01,
        "pulses": 150}
    labbrickParams = {}

    alazarConfig = {'clock_edge': 'rising', 'trigger_delay': 0,
                    'ch1_filter': False, 'ch1_enabled': True, 'samplesPerRecord': 5056,
                    'bufferCount': 10, 'trigger_edge1': 'rising', 'trigger_edge2': 'rising',
                    'ch2_range': 1, 'clock_source': 'reference', 'trigger_level2': 1.0, 'trigger_level1': 1.0,
                    'ch2_coupling': 'DC', 'trigger_coupling': 'DC', 'ch2_filter': False, 'trigger_operation': 'or',
                    'ch1_coupling': 'DC', 'trigger_source2': 'disabled', 'trigger_source1': 'external',
                    'recordsPerBuffer': 1, 'sample_rate': 5000, 'timeout': 3000, 'ch1_range': 1,
                    'ch2_enabled': True, 'recordsPerAcquisition': 1}
    aConfig = util.dict2obj(**alazarConfig)

    ehe = eHeExperiment(expt_path, prefix, alazarConfig, fridgeParams, filamentParams, newDataFile=True)
    print ehe.filename

    ehe.note('start experiment. ')

    def na_monit():
        ehe.na.take_one("monit")

    ehe.sample = lambda: None;
    ehe.sample.freqNoE = 8.012e9
    #ehe.sample.peakF = ehe.sample.freqNoE
    ehe.sample.freqWithE = 8023438335.47;

    ehe.plotter.clear('na spectrum')
    ehe.plotter.clear('nwa mag')
    ehe.plotter.clear('nwa phase')
    ehe.plotter.clear('nwa I')
    ehe.plotter.clear('nwa Q')

    ehe.trap.setup_volt_source(None, 3.5, 0, 'on')
    ehe.set_DC_mode()
    ehe.rinse_n_fire(threshold=60e-3, intCallback=na_monit);
    ehe.set_DC_mode()
    
    ehe.get_peak()
    # print 'now sleep 10 senconds'
    # sleep(10)
    ehe.get_peak()
    ehe.get_peak(nwa_center=ehe.sample.peakF, nwa_span=10e6)

    def set_n_get(high, low, resV=None):
        if resV == None:
            try:
                resV = self.res.get_volt()
            except:
                # just need to try again buddy!
                resV = self.res.get_volt()

        ehe.set_DC_mode()
        print "now sleep 2 seconds"
        sleep(2)
        ehe.get_peak()
        ehe.get_peak(nwa_center=ehe.sample.peakF, nwa_span=10e6)
        ehe.clear_na_plotter()
        ehe.set_volt_sweep(high, low, 0.05, resV, resV, 0.05, doublePass=True)
        ehe.get_na_sweep_voltage(ehe.sample.peakF, 2e6)

        ehe.clear_na_plotter()
        ehe.set_volt_sweep(high, low, 0.001, resV, resV, 0.05, doublePass=True)
        ehe.get_na_sweep_voltage(ehe.sample.peakF, 2e6)

        ehe.set_ramp_mode(high=high, low=low)
        ehe.trap.trigger()
        ehe.clear_nwa_plotter()
        ehe.set_alazar_average(average=1)
        ehe.nwa.config.range = [ehe.sample.peakF - 1e6, ehe.sample.peakF + 1e6, 320]
        ehe.nwa.sweep()

        ehe.clear_nwa_plotter()
        ehe.set_alazar_average(average=100)
        ehe.nwa.config.range = [ehe.sample.peakF - 1e6, ehe.sample.peakF + 1e6, 80]
        ehe.nwa.sweep()
        
    resV = 0.4
    set_n_get(3.2, 0.4)
    
    for trapV in arange(3.2, 0, 0.4):
        set_n_get(trapV, trapV - 0.4, resV)
        ehe.dataCache.note('resV: {}, trapV: {}'.format(resV, trapV))

    ehe.set_alazar_average(average=100)
    ehe.set_ramp_mode(high=3, low=0)
    ehe.lb.set_frequency(ehe.sample.peakF+0.3e6)
    ehe.set_ramp_stops(3.2, 0.4, n=1)
    ehe.res.set_Vs(1.0, 3, 0.001)
    ehe.nwa.scan()
    
