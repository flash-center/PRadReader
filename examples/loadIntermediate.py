#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
loadIntermediate.py: Example showing how to load and use a PRR intermediate file object

Created by Scott Feister on Thu Nov 16 15:41:38 2017
"""

from pradreader.reader import loadPRR

def myalgorithm(prad):
    pass

if __name__ == "__main__":
    filename = "../test/input.txt" # Path to your intermediate .txt file
    prad = loadPRR(filename)
    
    print(prad.s2r_cm)
    print(prad.s2d_cm)
    print(prad.Ep_MeV) 
    print(prad.bin_um)
    print(prad.flux2D) # 2D NumPy array
    print(prad.flux2D_ref) # 2D NumPy array
    print(prad.mask) # 2D NumPy array

    result = myalgorithm(prad)