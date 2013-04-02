#! /bin/env python

# Purpose:
#
# Take the output catalog from phosim2carsim_catalog.py and paint galaxies 
# one-by-one in GalSim. Standard procedure as follows:
# - define image
# - define PSF
# - define pixel
# - put down star and shift
# - put down galaxy and shift
# - choose to do photon shooting or not?

import sys, os, math, numpy, logging, time, galsim

def main(argv):
    """
    Make an image from a phosim-converted catalog.
    """
    logging.basicConfig(format="%(message)s", level=logging.INFO, stream=sys.stdout)
    logger = logging.getLogger("phosim2galsim_test1")

    configfilename='data/config'   # configuration file
    starfilename='data/star'       # star catalog
    galfilename='data/gal'         # galaxy catalog
    outfilename='output3.fits'
    if os.path.isfile(outfilename):
      os.remove(outfilename)

    # Get observation and instrument-specific parameters from the 
    # config file. We are using LSST here.

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

    logger.info('Starting...')

    full_image = galsim.ImageF(Chipsize, Chipsize)
    full_image.setScale(Pixelsize)
    im_center = full_image.bounds.center()
    im_center = galsim.PositionD(im_center.x, im_center.y)

    # Make the PSF profile:
    atm_psf = galsim.Kolmogorov(fwhm = Atmseeing)
    Optpsfsize=Optpsfsize*Airmass**0.6            # arcsec
    Optpsfbeta = 3                    
    Optpsftrunc = 10.*Optpsfsize                   # arcsec 
    opt_psf=galsim.Moffat(beta=Optpsfbeta, fwhm=Optpsfsize, trunc=Optpsftrunc)

    # Make the pixel:
    #pix = galsim.Pixel(Pixelsize)
    pix=1    # photon-shooting   

    #psf=galsim.Convolve([atm_psf, opt_psf, pix])
    psf=galsim.Convolve([atm_psf, opt_psf])

    galfile=open(galfilename,'r')
    gallines=galfile.readlines()
    galfile.close()
    for k in range(len(gallines)):
    #for k in range(1000):
      #print k 
      # individual galaxy component parameters
      parameters=gallines[k].split()
      # Initialize the random number generator we will be using for this object:
      rng = galsim.UniformDeviate(Seed)

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
      # ee1=float((numpy.real(gale*numpy.exp(-1j*galPhi))))
      # ee2=float(numpy.imag(gale*numpy.exp(-1j*galPhi)))
      # is the angle the right one we want?

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

      # Now apply the appropriate lensing effects for this position from 
      # the NFW halo mass.
      pos = galsim.PositionD(x,y) * Pixelsize

      # Build the final object
      final = galsim.Convolve([psf, gal])

      # Account for the non-integral portion of the position
      final.applyShift(dx*Pixelsize,dy*Pixelsize)

      # Draw the stamp image
      # stamp = final.draw(dx=Pixelsize)
      stamp=final.drawShoot(n_photons=galFlux, dx=Pixelsize)[0]

      # Recenter the stamp at the desired position:
      stamp.setCenter(ix,iy)

      # Find overlapping bounds
      bounds = stamp.bounds & full_image.bounds
      #print stamp.bounds, full_image.bounds, bounds
      full_image[bounds] += stamp[bounds]

      # move to bottom later!
      #rng = galsim.BaseDeviate(Seed)
      #full_image.addNoise(galsim.PoissonNoise(rng,sky_level=sky_level_pixel))

    starfile=open(starfilename,'r')
    starlines=starfile.readlines()
    starfile.close()
    for k in range(len(starlines)):
    #for k in range(50):
      #print k 
      # individual galaxy component parameters
      parameters=starlines[k].split()
      # Initialize the random number generator we will be using for this object:
      rng = galsim.UniformDeviate(Seed)

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

      # Now apply the appropriate lensing effects for this position from 
      # the NFW halo mass.
      pos = galsim.PositionD(x,y) * Pixelsize

      # Build the final object
      final = psf*star

      # Account for the non-integral portion of the position
      final.applyShift(dx*Pixelsize,dy*Pixelsize)

      # Draw the stamp image
      stamp=final.drawShoot(n_photons=star, dx=Pixelsize)[0]
      #stamp = final.draw(dx=Pixelsize)

      # Recenter the stamp at the desired position:
      stamp.setCenter(ix,iy)

      # Find overlapping bounds
      bounds = stamp.bounds & full_image.bounds
      #print stamp.bounds, full_image.bounds, bounds
      full_image[bounds] += stamp[bounds]

    # add sky background noise (does this add noise to the source too?)
    #full_image.addNoise(galsim.PoissonNoise(rng, sky_level=Sky))

    # Write the file to disk:
    full_image.write(outfilename)

if __name__ == "__main__":
    main(sys.argv)
