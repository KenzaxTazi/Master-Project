# -*- coding: utf-8 -*-
"""
Created on Sat Nov  3 19:02:46 2018

@author: tomzh
"""
import numpy as np


from subprocess import Popen, PIPE

# Important Indices
# 1, 2, 22


variables1km = {1:'lat', 2:'lon', 22:'num_layers', 50:'feature_classification_flags'}
variables5km = {1: 'lat', 2:'lon', 69:'feature_classification_flags', 76:'feature_optical_depth'}
print('f')
index = '1'

filename = "D:/Calipso/5km/CAL_LID_L2_05kmCLay-Standard-V4-20.2018-03-31T23-18-17ZN.hdf"
try:
    with Popen(["hdp", "dumpsds", "-i", str(index), "-ds", filename], stdout=PIPE) as proc:
        a = proc.stdout.read()
        print('g')
    
except(FileNotFoundError):
        with Popen(["C:/Program Files/HDF_Group/HDF/4.2.14/bin/hdp.exe", "dumpsds", "-i", str(index), "-ds", filename], stdout=PIPE, shell=True) as proc:
            a = proc.stdout.read()
            print('f')


# Process data into float array
b = str(a)
c = b.split(" \\r\\n")
d = np.array(c)
d[0] = d[0][2:]
e = d[:-1]
f = np.float64(e)


#b = str(a)
#c = b.split(" \\r\\n")
#d = np.array(c)
#d[0] = d[0][2:]
#e = d[:-1]
#lat = e[:21120]
#lat = np.float64(lat)
#lon = e[21120:]
#lon[0] = lon[0][8:]
#lon = np.float64(lon)
