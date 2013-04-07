imsim2galsim
============

Code to generate GalSim images that fit in the LSST simulation framework. 
This includes two projects:

1. Taking LSST PhoSim input gatalogs and generate approximately similar images.
 - Not sure how useful this is. You get the images faster than PhoSim, but much less accurate.
 - The one good thing is it shold be easy to put through DM.

2. Query from LSST ImSim databse and generate expected images. 
 - This has the advantage that the magnitudes are more accurate and does not need to go through the many intermediate steps. 
 - But this involves the database and (possibly) the galaxy generation code. Need to investigate if it's worth the trouble.

Both of these should be tested and can run through the LSST Data Management code.

This provides one (or probably two) parallel stream of simulation that can be done faster but with lower fidelity. Depending on the purpose of these simulations, one 
can choose from using the original ImSim/PhoSim framework or digress to using the GalSim framework here.

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

There are several ways to go from here.

------------------------------------------------------------
* I just want to generate some image that has roughly the LSST sky 
properties and is compatable with DM.


------------------------------------------------------------
* I am familiar with PhoSim and have the PhoSim instant catalogs handy.

1. Trim the PhoSim instant catalog into chip-size images.

2. Transform a PhoSim trimmed catalog into something GalSim understands
   phosim2galsim_catalog.py [] []

3. Generate GalSim image with the catalog from 2. 
   phosim2galsim_image.py [] []

------------------------------------------------------------
* I have the ImSim database setup and want to go from there.


=====================================================
What should be in a configuration file?
=====================================================

A configuration file should look like this (without 
the comments after '#'):
 
Id             9999     # id for that exposure      
Airmass        1.0      # airmass                   
Rot            0        # rotation angle (deg) of camer
Ra             0        # RA pointing
Dec            0        # DEC pointing
Seed           9999     # seed for noise
Filter         2        # filter id (ugrizy)
Atmseeing      0.6      # atmospheric seeing (") at zenith
Sky            0        # sky counts per pixel
Rx             2        # raft x-coordinate
Ry             2        # raft y-coordinate
Sx             1        # sensor x-coordinate
Sy             1        # sensor y-coordinate 
Saturation     1000000  # full well (e)
Chipsizex      4072     # x-direction pixels
Chipsizey      4072     # y-direction pixels
Pixelsize      0.2      # arcsec/pixel
Optpsfsize     0.35     # optical PSF FWHM (") at zenith

NB: default values (as listed) will be filled in if not provided in the config file
