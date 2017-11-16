#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
reader.py: Read in proton radiography of various sources (FLASH4, ...)
Includes the 'prad' class, which defines an object holding proton radiography data

Created by Scott Feister, J.T. Laune, and Alemayehu Bogale on Fri Jul 28 18:11:48 2017

Call via "python reader.py filename". Will prompt for additional info.
"""

import sys
import os
import datetime
# Python3 style input commmand even in Python2; get via "pip install future"
from builtins import input 
from re import match
import numpy as np
from .rdflash import readFlash4
from .rdmit import readmitcsv
from .rdcarlo import readCarlo
from .fluxmap import fluxPlot
from .rdgeneric import readtxt

class prad(object):
    """
    Object for handling all the attributes of a proton radiography construction
    problem. Typically, different proton radiograph formats are read into this
    object for use with other reconstruction tools.

    Inputs:
    
    Attributes:
        filename (string): full filename (including path) 
                        of the proton detector file;
                        e.g."/home/myouts/blob.out", 
                        where "blob.out" is the basename
        rtype (string): file format e.g. carlo, flash4, mitcsv
        s2r_cm (float): Distance from the source to the plasma (in cm)
        s2d_cm (float): Distance from the source to the screen (in cm)
        Ep_MeV (float): Proton energy (in MeV)
        bin_um (float): Pixel size of radiograph (in um)
        flux2D (array): 2D array of flux values
        flux2D_ref (array): 2D array of reference flux values
        mask (array): Flux mask (constructed based on x_select, y_select)
        x_select (tuple): (beginning, ending) in % of flux mask in y-direction
        y_select (tuple): (beginning, ending) in % of flux mask in y-direction

    Outputs:

    """
    def __init__(self, filename):
        # Attributes. 
        self.filename = filename
        self.rtype = None
        self.flux2D = None
        self.flux2D_ref = None
        self.s2r_cm = None  
        self.s2d_cm = None 
        self.Ep_MeV = None 
        self.bin_um = None
        self.mask = None
        self.x_select = (0,100)
        self.y_select = (0,100)
        
        # Prompts.
        self.prompts = {
                'rtype'  : 'Type of file? Options are "prr", "carlo",' \
                            '"mitcsv", "csv", "flash4": ',
                's2r_cm' : 'Distance from the source to the plasma (in cm): ',
                's2d_cm' : 'Distance from the source to the screen (in cm): ' ,             
                'Ep_MeV' : 'Proton energy (in MeV): ',
                'bin_um' : 'Pixel size of radiograph (in um): ',
                'x_select' : 'Flux % selection in x-direction.' \
                             'Enter two numbers separated by a space.' \
                             '(e.g., "0 100"): ', 
                'y_select' : 'Flux % selection in y-direction ' \
                             'Enter two numbers separated by a space. ' \
                             '(e.g., "0 100"): ', 
                }
    
    def __str__(self):
        return ("Prad object from '" 
                + self.filename + "'."
                + "Try <object>.show() for more details.")

    def show(self):
        """ Display details of the prad object """
        print("~~~~~~~ PRAD OBJECT CONTENTS ~~~~~~~")
        keys = vars(self).keys()
        goodkeys = set(keys) - {'prompts'} # Don't show the 'prompts'
        for k in sorted(goodkeys, key=str.lower):
            print(k + ": " + str(getattr(self, k)))
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

    # TODO: Make the prompting more general, to handle strings AND numbers
    def prompt(self):
        """
        If the attributes are not set, prompt the user for input.
        """
        print("The Prad object needs to be supplemented. "\
                "Please answer the following questions to complete the Prad object.")
        for key in self.prompts.keys():
            if getattr(self, key) is None:
                setattr(self, key, float(input(self.prompts[key])))
            if getattr(self,key) == (0,100):
                setattr(self, key, tuple(map(float, input(self.prompts[key]).split())))
        
    def genmask(self):
        """
        Generate the mask array from flux2D array size and x_select, y_select tuples
        """
        print("Generating 2D mask array...")
        self.mask = np.ones(self.flux2D.shape)
        start_x = self.x_select[0]
        end_x = self.x_select[1]
        start_y = self.y_select[0]
        end_y = self.y_select[1]
        
        xbeg = int(np.round((start_x/100.0) * self.mask.shape[0]))
        xend = int(np.round((end_x/100.0) * self.mask.shape[0]))
        ybeg = int(np.round((start_y/100.0) * self.mask.shape[1]))
        yend = int(np.round((end_y/100.0) * self.mask.shape[1]))
        self.mask[xbeg:xend, ybeg:yend] = 0
        print("Mask generated.")

    # TODO: Expand this to make a labeled plot the geometry of the target/detector
    # TODO: Show the masking in the flux map plot, e.g. via a labeled rectangle or shaded portion
    # TODO: Test this function works
    def plot(self, plotdir='plots'):
        """
        Save a flux map plot (wrapper for fluxmap.fluxPlot)
        Inputs:
            plotdir: string, Desired output folder for the output plots (folder tree
                        will be generated if not existing)
        Output files:
            PNG of the flux map
        """
        print("Making plots of flux map and reference flux map.")
        os.makedirs(plotdir, exist_ok=True) # Make the folder hierarchy; ok if it already exists
        fluxPlot(os.path.join(plotdir, "reference_flux.png"), self.flux2D, self.bin_um)
        fluxPlot(os.path.join(plotdir, "flux.png"), self.flux2D_ref, self.bin_um)
        print("Plots saved into directory '" + plotdir + "'")
        
    def read(self):
        """
        Read in a proton radiography input file
        """
        
        if self.rtype is None:
            self.rtype = input(self.prompts['rtype'])
        
        print("Reading contents of file: " + self.filename)
                
        if self.rtype == 'prr':
            self.__readPRR() # Intermediate file format; replace everything
            
        elif self.rtype == 'flash4':
            if self.bin_um == None:
                self.bin_um = float(input(self.prompts['bin_um']))
            s2r_cm, s2d_cm, Ep_MeV, flux2D, flux2D_ref = readFlash4(
                                                            self.filename, 
                                                            self.bin_um)
            self.flux2D = flux2D
            self.flux2D_ref = flux2D_ref
            self.s2r_cm = s2r_cm 
            self.s2d_cm = s2d_cm 
            self.Ep_MeV = Ep_MeV
        
        elif self.rtype == 'mitcsv':
            flux2D, flux2D_ref, bin_um = readmitcsv(self.filename)
            self.flux2D = flux2D
            self.flux2D_ref = flux2D_ref
            self.bin_um = bin_um
        
        elif self.rtype == 'csv':
            flux2D, flux2D_ref = readtxt(self.filename)
            self.flux2D = flux2D
            self.flux2D_ref = flux2D_ref
            
        elif self.rtype == 'carlo':
            s2r_cm, s2d_cm, Ep_MeV, flux2D, flux2D_ref= readCarlo(
                                                            self.filename, 
                                                            bin_um)
            
            self.flux2D = flux2D
            self.flux2D_ref = flux2D_ref
            self.s2r_cm = s2r_cm 
            self.s2d_cm = s2d_cm 
            self.Ep_MeV = Ep_MeV

        else:
            raise(Exception("Proton radiography type " 
                            + str(self.rtype) + " not recognized"))
                            
        print("File read complete.")

    def validate(self):
        """ Ensure the validity of the elements """
        print("Validating elements of the prad object...")
        #TODO: Validate the object here!
        pass
        print("[No validation function written! Continuing...]")

    def write(self, ofile='input.txt'):
        """ Create an intermediate text file 
        Inputs:
            ofile: Desired output filepath (e.g. "input.txt")
        Output file:
            input.txt (file): the intermediate file for every file input
                e.g. contains s2r_cm, s2d_cm, Ep_MeV, bin_um,
                flux2D, flux2D_ref, and mask
        Note: This object can be reloaded via:
            pr = reader.loadPRR('input.txt')
        """
        
        print("Writing intermediate prad object file.")
        with open(ofile, 'w') as out:
            out.write('# PRadReader (PRR) Generated Input File v1.01a\n')
            out.write('# Date generated: '
                      +str(datetime.datetime.now().date()) + ' '
                      +str(datetime.datetime.now().time()) + '\n')
            out.write("# s2r_cm " + str(self.s2r_cm) + "\n")
            out.write("# s2d_cm " + str(self.s2d_cm) + "\n")
            out.write("# Ep_MeV " + str(self.Ep_MeV) + "\n")
            out.write("# bin_um " + str(self.bin_um) + "\n")
            
            out.write("# flux2D " + str(self.flux2D.shape) + "\n")
            out.write("# flux2D_ref " + str(self.flux2D_ref.shape) + "\n")
            out.write("# x-mask " + str(self.x_select[0]) 
                      + " %" + " - " + str(self.x_select[1]) + " %" + "\n")
            out.write("# y-mask " + str(self.y_select[0]) 
                      + " %" + " - " + str(self.y_select[1]) + " %" + "\n")
        
        with open(ofile, 'ab') as out:
            np.savetxt(out, self.flux2D, delimiter=',', newline='\n')
            np.savetxt(out, self.flux2D_ref, delimiter=',', newline='\n')
        
        print("Intermediate prad object file written to '" + ofile + "'.")
    
    def __readPRR(self):
        """
        (Private) Read the pradreader intermediate file format
        """
        # TODO here: Check the PRR file version is appropriate!
        with open(self.filename) as f:
            # TODO here: Read in the file contents!
            pass
        
def loadPRR(ifile='input.txt'):
    """
    Loads in a pradreader (PRR) intermediate .txt file with no CLI input from user
    
    Useful function to be called from outside modules
    """
    pr = prad(ifile) # Initialize a prad object with this filename
    pr.rtype = 'prr' # Specify filetype
    pr.read() # Read in the file
    pr.genmask() # Generate the 2D mask from x/y tuples
    pr.validate() # Validate that all prad object elements are looking good
    return pr
    
if __name__ == "__main__":
    pr = prad(sys.argv[0]) # Set the filename, initialize the object
    # TODO Insert here: Try and guess the rtype by looking at the file (version 2)
    pr.read() # Read the file contents; prompt for file type as needed
    pr.show() # Display what was just read in
    pr.prompt() # Fill in the gaps on parameters
    pr.genmask() # Generate the mask from x/y tuples
    pr.validate() # Validate that the elements are looking good
    pr.plot(plotdir='plots') # Save some flux plots
    pr.write(ofile='input.txt') # Write the intermediate prad object file
