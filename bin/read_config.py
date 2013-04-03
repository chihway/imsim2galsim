#! /bin/env python

# 2013-04-03
#
# Purpose:
# To read in the configuration file (produced from phosim2galsim_catalog.py) 
# and define all parameters needed. If parameter is missing in the config 
# file then use default values.
# 

def read_config(configfilename):

  # default values, in case there are missing information
  Id=9999
  Airmass=1.0
  Rot=0
  Ra=0
  Dec=0
  Seed=9999
  Filter=2
  Atmseeing=0.6
  Sky=0
  Rx=2
  Ry=2
  Sx=1
  Sy=1
  Saturation=1000000
  Chipsizex=4072
  Chipsizey=4072
  Pixelsize=0.2
  Optpsfsize=0.35
  Exptime=15.0

  # read in file and update parameter values
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
    if (parameter[0]=='sky_count'):   # how is moon included?
      Sky=int(float(parameter[1])) 
    if (parameter[0]=='rx'):
      Rx=int(float(parameter[1])) 
    if (parameter[0]=='ry'):
      Ry=int(float(parameter[1])) 
    if (parameter[0]=='sx'):
      Sx=int(float(parameter[1])) 
    if (parameter[0]=='sy'):
      Sy=int(float(parameter[1])) 
    if (parameter[0]=='saturation'):
      Saturation=int(parameter[1]) 
    if (parameter[0]=='chipsizex'):
      Chipsizex=int(parameter[1]) 
    if (parameter[0]=='chipsizey'):
      Chipsizey=int(parameter[1]) 
    if (parameter[0]=='pixelsize'):
      Pixelsize=float(parameter[1])
    if (parameter[0]=='optseeing'):
      Optpsfsize=float(parameter[1])
    if (parameter[0]=='exptime'):
      Exptime=float(parameter[1])
  return Id, Airmass, Rot, Ra, Dec, Seed, Filter, Atmseeing, Sky, Rx, Ry, Sx, Sy, Saturation, Chipsizex, Chipsizey, Pixelsize, Optpsfsize, Exptime
