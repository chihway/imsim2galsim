
# 2013-06-24 Chihway Chang
#
# Purpose:
# Create giant lookup table to convert the magnitude to flux using the
# ImSim SEDs and LSST filters. (need to check whether all filters are 
# implimented correctly?) This giant lookup table will be used later 
# to facilitate GalSim simulations. All objects are specified at 20 mag.
# 
# Output: 
# File names are the same as that of the SED name and in each file there 
# are 3 columns (filter, redshift, # photons). For stars all redshift=0.
# We consider (for galaxies) from redshift 0 to 5 (?) with intervals of 
# 0.1, that gives 50 redshift bins times 6 filters. 
#
#                                # of spectrums     # of calculations
# input/flatSED/                 ?                  ?
#       galaxySED/               960                288000
#       ssmSED/                  26                 26
#       starSED/gizis_SED/       21                 21
#               kurucz/          103987             103987
#               mlt/             739                739
#               wDs/             3378               3378
#

import numpy, os, sys
import magNorm2LSSTFlux

SEDdir=
lookupdir=

# galaxy

SEDfiles = [ f for f in listdir(SEDdir+'/galaxySED')]
for sedid in range(len(SEDfiles)):
  outfilename=
  outfile=open()
  for filt in range(6):
    for zbin in range(50):
    
# ssm

SEDfiles = [ f for f in listdir(SEDdir+'/ssmSED')]
for sedid in range(len(SEDfiles)):
  outfilename=
  outfile=open()
  for filt in range(6):

# stars

starSEDclass=['gizis_SED','kurucz','mlt','wDs']
for starclassid in range(4):
  SEDfiles = [ f for f in listdir(SEDdir+'/starSED/'+starSEDclass[starclassid])]
  for sedid in range(len(SEDfiles)):
    outfilename=
    outfile=open()
    for filt in range(6):
