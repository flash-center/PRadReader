#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
fluxmap.py: Tools for generating and plotting flux maps

Covers:
* Generating flux maps (2D histograms) from proton x/y lists
* Plotting flux maps to bitmap using matplotlib

Created by Scott Feister & J.T. Laune on Fri Jul 28 18:11:48 2017
"""

import numpy as np
import matplotlib
matplotlib.use('Agg') # Headless plotting (avoids python-tk GUI requirement)
                      # Note: throws warning if another matplotlib engine is already initialized
import matplotlib.pyplot as plt # For flux map plots

def fluxMap(xp_cm, yp_cm, width_cm, bin_um):
    """ Make flux map from a list of proton x,y positions
    Inputs:
        xp_cm: 1D NumPy array of proton x positions on detector (center of detector is x = 0)
        yp_cm: 1D NumPy array of proton y positions on detector (center of detector is y = 0)
        width_cm: float, total width of the square detector, in cm
        bin_um: float, desired bin size for the 2D histogram, in microns
    Outputs:
        flux2D: 2D Histogram of proton flux, in units of protons/bin
        flux2D_cm2: 2D Histogram of proton flux, in units of protons/cm2
    
    Outputs 2D flux arrays with 'xy' indexing (axis 0 is y axis, axis 1 is x axis), not 'ij'
 
    Written by Scott Feister 2017-08-03
    """
    
    bins_cm = np.arange(-width_cm/2, width_cm/2, bin_um*1e-4) # 1D array of bin edges, in centimetres
    H, xedges_cm, yedges_cm = np.histogram2d(xp_cm, yp_cm, bins=bins_cm) # Histogram the x/y data

    flux2D = H.T # Perform a transpose (flip x/y axis) on the histogram so that it is in 'xy' indexing rather than 'ij' indexing
    
    # Convert H to proton fluence (protons/cm2)
    bin_cm2 = (bin_um*1e-4)**2 # Area of each bin
    flux2D_cm2 = flux2D / bin_cm2 # Convert flux2D (histogram array) from units of protons/bin into protons/cm2
    
    return flux2D, flux2D_cm2, xedges_cm, yedges_cm

def fluxPlot(outfn, flux2D, bin_um):
    """ Example plotting function for a radiograph, using matplotlib
    Inputs:
        outfn: String, full filename (including path) of the image file to write, e.g. "/home/myouts/myradiograph.png"
        flux2D: Numpy array, 2D, proton flux at the detector (a.u.)
        bin_um: Float, size of the square edge lengths with which to divide the detector for binning
    Outputs:
        Saves a flux map plot to the specified input file.
    
    Assume 'xy' indexing (axis 0 is y axis, axis 1 is x axis), not 'ij'
    
    Written by Scott Feister 2017-08-03
    """
    fig = plt.figure(figsize=(6,5))
    ax = fig.add_subplot(111)
    
    xmax = (flux2D.shape[1] + 1) * bin_um*1.0e-4 # X/ length of detector in cm
    ymax = (flux2D.shape[0] + 1) * bin_um*1.0e-4 # Y/ width of detector in cm

    cax = ax.pcolorfast([0, xmax], [0, ymax], flux2D/np.mean(flux2D), cmap='Greys')
    cbar = fig.colorbar(cax, label='Proton flux / Mean')
    ax.set_aspect('equal')

    ax.set_title('Proton radiograph, detector plane')  
    ax.set_xticks([0, np.round(xmax, 2)])
    ax.set_yticks([0, np.round(ymax, 2)])
    
    #plt.axis('off')
    plt.xlabel('Detector X (cm)', labelpad=-10)
    plt.ylabel('Detector Y (cm)', labelpad=-25)
        
    # Add lower left footer
    fluxMean_cm2 = np.mean(flux2D) / (bin_um * 1e-4)**2
    footString = "Mean: " + str(int(np.round(fluxMean_cm2))) + " cm$^{-2}$"
    fig.text(0.01, 0.01, footString, style='italic', horizontalalignment='left') # Lower right in figure units

    plt.tight_layout(rect=[0, 0.04, 1, 0.98])
    fig.savefig(outfn, dpi=150)
    
    plt.close(fig)
    return

def fluenceContrast(outfn, flux2D, flux2D_ref, bin_um, vmin=None, vmax=None):
    """ Example plotting function for a radiograph, using matplotlib
    Inputs:
        outfn: String, full filename (including path) of the image file to write, e.g. "/home/myouts/myradiograph.png"
        flux2D: Numpy array, 2D, proton flux at the detector (a.u.)
        flux2D_ref: Numpy array, 2D, reference proton flux at the detector (a.u.)
        bin_um: Float, size of the square edge lengths with which to divide the detector for binning
        vmin, vmax: Max and min for the colorplot
    Outputs:
        Saves a fluence contrast map plot  [ (flux - flux_ref) / flux_ref ] to the specified input file.
    
    Assume 'xy' indexing (axis 0 is y axis, axis 1 is x axis), not 'ij'
    
    Written by Scott Feister 2018-07-05
    """
    fig = plt.figure(figsize=(6,5))
    ax = fig.add_subplot(111)
    
    xmax = (flux2D.shape[1] + 1) * bin_um*1.0e-4 # X/ length of detector in cm
    ymax = (flux2D.shape[0] + 1) * bin_um*1.0e-4 # Y/ width of detector in cm

    fluence_contrast = (flux2D - flux2D_ref) / flux2D_ref
    
    if vmin is None:
        vmin = np.min(fluence_contrast)
    if vmax is None:
        vmax = np.max(fluence_contrast)
        
    cax = ax.pcolorfast([0, xmax], [0, ymax], fluence_contrast, cmap='viridis', vmin=vmin, vmax=vmax)
    cbar = fig.colorbar(cax, label='Fluence contrast (unitless)')
    ax.set_aspect('equal')

    ax.set_title('Fluence contrast, detector plane')  
    ax.set_xticks([0, np.round(xmax, 2)])
    ax.set_yticks([0, np.round(ymax, 2)])
    
    #plt.axis('off')
    plt.xlabel('Detector X (cm)', labelpad=-10)
    plt.ylabel('Detector Y (cm)', labelpad=-25)
        
    plt.tight_layout(rect=[0, 0.04, 1, 0.98])
    fig.savefig(outfn, dpi=150)
    
    plt.close(fig)
    return