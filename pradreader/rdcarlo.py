#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
rdcarlo.py: Proton radiography reades2d_cm specific to Carlo's format

Created by Alemayehu Bogale & Scott Feister on Thu Aug 17 12:31:25 2017

To generate the reference flux map, currently just takes the average of the signal flux map.

TODO:
    * Get a better reference flux from the FLASH proton count and geometry.
"""

import re
import sys
import os
import math
import numpy as np
import pandas as pd
from .fluxmap import fluxMap # For binning the proton list x/y values

def readCarlo(fname, bin_um = 320):
    """ Read in and histogram a Carlo's blob.out proton radiography file.
    Looks for a file in the same directory which specifies the detector setup.
    Histograms the list of proton positions into a flux array

    Inputs:
        fn: String, full filename (including path) of the proton detector file; e.g. "/home/myouts/blob.out", where "blob.out" is the basename
        bin_um: Float, size of the square edge lengths with which to divide the detector for binning
    Outputs:
        s2r_cm: Distance from the proton source to the interaction region, in cm
        s2d_cm: Distance from the proton source to the detector, in cm
        Ep_MeV: Proton energy in MeV
        flux: Numpy array, 2D, proton flux at the detector (counts/bin)
        flux_ref: Numpy array, 2D, REFERENCE proton flux at the detector (counts/bin) (flux2D_ref equals what flux2D would be in the absence of magnetic fields)

    Ws2r_Cmtten by Almeyahehu 2017-08-17
    """

    # Data file
    fd = open(fname, 'r')

    line = fd.readline()
    print("Parsing" + fname + "...")
    while not re.match('# Columns:', line):
        if re.search('^# Tkin:', line):
            Ep_MeV = float(line.split()[2])

        if re.match('# rs:', line):
            s2d_cm = float(line.split()[2])

        if re.match('# ri:', line):
            s2r_cm = float(line.split()[2])

        if re.match('# raperture:', line):
            rap = float(line.split()[2])
        line = fd.readline()

    while re.match('#', line): line = fd.readline()

    radius = rap * s2d_cm / s2r_cm  # radius of undeflected image of aperture at screen
    dmax = 0.98 * radius / math.sqrt(2.0) # half the width of the detector
    nbins = int(dmax * 2 / (bin_um/10000.0)) # number of bins per dimensions
    delta = 2.0 * dmax / nbins # width of a bin

    num_prot = 0

    fd.close()


    # Read in the file and grab the third and fourth columns for the x and y
    # coordinates.
    coord_xy = pd.read_csv(fname, header=None,
                               delim_whitespace=True, comment='#',
                               usecols=[3,4]).as_matrix()

    # Initialize an array that is the correct size and then assign bin numbers
    # to the initial coordinate matrix.
    num_prot = coord_xy.shape[0]
    coord_ij = np.zeros(coord_xy.shape)
    coord_ij[:,0] = ((coord_xy[:,0] +(dmax))/(bin_um*1e-4)).astype(int)
    coord_ij[:,1] = ((coord_xy[:,1] +(dmax))/(bin_um*1e-4)).astype(int)

    # Now we need to get rid of entries that are too large/too small.
    coord_xy = coord_xy[~((coord_ij > nbins).any(axis=1))]
    coord_ij = coord_ij[~((coord_ij > nbins).any(axis=1))]
    coord_xy = coord_xy[~((coord_ij < 0).any(axis=1))]


    print("Calculating reference flux...")
    mean = (num_prot * delta**2) / (math.pi * radius**2) # average fluence distrubution
    flux2D_ref = np.zeros((nbins,nbins))
    flux2D_ref[:] = mean # mean flux image


    print("Histogramming protons...")
    flux2D, flux2D_cm2, xedges_cm, yedges_cm = fluxMap(coord_xy[:,0], coord_xy[:,1], (dmax * 2), bin_um)


    return s2r_cm, s2d_cm, Ep_MeV, flux2D, flux2D_ref


def path_parse(fname, bin_um = 320):
    '''
    Parses input file and Returns the 2D array relevant to the actual magnetic
    field for verfication purposes

    Parameters
    ----------
    fn(string): full filename (including path) of the proton detector file; e.g. "/home/myouts/blob.out", where "blob.out" is the basename
    bin_um(float): size of the square edge lengths with which to divide the detector for binning

    Returns
    -------
    Bperp(2D array of (x,y) tuple): Magnetic Perpendicular Integral
    '''


    # Data file
    fd = open(fname, 'r')

    line = fd.readline()
    print("Parsing " + fname + "...")
    while not re.match('# Columns:', line):
        if re.search('^# Tkin:', line):
            Ep_MeV = float(line.split()[2])

        if re.match('# rs:', line):
            s2d_cm = float(line.split()[2])

        if re.match('# ri:', line):
            s2r_cm = float(line.split()[2])

        if re.match('# raperture:', line):
            rap = float(line.split()[2])
        line = fd.readline()

    while re.match('#', line): line = fd.readline()

    radius = rap * s2d_cm / s2r_cm  # radius of undeflected image of aperture at screen
    dmax = 0.98 * radius / math.sqrt(2.0) # half the width of the detector
    nbins = int(dmax * 2 / (bin_um/10000.0)) # number of bins per dimensions
    delta = 2.0 * dmax / nbins # width of a bin

    num_prot = 0

    flux = np.zeros((nbins,nbins)) # num. of protons per bin
    Bperp = np.zeros((nbins,nbins,2)) # B Path Integral
    J = np.zeros((nbins,nbins)) # Current Path Integral

    nprot = 0
    while line:

        nprot +=  1
        xx= float(line.split()[3])
        yy= float(line.split()[4])
        jj = float(line.split()[8])
        b0 = float(line.split()[9])
        b1 = float(line.split()[10])
        i = int((xx + dmax)/delta)
        j = int((yy + dmax)/delta)


        if (xx + dmax)/delta >= 0 and i < nbins and (yy + dmax)/delta >= 0 and j < nbins:
            flux[i,j] += 1
            Bperp[i,j,0] += b0
            Bperp[i,j,1] += b1
            J[i,j] += jj

        line = fd.readline()

    fd.close()

    print("Min, max, mean pixel counts, and delta: ")
    print(flux.min(), flux.max(), flux.mean(), delta)

    avg_fluence = nprot / (math.pi * radius**2)
    im_fluence = flux.sum() / (4 * dmax**2)

    for i in range(nbins):
        for j in range(nbins):
            try:
                Bperp[i,j,:] /= flux[i,j]
                J[i,j] /= flux[i,j]
            except ZeroDivisionError:
                print("Zero pixel, will screw everything up.")
                raise ValueError

    return Bperp, J, avg_fluence, im_fluence
