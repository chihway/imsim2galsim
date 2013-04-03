#! /bin/env python

# Purpose:
# Take the output catalog from phosim2carsim_catalog.py and paint 
# galaxies in GalSim. This process includes:
# - define image
# - define PSF
# - define pixel
# - put down star in stamps
# - put down galaxy in stamps
# - write everything into the image
#
# Usage:
#    phosim2galsim_image.py [config file] [star file] 
#                    [galaxy file] [output file] [photon-shooting mode]
#
# Required:
# - configuration file and/or defult_config
# - star catalog
# - galaxy catalog
#

import sys, os, math, numpy, logging, time, galsim

logging.basicConfig(format="%(message)s", level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger()

logger.info('Define all file names')
configfilename=sys.argv[1]      # configuration file
starfilename=sys.argv[2]        # star catalog
galfilename=sys.argv[3]         # galaxy catalog
outfilename=sys.argv[4]         # output file
photon=int(sys.argv[5])         # whether to use photon-shotting mode

if os.path.isfile(outfilename):
  os.remove(outfilename)
logger.info('Configuration file: '+str(configfilename))
logger.info('Star catalog file: '+str(starfilename))
logger.info('Galaxy catalog file: '+str(galfilename))
logger.info('Output file: '+str(outfilename))

logger.info('Get observation and instrument-specific parameters from the config file...')
configfile=open(configfilename,'r')
configlines=configfile.readlines()
configfile.close()
for i in range(len(configlines)):
  parameter=configlines[i].split()
  if (parameter[0]=='id'):
    Id=int(parameter[1]) 
  if (parameter[0]=='airmass'):
    Airmass=float(parameter[1]) 
  if (parameter[0]=='rotationangle'):
    Rot=float(parameter[1]) 
  if (parameter[0]=='pointingra'):
    Ra=float(parameter[1]) 
  if (parameter[0]=='pointingdec'):
    Dec=float(parameter[1]) 
  if (parameter[0]=='obsseed'):
    Seed=int(parameter[1]) 
  if (parameter[0]=='filter'):
    Filter=int(parameter[1]) 
  if (parameter[0]=='atmseeing'):
    Atmseeing=float(parameter[1]) 
  if (parameter[0]=='sky_count'):
    Sky=int(float(parameter[1])) 
  if (parameter[0]=='chipsize'):
    Chipsize=int(parameter[1]) 
  if (parameter[0]=='pixelsize'):
    Pixelsize=float(parameter[1])
  if (parameter[0]=='optpsfsize'):
    Optpsfsize=float(parameter[1])

logger.info('Defining image...')
full_image = galsim.ImageF(Chipsize, Chipsize)
full_image.setScale(Pixelsize)
im_center = full_image.bounds.center()
im_center = galsim.PositionD(im_center.x, im_center.y)

logger.info('Make the PSF: Kolmogorov atmosphere + Moffat optics')
atm_psf = galsim.Kolmogorov(fwhm = Atmseeing) # airmass-corrected
Optpsfsize=Optpsfsize*Airmass**0.6            # arcsec
Optpsfbeta = 3                                # what is this?
Optpsftrunc = 3.*Optpsfsize                   # arcsec 
opt_psf=galsim.Moffat(beta=Optpsfbeta, fwhm=Optpsfsize, trunc=Optpsftrunc)

logger.info('Make the pixels')
pix = galsim.Pixel(Pixelsize)

logger.info('Convolve PSF and pixel')
if (photon == 0):
  psf=galsim.Convolve([atm_psf, opt_psf, pix])
if (photon == 1):
  psf=galsim.Convolve([atm_psf, opt_psf])

logger.info('Now start putting down galaxies...')
galfile=open(galfilename,'r')
gallines=galfile.readlines()
galfile.close()
for k in range(len(gallines)):
  # individual galaxy component parameters
  parameters=gallines[k].split()

  # calculate the parameters
  x=float(parameters[2])
  y=float(parameters[3])
  galFlux=int(float(parameters[4])*25)
  galA=float(parameters[5])
  galB=float(parameters[6])
  galPhi=float(parameters[7])+numpy.pi/2
  galN=float(parameters[8])
  re=(galA*galB)**0.5
  gale=(galA**2-galB**2)/(galA**2+galB**2)

  # Make the galaxy profile with these values:
  gal = galsim.Sersic(half_light_radius=re, flux=galFlux, n=galN)
  gal.applyShear(e=gale, beta=galPhi*galsim.radians)

  # Get the integer values of these which will be the center of the 
  # postage stamp image.
  ix = int(math.floor(x+0.5))
  iy = int(math.floor(y+0.5))
  # The remainder will be accounted for in a shift
  dx = x - ix
  dy = y - iy
  # Build the final object
  final = galsim.Convolve([psf, gal])
  # Account for the non-integral portion of the position
  final.applyShift(dx*Pixelsize,dy*Pixelsize)

  # Draw the stamp image
  if (photon==0):
    stamp = final.draw(dx=Pixelsize)
  if (photon==1):
    stamp=final.drawShoot(n_photons=galFlux, dx=Pixelsize)[0]

  # Recenter the stamp at the desired position:
  stamp.setCenter(ix,iy)
  # Find overlapping bounds
  bounds = stamp.bounds & full_image.bounds
  full_image[bounds] += stamp[bounds]

logger.info('Next put down stars...')
starfile=open(starfilename,'r')
starlines=starfile.readlines()
starfile.close()
for k in range(len(starlines)):
  # individual galaxy component parameters
  parameters=starlines[k].split()

  # calculate the parameters
  x=float(parameters[2])
  y=float(parameters[3])
  starFlux=int(float(parameters[4])*25)

  # Make the galaxy profile with these values:
  star = starFlux 

  # Get the integer values of these which will be the center of the 
  # postage stamp image.
  ix = int(math.floor(x+0.5))
  iy = int(math.floor(y+0.5))
  # The remainder will be accounted for in a shift
  dx = x - ix
  dy = y - iy
  # Build the final object
  final = psf*star
  # Account for the non-integral portion of the position
  final.applyShift(dx*Pixelsize,dy*Pixelsize)

  # Draw the stamp image
  if (photon==0):
    stamp = final.draw(dx=Pixelsize)
  if (photon==1):
    stamp=final.drawShoot(n_photons=star, dx=Pixelsize)[0]
  
  # Recenter the stamp at the desired position:
  stamp.setCenter(ix,iy)
  # Find overlapping bounds
  bounds = stamp.bounds & full_image.bounds
  full_image[bounds] += stamp[bounds]

logger.info('Add sky background noise')
rng = galsim.UniformDeviate(Seed) # Initialize the random number generator 
full_image.addNoise(galsim.PoissonNoise(rng, sky_level=Sky))

logger.info('Now Write the file to disk')
full_image.write(outfilename)

