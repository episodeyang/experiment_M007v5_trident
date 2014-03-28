# -*- coding: utf-8 -*-
"""
Created on Mon Feb 06 22:13:59 2012

@author: Phil
"""


import numpy as np
from slab import SlabFile
from slab.dataanalysis import get_current_filename
import matplotlib.pyplot as plt

# from liveplot import LivePlotClient

from os import path
import textwrap2
import re
import util as util

class dataCacheProxy():
    def __init__(self, expInst, newFile=False, stack_prefix='stack_', filepath=None):
        if filepath == None:
            self.exp = expInst
            self.data_directory = expInst.expt_path
            self.prefix = expInst.prefix
            self.set_data_file_path(newFile)
            self.current_stack = ''
            self.stack_prefix = stack_prefix
            # self.currentStack = lambda:None;
            # self.currentStack.note = self.note
            # self.currentStack.set = self.set
            # self.currentStack.post = self.post
        else:
            self.path = filepath

    def set_data_file_path(self, newFile=False):
        try:
            if newFile == True:
                self.filename = get_next_filename(self.data_directory, self.prefix, suffix='.h5')
            else:
                self.filename = get_current_filename(self.data_directory, self.prefix, suffix='.h5')
        except AttributeError:
            self.filename = self.exp.filename;
        self.path = path.join(self.data_directory, self.filename)

    def add(self, keyString, data):
        def add_data(f, group, keyList, data):
            if len(keyList) == 1:
                f.add_data(group, keyList[0], data)
            else:
                try:
                    group.create_group(keyList[0])
                except ValueError:
                    pass
                return add_data(f, group[keyList[0]], keyList[1:], data)

        keyList = keyString.split('.')
        with SlabFile(self.path) as f:
            add_data(f, f, keyList, data)

    def append(self, keyString, data):
        def append_data(f, group, keyList, data):
            if len(keyList) == 1:
                f.append_data(group, keyList[0], data)
            else:
                try:
                    group.create_group(keyList[0])
                except ValueError:
                    pass
                return append_data(f, group[keyList[0]], keyList[1:], data)

        keyList = keyString.split('.')
        with SlabFile(self.path) as f:
            append_data(f, f, keyList, data)

    def post(self, route, data):
        """
        append a datapoint to the current data stack.
        """
        if self.current_stack != '':
            route = self.current_stack + "." + route
        self.append(route, data)

    def set(self, route, data):
        """
        add a datapoint to the current data stack.
        """
        if self.current_stack != '':
            route = self.current_stack + "." + route
        self.add(route, data)

    def get(self, keyString):
        def get_data(f, keyList):
            if len(keyList) == 1:
                return f[keyList[0]][...];
            else:
                return get_data(f[keyList[0]], keyList[1:])

        keyList = keyString.split('.')
        with SlabFile(self.path) as f:
            return get_data(f, keyList)

    def new_stack(self):
        try: index = int(self.current_stack[-5:]) + 1
        except: index = 0
        self.current_stack = self.stack_prefix + str(100000 + index)[1:]
        with SlabFile(self.path) as f:
            try:
                f.create_group(self.current_stack)
            except ValueError, error:
                print "{} already exists. Move to next index.".format(self.current_stack)
                self.new_stack()

    def note(self, string, keyString=None, printOption=False, maxLength=79):
        if keyString == None:
            keyString = 'notes'
        if (self.current_stack) >= 1:
            keyString = self.current_stack + '.' + keyString
        if printOption:
            print string
        with SlabFile(self.path) as f:
            for line in textwrap2.wrap(string, maxLength):
                f.append(keyString, line + ' ' * (maxLength - len(line)))

if __name__ == "__main__":
    print "running a test..."

    # Setting up the instance
    exp = lambda: None;
    exp.expt_path = './'
    exp.prefix = 'test'
    cache = dataCacheProxy(exp)

    # test data
    test_data_x = np.arange(0, 10, 0.01)
    test_data_y = np.sin(test_data_x)

    # example usage
    cache.append('key1', (test_data_x, test_data_y) )
    plt.plot(cache.get('key1')[0][1])
    cache.add('key2', (test_data_x, test_data_y) )
    plt.plot(cache.get('key2')[1])
    # plt.show()

    cache.add('group1.key1', (test_data_x, test_data_y) )
    plt.plot(cache.get('group1.key1')[1])
    cache.append('group1.key2', (test_data_x, test_data_y) )
    plt.plot(cache.get('group1.key2')[0][1])
    # plt.show()

    cache.add('group1.subgroup.key2', (test_data_x, test_data_y) )
    plt.plot(cache.get('group1.subgroup.key2')[1])
    cache.append('group1.subgroup.key3', (test_data_x, test_data_y) )
    plt.plot(cache.get('group1.subgroup.key3')[0][1])
    plt.show()


    #now data is saved in the dataCache
    #now I want to move some data to a better file
    #each experiment is a file, contains:
    # - notes
    # - actionTitle
    #   - configs
    #   - mags
    #   - fpts
    #   - vpts
