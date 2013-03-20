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
# Usage:
# print help message?

import os, numpy, sys
import magNorm2LSSTFlux         

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

pixelscale=0.2
chipsize=4072
optPSFsize=0.35
Filt=[ 'u','g','r','i','z','y4' ]
skysed='/nfs/slac/g/ki/ki06/lsst/chihway/phosim-v-3.2/data/sky/darksky_sed.txt'
filtdir='/nfs/slac/g/ki/ki06/lsst/chihway/phosim-v-3.2/data/lsst/'
seddir='/nfs/slac/g/ki/ki06/lsst/chihway/phosim-v-3.2/data/SEDs/'

print "reading in the parameters from "+str(infilename)
print "this may take a while..."

# first pass going through to grab observation parameters
for i in range(len(inlines)): 
  if (len(inlines[i].split())>=2):

    if (inlines[i].split()[0]=='obshistid'):
      string='obshistid '+str(inlines[i].split()[1])+'\n'
      print string
      outfile1.write(string)

    if (inlines[i].split()[0]=='altitude'):
      altitude=float(inlines[i].split()[1])
      airmass=1.0/numpy.cos(90.0-altitude)         
      # save parameter for later use
      string='airmass '+str(airmass)+'\n'
      print string
      outfile1.write(string)
   
    if (inlines[i].split()[0]=='rotationangle'):
      rotationangle=float(inlines[i].split()[1])
      # save parameter for later use
      string='rotationangle '+str(rotationangle)+'\n'
      print string
      outfile1.write(string)

    if (inlines[i].split()[0]=='pointingra'):
      pointingra=float(inlines[i].split()[1])
      # save parameter for later use
      string='pointingra '+str(pointingra)+'\n'
      print string
      outfile1.write(string)

    if (inlines[i].split()[0]=='pointingdec'):
      pointingdec=float(inlines[i].split()[1])
      # save parameter for later use
      string='pointingdec '+str(pointingdec)+'\n'
      print string
      outfile1.write(string)

    if (inlines[i].split()[0]=='obsseed'):
      string='obsseed '+str(inlines[i].split()[1])+'\n'
      print string
      outfile1.write(string)

    if (inlines[i].split()[0]=='filter'):
      filt=int(inlines[i].split()[1])
      # save parameter for later use
      string='filter '+str(filt)+'\n'
      print string
      outfile1.write(string)

    if (inlines[i].split()[0]=='totalseeing'):
      atmseeing=float(inlines[i].split()[1])
      # save parameter for later use
      string='atmseeing '+str(atmseeing)+'\n'
      print string
      outfile1.write(string)
  
    if (inlines[i].split()[0]=='zenith_v'):
      zenith_v=float(inlines[i].split()[1])
      # save parameter for later use
  
sky_count = magNorm2LSSTFlux.magNorm2LSSTFlux(str(skysed), str(filtdir)+'total_'+str(Filt[filt])+'.dat', zenith_v, 0.0) * pixelscale**2                 
# counts per pixels (the counts look low... need checking!)
string='sky_count '+str(sky_count)+'\n'
print string
outfile1.write(string)

totalseeing = ((atmseeing*airmass**0.6)**2+(optPSFsize*airmass**0.6)**2)**0.5
# adding the optics in quadrature
string='seeing '+str(totalseeing)+'\n'
print string
outfile1.write(string)

string='pixelsize '+str(pixelscale)+'\n'
print string
outfile1.write(string)

string='chipsize '+str(chipsize)+'\n'
print string
outfile1.write(string)

outfile1.close()

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
      galsim_x=(phosim_ra-pointingra)*60*60/0.2+(chipsize/2)
      galsim_y=(phosim_dec-pointingdec)*60*60/0.2+(chipsize/2)
      #print galsim_x, galsim_y
        
      if (galsim_x>=0 and galsim_x<=chipsize and galsim_y>=0 and galsim_y<=chipsize):
        os.system('gunzip '+str(seddir)+str(phosim_sed))
        galsim_flux=magNorm2LSSTFlux.magNorm2LSSTFlux(str(seddir)+str(phosim_sed)[:-3], str(filtdir)+'total_'+str(Filt[filt])+'.dat', phosim_mag, phosim_z) * pixelscale**2   
        os.system('gzip '+str(seddir)+str(phosim_sed)[:-3])

        galsim_kappa=phosim_kappa
        galsim_gamma1=phosim_gamma1
        galsim_gamma2=phosim_gamma2

        if ( str(inlines[i].split()[12]) == 'sersic2D' and galsim_flux>1):
          phosim_a=float(inlines[i].split()[13])
          phosim_b=float(inlines[i].split()[14])
          phosim_theta=float(inlines[i].split()[15])
          phosim_n=float(inlines[i].split()[16])
          string=str(phosim_id)+'\t'+'Sersic'+'\t'+str(galsim_x)+'\t'+str(galsim_y)+'\t'+str(galsim_flux)+'\t'+str(phosim_a)+'\t'+str(phosim_b)+'\t'+str(phosim_theta)+'\t'+str(phosim_n)+'\n'
          #print string
          outfile2.write(string)
   
        if ( str(inlines[i].split()[12]) == 'point' and galsim_flux>1):
          string=str(phosim_id)+'\t'+'Star'+'\t'+str(galsim_x)+'\t'+str(galsim_y)+'\t'+str(galsim_flux)+'\n'
          #print string
          outfile3.write(string)
 
    outfile2.close()
    outfile3.close()
