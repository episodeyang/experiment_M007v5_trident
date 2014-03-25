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
import matplotlib as mpl

from liveplot import LivePlotClient

from slab.instruments import Alazar, AlazarConfig
import cProfile
import pstats

import matplotlib as mlp
import util as util


def tic():
    global tic_time
    tic_time = time.time()


def toc():
    global tic_time
    return time.time() - tic_time


class eHeExperiment():
    def attachInstruments(self):
        self.im = InstrumentManager()
        self.na = self.im['NWA']
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

        self.res = lambda: 0

        def set_volt_res(volt):
            self.srs.set_volt(volt, channel=1)

        def get_volt_res():
            return self.srs.get_volt(channel=1)

        self.res.set_volt = set_volt_res
        self.res.get_volt = get_volt_res

        self.configNWA()
        self.na.take_one = self.na_take_one;

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

    def configNWA(self, params=None):
        if params != None:
            print "now load parameters for network analyzer"
            self.na.set_averages(params['avg'])
            self.na.set_power(params['power'])
            self.na.set_center_frequency(params['center'])
            self.na.set_span(params['span'])
            self.na.set_ifbw(params['ifbw'])
            self.na.set_sweep_points(params['sweep_pts'])
        self.na.set_trigger_source('BUS')
        self.na.set_trigger_average_mode(True)
        self.na.set_timeout(10000)
        #self.na.set_format('slog')

    def updateFilament(self, params):
        #self.note('update filament driver')
        self.fil.setup_driver(params['fil_amp'], params['fil_off'],
                              params['fil_freq'], params['fil_duration'])

    def set_DC_mode(self):
        self.lb.set_output(False)
        self.trap.setup_volt_source(None, 3, 0, 'off')

    def set_ramp_mode(self, high=None, low=None, offset=None, amp=None):
        """
        high and low overrides amp and offset.
        """
        if low !=None and high != None:
            amp = abs(high-low)
            offset = max(high, low) - amp
        if amp != None:
            self.trap.set_amplitude(amp)
        if offset != None:
            self.trap.set_offset(offset)
        self.lb.set_output(True)
        self.trap.set_burst_phase(90)
        self.trap.set_function('ramp')
        self.trap.set_burst_state('on')
        self.trap.set_trigger_source('ext')

    def DirectorySetup(self, exp_path, prefix):
        self.expt_path = exp_path
        self.prefix = prefix
        ### Saving the script
        print "Saved script as: %s" % save_script(self.expt_path, self.prefix)
        #        print get_script()
        self.datapath = make_datapath(self.expt_path, self.prefix)
        self.logfile = os.path.join(self.datapath, 'log.txt')

    def nwa_sweep(self, fpts=None, windowName="NWA", config=None):
        def amp(pair):
            return sqrt(pair[0] ** 2 + pair[1] ** 2)

        def phase(pair):
            if pair[1] != 0:
                theta = arctan(pair[0] / pair[1])
            else:
                theta = pi / 2;
            return theta

        if fpts == None:
            self.nwa.config.fpts = linspace(self.nwa.config.range[0], self.nwa.config.range[1],
                                            self.nwa.config.range[2])
        else:
            self.nwa.config.fpts = fpts;

        if self.alazar.config != config and config != None:
            print "new configuration file"
            self.alazar.config = AlazarConfig(config);
            print "config file has to pass through the AlazarConfig middleware."
            self.alazar.configure()

        mag = [];
        ch1s = [];
        tpts, ch1_pts, ch2_pts = self.alazar.acquire_avg_data()
        for f in self.nwa.config.fpts:
            self.lb.set_frequency(float(f))
            tpts, ch1_pts, ch2_pts = self.alazar.acquire_avg_data(excise=(0, -40))  #excise=(0,4992))

            ch1_avg = mean(ch1_pts)
            ch2_avg = mean(ch2_pts)
            amps = map(amp, zip(ch1_pts, ch2_pts))
            phases = map(phase, zip(ch1_pts, ch2_pts))
            mag.append(mean(amps))
            self.plotter.append_z('nwa mag', amps)
            self.plotter.append_z('nwa phase', phases)
            self.plotter.append_z('nwa I', ch1_pts)
            self.plotter.append_z('nwa Q', ch2_pts)
            with SlabFile(self.filename) as f:
                f.append_line('nwa mag', amps)
                f.append_line('nwa phase', phases)
                f.append_line('nwa I', ch1_pts)
                f.append_line('nwa Q', ch2_pts)
        return mag

    def gate_sweep(self, config):
        print "Configuring card"
        scope_settings = AlazarConfig(config)
        card = Alazar(scope_settings)
        card.configure()
        print "Sweep gate voltage"
        tpts, ch1_pts, ch2_pts = card.acquire_avg_data(excise=(0, 4950))

    def na_take_one(self, plotName='na spectrum'):
        """Setup Network Analyzer to take a single averaged trace and grab data,
        either saving it to fname or returning it"""
        self.na.clear_averages()
        self.na.trigger_single()
        self.na.averaging_complete()
        ans = self.na.read_data()
        if plotName == None:
            plotName = 'na spectrum';
        self.plotter.append_z(plotName, ans[1])
        return ans

    def get_na_sweep_voltage(self, center=None, span=None, plotName=None):
        if center != None:
            self.na.set_center_frequency(center)
        if span != None:
            self.na.set_span(span)
        for trapV, resV in zip(self.trapVs, self.resVs):
            self.trap.set_volt(trapV)
            self.res.set_volt(resV)
            fpts, mag, phase = self.na.take_one(plotName=plotName)
        offset, amplitude, center, hwhm = dsfit.fitlor(fpts, dBmtoW(mag))
        print "center frequency is: ", center
        return center

    def set_volt_sweep(self, trapStart, trapEnd, trapStep, resStart, resEnd, resStep, doublePass=False, showPlot=False):
        if doublePass:
            self.pts = (((trapStart, trapEnd, trapStart), trapStep), )
        else:
            self.pts = (((trapStart, trapEnd), trapStep),)
        self.tvps = util.Vramps(self.pts)
        self.pts = (((resStart, resEnd), resStep),)
        self.rvps = util.Vramps(self.pts)  #, 0.25,0.1])#Vramps(pts)
        self.trapVs = util.flatten(outer(ones(len(self.rvps)), self.tvps))
        self.resVs = util.flatten(outer(self.rvps, ones(len(self.tvps))))
        if showPlot:
            plt.plot(self.resVs, self.trapVs)
            plt.xlim(-1.6, 1.6)
            plt.ylim(-0.8, 1.8)
        print "estimated time is %d days %d hr %d minutes." % util.days_hours_minutes(len(self.trapVs))  # *2)

    def rinse_n_fire(self, threshold=None, intCallback=None):
        self.note("unbias the trap for a second")
        self.res.set_volt(-3)
        self.srs.set_output(1, True)
        self.note("make sure the probe is off before the baseline")
        time.sleep(1)

        self.note('firing the filament')
        self.res.set_volt(1.5)
        self.fil.fire_filament(400, 0.01)

        self.note("Now wait for cooldown while taking traces")
        if threshold == None:
            threshold = 60e-3;
        while self.fridge.get_mc_temperature() > threshold or (time.time() - self.t0) < 360:
            print '.',
            if intCallback != None:
                intCallback();
        self.note("fridge's cold, start sweeping...")
        self.note("sweep probe frequency and trap electrode")

    def get_peak(self, set_nwa=True, nwa_span=20e6):
        if set_nwa :
            self.na.set_sweep_points(320)
            self.na.set_center_frequency(self.sample.freqNoE)
            self.na.set_span(nwa_span)
        fpts, mag, phase = self.na.take_one()
        self.sample.peakF = fpts[argmax(mag)]
        print "the peak is found at: ", self.sample.peakF
        return fpts, mag, phase

    def na_get_trap_sweep(self):
        self.trap.setup_volt_source(None, 3, 0, 'off')
        self.set_sweep(1.25, 0.25, 0.1, 0.8, 0.8, 0.05, doublePass=True)


if __name__ == "__main__":
    print "main just ran but nothing is here."
