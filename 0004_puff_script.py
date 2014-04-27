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
    ehe.note('putting puffs into the sample box')

    ehe.sample = lambda: None
    ehe.sample.freqNoE = 8.012e9
    #ehe.sample.peakF = ehe.sample.freqNoE
    ehe.sample.freqWithE = 8023438335.47

    ehe.note('start puffing')
    while ehe.heman.get_puffs() < 60: #Fill in the number to which you want to fill.
        ehe.note ("Puff %d" % (ehe.heman.get_puffs()+1))
        ehe.heman.puff(pressure=0.25,min_time=60,timeout=600)

        ehe.note ( "Wait for cooldown")
        settled=False
        start_time=time.time()

        fpts, mags, phases =  ehe.na.take_one('nwa')
        ehe.dataCache.set('fpts',fpts)
        while not settled:
            settled=(ehe.fridge.get_mc_temperature() < 0.040) and ((time.time()-start_time)>60.0)
            fpts, mags, phases =  ehe.na.take_one('nwa')
            ehe.dataCache.post('mags', mags)
            ehe.dataCache.post('phases', phases)
            ehe.dataCache.post('time', time()-ehe.t0)
            offset, amplitude, center, hwhm = dsfit.fitlor(fpts, dBmtoW(mag))
            ehe.dataCache.post('f0', offset)
            ehe.dataCache.post('hwhm', hwhm)


        # ehe.resVs = [0,]*20
        # ehe.trapVs = [0,]*20
        # ehe.take_trace(power='-5')