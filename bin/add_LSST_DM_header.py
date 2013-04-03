#! /bin/env python

# 2013-04-03 Chihway Chang
#
# Purpose:
# Add header to GalSim images, according to a configuration file.
# Currently is somewhat LSST specific, but of course can be generalized.

def add_LSST_DM_header(fitsfile, configfile):
  import pyfits, numpy, os, sys
  image=pyfits.open(fitefile)
