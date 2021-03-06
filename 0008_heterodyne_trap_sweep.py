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
import time

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

    # naParams = {
    #     'power': -15,
    #     'ifbw': 50,
    #     'sweep_points': 320,
    #     'avg': 1,
    # }
    alazarConfig = {'clock_edge': 'rising', 'trigger_delay': 0,
                    'ch1_filter': False, 'ch1_enabled': True,
                    'samplesPerRecord': 49024,
                    'recordsPerBuffer': 200,
                    'recordsPerAcquisition': 20000,
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

    ehe.trap.setup_volt_source(None, 1.7, 1.3, 'on')
    ehe.set_DC_mode()

    ehe.na.set_power(-5)
    ehe.na.set_ifbw(50)
    ehe.na.set_span(40e6)
    ehe.na.set_center_frequency(ehe.sample.freqNoE)
    ehe.rinse_n_fire(threshold=.900, intCallback=na_monit, timeout=60, resV=1.5, pulses=2, delay=0.01)

    #ehe.res.set_volt(0.8)
    time.sleep(10)

    ehe.set_DC_mode()
    ehe.get_peak()
    ehe.get_peak(nwa_center=ehe.sample.peakF, nwa_span=5e6)
    ehe.get_peak(nwa_center=ehe.sample.peakF, nwa_span=2e6)

    ehe.set_ramp_mode(2., 0.8, symmetric=False)
    ehe.nwa.config.range = [ehe.sample.peakF - 1e6, ehe.sample.peakF + 1e6, 200]
    ehe.heterodyne_spectrum()

    ehe.set_volt_sweep(1, 1, 0.1, 0.8, 0.0, 0.002)
    # ehe.set_ramp_mode(3.0, 0, symmetric=False)
    ampI, ampQ = ehe.heterodyne_resV_sweep(trackMode=True, trapTrack=True, trapAmp=0.8, offsetV=1.1)

    # ehe.set_volt_sweep(1, 1, 0.1, 1.0, 0.5, 0.0005)
    # ehe.set_ramp_mode(3.0, 0, symmetric=False)
    # ampI, ampQ = ehe.heterodyne_resV_sweep(trackMode=True, trapTrack=False, trapAmp=1, offsetV=0.7)
