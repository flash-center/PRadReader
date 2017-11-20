#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
loadPickle.py: Example showing how to load and use a PRR pickled file object (quick and dirty use recommended only; use intermediate file object for sharing data files)

This example will work only after running Example 1.

Created by Scott Feister on Thu Nov 16 15:41:38 2017
"""

from pradreader.reader import loadPRRp

def myalgorithm(prad):
    """ Your algorithm that runs on proton radiography data """
    pass

if __name__ == "__main__":
    filename = "./input.p" # Path to your intermediate .txt file
    prad = loadPRRp(filename) # Load your proton radiography file
    
    print(prad.s2r_cm)
    print(prad.s2d_cm)
    print(prad.Ep_MeV) 
    print(prad.bin_um)
    print(prad.flux2D) # 2D NumPy array
    print(prad.flux2D_ref) # 2D NumPy array
    print(prad.mask) # 2D NumPy array

    result = myalgorithm(prad) # Run your algorithm