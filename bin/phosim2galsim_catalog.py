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
# - input PhoSim trimmed catalog
# - filter files, used by magNorm2LSSTFlux.py
# - SED files (star, galaxy, sky), used by magNorm2LSSTFlux.py
#
# Usage:
#   phosim2galsim_catalog.py [switches] [input catalog] 
#          [output config file] [output galaxy file] [output star file]
#
# Note: 
# This runs a while, mainly due to the magnitude conversion involves 
# integration of each galaxy SED...
#

import os, numpy, sys, logging
import magNorm2LSSTFlux                  # magnitude converter

def findchipcenter(ra, dec, rot, rx, ry, sx, sy, 
                                 dxchip, dychip, dxgap, dygap):
  "Find RA/DEC of the center of chip in degrees in a mosaic camera \
   after rotation"
  x_c=(rx*3+sx-7)*dxchip+(rx-2)*dxgap  # x(deg) from center of camera
  y_c=(ry*3+sy-7)*dychip+(ry-2)*dygap  # y(deg) from center of camera
  centerx=ra+x_c*numpy.cos(rot*deg2rad)+y_c*numpy.sin(rot*deg2rad)
  centery=dec+(-1)*x_c*numpy.sin(rot*deg2rad)+y_c*numpy.cos(rot*deg2rad)  
  return (centerx, centery)

def rotate(x,y,theta):
  " rotate a vector"
  x_rot=x*numpy.cos(theta)+y*numpy.sin(theta)
  y_rot=-1*x*numpy.sin(theta)+y*numpy.cos(theta)
  return (x_rot, y_rot)

def rotateshear(x,y,theta):
  "rotate a spinor" 
  x_rot=numpy.real((x+1j*y)*numpy.exp(-2j*theta))
  y_rot=numpy.imag((x+1j*y)*numpy.exp(-2j*theta))
  return (x_rot, y_rot)

infilename=sys.argv[1]                   # intput PhoSim catalog
outfilename1=sys.argv[2]                 # output GalSim catalog - config
outfilename2=sys.argv[3]                 # output GalSim catalog - galaxy
outfilename3=sys.argv[4]                 # output GalSim catalog - star

infile=open(infilename,'r')
if os.path.isfile(outfilename1):
  os.remove(outfilename1)
if os.path.isfile(outfilename2):
  os.remove(outfilename2)
if os.path.isfile(outfilename3):
  os.remove(outfilename3)
outfile1=open(outfilename1,'a')         
outfile2=open(outfilename2,'a')
outfile3=open(outfilename3,'a')
inlines=infile.readlines()

# hardcoded! change as needed
pixelsize = 0.2                         # arcsec/pix
chipsizex = 4000                        # x-direction pixels   
sgapx = 225                             # x-direction gap between chips
rgapx = 25                              # x-direction gap between rafts
chipsizey = 4072                        # y-direction pixels
sgapy = 153                             # y-direction gap between chips
rgapy = 178                             # y-direction gap between rafts
optPSFsize = 0.35                       # from SRD (at zenith)
saturation = 100000                     # number of electrons @ full well
Filt=[ 'u','g','r','i','z','y4' ]
skysed='/nfs/slac/g/ki/ki06/lsst/chihway/phosim-v-3.2/data/sky/darksky_sed.txt'
filtdir='/nfs/slac/g/ki/ki06/lsst/chihway/phosim-v-3.2/data/lsst/'
seddir='/nfs/slac/g/ki/ki06/lsst/chihway/phosim-v-3.2/data/SEDs/'

# useful conversions
deg2pix=60.0*60.0/pixelsize
deg2rad=1.0/180.0*numpy.pi
arcsec2deg=1.0/60.0/60.0

logging.basicConfig(level=logging.INFO, stream=sys.stdout, format='%(message)s') 
#filename='phosim2galsim_catalog.log', filemode='w',
logger = logging.getLogger() 

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
      rx=int(str(inlines[i].split()[1])[1])
      ry=int(str(inlines[i].split()[1])[2])
      sx=int(str(inlines[i].split()[1])[5])
      sy=int(str(inlines[i].split()[1])[6])
      # save parameter for later use
      string='rx '+str(rx)+'\n'
      logger.info(string)
      outfile1.write(string)
      string='ry '+str(ry)+'\n'
      logger.info(string)
      outfile1.write(string)
      string='sx '+str(sx)+'\n'
      logger.info(string)
      outfile1.write(string)
      string='sy '+str(sy)+'\n'
      logger.info(string)
      outfile1.write(string)

sky_count = magNorm2LSSTFlux.magNorm2LSSTFlux(str(skysed), str(filtdir)
  +'total_'+str(Filt[filt])+'.dat', zenith_v, 0.0) * pixelsize**2                 
# counts per pixels (the counts look low... need checking!)
string='sky_count '+str(sky_count)+'\n'
logger.info(string)
outfile1.write(string)

string='optseeing '+str(optPSFsize)+'\n'
logger.info(string)
outfile1.write(string)

string='pixelsize '+str(pixelsize)+'\n'
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

string='saturation '+str(saturation)+'\n'
logger.info(string)
outfile1.write(string)

logger.info("Figure out the center coordinate for this chip \
                 (flat sky approximation! can be off at edge of field).")

dxchip = (chipsizex+sgapx)*pixelsize*arcsec2deg
dychip = (chipsizey+sgapy)*pixelsize*arcsec2deg
dxraft = (rgapx)*pixelsize*arcsec2deg
dyraft = (rgapy)*pixelsize*arcsec2deg
center=findchipcenter(pointingra, pointingdec, rotationangle,  
         rx, ry, sx, sy, dxchip, dychip, dxraft, dyraft)
chipcenterx=center[0]        # chip center x in deg
chipcentery=center[1]        # chip center y in deg
#print center

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
      logger.debug("Rotate and shift position so that image is centerd with chip.")
      galsim_x_norot=(phosim_ra-chipcenterx)*deg2pix+(chipsizex/2)   # is this right?
      galsim_y_norot=(phosim_dec-chipcentery)*deg2pix+(chipsizey/2)
      #print galsim_x_norot, galsim_y_norot
      galsim_coor=rotate(galsim_x_norot, galsim_y_norot, rotationangle*deg2rad)
      galsim_x= galsim_coor[0]
      galsim_y= galsim_coor[1]
      #print galsim_x, galsim_y
        
      if (galsim_x>=0 and galsim_x<=chipsizex and galsim_y>=0 and galsim_y<=chipsizey):
        # magnitude conversion, copy SED over 
        os.system('cp '+str(seddir)+str(phosim_sed)+' tempspec_R'+str(rx)+str(ry)+'_S'+str(sx)+str(sy)+'.gz')
        os.system('gunzip tempspec_R'+str(rx)+str(ry)+'_S'+str(sx)+str(sy)+'.gz')
        galsim_flux=magNorm2LSSTFlux.magNorm2LSSTFlux('tempspec_R'+str(rx)+str(ry)+'_S'+str(sx)+str(sy), 
                   str(filtdir)+'total_'+str(Filt[filt])+'.dat', 
                   phosim_mag, phosim_z) * pixelsize**2   
        os.system('rm -f tempspec_R'+str(rx)+str(ry)+'_S'+str(sx)+str(sy))

        # shear is defined in telescope coordinate, so this needs to be rotated as well
        logger.debug("Rotate shear as well.")
        galsim_kappa=phosim_kappa
        galsim_gamma=rotateshear(phosim_gamma1, phosim_gamma2, rotationangle*deg2rad)
        galsim_gamma1=galsim_gamma[0]
        galsim_gamma2=galsim_gamma[1]

        if ( str(inlines[i].split()[12]) == 'sersic2D' and galsim_flux>1):
          phosim_a=float(inlines[i].split()[13])
          phosim_b=float(inlines[i].split()[14])
          phosim_theta=float(inlines[i].split()[15])
          phosim_n=float(inlines[i].split()[16])
          string=str(phosim_id)+'\t'+'Sersic'+'\t'+str(galsim_x)+'\t'+str(galsim_y) \
                +'\t'+str(phosim_z)+'\t'+str(galsim_flux)+'\t'+str(phosim_a)        \
                +'\t'+str(phosim_b)+'\t'+str(phosim_theta)+'\t'+str(phosim_n)       \
                +'\t'+str(galsim_kappa)+'\t'+str(galsim_gamma1)+'\t'+str(galsim_gamma2)+'\n'
          #print string
          outfile2.write(string)
   
        if ( str(inlines[i].split()[12]) == 'point' and galsim_flux>1):
          string=str(phosim_id)+'\t'+'Star'+'\t'+str(galsim_x)+'\t'+str(galsim_y) \
                +'\t'+str(galsim_flux)+'\n'
          #print string
          outfile3.write(string)
 
    outfile2.close()
    outfile3.close()
