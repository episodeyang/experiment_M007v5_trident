# -*- coding: utf-8 -*-
"""
Created on Mon Feb 06 22:13:59 2012

@author: Phil
"""

import math
import textwrap2

from numpy import *
from slab import *
from slab.instruments import InstrumentManager
from slab import dsfit

from liveplot import LivePlotClient

from slab.instruments import Alazar, AlazarConfig
import cProfile
import pstats


def tic():
    global tic_time
    tic_time = time.time()


def toc():
    global tic_time
    return time.time() - tic_time


class eHeExperiment():
    def attachInstruments(self):
        self.im = InstrumentManager()
        # self.na=self.im['NWA']
        self.heman = self.im['heman']
        self.srs = self.im['SRS']
        self.fridge = self.im['FRIDGE']
        self.fil = self.im['fil']
        #self.res = self.im['res']
        #self.trap = self.im['trap']
        #self.lb1 = self.im['LB1']
        self.lb = self.im['labbrick']
        #self.bnc = self.im['BNC']
        self.trap = self.im['BNC_trap']
        self.trigger = self.im['BNC_sync']
        self.alazar = Alazar()

    def __init__(self, expt_path, prefix, alazar_config, fridgeParams, filamentParams):
        self.expt_path = expt_path
        self.prefix = prefix
        self.filename = get_next_filename(expt_path, prefix, suffix='.h5')

        self.plotter = LivePlotClient()
        self.attachInstruments();
        self.fil.params = filamentParams
        self.fil.update = self.updateFilament
        self.fil.update(self.fil.params)

        # self.na.set_default_state()
        # self.na.params = naParams
        # self.na.update = self.updateNWA

        self.fridge.params = fridgeParams

        #        self.lb.set_output(False)
        self.lb.set_pulse_ext(False)
        self.lb.set_mod(False)
        self.lb.set_power(0)

        self.alazar.config = AlazarConfig(alazar_config)
        self.alazar.configure()

        self.nwa = lambda: None;
        self.nwa.sweep = self.nwa_sweep;
        self.nwa.config = lambda: None;

        #this is the dataCache attached to the experiment.
        self.dataCache = lambda x: x;

        # self.DirectorySetup(folder,prefix+r"-puff_"+str(self.im['heman'].get_puffs()))

        self.count = -1
        self.t0 = time.time()

    def get_hf(self):
        return SlabFile(self.filename)

    def note(self, string):
        max_length = 79;
        print string;
        with h5File(self.filename) as hf:  #default is "a"
            for line in textwrap2.wrap(string, max_length):
                hf.append('notes', line + ' ' * (max_length - len(line)))

    def updateFilament(self, params):
        #self.note('update filament driver')
        self.fil.setup_driver(params['fil_amp'], params['fil_off'],
                              params['fil_freq'], params['fil_duration'])

    def DirectorySetup(self, exp_path, prefix):
        self.expt_path = exp_path
        self.prefix = prefix
        ### Saving the script
        print "Saved script as: %s" % save_script(self.expt_path, self.prefix)
        #        print get_script()
        self.datapath = make_datapath(self.expt_path, self.prefix)
        self.logfile = os.path.join(self.datapath, 'log.txt')

    def nwa_sweep(self, fpts=None, windowName="NWA", config=None):
        if fpts == None:
            fpts = linspace(self.nwa.config.range[0], self.nwa.config.range[1], self.nwa.config.range[2])
        if self.alazar.config != config and config != None:
            print "new configuration file"
            self.alazar.config = AlazarConfig(config);
            print "config file has to pass through the AlazarConfig middleware."
            self.alazar.configure()

        mag = [];
        tpts, ch1_pts, ch2_pts = self.alazar.acquire_avg_data()
        for f in fpts:
            self.lb.set_frequency(f)
            tpts, ch1_pts, ch2_pts = self.alazar.acquire_avg_data()  #excise=(0,4992))

            ch1_avg = mean(ch1_pts)
            ch2_avg = mean(ch2_pts)
            mag.append(ch2_avg)
            self.plotter.append_z(windowName, ch1_pts)
        return mag

    def gate_sweep(self, config):
        print "Configuring card"
        scope_settings = AlazarConfig(config)
        card = Alazar(scope_settings)
        card.configure()
        print "Sweep gate voltage"
        tpts, ch1_pts, ch2_pts = card.acquire_avg_data(excise=(0, 9000))


if __name__ == "__main__":
    expt_path = r'S:\_Data\131021 - EonHe M007v5 Trident\014_testAlazarSweep'
    prefix = 'test'
    fridgeParams = {
        'wait_for_temp': 0.040,
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
                    'ch1_filter': False, 'ch1_enabled': True, 'samplesPerRecord': 576,
                    'bufferCount': 10, 'trigger_edge1': 'rising', 'trigger_edge2': 'rising',
                    'ch2_range': 1, 'clock_source': 'reference', 'trigger_level2': 1.0, 'trigger_level1': 1.0,
                    'ch2_coupling': 'DC', 'trigger_coupling': 'DC', 'ch2_filter': False, 'trigger_operation': 'or',
                    'ch1_coupling': 'DC', 'trigger_source2': 'disabled', 'trigger_source1': 'external',
                    'recordsPerBuffer': 1, 'sample_rate': 4, 'timeout': 1000, 'ch1_range': 4,
                    'ch2_enabled': True, 'recordsPerAcquisition': 1}

    ehe = eHeExperiment(expt_path, prefix, alazarConfig, fridgeParams, filamentParams)
    ehe.note('start experiment. ')

    fpts = linspace(8.0125e9 - 10e6, 8.0125e9 + 10e6, 51)
    ehe.plotter.remove('NWA')
    mag = ehe.nwa.sweep(fpts)
    fits = dsfit.fitlor(fpts, mag)
    print
