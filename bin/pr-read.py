#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pr-read.py: Command-line tool for reading in various file formats and outputting a text file

Created by Scott Feister, J.T. Laune, and Alemayehu Bogale on Mon Nov 20 14:43:18 2017

Call via "python pr-read.py filename". Will prompt user for additional info.

"""

import sys
from pradreader.reader import prad

# TODO: Add optional flags for output files, anything else
if __name__ == "__main__":
    pr = prad(sys.argv[1]) # Set the filename, initialize the object
    # TODO Insert here: Try and guess the rtype by looking at the file (version 2)
    pr.read() # Read the file contents; prompt for file type as needed
    pr.show() # Display what was just read in
    pr.prompt() # Fill in the gaps on parameters
    pr.genmask() # Generate the mask from x/y tuples
    pr.validate() # Validate that the elements are looking good
    pr.write(ofile='input.txt') # Write the intermediate prad object file (shared uses)
    pr.pickle(ofile='input.p') # Write the pickled prad object file (quick and dirty uses)
    pr.plot(plotdir='plots') # Save some flux plots


