#! /bin/env python

# 2013-04-03 Chihway Chang
#
# Purpose:
# Add header to GalSim images, according to a configuration file.
# Currently is somewhat LSST specific, but of course can be generalized.
#
    
def add_header(fitsfile, configfile, outfile):
  import pyfits, numpy
  import read_config
  Filt=[ 'u','g','r','i','z','y4' ]
  deg2rad=1.0/180*numpy.pi

  image=pyfits.open(fitsfile)
  Id, Airmass, Rot, Ra, Dec, Seed, Filter, Atmseeing, Sky, Rx, Ry, Sx, Sy, Saturation, Chipsizex, Chipsizey, Pixelsize, Optpsfsize, Exptime = read_config.read_config(configfile)
  hdr=image[0].header
  hdr.update('CTYPE1', 'RA---TAN')
  hdr.update('CRPIX1', int(Chipsizex/2))
  hdr.update('CRVAL1', Ra)
  hdr.update('CTYPE2', 'DEC---TAN')
  hdr.update('CRPIX2', int(Chipsizey/2))
  hdr.update('CRVAL2', Dec)
  hdr.update('CD1_1', 5.555553E-05)         # need fix
  hdr.update('CD1_2', -0.)                  # need fix
  hdr.update('CD2_1', 0.)                   # need fix
  hdr.update('CD2_2', 5.555553E-05)         # need fix
  hdr.update('RADESYS', 'ICRS')
  hdr.update('EQUINOX', 2000.)
  hdr.update('EPOCH', 2000.)
  hdr.update('EXPTIME', Exptime)
  hdr.update('DARKTIME', Exptime)     # 'actual' exposure time?
  hdr.update('FILTNM', Filter)
  hdr.update('FILTER', Filt[Filter])
  hdr.update('PRA', Ra*deg2rad)
  hdr.update('PDEC', Dec*deg2rad)
  hdr.update('RA_DEG', Ra)             # is this duplicate?
  hdr.update('DEC_DEG', Dec)           # is this duplicate?

  # others considering GalSim generation and bookeeping

  image[0].header=hdr 
  image.writeto(outfile) 
  image.close()
