# -*- coding: utf-8 -*-
"""
Created on Mon Feb 06 22:13:59 2012

@author: Phil
"""

from numpy import *
from slab import *
from slab.instruments import InstrumentManager

from slab.instruments import Alazar, AlazarConfig
import cProfile    
import pstats
    

class eHeExperiment():
    def __init__(self,expt_path,prefix):
        self.im=InstrumentManager()
        self.expt_path=expt_path
        self.prefix=prefix
        
        self.filename=get_next_filename(expt_path,prefix,suffix='.h5')

        self.plotter=ScriptPlotter()
               
        
    def get_hf(self):
        return SlabFile(self.filename)
      
    def frequency_sweep(self,fpts,config,rf,lo=None):
        self.plotter.init_plot("Ch1 and Ch2", rank=1,accum=False)
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
            tpts,ch1_pts,ch2_pts=card.acquire_avg_data()#excise=(0,4992))
            
            ch1=mean(ch1_pts)
            ch2=mean(ch2_pts)
            #self.plotter.msg("Frequency: %f\tVoltage: %f" % (f,ch1))
            self.plotter.plot((tpts,ch1_pts),"Ch1 and Ch2")
            #self.plotter.plot((tpts,ch2_pts), "Ch1 and Ch2")
            self.plotter.plot((f,ch1),"Ch1_avg")                     
            self.plotter.plot(ch1_pts,"transmission transposed" )

        
    def gate_sweep(self,config):
        self.plotter.init_plot("Ch1",rank=1,accum=False)
        print "Configuring card"
        scope_settings= AlazarConfig(config)
        card=Alazar(scope_settings)  
        card.configure()
        print "Sweep gate voltage"        
        tpts,ch1_pts,ch2_pts=card.acquire_avg_data(excise=(0,9000))
        
        self.plotter.plot((tpts,ch1_pts),"Ch1")

def main():
    expt_path=r'S:\_Data\131021 - EonHe M007v5 Trident\014_testAlazarSweep'
    prefix='test'
    ehe=eHeExperiment(expt_path,prefix)
    
    fsweep_config={'clock_edge': 'rising', 'trigger_delay': 0, 
           'ch1_filter': False, 'ch1_enabled': True, 'samplesPerRecord': 576, 
           'bufferCount': 10, 'trigger_edge1': 'rising', 'trigger_edge2': 'rising',
            'ch2_range': 1, 'clock_source': 'reference', 'trigger_level2': 1.0, 'trigger_level1': 1.0,
            'ch2_coupling': 'DC', 'trigger_coupling': 'DC', 'ch2_filter': False, 'trigger_operation': 'or',
            'ch1_coupling': 'DC', 'trigger_source2': 'disabled', 'trigger_source1': 'external', 
            'recordsPerBuffer': 1, 'sample_rate': 4, 'timeout': 1000, 'ch1_range': 4, 
            'ch2_enabled': True, 'recordsPerAcquisition': 1}        

    
#sample_rate in ksps
#smaplesPerRecord number of points per record --> ie record acquisition time is samplesperRecord/sample_rate in ms
#records perAcquisition total number of records to take --> ie total acq time for whole proces is recordsPerAcquisition*samplesperRecord/sample_rate


    gate_config={'clock_edge': 'rising', 'trigger_delay': 0, 'ch1_filter': False, 'ch1_enabled': True, 
            'samplesPerRecord': 9984, 'bufferCount': 10, 'trigger_edge1': 'rising', 'trigger_edge2': 'rising',
            'ch2_range': 4, 'clock_source': 'reference', 'trigger_level2': 1.0, 'trigger_level1': 1.0,
            'ch2_coupling': 'DC', 'trigger_coupling': 'DC', 'ch2_filter': False, 'trigger_operation': 'or',
            'ch1_coupling': 'DC', 'trigger_source2': 'disabled', 'trigger_source1': 'external', 
            'recordsPerBuffer': 10, 'sample_rate': 10000, 'timeout': 10000, 'ch1_range': 4, 
            'ch2_enabled': False, 'recordsPerAcquisition': 10000}        

    for i in range(1):
        fpts=linspace(8.0125e9-10e6,8.0125e9+10e6,151)
        ehe.frequency_sweep(fpts,fsweep_config,ehe.im['labbrick'])
#    ehe.gate_sweep(gate_config)
    


if __name__=="__main__":
#    cProfile.run("main()",'stats')
#    p=pstats.Stats('stats')
#    p.sort_stats('cumulative').print_stats(20)
    main()