#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
readtests.py: A couple examples/tests of pradreader

Created by Scott Feister on Wed Nov 15 12:10:17 2017
"""
import sys
sys.path.append("..") # TODO: Not need this line.

import pradreader
from pradreader import reader

if __name__ == "__main__":
    print("Import successful!")
    myrad = reader.prad('rad1.csv') # Set the filename, initialize the object
    myrad.read() # Read the file contents; prompt for file type as needed
    myrad.genmask() # Generate the mask from x/y tuples (just to test for failure)
    myrad.show() # Display what was just read in
    myrad.prompt() # Fill in the gaps on parameters
    myrad.genmask() # Re-generate the mask from x/y tuples
    myrad.write(ofile='input.txt')
    myrad.plot(plotdir='plots')