#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
createRad1.py: Creates rad1.csv, the example flux input used in other examples

This script is included just to create a test file to be used in examples 1, 2a, and 2b. See those examples for typical use of PRadReader.

Created by Scott Feister on Mon Nov 20 15:09:05 2017
"""

import numpy as np
np.random.seed(0) # Make the 'random numbers' predictable

if __name__ == "__main__":
    xgv = np.linspace(-2, 2, 500)
    ygv = np.linspace(-2, 2, 501)
    X, Y = np.meshgrid(xgv, ygv)
    
    FluxBase = 200 + 25.12 * X * Y**3 - Y * X**3 # Any function will do fine

    FluxNoise = np.random.normal(scale=10.0, size=FluxBase.shape)
    
    Flux = np.abs(FluxBase + FluxNoise)
    
    np.savetxt('rad1.csv', Flux, fmt='%3.1f')
