#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
example2a_loadIntermediate.py: Example showing how to load and use a PRR intermediate file object

This example will work only after running Example 1.

Created by Scott Feister on Thu Nov 16 15:41:38 2017
"""

from pradreader.reader import loadPRR

def myalgorithm(prad):
    """ Your algorithm that runs on proton radiography data """
    pass

if __name__ == "__main__":
    filename = "./input.txt" # Path to your intermediate .txt file
    prad = loadPRR(filename) # Load your proton radiography file
    
    print(prad.s2r_cm)
    print(prad.s2d_cm)
    print(prad.Ep_MeV) 
    print(prad.bin_um)
    print(prad.flux2D) # 2D NumPy array
    print(prad.flux2D_ref) # 2D NumPy array
    print(prad.mask) # 2D NumPy array

    result = myalgorithm(prad) # Run your algorithm