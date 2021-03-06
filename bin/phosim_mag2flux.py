
# 2013-06-24 Chihway Chang
#
# Purpose:
# See run_phosim_mag2flux.sh
# 
# Output: 
# File names are the same as that of the SED name and in each file there 
# are 3 columns (filter, redshift, # photons). For stars all redshift=0.
# We consider (for galaxies) from redshift 0 to 5 (?) with intervals of 
# 0.1, that gives 50 redshift bins times 6 filters. 
#

import numpy, os, sys
import magNorm2LSSTFlux

Filt=[ 'u','g','r','i','z','y4' ]
skysed='/nfs/slac/g/ki/ki06/lsst/chihway/phosim-v-3.2/data/sky/darksky_sed.txt'
filtdir='/nfs/slac/g/ki/ki06/lsst/chihway/phosim-v-3.2/data/lsst/'
seddir='/nfs/slac/g/ki/ki06/lsst/chihway/phosim-v-3.2/data/SEDs/'
outdir='/nfs/slac/g/ki/ki08/chihway/imsim2galsim/input/mag2flux'
pixelsize=0.2

subseddir=str(sys.argv[1])
sedfile=str(sys.argv[2])
Nzbines=int(sys.argv[3])

outfilename=str(outdir)+'/'+str(subseddir)+'/'+str(sedfile[:-3])
if os.path.isfile(outfilename):
  os.remove(outfilename)
outfile=open(outfilename,'a')
for filt in range(6):
  for zbin in range(Nzbines):
    z=zbin*0.1
    os.system('cp '+str(seddir)+'/'+str(subseddir)+'/'+str(sedfile)+' tempspec_'+str(sedfile))
    os.system('gunzip tempspec_'+str(sedfile))
    galsim_flux=magNorm2LSSTFlux.magNorm2LSSTFlux('tempspec_'+str(sedfile[:-3]), str(filtdir)+'total_'+str(Filt[filt])+'.dat', 20.0, z) * pixelsize**2   
    os.system('rm -f tempspec_'+str(sedfile[:-3]))
    outfile.write(str(filt)+'\t'+str(z)+'\t'+str(galsim_flux)+'\n')
    #print galsim_flux
outfile.close()

