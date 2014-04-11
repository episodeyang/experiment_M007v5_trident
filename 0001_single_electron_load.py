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
    ehe.sample.freqWithE = 8023438335.47;

    ehe.clear_nwa_plotter()
    ehe.clear_na_plotter()

    ehe.trap.setup_volt_source(None, 3.5, 0, 'on')
    ehe.set_DC_mode()
    ehe.rinse_n_fire(threshold=60e-3, intCallback=na_monit);
    ehe.set_DC_mode()
    ehe.set_ramp_mode(offset=3.5, amp=0.25)

    #ehe.res.set_volt(-1.5)
    ehe.res.set_volt(0.5)

    ehe.get_peak()
    print 'now sleep 3 seconds'
    sleep(3)
    ehe.get_peak()
    ehe.get_peak(nwa_center=ehe.sample.peakF, nwa_span=10e6)
    ehe.get_peak(nwa_center=ehe.sample.peakF, nwa_span=3e6)
    ehe.nwa.config.range = [ehe.sample.peakF - 1e6, ehe.sample.peakF + 1e6, 320]

    for offset in linspace(1.0, 0.5, 50):
        ehe.clear_nwa_plotter()
        ehe.trap.set_offset(offset)
        ehe.set_alazar_average(average=1)
        ehe.nwa.sweep()

        ehe.set_alazar_average(average=100)
        ehe.nwa.sweep()

    ehe.res.set_volt(0.0)

    ehe.get_peak()
    print 'now sleep 3 seconds'
    sleep(3)
    ehe.get_peak()
    ehe.get_peak(nwa_center=ehe.sample.peakF, nwa_span=10e6)
    ehe.get_peak(nwa_center=ehe.sample.peakF, nwa_span=3e6)
    ehe.nwa.config.range = [ehe.sample.peakF - 1e6, ehe.sample.peakF + 1e6, 320]

    for offset in linspace(0.5, 0, 50):
        ehe.clear_nwa_plotter()
        ehe.trap.set_offset(offset)
        ehe.set_alazar_average(average=1)
        ehe.nwa.sweep()

        ehe.set_alazar_average(average=100)
        ehe.nwa.sweep()
