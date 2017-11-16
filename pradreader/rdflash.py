#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
rdflash.py: Proton radiography readers specific to the FLASH4 format

Created by Scott Feister & J.T. Laune on Fri Jul 28 18:11:48 2017

To generate the reference flux map, currently just takes the average of the signal flux map.

TODO:
    * Get a better reference flux from the FLASH proton count and geometry.
"""

import re
import os
import numpy as np
from .fluxmap import fluxMap # For binning the proton list x/y values

def readFlash4(fn, bin_um = 320):
    """ Read in and histogram a FLASH4 proton radiography file.
    Looks for a file in the same directory which specifies the detector setup.
    Histograms the list of proton positions into a flux array

    Inputs:
        fn: String, full filename (including path) of the proton detector file; e.g. "/home/myouts/lasslab_ProtonDetectorFile01_2.201E-09", where "lasslab_" can be any basename
            Note: The folder must also contain "lasslab_ProtonImagingDetectors.txt", "lasslab_ProtonBeamsPrint.txt", and "lasslab_ProtonImagingMainPrint.txt",  where "lasslab_" is the same basename as above
        bin_um: Float, size of the square edge lengths with which to divide the detector for binning
    Outputs:
        s2r_cm: Distance from the proton source to the interaction region, in cm
        s2d_cm: Distance from the proton source to the detector, in cm
        Ep_MeV: Proton energy in MeV
        flux2D: Numpy array, 2D, proton flux at the detector (counts/bin)
        flux2D_ref: Numpy array, 2D, REFERENCE proton flux at the detector (counts/bin) (flux2D_ref equals what flux2D would be in the absence of magnetic fields)

    Written by Scott Feister 2017-08-03
    """

    # Check if a much-faster-to-read version of the input file exists already (NumPy dump .npz extension)
    if os.path.isfile(fn.replace('.gz', '') + '.npz'):
        fn = fn.replace('.gz', '') + '.npz' # If this faster file exists, redefine the "filename" to be that.

    folder, name = os.path.split(fn)
    p = re.compile(r'^(\w*?)ProtonDetectorFile([0-9]+)_(\S*?)(\.[npgz]*?){0,1}$') # Extract info from filename, e.g. "lasslab_ProtonDetectorFile01_2.200E-08" ==> ("lasslab_", "01", "2.2000E-08")
    m = p.findall(name)
    #print m

    if not m: # Filename did not match our pattern, throw an error
        raise(Exception("Input filename does not match the known '[basename]ProtonDetectorFile[number]_[time] (+ optional .gz or .npz) pattern."))

    basenm = m[0][0] # (Simulation basename, e.g. "lasslab_")
    detnum = int(m[0][1]) # Proton detector/beam number (e.g. 1, 2, 3,..)
    # time_ns = float(m[0][2])*1e9 # Simulation time, in nanoseconds
    ext = m[0][3] # filename extension; can be .gz or .npz

    print("Reading beam/detector metadata...")
    _, s2d_cm, width_cm = detParse(folder, basenm, detnum)
    _, Ep_MeV, s2r_cm, ap_deg, nprot = beamParse(folder, basenm, detnum)

    print("Reading the list of protons...")
    # Read the file as a whole into memory
    if ext == '' or ext == '.gz': # filename has no extension or '.gz', so it's the native FLASH output or a gzipped version of it
        print("Note: Using original FLASH file this time (slow) but saving a faster NumPy .npz file for next time...")
        dat = np.genfromtxt(fn)
        np.savez_compressed(fn.replace('.gz', '') + '.npz', dat=dat) # Store it in .npz format for faster read-in next time
    elif ext == '.npz': # filename has '.npz' extension; the FLASH output has been loaded into NumPy once before, then saved back in NumPy format (not a native FLASH output)
        print("Note: Using the NumPy .npz file (fast)...")
        with np.load(fn) as data:
            dat = data['dat']
    else:
        raise(Exception("Filename extension not recognized as blank, '.gz', or '.npz'"))

    [xp_cm, yp_cm] = (dat[:,(0,1)].T - 0.5) * width_cm # Convert scatter points from 0 to 1 grid into -x to +x centimeters

    print("Histogramming protons...")
    flux2D, flux2D_cm2, xedges_cm, yedges_cm = fluxMap(xp_cm, yp_cm, width_cm, bin_um)

    print("Calculating reference flux (small angle approx.)...")
    # TODO: Lose the small angle approximation

    ## Calculate beam protons per sterradian
    #beamsr = 2 * np.pi * (1 - np.cos(np.deg2rad(ap_deg)/2.0)) # Solid angle of the beam, based on its full aperture angle
    #protsr = nprot / beamsr # Beam protons per sterradian

    ## Calculate solid angle of detector (small angle approx.)
    #alph = width_cm / (2 * s2d_cm) # Detector subtended angle in radians (small angle approx.)
    #detsr = 4 * np.arccos(np.sqrt( (1 + 2 * alph**2) / (1 + alph**2)**2 ) ) # Detector solid angle relative to capsule center, in s.r.

    # Calculate the undeflected beam radius
    protrad_cm = s2d_cm * np.tan(np.deg2rad(ap_deg/2.0)) # Radius of undeflected cone in the detector plane, in centimeters

    # Calculate protons per centimeter squared, at the detector plane (small angle approximation)
    prot_cm2 = nprot / (np.pi * protrad_cm**2) # Beam protons/cm^2, at the detector plane

    prot_bin = prot_cm2 * (bin_um * 1.0e-4)**2 # Beam protons per flux bin

    X, Y = np.meshgrid((xedges_cm[:-1] + xedges_cm[1:]) / 2.0, (yedges_cm[:-1] + yedges_cm[1:]) / 2.0)
    R = np.sqrt(X**2 + Y**2)

    flux2D_ref = np.zeros(flux2D.shape)
    flux2D_ref[R < protrad_cm] = prot_bin

    return s2r_cm, s2d_cm, Ep_MeV, flux2D, flux2D_ref

def mainParse(folder, basenm):
    """ Parse the FLASH4 '[basename]ProtonImagingMainPrint.txt' file for a given beam number
    Inputs:
        folder: String, Folder path in which '[basename]_ProtonImagingDetectors.txt' can be found
        basenm: String, Basename used in the FLASH4 simulation
    Outputs:
        maindict: Python dict, containing various information found in ProtonImagingMainPrint.txt

    Written by Scott Feister 2017-08-03
    """
    # Create the "ProtonImagingMainPrint.txt" full filename
    fn = os.path.join(folder, basenm + "ProtonImagingMainPrint.txt")

    # Read in file contents to buffer
    with open(fn) as f:
        txraw = f.read()

    # Parse the buffer, re-structuring the line-by-line definitions into a python dictionary
    maindict = {}
    p = re.compile('^\s*(.*?)\s*=\s*(.*?)\s*$', re.MULTILINE)
    matches = p.findall(txraw)
    for m in matches:
        maindict[m[0]] = m[1]

    # Return the dictionary
    return maindict

def beamParse(folder, basenm, beamnum = 1):
    """ Parse the FLASH4 '[basename]ProtonBeamsPrint.txt' file for a given beam number
    Inputs:
        folder: String, Folder path in which '[basename]ProtonBeamsPrint.txt' can be found
        basenm: String, Basename used in the FLASH4 simulation
        beamnum: Integer, Proton beam number to analyze (1, 2, ..., 8, or 9)
    Outputs:
        beamdict: Python dict, containing various information about this proton beam
        Ep_MeV: Float, proton energy in MeV
        s2r_cm: Float, Distance from the proton source to the interaction region (FLASH target), in cm
        ap_deg: Float, Beam aperture angle, in degrees
        nprot:  Integer, Number of protons contained in the beam

    Written by Scott Feister 2017-08-03
    """

    # Create the "ProtonBeamsPrint.txt" full filename
    fn = os.path.join(folder, basenm + "ProtonBeamsPrint.txt")

    # Read in file contents to buffer
    with open(fn) as f:
        txraw = f.read()

    # Split the buffer into beam number sections
    p = re.compile(r'PROTON BEAM NR  (\d)') # The file is organized into sections, one for each proton beam. Each section starts with 'PROTON BEAM NR  #', so we search for that to split the file
    txsplit = re.split(p, txraw) # txsplit will be a list of form ['blank', number, 'contents', number, 'contents', number, 'contents']; each number refers to another beam, and its contents follow the number.

    # Extract a buffer section corresponding to desired beam number
    ix = txsplit.index(str(beamnum)) # Find the element of the txsplit list matching the desired beam number
    txbeam = txsplit[ix + 1] # Beam info string for the desired beam number only, which is the element of the txsplit list which comes *after* the number itself

    # Parse this buffer section, re-structuring the line-by-line definitions into a python dictionary
    beamdict = {}
    p2 = re.compile('^\s*(.*?)\s*=\s*(.*?)\s*$', re.MULTILINE)
    matches = p2.findall(txbeam)
    for m in matches:
        beamdict[m[0]] = m[1]

    # Extract four important values from the python dictionary
    Ep_MeV = float(beamdict["Proton energy (in MeV)"]) # Proton energy, in MeV
    s2r_cm = float(beamdict[r"Distance capsule center --> target center"])
    ap_deg = np.around(np.rad2deg(float(beamdict["Beam aperture angle (rad)"])),11) # Cone aperture angle (full-angle), in degrees. Round to 11th decimal place (to avoid rad2deg mismatches; present 1.0 rather than 0.99999999999980005)
    nprot = int(beamdict[r"Number of protons in beam"])


    # Return the dictionary as well as the important values
    return beamdict, Ep_MeV, s2r_cm, ap_deg, nprot

def detParse(folder, basenm, detnum = 1):
    """ Parse the FLASH4 '[basename]ProtonImagingDetectors.txt' file for a given beam/detector number
    Inputs:
        folder: String, Folder path in which '[basename]_ProtonImagingDetectors.txt' can be found
        basenm: String, Basename used in the FLASH4 simulation
        detnum: Integer, Detector number to analyze (1, 2, ..., 8, or 9)
    Outputs:
        detdict: Python dict, containing various information about this detector
        s2d_cm: Float, Distance from the proton source to the detector, in cm
        width_cm: Float, total width of the square detector, in cm

    Written by Scott Feister 2017-08-03
    """

    # Create the "_ProtonImagingDetectors.txt" full filename
    fn = os.path.join(folder, basenm + "ProtonImagingDetectors.txt")

    # Read in file contents to buffer
    with open(fn) as f:
        txraw = f.read()

    # Split the buffer into detector number sections
    p = re.compile(r'PROTON DETECTOR NR  (\d)') # The file is organized into sections, one for each detector. Each section starts with 'PROTON DETECTOR NR  #', so we search for that to split the file
    txsplit = re.split(p, txraw) # txsplit will be a list of form ['blank', number, 'contents', number, 'contents', number, 'contents']; each number refers to another detector, and its contents follow the number.

    # Extract a buffer section corresponding to desired detector number
    ix = txsplit.index(str(detnum)) # Find the element of the txsplit list matching the desired detector number
    txdet = txsplit[ix + 1] # Detector info string for the desired detector number only, which is the element of the txsplit list which comes *after* the number itself

    # Parse this buffer section, re-structuring the line-by-line definitions into a python dictionary
    detdict = {}
    p2 = re.compile('^\s*(.*?)\s*=\s*(.*?)\s*$', re.MULTILINE)
    matches = p2.findall(txdet)
    for m in matches:
        detdict[m[0]] = m[1]

    # Extract two important values from the python dictionary
    s2d_cm = float(detdict["Detector distance from beam capsule center"]) # Distance from capsule center to CR39 center
    width_cm = float(detdict["Detector square side length (cm)"]) # Length of one side of the square CR39 detector, in cm

    # Return the dictionary as well as the important values
    return detdict, s2d_cm, width_cm
