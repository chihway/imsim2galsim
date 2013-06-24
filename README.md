
imsim2galsim
============

Code to generate GalSim images that fit in the LSST simulation framework. 
This includes two projects:

1. Taking LSST PhoSim input catalogs and generate approximately similar images.

2. Running these GalSim images through LSST DM. 

The ultimate goal is to compare the output catalogs of GalSim and PhoSim. If 
they look sufficiently close, we can use the GalSim line to do analyses. In 
principle this would save time...

These simulations will be faster but with lower fidelity. Depending on the purpose, 
one can choose from using the original ImSim/PhoSim framework or digress to using 
the GalSim framework here.

============================================================
What is in this repo
============================================================

bin/  ==> python scripts that do the work
- phosim2galsim_catalog.py
- phosim2galsim_image.py
- read_config.py
- add_LSST_DM_header.py
- magNorm2LSSTFlux.py

input/  ==> the phosim input catalogs and lookup table for mag conversion
- raytrace_XXX
- mag2flux_star.dat
- mag2flux_gal.dat

example/  ==> demo of how these things run, instructions in README

NB1: Recommend generate work/ directory to run things and intermediate files.

NB2: The full framework starts of the trimmed, single-chip phosim catalogs.
See below 'Pre-requisite/phosim' for how these can be generated from scratch.

============================================================
Pre-requisite
============================================================

* GalSim

* PhoSim



Install and setup:
- GalSim

Will be useful to have:
- ImSim
- DM stack 

Setup script in principle locates all of these before running.

============================================================
How to run
============================================================

There are several ways to go from here.

------------------------------------------------------------
* I just want to generate some image that has roughly the LSST sky 
properties and is compatable with DM.

1. Sample the galaxy population and generate a catalog

2. Generate GalSim images with catalog from 1.


------------------------------------------------------------
* I am familiar with PhoSim and have the PhoSim instant catalogs handy.

1. Trim the PhoSim instant catalog into chip-size images.

2. Transform a PhoSim trimmed catalog into something GalSim understands
   phosim2galsim_catalog.py [ input ImSim catalog ] [ output config file ] [ output glaxy catalog ] [ output star catalog ]

3. Generate GalSim image with the catalog from 2. 
   phosim2galsim_image.py [ input config file ] [ input star file ] [ input galaxy file ] [ output temp fits file ] [ output final fits file ] [ whether to use approximate magnitude conversion ] [ whether to use photon shooting ]

------------------------------------------------------------
* I have the ImSim database setup and want to go from there.

1. Query some patch of sky ~ LSST fov

2. Select some observing parameters

3. Make chip-size images (or full-field image?)



=====================================================
What should be in a configuration file?
=====================================================

A configuration file should look like this (without the comments after '#'):
 
Id             9999     # id for that exposure      

Airmass        1.0      # airmass                   

Rot            0        # rotation angle (deg) of camera

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
