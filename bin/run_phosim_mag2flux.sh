#! /bin/sh

# Purpose:
#
# Wrapper script to parallelize the phosim_mag2flux.py over all SEDs 
# Create files to convert the magnitude to flux using the ImSim SEDs 
# and LSST filters. (need to check whether all filters are implimented 
# correctly?) These will be used later to facilitate GalSim simulations. 
# All objects are specified at 20 mag.
#
#                                # of spectrums     # of calculations
# input/flatSED/                 ?                  ?
#       galaxySED/               960                288000
#       ssmSED/                  26                 26
#       starSED/gizis_SED/       21                 21
#               kurucz/          103987             103987
#               mlt/             739                739
#               wDs/             3378               3378
#

# galaxies
cd /nfs/slac/g/ki/ki08/chihway/SEDs/galaxySED
files=($(find -E . -type f -regex "*.gz"))

cd /nfs/slac/g/ki/ki08/chihway/imsim2galsim/work
for item in ${files[*]}
do

#bsub -q kipac-ibq 
/afs/slac/g/ki/software/python/2.7.3/bin/python phosim_mag2flux.py galaxySED item

done

# ssm

# stars