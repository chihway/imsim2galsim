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
# Note:
# Super bright stars currently do not make sensible images. I think it's 
# fine to leave it as is, but the effect of the bright star is conservative 
# in this way. (no bleeding, no halo)

import sys, os, math, numpy, logging, time, galsim
import read_config
import add_LSST_DM_header

logging.basicConfig(format="%(message)s", level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger()

logger.info('Define all file names')
configfilename=sys.argv[1]      # configuration file
starfilename=sys.argv[2]        # star catalog
galfilename=sys.argv[3]         # galaxy catalog
tempoutfilename=sys.argv[4]     # output file without header
outfilename=sys.argv[5]         # output file with header
photon=int(sys.argv[6])         # whether to use photon-shotting mode

if os.path.isfile(outfilename):
  os.remove(outfilename)
if os.path.isfile(tempoutfilename):
  os.remove(tempoutfilename)

logger.info('Configuration file: '+str(configfilename))
logger.info('Star catalog file: '+str(starfilename))
logger.info('Galaxy catalog file: '+str(galfilename))
logger.info('Output file: '+str(outfilename))

logger.info('Get observation and instrument-specific parameters from the config file...')
Id, Airmass, Rot, Ra, Dec, Seed, Filter, Atmseeing, Sky, Rx, Ry, Sx, Sy, Saturation, Chipsizex, Chipsizey, Pixelsize, Optpsfsize, Exptime = read_config.read_config(configfilename)

logger.info('Defining image...')
full_image = galsim.ImageF(Chipsizex, Chipsizey)
full_image.setScale(Pixelsize)
im_center = full_image.bounds.center()
im_center = galsim.PositionD(im_center.x, im_center.y)

logger.info('Make the PSF: Kolmogorov atmosphere + Moffat optics')
atm_psf = galsim.Kolmogorov(fwhm = Atmseeing*Airmass**0.6) # arcsec
Optpsfsize=Optpsfsize*Airmass**0.6                         # arcsec
Optpsfbeta = 3                                             # what is this?
Optpsftrunc = 3.*Optpsfsize                                # arcsec 
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
  z=float(parameters[4])
  galFlux=int(float(parameters[5])*25)
  galA=float(parameters[6])
  galB=float(parameters[7])
  galPhi=float(parameters[8])+numpy.pi/2
  # this will change in the next phosim version!!
  galN=float(parameters[9])
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
    stamp = final.draw(wmult=5, dx=Pixelsize)
  if (photon==1):
    stamp=final.drawShoot(wmult=5, n_photons=galFlux, dx=Pixelsize)

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
    stamp = final.draw(wmult=5, dx=Pixelsize)
  if (photon==1):
    stamp=final.drawShoot(wmult=5, n_photons=star, dx=Pixelsize)
  
  # Recenter the stamp at the desired position:
  stamp.setCenter(ix,iy)
  # Find overlapping bounds
  bounds = stamp.bounds & full_image.bounds
  full_image[bounds] += stamp[bounds]

logger.info('Add sky background noise')
rng = galsim.UniformDeviate(Seed) # Initialize the random number generator 
full_image.addNoise(galsim.PoissonNoise(rng, sky_level=Sky))

logger.info('Now Write the file to disk')
full_image.write(tempoutfilename)

logger.info('Re-open the fits files to append the appropriate headers')
add_LSST_DM_header.add_header(tempoutfilename, configfilename, outfilename)
