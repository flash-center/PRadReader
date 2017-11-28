"""
rdgeneric.py: Proton radiography readers for generic formats, like CSV.

Currently only supports readers for the csv-style file format (np.loadtxt).

Created by Scott Feister on Fri Oct 20 14:00:22 2017
"""

import numpy as np

def readtxt(fn, delimiter=None):
    """
    Read in a generic text file containing a 2D flux array as delimited values.

    Inputs:
        fn (str): Full file name.

    Outputs:
        flux2D (array): Numpy 2D array of proton flux at the detector
                        (counts/bin).
        flux2D_ref (array): REFERENCE proton flux at the detector (counts/bin).
                            Equals what flux2D would be in the 
                            absence of magnetic fields.
    """
    # Open up the file for reading.
    flux2D = np.loadtxt(fn, delimiter=delimiter)
    flux2D_ref = np.zeros(flux2D.shape)
    flux2D_ref[:] = np.mean(flux2D)
    
    return(flux2D, flux2D_ref)
