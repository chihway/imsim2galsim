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
# - input PhoSim trimmed catalog
#
# Usage:
#   phosim2galsim_catalog2.py [switches] [input catalog] 
#          [output config file] [output galaxy file] [output star file]
#

import os, numpy, sys, logging

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
  " rotate an array of vectors"
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
if os.path.isfile('temp_star'):
  os.remove('temp_star')
if os.path.isfile('temp_gal'):
  os.remove('temp_gal')

outfile1=open(outfilename1,'a')         
outfile2=open(outfilename2,'a')
outfile3=open(outfilename3,'a')
tempoutfile2=open('temp_gal','a')
tempoutfile3=open('temp_star','a')

inlines=infile.readlines()

# hardcoded! change as needed
pixelsize = 0.2                         # arcsec/pix
chipsizex = 4000                        # x-direction pixels   
sgapx = 225                             # x-direction gap between chips
rgapx = 25                              # x-direction gap between rafts
chipsizey = 4072                        # y-direction pixels
sgapy = 153                             # y-direction gap between chips
rgapy = 25                              # (178?) y-direction gap between rafts
optPSFsize = 0.35                       # from SRD (at zenith)
saturation = 100000                     # number of electrons @ full well
Filt=[ 'u','g','r','i','z','y4' ]
skysed='/nfs/slac/g/ki/ki06/lsst/chihway/phosim-v-3.2/data/sky/darksky_sed.txt'
filtdir='/nfs/slac/g/ki/ki06/lsst/chihway/phosim-v-3.2/data/lsst/'
seddir='/nfs/slac/g/ki/ki06/lsst/chihway/phosim-v-3.2/data/SEDs/'
mag2fluxdir='/nfs/slac/g/ki/ki08/chihway/imsim2galsim/input/mag2flux/'

# useful conversions
deg2pix=60.0*60.0/pixelsize
deg2rad=1.0/180.0*numpy.pi
arcsec2deg=1.0/60.0/60.0

logging.basicConfig(level=logging.INFO, stream=sys.stdout, format='%(message)s') 
#filename='phosim2galsim_catalog.log', filemode='w',
logger = logging.getLogger() 

logger.info("reading in the observing parameters from "+str(infilename))
logger.info("and make two temp catalogs. This may take a while...")
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

    if (inlines[i].split()[0]=='vistime'):
      vistime=float(inlines[i].split()[1])
      # save parameter for later use

    if (inlines[i].split()[0]=='nsnap'):
      nsnap=float(inlines[i].split()[1])
      # save parameter for later use

    # makes these files for later use
    if (inlines[i].split()[0]=='object' and inlines[i].split()[12]=='point'):
      tempoutfile3.write(inlines[i])

    if (inlines[i].split()[0]=='object' and inlines[i].split()[12]=='sersic2D'):
      tempoutfile2.write(inlines[i])

# kill this for testing
#sky_count = magNorm2LSSTFlux.magNorm2LSSTFlux(str(skysed), str(filtdir)
#  +'total_'+str(Filt[filt])+'.dat', zenith_v, 0.0) * pixelsize**2 
sky_count=0
   
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

string='exptime '+str((vistime-3.0*(nsnap-1))/nsnap)+'\n'
logger.info(string)
outfile1.write(string)

logger.info("Figure out the center coordinate for this chip")
logger.info("(flat sky approximation! can be off at edge of field).")

dxchip = (chipsizex+sgapx)*pixelsize*arcsec2deg
dychip = (chipsizey+sgapy)*pixelsize*arcsec2deg
dxraft = (rgapx)*pixelsize*arcsec2deg
dyraft = (rgapy)*pixelsize*arcsec2deg
center=findchipcenter(pointingra, pointingdec, -1*rotationangle,  
         rx, ry, sx, sy, dxchip, dychip, dxraft, dyraft) 
                             # rotation angle goes the other direction!
chipcenterx=center[0]        # chip center x in deg
chipcentery=center[1]        # chip center y in deg
#print center

logger.info("Finish reading observing parameters and making temp catalogs.")
outfile1.close()
tempoutfile2.close()
tempoutfile3.close()

logger.info("Now get parameters from galaxies...")
# second pass going through to grab object parameters

galData=numpy.genfromtxt('temp_gal')
phosim_id=galData[:,1]
phosim_ra=galData[:,2]
phosim_dec=galData[:,3]
phosim_mag=galData[:,4]
phosim_z=galData[:,6]
phosim_kappa=galData[:,7]
phosim_gamma1=galData[:,8]
phosim_gamma2=galData[:,9]
phosim_a=galData[:,13]
phosim_b=galData[:,14]
phosim_theta=galData[:,15]
phosim_n=galData[:,16]

# add rotation (positions and shearing)!!
logger.info("Rotate and shift position so that image is centerd with chip.")
galsim_x_norot=(phosim_ra-chipcenterx)*deg2pix   # is this right?
galsim_y_norot=(phosim_dec-chipcentery)*deg2pix
#print galsim_x_norot, galsim_y_norot
galsim_coor=rotate(galsim_x_norot, galsim_y_norot, rotationangle*deg2rad)
galsim_x= galsim_coor[0]+(chipsizex/2)
galsim_y= galsim_coor[1]+(chipsizey/2)
#print galsim_x, galsim_y

# shear is defined in telescope coordinate, so this needs to be rotated as well
logger.info("Rotate shear as well.")
galsim_kappa=phosim_kappa
galsim_gamma=rotateshear(phosim_gamma1, phosim_gamma2, -1*rotationangle*deg2rad) # not tested yet
galsim_gamma1=galsim_gamma[0]
galsim_gamma2=galsim_gamma[1]

tempfile=open('temp_gal','r')
tempinlines=tempfile.readlines()
tempfile.close()
for i in range(len(phosim_id)):
  sed=str(tempinlines[i].split()[5])
  if (galsim_x[i]>=0 and galsim_x[i]<=chipsizex and galsim_y[i]>=0 and galsim_y[i]<=chipsizey):
    zbin=int(phosim_z[i]/0.1)
    flux1=float(open(str(mag2fluxdir)+str(sed)[:-3]).readlines()[filt*50+zbin][2])
    flux2=float(open(str(mag2fluxdir)+str(sed)[:-3]).readlines()[filt*50+zbin+1][2])
    galsim_flux=flux1+(flux2-flux1)*(phosim_z[i]-(zbin*0.1))/0.1
    print galsim_flux

    #if (galsim_flux>1):
    string=str(phosim_id[i])+'\t'+'Sersic'+'\t'+str(galsim_x[i])+'\t'+str(galsim_y[i])+'\t'+str(phosim_z[i])+'\t'+str(galsim_flux)+'\t'+str(phosim_a[i]) +'\t'+str(phosim_b[i])+'\t'+str(phosim_theta[i]-(rotationangle*deg2rad))+'\t'+str(phosim_n[i])+'\t'+str(galsim_kappa[i])+'\t'+str(galsim_gamma1[i])+'\t'+str(galsim_gamma2[i])+'\n'
    # note rotation angle, units change in the next phosim version
    outfile2.write(string)
outfile2.close()   

logger.info("Now get parameters from stars...")
# second pass going through to grab object parameters

starData=numpy.genfromtxt('temp_star')
phosim_id=starData[:,1]
phosim_ra=starData[:,2]
phosim_dec=starData[:,3]
phosim_mag=starData[:,4]
phosim_z=starData[:,6]

# add rotation (positions and shearing)!!
logger.debug("Rotate and shift position so that image is centerd with chip.")
galsim_x_norot=(phosim_ra-chipcenterx)*deg2pix   # is this right?
galsim_y_norot=(phosim_dec-chipcentery)*deg2pix
#print galsim_x_norot, galsim_y_norot
galsim_coor=rotate(galsim_x_norot, galsim_y_norot, rotationangle*deg2rad)
galsim_x= galsim_coor[0]+(chipsizex/2)
galsim_y= galsim_coor[1]+(chipsizey/2)
#print galsim_x, galsim_y

tempfile=open('temp_star','r')
tempinlines=tempfile.readlines()
tempfile.close()
for i in range(len(phosim_id)):
#for i in range(3000):
  sed=str(tempinlines[i].split()[5])
  if (galsim_x[i]>=0 and galsim_x[i]<=chipsizex and galsim_y[i]>=0 and galsim_y[i]<=chipsizey):
    galsim_flux=float(open(str(mag2fluxdir)+str(sed)[:-3]).readlines()[filt])[2]
    print galsim_flux

    #if (galsim_flux>1):
    string=str(phosim_id[i])+'\t'+'Star'+'\t'+str(galsim_x[i])+'\t'+str(galsim_y[i]) \
                +'\t'+str(galsim_flux)+'\n'
          #print string
    outfile3.write(string)
outfile3.close()
