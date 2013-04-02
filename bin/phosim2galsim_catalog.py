#! /bin/env python

# 2013-03-12 Chihway Chang
#
# Purpose:
# Convert PhoSim catalog to something easily used by GalSim. This includes
# converting the sky coordinates and magnitudes etc. We use the PhoSim 
# catalogs "after" trimming, that is, each catalog is for a single LSST 
# chip and not the full focal plane. This probably means that we will need 
# part of the PhoSim script to do the trimming before using this one.
#
# Require:
# - magnitude converter: magNorm2LSSTFlux.py
# - position converter: findchipcenter.py
# - input PhoSim trimmed catalog
# - filter files, used by magNorm2LSSTFlux.py
# - SED files (star, galaxy, sky), used by magNorm2LSSTFlux.py
#
# Usage:
#   phosim2galsim_catalog.py [switches] [input catalog] 
#                 [output config file] [output star file] [output galaxy file]
#
#

import os, numpy, sys, logging
import magNorm2LSSTFlux                  # magnitude converter
import findchipcenter                    # find chip center

infilename=sys.argv[1]                   # intput PhoSim catalog
outfilename1=sys.argv[2]                 # output GalSim catalog - config
outfilename2=sys.argv[3]                 # output GalSim catalog - star
outfilename3=sys.argv[4]                 # output GalSim catalog - galaxy

infile=open(infilename,'r')
if os.path.isfile(outfilename):
  os.remove(outfilename)
outfile1=open(outfilename1,'a')         
outfile2=open(outfilename2,'a')
outfile3=open(outfilename3,'a')

inlines=infile.readlines()

# hardcoded! change as needed
pixelscale = 0.2                        # arcsec/pix
chipsizex = 4000                        # x-direction pixels   
sgapx = 225                             # x-direction gap between chips
rgapx = 25                              # x-direction gap between rafts
chipsizey = 4072                        # y-direction pixels
sgapy = 153                             # y-direction gap between chips
rgapy = 178                             # y-direction gap between rafts
optPSFsize = 0.35                       # from SRD (at zenith)
Filt=[ 'u','g','r','i','z','y4' ]
skysed='/nfs/slac/g/ki/ki06/lsst/chihway/phosim-v-3.2/data/sky/darksky_sed.txt'
filtdir='/nfs/slac/g/ki/ki06/lsst/chihway/phosim-v-3.2/data/lsst/'
seddir='/nfs/slac/g/ki/ki06/lsst/chihway/phosim-v-3.2/data/SEDs/'

# useful conversions
deg2pix=60.0*60.0*pixelsize
deg2rad=1.0/180.0*numpy.pi
arcsec2deg=1.0/60.0/60.0

logging.basicConfig(filename='phosim2galsim_catalog.log', filemode='w', level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger('phosim2galsim_catalog') 

logger.info("reading in the observing parameters from "+str(infilename))
logger.info("this may take a while...")

# first pass going through to grab observation parameters
for i in range(len(inlines)): 
  if (len(inlines[i].split())>=2):

    if (inlines[i].split()[0]=='obshistid'):
      string='obshistid '+str(inlines[i].split()[1])+'\n'
      logger.info(string)
      outfile1.write(string)

    if (inlines[i].split()[0]=='altitude'):
      altitude=float(inlines[i].split()[1])
      airmass=1.0/numpy.cos(90.0-altitude)         
      # save parameter for later use
      string='airmass '+str(airmass)+'\n'
      logger.info(string)
      outfile1.write(string)
   
    if (inlines[i].split()[0]=='rotationangle'):
      rotationangle=float(inlines[i].split()[1])
      # save parameter for later use
      string='rotationangle '+str(rotationangle)+'\n'
      logger.info(string)
      outfile1.write(string)

    if (inlines[i].split()[0]=='pointingra'):
      pointingra=float(inlines[i].split()[1])
      # save parameter for later use
      string='pointingra '+str(pointingra)+'\n'
      logger.info(string)
      outfile1.write(string)

    if (inlines[i].split()[0]=='pointingdec'):
      pointingdec=float(inlines[i].split()[1])
      # save parameter for later use
      string='pointingdec '+str(pointingdec)+'\n'
      logger.info(string)
      outfile1.write(string)

    if (inlines[i].split()[0]=='obsseed'):
      string='obsseed '+str(inlines[i].split()[1])+'\n'
      logger.info(string)
      outfile1.write(string)

    if (inlines[i].split()[0]=='filter'):
      filt=int(inlines[i].split()[1])
      # save parameter for later use
      string='filter '+str(filt)+'\n'
      logger.info(string)
      outfile1.write(string)

    if (inlines[i].split()[0]=='totalseeing'):
      atmseeing=float(inlines[i].split()[1])
      # save parameter for later use
      string='atmseeing '+str(atmseeing)+'\n'
      logger.info(string)
      outfile1.write(string)
  
    if (inlines[i].split()[0]=='zenith_v'):
      zenith_v=float(inlines[i].split()[1])
      # save parameter for later use
  
    if (inlines[i].split()[0]=='chipid'):
      rx=str(inlines[i].split()[1])[1]
      ry=str(inlines[i].split()[1])[2]
      sx=str(inlines[i].split()[1])[5]
      sy=str(inlines[i].split()[1])[6]
      # save parameter for later use
  
sky_count = magNorm2LSSTFlux.magNorm2LSSTFlux(str(skysed), str(filtdir)+'total_'+str(Filt[filt])+'.dat', zenith_v, 0.0) * pixelscale**2                 
# counts per pixels (the counts look low... need checking!)
string='sky_count '+str(sky_count)+'\n'
logger.info(string)
outfile1.write(string)

string='optseeing '+str(optPSFseeing)+'\n'
logger.info(string)
outfile1.write(string)

string='pixelsize '+str(pixelscale)+'\n'
logger.info(string)
outfile1.write(string)

string='chipsizex '+str(chipsizex)+'\n'
logger.info(string)
outfile1.write(string)

string='chipsizey '+str(chipsizey)+'\n'
logger.info(string)
outfile1.write(string)

string='sgapx '+str(sgapx)+'\n'
logger.info(string)
outfile1.write(string)

string='sgapy '+str(sgapy)+'\n'
logger.info(string)
outfile1.write(string)

string='rgapx '+str(rgapx)+'\n'
logger.info(string)
outfile1.write(string)

string='rgapy '+str(rgapy)+'\n'
logger.info(string)
outfile1.write(string)

logger.info("Figure out the center coordinate for this chip 
                 (flat sky approximation! can be off at edge of field).")

dxchip = (chipsizex+sgapx)*pixelscale*arcsec2deg
dychip = (chipsizey+sgapy)*pixelscale*arcsec2deg
dxraft = (rgapx)*pixelscale*arcsec2deg
dyraft = (rgapy)*pixelscale*arcsec2deg
center=findchipcenter(pointingra, pointingdec, rotationangle, 
                      rx, ry, sx, sy, dxchip, dychip, dxraft, dyraft)
chipcenterx=center[0]                          
chipcentery=center[1]

logger.info("Finish reading observing parameters.")
outfile1.close()

logger.info("Now get parameters from stars and galaxies...")
# second pass going through to grab object parameters
for i in range(len(inlines)):
  if (len(inlines[i].split())>=2):
    outfile2=open(outfilename2,'a')
    outfile3=open(outfilename3,'a')

    if (inlines[i].split()[0]=='object'):
      phosim_id=float(inlines[i].split()[1])
      phosim_ra=float(inlines[i].split()[2])
      phosim_dec=float(inlines[i].split()[3])
      phosim_mag=float(inlines[i].split()[4])
      phosim_sed=inlines[i].split()[5]
      phosim_z=float(inlines[i].split()[6])
      phosim_kappa=float(inlines[i].split()[7])
      phosim_gamma1=float(inlines[i].split()[8])
      phosim_gamma2=float(inlines[i].split()[9])

      # add rotation (positions and shearing)!!
      logger.info("Rotate and shift position so that image is centerd with chip.")
      galsim_x_norot=(phosim_ra-centerx)*deg2pix+(chipsize/2)
      galsim_y_norot=(phosim_dec-centery)*deg2pix+(chipsize/2)
      galsim_x=galsim_x_norot*numpy.cos(rotationangle*deg2rad)
              +galsim_y_norot*numpy.sin(rotationangle*deg2rad)
      galsim_y=-1*galsim_x_norot*numpy.sin(rotationangle*deg2rad)
                 +galsim_y_norot*numpy.cos(rotationangle*deg2rad)
      #print galsim_x, galsim_y
        
      if (galsim_x>=0 and galsim_x<=chipsizex and galsim_y>=0 and galsim_y<=chipsizey):
        os.system('gunzip '+str(seddir)+str(phosim_sed))
        galsim_flux=magNorm2LSSTFlux.magNorm2LSSTFlux(str(seddir)
                   +str(phosim_sed)[:-3], str(filtdir)+'total_'+str(Filt[filt])+'.dat'
                   , phosim_mag, phosim_z) * pixelscale**2   
        os.system('gzip '+str(seddir)+str(phosim_sed)[:-3])

        # shear is defined in telescope coordinate, so this needs to be rotated as well
        logger.info("Rotate shear as well.")
        galsim_kappa=phosim_kappa
        galsim_gamma1=numpy.real((phosim_gamma1+1j*phosim_gamma2)
                      *numpy.exp(-2j*rotationangle*deg2rad))
        galsim_gamma2=numpy.imag((phosim_gamma1+1j*phosim_gamma2)
                      *numpy.exp(-2j*rotationangle*deg2rad))

        if ( str(inlines[i].split()[12]) == 'sersic2D' and galsim_flux>1):
          phosim_z=
          phosim_a=float(inlines[i].split()[13])
          phosim_b=float(inlines[i].split()[14])
          phosim_theta=float(inlines[i].split()[15])
          phosim_n=float(inlines[i].split()[16])
          string=str(phosim_id)+'\t'+'Sersic'+'\t'+str(galsim_x)+'\t'+str(galsim_y)
                +'\t'+str(galsim_flux)+'\t'+str(phosim_a)+'\t'+str(phosim_b)
                +'\t'+str(phosim_theta)+'\t'+str(phosim_n)+'\t'+str(galsim_kappa)
                +'\t'+str(galsim_gamma1)+'\t'+str(galsim_gamma2)+'\n'
          #print string
          outfile2.write(string)
   
        if ( str(inlines[i].split()[12]) == 'point' and galsim_flux>1):
          string=str(phosim_id)+'\t'+'Star'+'\t'+str(galsim_x)+'\t'+str(galsim_y)
                +'\t'+str(galsim_flux)+'\n'
          #print string
          outfile3.write(string)
 
    outfile2.close()
    outfile3.close()
