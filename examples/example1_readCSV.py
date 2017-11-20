#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
example1_readCSV.py: An example of reading/saving the rad1.csv flux file

Created by Scott Feister on Wed Nov 15 12:10:17 2017
"""

from pradreader import reader

if __name__ == "__main__":
    print("Import successful!")
    pr = reader.prad('rad1.csv') # Set the filename, initialize the object
    pr.read() # Read the file contents; prompt for file type as needed
    pr.genmask() # Generate the mask from x/y tuples (just to test for failure)
    pr.show() # Display what was just read in
    pr.prompt() # Fill in the gaps on parameters
    pr.genmask() # Re-generate the mask from x/y tuples
    pr.write(ofile='input.txt')
    pr.pickle(ofile='input.p')
    pr.plot(plotdir='plots')