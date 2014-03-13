# -*- coding: utf-8 -*-
"""
Created on Wed Nov 27 16:43:43 2013

@author: Phil
"""

from slab import *
from slab.instruments import InstrumentManager
from numpy import *
import time,datetime


def take_one(na,fname=None):
    """Setup Network Analyzer to take a single averaged trace and grab data, 
    either saving it to fname or returning it"""
    na.clear_averages()
    na.trigger_single()
    time.sleep(na.query_sleep)
    na.averaging_complete()
    if fname is not None:
        na.save_file(fname)
    ans=na.read_data()
    return ans

def note(mstr,logfile):
    print mstr
    f=open(logfile,'a+')
    f.write(str(datetime.date.today())+'-'+mstr+'\n')
    f.close()          

def addpt(datapath,prefix,data,state):
    with h5File(os.path.join(datapath,prefix+".h5")) as hf: #default is "a"   
        for key in state.keys():
            hf.append(key,state[key])            
        for ii, key in enumerate(['fpts','mags','phases']):
            hf.append(key,data[ii])

def tic():
    global tic_time
    tic_time=time.time()

def toc():
    global tic_time
    return time.time()-tic_time

def ramp(start,finish,step):
    if start < finish: Vs = concatenate((arange(start,finish,abs(step)),array([finish,])))
    else: Vs = concatenate((arange(start,finish,-abs(step)),array([finish,])))
    try: 
        if Vs[-1] == Vs[-2]:
            Vs = Vs[:-1]
    except IndexError: pass;
    return Vs
def ramps(pts,step):
    seg=array([])        
    for i in range(1,len(pts)):
        seg=concatenate((seg,ramp(pts[i-1],pts[i],step)))
    return seg
def Vramps(points_steps):
    segs=array([])
    for points,step in points_steps:
        segs=concatenate((segs,ramps(points,step)))
    return segs
    
def flatten(mat):
    out = [];
    for row in mat:
        out += list(row)
    return out
def days_hours_minutes(seconds):
    days = seconds/(3600*24)
    hours = seconds/3600 - days*24
    minutes = seconds/60 - days *24*60 - hours * 60
    return days, hours, minutes


class experiment():
    def initInstruments(self):
        self.im=InstrumentManager()
        self.na=self.im['NWA']
        self.heman=self.im['heman']        
        self.srs=self.im['SRS']
        self.fridge=self.im['FRIDGE']
        self.fil = self.im['fil']
        #self.res = self.im['res']
        #self.trap = self.im['trap']
        #self.lb1 = self.im['LB1']
        self.lb = self.im['labbrick']
        #self.bnc = self.im['BNC']
        self.trap = self.im['BNC_trap']
        self.trigger = self.im['BNC_sync']

        self.na.set_default_state()
        
#        self.res.set_mode('VOLT')
#        self.trap.set_mode('VOLT')

#        self.LB1.set_output(False)
#        self.LB1.set_pulse_ext(False)
#        self.LB1.set_mod(False)
#        self.LB1.set_power(0)#10dBm max
#        self.LB1.set_frequency(7e9)
        self.plotter=ScriptPlotter()
   
    def updateNWA(self, params):
        #### NWA parameters
        #na.set_default_state()
        #print params
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
        self.fil.setup_driver(params['fil_amp'],params['fil_off'],
                              params['fil_freq'],params['fil_duration'])
    
    def DirectorySetup(self, exp_path, prefix):
        self.expt_path = exp_path
        self.prefix = prefix
    ### Saving the script
        print "Saved script as: %s" % save_script(self.expt_path,self.prefix)
#        print get_script()
        self.datapath=make_datapath(self.expt_path,self.prefix)
        self.logfile=os.path.join(self.datapath,'log.txt')

    def set_sweep(self,trapStart, trapEnd, trapStep, resStart, resEnd, resStep, doublePass = False, showPlot = False):
        if doublePass :
            self.pts = (((trapStart, trapEnd, trapStart), trapStep), )
        else:
            self.pts = (((trapStart,trapEnd), trapStep),)
        self.tvps = Vramps(self.pts)
        self.pts = (((resStart,resEnd), resStep),)
        self.rvps = Vramps(self.pts)#, 0.25,0.1])#Vramps(pts)
        self.trapVs = flatten(outer(ones(len(self.rvps)),self.tvps))
        self.resVs = flatten(outer(self.rvps, ones(len(self.tvps))))
        if showPlot:
            plt.plot(self.resVs, self.trapVs)
            plt.xlim(-1.6, 1.6)
            plt.ylim(-0.8,1.8)
        print "estimated time is %d days %d hr %d minutes." % days_hours_minutes(len(self.trapVs)*2)
    
    def set_diagonal_sweep(self, trapRange, trapStep, trapStart, trapEnd, resStart, resEnd, resStep, double_pass = False, showPlot = False):
        self.set_sweep(trapRange[0], trapRange[1], trapStep, resStart, resEnd, resStep, double_pass = double_pass)
        def add_offset(resV):
            return trapEnd + (trapStart-trapEnd)/(resStart - resEnd)*(resV-resEnd)
        for ind in range(len(self.trapVs)):
            self.trapVs[ind] += add_offset(self.resVs[ind])
        if showPlot:
            plt.plot(self.resVs, self.trapVs)
        #Already printing the estimate in set_sweep call.
        #print "estimated time is %d days %d hr %d minutes." % days_hours_minutes(len(self.trapVs)*2)
        
    def take_trace(self, power=None):
        note ("sweep power {}".format(power),self.logfile)
        if power != None: 
            self.na.params['SmallPeak'] = self.na.params["PowerSettings"][power]
        for (self.resv, self.trapv) in zip(self.resVs, self.trapVs):
            self.run(self.resv,self.trapv)        

    def note(self,string):
        note(string, self.logfile)
        with h5File(os.path.join(self.datapath,self.prefix+".h5")) as hf: #default is "a"   
            hf.append('notes',string)            
    

    def run(self,resV=None,trapV=None):
        if resV==None:
            try: 
                resV = self.res.get_volt()
            except ValueError:
                resV = self.res.get_volt()
        else: 
            self.res.set_volt(resV)
        if trapV==None:
            try:
                trapV = self.trap.get_volt()
            except ValueError:
                trapV = self.trap.get_volt()
        else: 
            self.trap.set_volt(trapV)
        
        temperature = self.fridge.get_mc_temperature()
            
        t=time.time()-self.t0
    
        self.na.update(self.na.params['BigPeak'])
        self.na.clear_averages()
        self.na.trigger_single()
        
        probe_frequency = self.lb.get_frequency();
        state ={'tpts':t,'resV':resV,'trapV':trapV,'temperature':temperature,
                'puffs':self.heman.get_puffs(), 'probe': probe_frequency}    
        
        self.na.averaging_complete()
        data = self.na.read_data()
        addpt(self.datapath,self.prefix+"-Big",data,state)
        print '.',
    
        self.updateNWA(self.na.params['SmallPeak'])
        self.na.clear_averages()
        self.na.trigger_single()
        temperature=self.fridge.get_mc_temperature()
        state={'tpts':t,'resV':resV,'trapV':trapV,'temperature':temperature,
                'puffs':self.heman.get_puffs(), 'probe': probe_frequency}    
        
        self.na.averaging_complete()
        data = self.na.read_data()
        addpt(self.datapath,self.prefix+"-Small",data,state)
        self.count += 1 
        print '.',
            
    def __init__(self,folder, prefix, fridgeParams,filamentParams, naParams,labbrickParams):
        self.initInstruments()        
        self.fil.params = filamentParams
        self.fil.update = self.updateFilament
        self.fil.update(self.fil.params)        
        
        self.na.params = naParams
        self.na.update = self.updateNWA
        self.fridge.params = fridgeParams
        
#        self.lb.set_output(False)
        self.lb.set_pulse_ext(False)
        self.lb.set_mod(False)
        self.lb.set_power(0)
        

#        self.DirectorySetup(r".\008_2Tone", 
#                       "M007v5TDT-puff_"+str(self.im['heman'].get_puffs())
#                       )        
        self.DirectorySetup(folder,prefix+r"-puff_"+str(self.im['heman'].get_puffs())
                       )        
        
        self.count=-1
        self.t0 = time.time()
    
    def frequency_sweep(self,fpts,config,rf,lo=None):
        self.plotter.init_plot("Ch1", rank=1,accum=False)
        self.plotter.init_plot("Ch1_avg",rank=1,accum=True)
        self.plotter.init_plot("transmission transposed", rank=2)
        print "Configuring card"
        scope_settings= AlazarConfig(config)
        card=Alazar(scope_settings)  
        card.configure()
        print "Sweep frequency"        
        tpts,ch1_pts,ch2_pts=card.acquire_avg_data()
            
        for f in fpts:
            rf.set_frequency(f)
            time.sleep(.01)
            tpts,ch1_pts,ch2_pts=card.acquire_avg_data(excise=(0,9000))
            
            ch1=mean(ch1_pts)
            ch2=mean(ch2_pts)
            #self.plotter.msg("Frequency: %f\tVoltage: %f" % (f,ch1))
            self.plotter.plot((tpts,ch1_pts),"Ch1")   
            self.plotter.plot((f,ch1),"Ch1_avg")                     
            self.plotter.plot(ch1_pts,"transmission transposed" )