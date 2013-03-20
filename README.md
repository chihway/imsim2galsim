imsim2galsim
============

Code to generate GalSim images that fit in the LSST simulation framework. 
This includes:
1. Can use the LSST ImSim catalogs as input to generate semi-similar images.
2. Contains the correct headers so that the LSST Data Management code can process it.

This provides a parallel stream of simulation that can be done faster but with lower 
fidelity. Depending on the purpose of these simulations, one can choose from using the 
original ImSim/PhoSim framework or digress to using the GalSim framework here.

============================================================
What is in this repo
============================================================

bin/ python scripts that do the work
- phosim2galsim_catalog.py
- phosim2galsim_image.py

data/ input catalogs (from PhoSim)
- raytrace

docs/ 

============================================================
Pre-requisite
============================================================

GalSim, ImSim, and DM stack are all installed
use setup script to locate all of these

============================================================
How to run
============================================================

1. Transform a PhoSim trimmed catalog into something GalSim understands
   phosim2galsim_catalog.py [] []
   

2. Generate GalSim image with the catalog from 1. 
   One has the option of generating images with or without sky, with or 
   without photon noise, with or without shear, etc.
 
   phosim2galsim_image.py [] []




