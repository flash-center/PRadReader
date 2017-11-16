"""
rdmit.py: Proton radiography readers specific to the MIT formats.

Currently only supports readers for the CSV file formats.

TODO:
    * Do some error checking on the filename & what not.
"""

import csv
import numpy as np
import re

def readmitcsv(fn):
    """
    Read in a CSV file in the MIT format and return the proton histogram and
    the bin size.

    Inputs:
        fn (str): Full file name.

    Outputs:
        flux2D (array): Numpy 2D array of proton flux at the detector
                        (counts/bin).
        flux2D_ref (array): REFERENCE proton flux at the detector (counts/bin).
                            Equals what flux2D would be in the 
                            absence of magnetic fields.
        bin_um (float): Pixel size in um.
    """
    # Open up the file for reading.
    with open(fn, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        
        # Iterate the reader over line 1.
        for i in range(1):
            next(reader)
        
        # Grab the dimensions from the second line.
        dim_str = next(reader)[0]
        # Search for an following an equals sign with a space after it.
        # Then search for an int following an x with a space after it.
        # Initialize the array in the correct dimensions.
        # Note: dim1 is the vert dim, dim2 is the horiz dim.
        dim2 = int(re.search('(?<=\= )\w+', dim_str).group(0))
        dim1 = int(re.search('(?<=x )\w+', dim_str).group(0))
        flux2D = np.zeros((dim1, dim2))

        # Grab the first value from the 3rd line, which will be a string
        # specifying the pixel size.
        # # Search for a float following an equals sign with a space after it.
        # TODO Do some error checking.
        pxl_str = next(reader)[0]
        bin_um = float(re.search('(?<=\= )\w+\.\w+', pxl_str).group(0))
       
        # Iterate another two lines over 4 and 5.
        for i in range(2):
            next(reader)

        # Read in the rest of the file as a numpy array.
        for i, row in enumerate(reader):
            for j, word in enumerate(row):
                flux2D[i,j] = float(word)

        # Flip the array upside down, since the top row of the array
        # in the file corresponds to the bottom row of the image, and the left
        # side corresponds to the left side.
        flux2D = np.flipud(flux2D)

        # Calculate the reference flux image.
        # TODO: Get a better reference flux image.
        flux2D_ref = np.zeros((dim1, dim2))
        flux2D_ref[:] = np.mean(flux2D)
        
    return(flux2D, flux2D_ref, bin_um)



