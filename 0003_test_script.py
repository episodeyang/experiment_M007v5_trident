# -*- coding: utf-8 -*-
"""
Created on Mon Feb 06 22:13:59 2012

@author: Ge Yang
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
    ehe.note('quick experiment to seep feature movement')
    ehe.note('set SRS bandwidth to 30kHz')

    def na_monit():
        ehe.na.take_one("monit")

    ehe.sample = lambda: None
    ehe.sample.freqNoE = 8.012e9
    #ehe.sample.peakF = ehe.sample.freqNoE
    ehe.sample.freqWithE = 8023438335.47


    ehe.clear_na_plotter()
    ehe.clear_nwa_plotter()

    ehe.trap.setup_volt_source(None, 3.5, 0., 'on')
    ehe.set_DC_mode()
    #ehe.rinse_n_fire(threshold=60e-3, intCallback=na_monit);
    ehe.set_DC_mode()
    
    ehe.get_peak()
    print 'now sleep 1 sencond'
    sleep(1)
    ehe.get_peak()
    ehe.get_peak(nwa_center=ehe.sample.peakF, nwa_span=2e6)
    ehe.na.set_output(False)
    ehe.rf.set_output(True)
    ehe.rf.set_frequency(ehe.sample.peakF)    

    
#
#    def set_n_get(high, low, resV=None, step_coarse=0.05, step_fine=.001, take_non_averaged=True):
#        if resV == None:
#            try:
#                resV = ehe.res.get_volt()
#            except:
#                # just need to try again buddy!
#                resV = ehe.res.get_volt()
#
#        ehe.set_DC_mode()
#
#        ehe.get_peak()
#        ehe.get_peak(nwa_center=ehe.sample.peakF, nwa_span=10e6)
#        if step_coarse != None:
#            ehe.clear_na_plotter()
#            ehe.set_volt_sweep(high, low, step_coarse, resV, resV, 0.05, doublePass=True)
#            ehe.get_na_sweep_voltage(ehe.sample.peakF, 2e6)
#
#        if step_fine != None:
#            ehe.clear_na_plotter()
#            ehe.set_volt_sweep(high, low, step_fine, resV, resV, 0.05, doublePass=True)
#            ehe.get_na_sweep_voltage(ehe.sample.peakF, 2e6)
#
#        ehe.set_ramp_mode(high=high, low=low)
#        print "now sleep 0.4 seconds"
#        sleep(0.4)
#        ehe.trap.trigger()
#        ehe.clear_nwa_plotter()
#
#        if take_non_averaged:
#            ehe.set_alazar_average(average=1)
#            ehe.nwa.config.range = [ehe.sample.peakF - 1e6, ehe.sample.peakF + 1e6, 320]
#            ehe.nwa.sweep()
#
#        ehe.clear_nwa_plotter()
#        ehe.set_alazar_average(average=100)
#        ehe.nwa.config.range = [ehe.sample.peakF - 1e6, ehe.sample.peakF + 1e6, 80]
#        ehe.nwa.sweep()
#
#    set_n_get(3.0, 0.25, 1.5, 0.5, 0.05, False)


    # ehe.set_ramp_mode(high=3.0, low=0.25)
    # ehe.trap.trigger()
    # print "now sleep 0.4 seconds"

    # allowed = [0, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 1.2, 1.6, 1.8]
    # for resV in arange(3.0, 0.0, -0.05):
    #     # set_n_get(3.2, 0.4, resV, step_coarse=0.1, step_fine=0.01)
    #     ehe.res.set_volt(resV)
    #     sleep(0.4)
    #     ehe.clear_nwa_plotter()
    #     ehe.clear_nwa_plotter()
    #     ehe.set_alazar_average(average=100)
    #     # ehe.nwa.config.range = [ehe.sample.peakF - 4e6, ehe.sample.peakF + 4e6, 80]
    #     ehe.nwa.config.range = [8.0015e9, 8.0135e9, 640]
    #     ehe.nwa.sweep()
    #     # set_n_get(3.2, 2.8, resV, step_coarse=None, step_fine=0.005, take_non_averaged=False)
    #     # set_n_get(2.8, 2.4, resV, step_coarse=None, step_fine=0.005, take_non_averaged=False)
    #     # set_n_get(2.4, 2.0, resV, step_coarse=None, step_fine=0.005, take_non_averaged=False)
    #     # set_n_get(2.0, 1.6, resV, step_coarse=None, step_fine=0.005, take_non_averaged=False)
    #     # set_n_get(1.6, 1.2, resV, step_coarse=None, step_fine=0.005, take_non_averaged=False)
    #     # set_n_get(1.2, 0.8, resV, step_coarse=None, step_fine=0.005, take_non_averaged=False)
    #     # set_n_get(0.8, 0.4, resV, step_coarse=None, step_fine=0.005, take_non_averaged=False)
    #     if resV < allowed[-1]:
    #         allowed = allowed[:-1]
    #         print "now take some resV single f sweeps"
    #         ehe.get_peak()
    #         ehe.get_peak(nwa_center=ehe.sample.peakF, nwa_span=10e6)
    #         ehe.set_alazar_average(average=100)
    #         ehe.set_ramp_mode(high=3, low=0)
    #         frequency = ehe.sample.peakF
    #         ehe.lb.set_frequency(frequency)
    #         ehe.res.set_Vs(resV, 3, 0.01)
    #         ehe.set_ramp_stops(3.0, 0.4, n=1)
    #         ehe.nwa.scan()
    #         ehe.dataCache.note('probe frequency is set at {:.9f}'.format(frequency/1e9))
    #         ehe.set_ramp_stops(3.0, 0.4, n=5)
    #         ehe.nwa.scan()
    #         ehe.dataCache.note('probe frequency is set at {:.9f}'.format(frequency/1e9))
    #         ehe.set_ramp_mode(high=3.0, low=0.25)
    #         ehe.trap.trigger()
