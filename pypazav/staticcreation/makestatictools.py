"""
Created on Thu Jan 30 10:13:51 2020
STATIC CREATION FILE TURNED INTO FUNCTIONS

"""

def loadascgeodata(filename):
    '''
    either use geodatatools which return an array anyway or use this to import from .asc files.
    loads a <filename>.asc geodata file and returns the data as a numpy array, the x and y coordinates
    of the origin (lower left corner of the area) and its resolution (pixel size). 
    Returns tuple (array, xll, yll, res). 
    
    Example usage: topo,xorig,yorig,_ = loadascgeodata('test.asc')
    -> Imports the data from test.asc and drops the altitude info in topo, its origin to xorig and yorig
    and omits the output of the resolution (by specifying "_"),
    
    Parameters
    ----------
    filename : string
        file name or path to file respectively.

    Returns
    -------
    arr : np.array
        raster information as numpy array.
    xll : float
        x coordinate of the lower left corner of the data in the file.
    yll : float
        y coordinate of the lower left corner of the data in the file.
    res : float
        pixel width of the data contained in the file.
        
    '''
    import numpy as np
    arr = np.loadtxt(filename, skiprows=6) #a ascii geodata file has 6 header rows with metadata
    xll = np.loadtxt(filename, max_rows=6, usecols=(1))[2] #x coord of lower left point
    yll = np.loadtxt(filename, max_rows=6, usecols=(1))[3] #x coord of lower left point
    res = np.loadtxt(filename, max_rows=6, usecols=(1))[4] #x coord of lower left point
    print('\nLoaded Geodata contained in File:\t'+str(filename)+'\nCoordinates of LL corner:\t\t '+str(xll)+
          ' / '+str(yll)+'\nGrid Resolution:\t\t\t'+str(res)+'\nArray Shape:\t\t\t\t'+str(arr.shape))
    return arr,xll,yll,res


def shifttopodown(arr):
    '''
    shifts topography array down so lowest value is 0. Subtracts the minimum value from the specified input array.

    example usage: topo = shifttopodown(topo)
    
    Parameters
    ----------
    arr : np.array
        Topography as numpy array.

    Returns
    -------
    normed : np.array
        Array shifted down by amount.
        
    '''
    import numpy as np
    amount = arr.min()
    normed = arr - amount
    print('Shifted the input array downwards by '+str(np.round(amount,3))+' meters.')
    return normed


def childifyfilename(fileout, ischild):
    '''
    Modifies filename according to ischild identifier (if child 1 -> _N02) addendm to filename.

    Parameters
    ----------
    fileout : str
        original fileoutname (<RUN>_static).
    ischild : int
        running number of child ID.

    Returns
    -------
    newname : str
        added _NXX to the fileout name.

    '''
    if ischild != 0:
        newname = fileout+'_N0'+str(ischild+1)
    else:
        newname = fileout
    return newname


#%%
#params for createstaticfile

ischild = 0


def mapbbclasses(bbarr):
    '''
    Take the TLM bodenbedeckung as numpy array (see geodatatools.py or loadascgeodata())
    and translate the tlm classes into palm classes. This works based on the Bodenbedeckung-
    Dataset so far. The pavement-array is empty for now - use other functions to define pavements.

    Parameters
    ----------
    bbarr : np.arr
        numpy array of TLM bodenbedeckung.

    Returns
    -------
    vegarr : np.arr
        vegetation classification for palm.
    pavarr : np.arr
        pavement classification for palm. returned empty so far.
    watarr : np.arr
        water classification for palm.

    '''
    import numpy as np
    
    #vegetation array
    vegarr = np.ones(bbarr.shape)*-127
    vegarr[bbarr==0]   = 3  # unclassified > short grass
    vegarr[bbarr==1]   = 9  # fels > desert
    vegarr[bbarr==6]   = 16 # gebueschwald > deciduous shrubs
    vegarr[bbarr==7]   = 9  # lockergestein > desert
    vegarr[bbarr==9]   = 13 # Gletscher > ice caps and glaciers
    vegarr[bbarr==11]  = 14 # Feuchtgebiet > bogs and marshes
    vegarr[bbarr==12]  = 17 # Wald > mixed Forest/woodland
    vegarr[bbarr==13]  = 18 # Wald offen > interrupted forest

    #pavement array
    pavarr = np.ones(bbarr.shape)*-127
    # pavarr[arr==7]   = 9

    #water array
    watarr = np.ones(bbarr.shape)*-127
    watarr[bbarr==5]   = 2 #fliessgewaesser > river
    watarr[bbarr==10]  = 1 #stehendes gewaesser > lake

    #soiltype array
    soilarr = np.ones(bbarr.shape)*-127
    soilarr[bbarr==0] = 2 #medium
    soilarr[bbarr==1] = 1 #coarse
    soilarr[bbarr==5] = 2 #
    soilarr[bbarr==6] = 2 #
    soilarr[bbarr==7] = 1 #
    soilarr[bbarr==9] = 1 #
    soilarr[bbarr==11] = 1 #
    soilarr[bbarr==12] = 1 #
    soilarr[bbarr==13] = 1 #

       
    print(np.unique(vegarr))
    print(np.unique(pavarr))
    print(np.unique(watarr))
    print(np.unique(soilarr))
    
    #pavearr can be processed further in other functions with more tlm datasets.
    #if modified -> change function header info.
        
    return vegarr,pavarr,watarr


def makesurffractarray(vegarr,pavarr,watarr):
    '''
    Takes vegetation, pavement and water classification arrays for palm, creates a
    surface fraction array out of it.

    Parameters
    ----------
    vegarr : np.array
        vegetation classification array.
    pavarr : np.array
        pavement classification array.
    watarr : np.array
        water classification array.

    Returns
    -------
    sfr : np.array
        surface fraction array

    '''
    import numpy as np
    sfr = np.ones((3,vegarr.shape[0], vegarr.shape[1]))
    sfrveg = np.ones(vegarr.shape)
    sfrveg[vegarr != -127] = 1
    sfrveg[vegarr == -127] = 0
    sfrpav = np.ones(pavarr.shape)
    sfrpav[pavarr != -127] = 1
    sfrpav[pavarr == -127] = 0
    sfrwat = np.ones(watarr.shape)
    sfrwat[watarr != -127] = 1
    sfrwat[watarr == -127] = 0
    sfr[0,:,:] = sfrveg
    sfr[1,:,:] = sfrpav
    sfr[2,:,:] = sfrwat
    return sfr









def createstaticfile():
    import xarray as xr
    


























