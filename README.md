
DISCLAIMER
============
This repo is work in progress. Please check with me (chihway54@gmail.com) 
first if you plan to use it for anything. 


imsim2galsim
============

Code to generate GalSim images that fit in the LSST simulation framework. 
This includes two projects:

1. Taking LSST ImSim input catalogs and generate approximately similar images.

2. Running these GalSim images through LSST DM. 

The ultimate goal is to compare the output catalogs of GalSim and ImSim. If 
they look sufficiently close, we can use the GalSim line to do analyses. In 
principle this would save time...

These simulations will be faster but with lower fidelity. Depending on the 
purpose, one can choose from using the original ImSim framework or digress 
to using the GalSim framework here. Each LSST chips takes <1 minute to 
generate the intermediate catalog and 10 minutes to make the image. Further 
optimization is highly possible.

============================================================
What is in this repo
============================================================

bin/  ==> python scripts that do the work
- phosim2galsim_catalog.py   (make intermediate catalog)
- phosim2galsim_catalog2.py  (make intermediate catalog, with pre-calculated
                              magnitude conversion)
- phosim2galsim_image.py     (make final GalSim image)
- read_config.py             (used by phosim2galsim_image)
- add_LSST_DM_header.py      (used by phosim2galsim_image)
- phosim_trimcat             (make chip-size imsim catalogs)
- run_phosim_mag2flux.sh     (wrapper script for phosim_mag2flux)
- phosim_mag2flux.py         (look through redshift and filter)
- magNorm2LSSTFlux.py        (convert mag to flux)

input/  ==> the imsim input catalogs and lookup table for mag conversion
- raytrace_XXX
- mag2flux.tar.gz

example/  ==> demo of how these things run, instructions in README
- README
- rotation_0.tar.gz

NB1: Recommend generate work/ directory to run things and put intermediate 
files. This is the default assumption for all instructions.

NB2: The full framework starts of the trimmed, single-chip imsim catalogs.
See below 'Pre-requisite/ImSim' for how these can be generated from scratch.

============================================================
Pre-requisite
============================================================

* GalSim (https://github.com/GalSim-developers/GalSim)
See github site for all the details about installation etc.

* ImSim (https://dev.lsstcorp.org/cgit/LSST/sims/phosim.git/)
Only really the beginning part of the simulation code is needed for the 
purpose of this project (unless you want to make imsim images yourself), 
but you should install the full ImSim since everything seems to be sort 
of integrated...

If you also download all the SEDs, you can run the magnitude conversion 
code yourself. Otherwise use the conversion provided in input/mag2flux/

Once you have ImSim set up. You can run:

cd YourImsimInstallation/work
../phosim TheCatalogYouWantToRun

This will produce a bunch of images and at the same time kill all the 
intermediate files, which is kind of a shame...

Alternatively, you can use the scripts in 'phosim_trimcat' in the bin/ 
directory instead of 'phosim' to generate the trimmed catalogs (with file 
name 'raytrace_XXXX') that will become the input to the main scripts in 
this project.

* LSST DM (https://dev.lsstcorp.org/trac/wiki/Installing/Winter2013#StepbystepinstructionsforLinux)
Here's a useful instruction for how to install it at SLAC:
http://kipac.stanford.edu/collab/research/lensing/slac/HowTo/imsimDMpipeline
But note that this can be extremely difficult if you are doing it elsewhere. 

NB: check inside scripts to swap out where all these codes are located.

============================================================
How to run
============================================================

1. Trim the PhoSim instant catalog into chip-size images.

2. Transform a PhoSim trimmed catalog into something GalSim understands
   phosim2galsim_catalog.py [ input ImSim catalog ] [ output config file ] [ output glaxy catalog ] [ output star catalog ]

3. Generate GalSim image with the catalog from 2. 
   phosim2galsim_image.py [ input config file ] [ input star file ] [ input galaxy file ] [ output temp fits file ] [ output final fits file ] [ whether to use approximate magnitude conversion ] [ whether to use photon shooting ]

(with photon-shooting=1, the speed of the image generation will scale with the number of photons)

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
