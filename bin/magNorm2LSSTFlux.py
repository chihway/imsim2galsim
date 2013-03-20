import numpy as np

def _AB(wave, flambda, wave0):
    """Returns the AB magnitude at wave0 (nm) of spectrum specified by
    SEDwave (in nm), and flambda (in erg/s/cm^2/Ang).
    """
    speedOfLight = 2.99792458e18 # units are Angstrom Hz
    fNu = flambda * (wave * 10)**2 / speedOfLight # wave from nm -> Angstrom
    AB = -2.5 * np.log10(np.interp(wave0, wave, fNu)) - 48.6
    return AB

def _integratedFlux(wave, flambda, filterWave, filterThroughput, expTime=15.0, effDiam=670):
    """Integrates product of SED and filter throughput, and multiplies
    by typical LSST exposure time (in seconds) and collecting area
    (specified by effective diameter in cm) to estimate the number of
    photons collected by CCD.

    Units
    -----

    wave, filterWave : nm
    flambda : erg/s/cm^2/Ang
    filterThroughput : dimensionless
    expTime : seconds
    effDiam : cm (effective diameter of aperture)
    """
    waveUnion = np.union1d(wave, filterWave) #note union1d sorts its output
    flambdaInterp = np.interp(waveUnion, wave, flambda)
    ThroughputInterp = np.interp(waveUnion, filterWave, filterThroughput)
    dWave = waveUnion[1:] - waveUnion[0:-1]
    dWave = np.append(dWave, dWave[-1])
    dWave *= 10 # nm -> Ang
    hc = 1.98644521e-9 # (PlanckConstant * speedOfLight) in erg nm
    photonRate = (flambdaInterp * ThroughputInterp * (waveUnion / hc) * dWave).sum() # photons/sec/cm2
    return photonRate * np.pi * (effDiam / 2)**2 * expTime # photons!


def magNorm2LSSTFlux(SEDFile, filterFile, magNorm, redshift=0.0):
    """Predict LSST PhoSim flux (in total number of collected photons)
    for an object with SED specified by SEDFile through a filter
    specified by filterFile, and a PhoSim normalization of magNorm.

    The format of the SEDFile is 2 columns with first column the
    wavelength in nm, and the second column the flambda flux in
    erg/s/cm2/Ang.

    The format of the filterFile is 2 columns with first column the
    wavelength in nm and the second column the throughput (assumed to
    be everything: sky, filter, CCD, etc.) in fraction of
    above-atmosphere photons eventually accepted.
    """
    SEDData = np.genfromtxt(SEDFile)
    SEDWave = SEDData[:,0]
    SEDFlambda = SEDData[:,1]
    filterData = np.genfromtxt(filterFile)
    filterWave = filterData[:,0]
    filterThroughput = filterData[:,1]

    AB = _AB(SEDWave, SEDFlambda, 500.0)
    flux = _integratedFlux(SEDWave * (1.0 + redshift), SEDFlambda / (1.0 + redshift), filterWave, filterThroughput)
    return flux * 10**(-0.4 * (magNorm - AB)) * 0.76 #empirical fudge factor!

if __name__ == "__main__":
    print magNorm2LSSTFlux("../../data/SEDs/PB12/KIN_Sa_ext.ascii", "filters/LSST_g.dat", 19.945, 0.0)
    print magNorm2LSSTFlux("../../data/SEDs/PB12/KIN_Sa_ext.ascii", "filters/LSST_g.dat", 16.946, 1.0)
