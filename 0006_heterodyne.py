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

from slab import dataanalysis

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
                    'samplesPerRecord': 50112, 'recordsPerBuffer': 1,
                    # 'samples_per_buffer': 2000064,
                    # 'samples_per_record': 2000064,
                    # 'seconds_per_buffer': 1.0e-6,
                    # 'seconds_per_record': 1.0e-6,
                    # 'records_per_buffer': 1,
                    # 'records_per_acquisition': 1,
                    # 'bytes_per_buffer': 4000128,
                    'bufferCount': 10, 'trigger_edge1': 'rising', 'trigger_edge2': 'rising',
                    'ch2_range': 0.2, 'clock_source': 'reference', 'trigger_level2': .5, 'trigger_level1': 0.5,
                    'ch2_coupling': 'AC', 'trigger_coupling': 'DC', 'ch2_filter': False, 'trigger_operation': 'or',
                    'ch1_coupling': 'AC', 'trigger_source2': 'disabled', 'trigger_source1': 'external',
                    'sample_rate': 50000, 'timeout': 30000, 'ch1_range': 0.2,
                    'ch2_enabled': True, 'recordsPerAcquisition': 1}
    aConfig = util.dict2obj(**alazarConfig)

    ehe = eHeExperiment(expt_path, prefix, alazarConfig, fridgeParams, filamentParams, newDataFile=False)
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

    ehe.trap.setup_volt_source(None, 3.5, 0., 'on')
    ehe.set_DC_mode()
    # ehe.rinse_n_fire(threshold=.150, intCallback=na_monit)

    ehe.set_DC_mode()
    ehe.get_peak()
    ehe.get_peak(nwa_center=ehe.sample.peakF, nwa_span=2e6)
    ehe.na.set_output(False)
    ehe.rf.set_output(True)
    ehe.rf.set_frequency(ehe.sample.peakF)
    ehe.offsetF = 0.2e6
    ehe.lo.set_output(True)
    ehe.lo.set_frequency(ehe.sample.peakF + ehe.offsetF)

    ehe.set_ramp_mode(2.0, 1.)
    # sleep(1.0)
    ehe.nwa.config.range = [ehe.sample.peakF-5e6, ehe.sample.peakF+5e6, 400]
    for i in range(100):
        ampI, ampQ = ehe.heterodyne_spectrum()

    amps = util.amps(ampI, ampQ)
    ehe.plotter.plot_z('amps', amps, extent=[ehe.nwa.config.range[0:2], ehe.get_trap_high_low()])
    ehe.plotter.plot_z('amps', amps, extent=[ehe.nwa.config.range[0:2], ehe.get_trap_high_low()])
    imshow(amps, aspect='auto', interpolation='none', origin='lower')
