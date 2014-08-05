# -*- coding: utf-8 -*-
"""
Created on Mon Feb 06 22:13:59 2012

@author: Ge Yang
"""

import math
import textwrap2


from numpy import *
from slab import *
from slab.instruments import InstrumentManager

from liveplot import LivePlotClient

from slab.instruments import Alazar, AlazarConfig
import cProfile
import pstats

import util as util
from ehe_experiment import eHeExperiment
import time

from slab import dataanalysis
import matplotlib.pyplot as plt

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
                    'ch1_filter': False, 'ch1_enabled': True,
                    'samplesPerRecord': 49024,
                    'recordsPerBuffer': 200,
                    'recordsPerAcquisition': 10000,
                    # 'samples_per_buffer': 2000064,
                    # 'samples_per_record': 2000064,
                    # 'seconds_per_buffer': 1.0e-6,
                    # 'seconds_per_record': 1.0e-6,
                    # 'records_per_buffer': 1,
                    # 'records_per_acquisition': 1,
                    # 'bytes_per_buffer': 4000128,
                    'bufferCount': 1, 'trigger_edge1': 'rising', 'trigger_edge2': 'rising',
                    'ch2_range': 1.0, 'clock_source': 'reference', 'trigger_level2': .5, 'trigger_level1': 0.5,
                    'ch2_coupling': 'AC', 'trigger_coupling': 'DC', 'ch2_filter': False, 'trigger_operation': 'or',
                    'ch1_coupling': 'AC', 'trigger_source2': 'disabled', 'trigger_source1': 'external',
                    'sample_rate': 50000, 'timeout': 30000, 'ch1_range': 1.0,
                    'ch2_enabled': True}
    aConfig = util.dict2obj(**alazarConfig)

    ehe = eHeExperiment(expt_path, prefix, alazarConfig, fridgeParams, filamentParams, newDataFile=True)
    print ehe.filename

    ehe.note('start experiment. ')
    ehe.note('set SRS bandwidth to 1MHz')
    ehe.note('record heterodyne singnal, and get I and Q')

    def na_monit():
        ehe.na.take_one("monit")

    ehe.sample = lambda: None
    ehe.sample.freqNoE = 8.012e9
    #ehe.sample.peakF = ehe.sample.freqNoE
    ehe.sample.freqWithE = 8023438335.47

    ehe.clear_na_plotter()
    ehe.clear_nwa_plotter()

    # this loads the sample, and then sweeps the resonator
    # and the trap.
    ehe.offsetF = -0.25e6
    ehe.IF = 0.2e6

    #ehe.trap.setup_volt_source(None, 1.7, 1.3, 'on')
    ehe.set_DC_mode()

    # plt.plot(ehe.trapVs, ehe.resVs, 'r+')
    # plt.xlabel('trap V')
    # plt.ylabel('resonator V')
    # plt.show()

    #   ehe.res.set_volt(-6)
    #   ehe.trap.set_volt(-6)
    #   time.sleep(10)

    # resStart = 1.
    # resEnd = 0.0
    # ehe.dataCache.note('trying to sweep the trap at zero voltage')
    # for resEnd in array([0.00]*30):
    #     ehe.res.set_volt(-3)
    #     ehe.trap.set_volt(-3)
    #     time.sleep(10)
    #     ehe.na.set_span(50e6)
    #     ehe.na.set_center_frequency(ehe.sample.freqNoE - 15e6)
    #     ehe.rinse_n_fire(threshold=.905, intCallback=na_monit, timeout=10, resV=1.0, trapV=2.0, pulses=200, delay=0.01)
    #
    #     ehe.set_DC_mode()
    #     ehe.res.set_volt(1)
    #     ehe.trap.set_volt(1)
    #     time.sleep(10)
    #     ehe.res.set_volt(0.8)
    #     ehe.trap.set_volt(1.6)
    #
    #     ehe.set_DC_mode(2, -2)
    #     ehe.na.set_sweep_points(360)
    #     ehe.na.set_power(-25)
    #     ehe.na.set_averages(1)
    #     ehe.na.set_ifbw(150)
    #     ehe.get_peak()
    #     ehe.get_peak(nwa_center=ehe.sample.peakF, nwa_span=5e6)
    #     ehe.get_peak(nwa_center=ehe.sample.peakF, nwa_span=2e6)
    #     # ehe.na.set_averages(2)
    #     ehe.na.set_power(-25)
    #
    #     quickResEnd = -0.1
    #     seg0 = util.dualRamp([resStart, resStart + 2.0], [-1.0, -1.0 + 1.8], 400)
    #     seg1 = util.dualRamp([-1.0, -1.0 + 1.8], [quickResEnd, quickResEnd + 0.8], 400)
    #
    #     print seg0[:5]
    #
    #     for resV, trapV in zip(concatenate((seg0[0], seg1[0]),), concatenate((seg0[1], seg1[1]), )):
    #         print resV,
    #         time.sleep(0.01)
    #         ehe.res.set_volt(resV)
    #         ehe.trap.set_volt(trapV)
    #
    #     ehe.get_peak()
    #     ehe.get_peak(nwa_center=ehe.sample.peakF, nwa_span=5e6)
    #     ehe.get_peak(nwa_center=ehe.sample.peakF, nwa_span=2e6)
    #
    #     ehe.resVs, ehe.trapVs = util.dualRamp([quickResEnd, quickResEnd + 0.8], [resEnd, resEnd + 0.8], 100)
    #     ehe.peak_track_voltage_sweep(center=ehe.sample.freqNoE - 11e6, span=2e6, npts=160, dynamicWindowing=True)
    #     ehe.dataCache.set('resStart', resStart)
    #     ehe.dataCache.set('resEnd', resEnd)
    #
    #     seg0 = util.dualRamp([resEnd, resEnd + 0.8], [resEnd, .0], 800)
    #     seg1 = util.dualRamp([resEnd, 0.8], [resEnd, resEnd + 1.0], 50)
    #     ehe.resVs = concatenate((seg0[0], seg1[0]))
    #     ehe.trapVs = concatenate((seg0[1], seg1[1]))
    #     # ehe.resVs, ehe.trapVs = seg0
    #     ehe.peak_track_voltage_sweep(center=ehe.sample.peakF + 2e6/5., span=2e6, npts=160, dynamicWindowing=False)
    #     ehe.dataCache.set('resStart', resStart)
    #     ehe.dataCache.set('resEnd', resEnd)
    #
    #     ehe.resVs, ehe.trapVs = util.dualRamp([resEnd, .0], [-3, -3], 20)
    #     ehe.peak_track_voltage_sweep(span=2e6, npts=160, dynamicWindowing=True)
    #     ehe.dataCache.set('resStart', resStart)
    #     ehe.dataCache.set('resEnd', resEnd)
