# -*- coding: utf-8 -*-
"""
Created on Mon Feb 06 22:13:59 2012

@author: Phil
"""


from numpy import *
from slab import *
import matplotlib as mpl

from liveplot import LivePlotClient

from os import path
import textwrap2
import matplotlib as mlp
import util as util

class dataCacheProxy():
    def __init__(self, expInst, newFile=False):
        self.exp = expInst
        self.data_directory = expInst.expt_path
        self.prefix = expInst.prefix
        self.set_data_file_path(newFile)

    def set_data_file_path(self, newFile=False):
        if self.exp.filename == None:
            if newFile == True:
                self.filename = get_next_filename(self.data_directory, self.prefix, suffix='.h5')
            else:
                self.filename = get_current_filename(self.data_directory, self.prefix, suffix='.h5')
        else: self.filename = self.exp.filename;
        self.path = path.join(self.data_directory, self.filename)

    def add(self, keyString, data):
        def add_data(f, keyList, data):
            if len(keyList) == 1:
                f.add(keyList[0], data)
            else:
                return add_data(f[key[0]], keyList[1:])

        keyList = keyString.split('.')
        with SlabFile(self.path) as f:
            add_data(f, keyList, data)

    def append(self, keyString, data):
        def append_data(f, keyList, data):
            if len(keyList) == 1:
                f.append(keyList[0], data)
            else:
                return append_data(f[key[0]], keyList[1:])

        keyList = keyString.split('.')
        with SlabFile(self.path) as f:
            append_data(f, keyList, data)

    def get(self, keyString):
        def get_data(f, keyList):
            if len(keyList) == 1:
                return f[keyList[0]][...];
            else:
                return get_data(f[key[0]], keyList[1:])

        keyList = keyString.split('.')
        with SlabFile(self.path) as f:
            return get_data(f, keyList)

    def note(self, string, keyString='notes', printOption=False, maxLength=79):
        if not printOption:
            print string
        with SlabFile(self.path) as f:
            for line in textwrap2.wrap(string, maxLength):
                f.append(keyString, line + ' ' * (maxLength - len(line)))

if __name__ == "__main__":
    print "main just ran but nothing is here."
    # example usage
    data = dataCacheProxy()
    data.append('exp.run01.mags', some_data)
    ehe.run_some_script()
    #now data is saved in the dataCache
    #now I want to move some data to a better file
    #each experiment is a file, contains:
    # - notes
    # - actionTitle
    #   - configs
    #   - mags
    #   - fpts
    #   - vpts
