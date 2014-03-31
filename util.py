__author__ = 'Ge Yang'
from numpy import *
from time import time, sleep
from datetime import datetime

def tic():
    global tic_time
    tic_time = time.time()

def toc():
    global tic_time
    return time.time() - tic_time

def get_date_time_string():
    now = datetime.now()
    return "{}/{}/{} {}:{}:{}".format(now.year, now.month, now.day, now.hour, now.minute, now.second)


def ramp(start, finish, step):
    if start < finish:
        Vs = concatenate((arange(start, finish, abs(step)), array([finish, ])))
    else:
        Vs = concatenate((arange(start, finish, -abs(step)), array([finish, ])))
    try:
        if Vs[-1] == Vs[-2]:
            Vs = Vs[:-1]
    except IndexError:
        pass;
    return Vs


def ramps(pts, step):
    seg = array([])
    for i in range(1, len(pts)):
        seg = concatenate((seg, ramp(pts[i - 1], pts[i], step)))
    return seg


def Vramps(points_steps):
    segs = array([])
    for points, step in points_steps:
        segs = concatenate((segs, ramps(points, step)))
    return segs


def flatten(mat):
    out = [];
    for row in mat:
        out += list(row)
    return out


def days_hours_minutes(seconds):
    days = seconds / (3600 * 24)
    hours = seconds / 3600 - days * 24
    minutes = seconds / 60 - days * 24 * 60 - hours * 60
    return days, hours, minutes

class dict2obj:
    def __init__(self, **entries):
        self.__dict__.update(entries)
    def __repr__(self):
        return '<%/s>'%str('\n'.join('%s:%s'%(k,repr(v)) for (k,v) in self.__dict__.iteritems()))

def amp(pair):
    return sqrt(pair[0] ** 2 + pair[1] ** 2)

def phase(pair):
    if pair[1] != 0:
        theta = arctan(pair[0] / pair[1])
    else:
        theta = pi / 2;
    return theta
