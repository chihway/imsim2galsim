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
files=($(find . -name "*.gz"))

cd /nfs/slac/g/ki/ki08/chihway/imsim2galsim/work
for item in ${files[*]}
do

item2=${item:2}
if [ ! -f /nfs/slac/g/ki/ki08/chihway/imsim2galsim/input/mag2flux/galaxySED/${item2%.gz} ]
then

#echo $item
#echo ${files[item]}
bsub -q kipac-ibq -o ../log/log_${item:2} /afs/slac/g/ki/software/python/2.7.3/bin/python /nfs/slac/g/ki/ki08/chihway/imsim2galsim/bin/phosim_mag2flux.py galaxySED ${item:2} 50

sleep 0.5

fi

done

# ssm
cd /nfs/slac/g/ki/ki08/chihway/SEDs/ssmSED
files=($(find . -name "*.gz"))

cd /nfs/slac/g/ki/ki08/chihway/imsim2galsim/work
for item in ${files[*]}
do

item2=${item:2}
if [ ! -f /nfs/slac/g/ki/ki08/chihway/imsim2galsim/input/mag2flux/ssmSED/${item2%.gz} ]
then

#echo $item
#echo ${files[item]}
bsub -q kipac-ibq -o ../log/log_${item:2} /afs/slac/g/ki/software/python/2.7.3/bin/python /nfs/slac/g/ki/ki08/chihway/imsim2galsim/bin/phosim_mag2flux.py ssmSED ${item:2} 1

sleep 0.5

fi

done

# stars
for startype in gizis_SED kurucz mlt wDs
do

cd /nfs/slac/g/ki/ki08/chihway/SEDs/starSED/${startype}
files=($(find . -name "*.gz"))

cd /nfs/slac/g/ki/ki08/chihway/imsim2galsim/work
for item in ${files[*]}
do

item2=${item:2}
if [ ! -f /nfs/slac/g/ki/ki08/chihway/imsim2galsim/input/mag2flux/starSED/${startype}/${item2%.gz} ]
then

#echo $item
#echo ${files[item]}
bsub -q xxl -o ../log/log_${item:2} /afs/slac/g/ki/software/python/2.7.3/bin/python /nfs/slac/g/ki/ki08/chihway/imsim2galsim/bin/phosim_mag2flux.py starSED/${startype} ${item:2} 1

sleep 0.1

fi

done
done

